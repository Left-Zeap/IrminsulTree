"""
内存图存储 - 替代 Neo4j
使用字典存储，JSON 持久化，支持数据修复和分文件存储
"""
import json
import logging
import sys
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from datetime import datetime
import uuid

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import Node, Edge, NodeType, RelationType
from config import DATA_DIR, MAX_FILE_SIZE, MAX_NODES_PER_FILE, LOG_LEVEL

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GraphStorage:
    """图存储类 - 内存存储 + JSON 持久化（支持分文件）"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 主数据文件
        self.main_file = self.data_dir / "graph_data.json"
        # 分文件目录
        self.parts_dir = self.data_dir / "parts"
        self.parts_dir.mkdir(exist_ok=True)
        
        # 内存存储
        self.nodes: Dict[str, Node] = {}  # id -> Node
        self.edges: Dict[str, Edge] = {}  # id -> Edge
        
        # 索引
        self.node_name_index: Dict[Tuple[str, str], str] = {}  # (type, name) -> id
        self.adjacency: Dict[str, List[str]] = {}  # node_id -> [edge_id, ...]
        
        # 加载数据
        self.load()
    
    # ==================== 数据修复 ====================
    
    def _repair_node_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """修复节点数据，填充缺失字段"""
        repaired = dict(data)  # 复制原数据
        
        # 必需字段检查和修复
        if "id" not in repaired or not repaired["id"]:
            repaired["id"] = str(uuid.uuid4())[:8]
            logger.warning(f"Node missing id, assigned new id: {repaired['id']}")
        
        if "name" not in repaired or not repaired["name"]:
            repaired["name"] = "未命名节点"
            logger.warning(f"Node {repaired.get('id', '?')} missing name, using default")
        
        if "node_type" not in repaired or not repaired["node_type"]:
            repaired["node_type"] = "Entry"  # 默认类型
            logger.warning(f"Node {repaired['id']} missing type, using Entry")
        
        # 确保 node_type 是有效的
        valid_types = [t.value for t in NodeType]
        if repaired["node_type"] not in valid_types:
            logger.warning(f"Node {repaired['id']} has invalid type {repaired['node_type']}, using Entry")
            repaired["node_type"] = "Entry"
        
        # 列表字段修复
        list_fields = ["aliases", "sub_events", "sub_locations", "sub_quests", 
                      "sub_organizations", "poi_codes"]
        for field in list_fields:
            if field not in repaired or repaired[field] is None:
                repaired[field] = []
            elif not isinstance(repaired[field], list):
                # 如果不是列表，尝试转换或重置
                if isinstance(repaired[field], str):
                    repaired[field] = [repaired[field]] if repaired[field] else []
                else:
                    repaired[field] = []
        
        # 可选字符串字段修复
        optional_str_fields = ["category", "misc_category", "version"]
        for field in optional_str_fields:
            if field not in repaired:
                repaired[field] = None
        
        # 时间字段修复
        time_fields = ["birth_year", "death_year", "start_time", "end_time"]
        for field in time_fields:
            if field not in repaired or repaired[field] == "":
                repaired[field] = None
            # 尝试转换为整数
            elif repaired[field] is not None:
                try:
                    repaired[field] = int(repaired[field])
                except (ValueError, TypeError):
                    repaired[field] = None
        
        # 时间戳字段修复
        if "created_at" not in repaired or not repaired["created_at"]:
            repaired["created_at"] = datetime.now().isoformat()
        if "updated_at" not in repaired or not repaired["updated_at"]:
            repaired["updated_at"] = datetime.now().isoformat()
        
        # properties 字段
        if "properties" not in repaired or repaired["properties"] is None:
            repaired["properties"] = {}
        elif not isinstance(repaired["properties"], dict):
            repaired["properties"] = {}
        
        return repaired
    
    def _repair_edge_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """修复边数据，填充缺失字段"""
        repaired = dict(data)
        
        # 必需字段
        if "id" not in repaired or not repaired["id"]:
            repaired["id"] = str(uuid.uuid4())[:8]
        
        if "source_id" not in repaired or not repaired["source_id"]:
            logger.error("Edge missing source_id, skipping")
            return None  # 无法修复，返回 None 表示跳过
        
        if "target_id" not in repaired or not repaired["target_id"]:
            logger.error("Edge missing target_id, skipping")
            return None
        
        if "rel_type" not in repaired or not repaired["rel_type"]:
            repaired["rel_type"] = "ASSOCIATED_WITH"  # 默认关系
            logger.warning(f"Edge {repaired['id']} missing rel_type, using default")
        
        # 确保 rel_type 有效
        valid_rels = [r.value for r in RelationType]
        if repaired["rel_type"] not in valid_rels:
            logger.warning(f"Edge {repaired['id']} has invalid rel_type, using default")
            repaired["rel_type"] = "ASSOCIATED_WITH"
        
        # direction 字段
        if "direction" not in repaired or repaired["direction"] not in ["directed", "undirected"]:
            repaired["direction"] = "directed"
        
        # label 字段修复
        if "label" not in repaired:
            repaired["label"] = None
        elif isinstance(repaired["label"], list):
            # 转换列表为元组格式
            if len(repaired["label"]) == 2:
                try:
                    start = int(repaired["label"][0]) if repaired["label"][0] is not None else None
                    end = int(repaired["label"][1]) if repaired["label"][1] is not None else None
                    repaired["label"] = (start, end)
                except (ValueError, TypeError):
                    repaired["label"] = str(repaired["label"])
            else:
                repaired["label"] = str(repaired["label"])
        
        # 时间戳
        if "created_at" not in repaired or not repaired["created_at"]:
            repaired["created_at"] = datetime.now().isoformat()
        
        # properties
        if "properties" not in repaired or repaired["properties"] is None:
            repaired["properties"] = {}
        elif not isinstance(repaired["properties"], dict):
            repaired["properties"] = {}
        
        return repaired
    
    # ==================== 持久化 ====================
    
    def load(self):
        """从 JSON 文件加载数据（支持分文件）"""
        # 首先尝试加载主文件
        if self.main_file.exists():
            try:
                self._load_from_file(self.main_file)
                logger.info(f"Loaded from main file: {self.main_file}")
            except Exception as e:
                logger.error(f"Error loading main file: {e}")
        
        # 然后加载分文件
        part_files = sorted(self.parts_dir.glob("graph_data_part_*.json"))
        for part_file in part_files:
            try:
                self._load_from_file(part_file)
                logger.info(f"Loaded from part file: {part_file}")
            except Exception as e:
                logger.error(f"Error loading part file {part_file}: {e}")
        
        logger.info(f"Total loaded: {len(self.nodes)} nodes and {len(self.edges)} edges")
    
    def _load_from_file(self, file_path: Path):
        """从单个文件加载数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 加载节点
        for node_data in data.get('nodes', []):
            try:
                # 修复数据
                repaired_data = self._repair_node_data(node_data)
                node = Node(**repaired_data)
                self.nodes[node.id] = node
                self.node_name_index[(node.node_type.value, node.name)] = node.id
            except Exception as e:
                logger.error(f"Error loading node {node_data.get('id', '?')}: {e}")
        
        # 加载边
        for edge_data in data.get('edges', []):
            try:
                # 修复数据
                repaired_data = self._repair_edge_data(edge_data)
                if repaired_data is None:  # 无法修复，跳过
                    continue
                edge = Edge(**repaired_data)
                self.edges[edge.id] = edge
                self._update_adjacency(edge)
            except Exception as e:
                logger.error(f"Error loading edge {edge_data.get('id', '?')}: {e}")
    
    def save(self):
        """保存数据到 JSON 文件（自动分文件）"""
        try:
            # 准备数据
            nodes_list = [n.to_dict() for n in self.nodes.values()]
            edges_list = [e.to_dict() for e in self.edges.values()]
            
            # 检查是否需要分文件
            total_size = len(json.dumps({"nodes": nodes_list, "edges": edges_list}))
            need_split = (total_size > MAX_FILE_SIZE or 
                         len(nodes_list) > MAX_NODES_PER_FILE)
            
            if need_split:
                self._save_split_files(nodes_list, edges_list)
            else:
                # 保存到单个文件
                data = {
                    "nodes": nodes_list,
                    "edges": edges_list,
                    "metadata": {
                        "saved_at": datetime.now().isoformat(),
                        "total_nodes": len(nodes_list),
                        "total_edges": len(edges_list),
                        "version": "1.0"
                    }
                }
                
                with open(self.main_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # 清理旧的分文件
                self._clean_part_files()
                
                logger.info(f"Saved to main file: {len(nodes_list)} nodes, {len(edges_list)} edges")
        
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise
    
    def _save_split_files(self, nodes_list: List[Dict], edges_list: List[Dict]):
        """分文件保存大数据"""
        # 清理旧文件
        self._clean_part_files()
        
        # 计算分片
        num_parts = max(
            len(nodes_list) // MAX_NODES_PER_FILE + 1,
            2  # 至少分成2个文件
        )
        nodes_per_part = len(nodes_list) // num_parts + 1
        
        # 创建节点ID到分片的映射
        node_id_to_part: Dict[str, int] = {}
        for i, node in enumerate(nodes_list):
            part_idx = i // nodes_per_part
            node_id_to_part[node['id']] = part_idx
        
        # 按分片组织节点
        parts_nodes: Dict[int, List[Dict]] = {i: [] for i in range(num_parts)}
        for node in nodes_list:
            part_idx = node_id_to_part.get(node['id'], 0)
            parts_nodes[part_idx].append(node)
        
        # 按分片组织边（根据源节点）
        parts_edges: Dict[int, List[Dict]] = {i: [] for i in range(num_parts)}
        for edge in edges_list:
            part_idx = node_id_to_part.get(edge['source_id'], 0)
            parts_edges[part_idx].append(edge)
        
        # 保存每个分片
        for part_idx in range(num_parts):
            part_data = {
                "nodes": parts_nodes[part_idx],
                "edges": parts_edges[part_idx],
                "metadata": {
                    "part_index": part_idx,
                    "total_parts": num_parts,
                    "saved_at": datetime.now().isoformat(),
                    "total_nodes_in_part": len(parts_nodes[part_idx]),
                    "total_edges_in_part": len(parts_edges[part_idx])
                }
            }
            
            part_file = self.parts_dir / f"graph_data_part_{part_idx:03d}.json"
            with open(part_file, 'w', encoding='utf-8') as f:
                json.dump(part_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved part {part_idx}: {len(parts_nodes[part_idx])} nodes, "
                       f"{len(parts_edges[part_idx])} edges")
        
        # 保存索引文件
        index_data = {
            "is_split": True,
            "total_parts": num_parts,
            "total_nodes": len(nodes_list),
            "total_edges": len(edges_list),
            "saved_at": datetime.now().isoformat(),
            "node_distribution": {str(k): len(v) for k, v in parts_nodes.items()}
        }
        
        with open(self.data_dir / "index.json", 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        # 删除主文件（使用分文件模式）
        if self.main_file.exists():
            self.main_file.unlink()
        
        logger.info(f"Data split into {num_parts} files")
    
    def _clean_part_files(self):
        """清理旧的分文件"""
        for part_file in self.parts_dir.glob("graph_data_part_*.json"):
            part_file.unlink()
        index_file = self.data_dir / "index.json"
        if index_file.exists():
            index_file.unlink()
    
    def _update_adjacency(self, edge: Edge):
        """更新邻接表"""
        if edge.source_id not in self.adjacency:
            self.adjacency[edge.source_id] = []
        self.adjacency[edge.source_id].append(edge.id)
        
        if edge.direction == "undirected":
            if edge.target_id not in self.adjacency:
                self.adjacency[edge.target_id] = []
            self.adjacency[edge.target_id].append(edge.id)
    
    # ==================== 节点操作 ====================
    
    def create_node(self, node: Node) -> str:
        """创建节点"""
        # 检查同名节点
        key = (node.node_type.value, node.name)
        if key in self.node_name_index:
            # 更新现有节点
            existing_id = self.node_name_index[key]
            existing = self.nodes[existing_id]
            # 合并数据
            for field, value in node.model_dump().items():
                if value is not None and field not in ['id', 'created_at']:
                    setattr(existing, field, value)
            existing.updated_at = datetime.now().isoformat()
            self.save()
            return existing_id
        
        # 创建新节点
        self.nodes[node.id] = node
        self.node_name_index[key] = node.id
        self.save()
        return node.id
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """获取节点"""
        return self.nodes.get(node_id)
    
    def get_node_by_name(self, node_type: str, name: str) -> Optional[Node]:
        """通过名称获取节点"""
        key = (node_type, name)
        node_id = self.node_name_index.get(key)
        if node_id:
            return self.nodes.get(node_id)
        return None
    
    def update_node(self, node_id: str, updates: Dict[str, Any]) -> bool:
        """更新节点"""
        node = self.nodes.get(node_id)
        if not node:
            return False
        
        for field, value in updates.items():
            if hasattr(node, field) and field not in ['id', 'created_at']:
                setattr(node, field, value)
        
        node.updated_at = datetime.now().isoformat()
        self.save()
        return True
    
    def delete_node(self, node_id: str) -> bool:
        """删除节点及其关系"""
        if node_id not in self.nodes:
            return False
        
        node = self.nodes[node_id]
        
        # 删除相关边
        edges_to_remove = []
        for edge_id, edge in self.edges.items():
            if edge.source_id == node_id or edge.target_id == node_id:
                edges_to_remove.append(edge_id)
        
        for edge_id in edges_to_remove:
            self.delete_edge(edge_id)
        
        # 删除节点
        del self.nodes[node_id]
        key = (node.node_type.value, node.name)
        if key in self.node_name_index:
            del self.node_name_index[key]
        
        self.save()
        return True
    
    def search_nodes(self, 
                     node_type: Optional[str] = None,
                     name_pattern: Optional[str] = None,
                     limit: int = 100) -> List[Node]:
        """搜索节点"""
        results = []
        
        for node in self.nodes.values():
            # 类型筛选
            if node_type and node.node_type.value != node_type:
                continue
            
            # 名称筛选
            if name_pattern:
                if name_pattern.lower() not in node.name.lower():
                    # 也搜索别名
                    aliases_match = any(name_pattern.lower() in alias.lower() 
                                       for alias in node.aliases)
                    if not aliases_match:
                        continue
            
            results.append(node)
            if len(results) >= limit:
                break
        
        return results
    
    def get_all_nodes(self, node_type: Optional[str] = None) -> List[Node]:
        """获取所有节点"""
        if node_type:
            return [n for n in self.nodes.values() if n.node_type.value == node_type]
        return list(self.nodes.values())
    
    # ==================== 边操作 ====================
    
    def create_edge(self, edge: Edge) -> str:
        """创建边"""
        # 检查节点是否存在
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            raise ValueError("Source or target node does not exist")
        
        self.edges[edge.id] = edge
        self._update_adjacency(edge)
        self.save()
        return edge.id
    
    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """获取边"""
        return self.edges.get(edge_id)
    
    def get_node_edges(self, node_id: str, direction: str = "both") -> List[Edge]:
        """获取节点的边"""
        results = []
        
        for edge in self.edges.values():
            if direction in ["out", "both"] and edge.source_id == node_id:
                results.append(edge)
            elif direction in ["in", "both"] and edge.target_id == node_id:
                results.append(edge)
            elif direction == "both" and edge.direction == "undirected":
                if edge.source_id == node_id or edge.target_id == node_id:
                    if edge not in results:
                        results.append(edge)
        
        return results
    
    def delete_edge(self, edge_id: str) -> bool:
        """删除边"""
        if edge_id not in self.edges:
            return False
        
        del self.edges[edge_id]
        # 重建邻接表
        self.adjacency = {}
        for edge in self.edges.values():
            self._update_adjacency(edge)
        
        self.save()
        return True
    
    # ==================== 图算法 ====================
    
    def find_path(self, source_id: str, target_id: str, 
                  max_depth: int = 5) -> Optional[List[Edge]]:
        """使用 BFS 查找最短路径"""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None
        
        from collections import deque
        
        # BFS
        queue = deque([(source_id, [])])
        visited = {source_id}
        
        while queue:
            current_id, path = queue.popleft()
            
            if len(path) > max_depth:
                continue
            
            if current_id == target_id and path:
                return path
            
            # 获取相邻边
            for edge_id in self.adjacency.get(current_id, []):
                edge = self.edges[edge_id]
                
                # 确定下一个节点
                if edge.source_id == current_id:
                    next_id = edge.target_id
                else:
                    next_id = edge.source_id
                
                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, path + [edge]))
        
        return None
    
    def get_neighbors(self, node_id: str) -> List[Node]:
        """获取邻居节点"""
        neighbor_ids = set()
        
        for edge in self.edges.values():
            if edge.source_id == node_id:
                neighbor_ids.add(edge.target_id)
            elif edge.target_id == node_id:
                neighbor_ids.add(edge.source_id)
        
        return [self.nodes[nid] for nid in neighbor_ids if nid in self.nodes]
    
    def get_subgraph(self, node_ids: List[str], depth: int = 1) -> Tuple[List[Node], List[Edge]]:
        """获取子图"""
        result_nodes = set(node_ids)
        result_edge_ids = set()  # 使用 ID 去重
        current_level = set(node_ids)
        
        for _ in range(depth):
            next_level = set()
            for node_id in current_level:
                for edge in self.edges.values():
                    if edge.id in result_edge_ids:
                        continue  # 跳过已添加的边
                    
                    if edge.source_id == node_id:
                        result_edge_ids.add(edge.id)
                        if edge.target_id not in result_nodes:
                            next_level.add(edge.target_id)
                            result_nodes.add(edge.target_id)
                    elif edge.target_id == node_id:
                        result_edge_ids.add(edge.id)
                        if edge.source_id not in result_nodes:
                            next_level.add(edge.source_id)
                            result_nodes.add(edge.source_id)
            current_level = next_level
        
        return (
            [self.nodes[nid] for nid in result_nodes if nid in self.nodes],
            [self.edges[eid] for eid in result_edge_ids if eid in self.edges]
        )
    
    # ==================== 统计 ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "nodes_by_type": {}
        }
        
        for node in self.nodes.values():
            t = node.node_type.value
            stats["nodes_by_type"][t] = stats["nodes_by_type"].get(t, 0) + 1
        
        return stats
    
    # ==================== 备份和恢复 ====================
    
    def create_backup(self, backup_dir: Optional[str] = None) -> str:
        """创建备份"""
        if backup_dir is None:
            backup_dir = self.data_dir / "backups"
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"backup_{timestamp}.json"
        
        data = {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges.values()],
            "metadata": {
                "backup_time": datetime.now().isoformat(),
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges)
            }
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Backup created: {backup_file}")
        return str(backup_file)


# 全局存储实例（单例）
_storage_instance: Optional[GraphStorage] = None


def get_storage(data_dir: str = "data") -> GraphStorage:
    """获取存储实例"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = GraphStorage(data_dir)
    return _storage_instance
