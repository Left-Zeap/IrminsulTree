"""
可视化组件 - 生成多种格式的可视化数据
"""
from typing import List, Dict, Any, Optional
import json

from core.models import Node, Edge, NodeType


# 节点颜色配置
NODE_COLORS = {
    "Person": "#FF6B6B",
    "Event": "#4ECDC4",
    "Location": "#45B7D1",
    "Quest": "#96CEB4",
    "Organization": "#FFEAA7",
    "Misc": "#DDA0DD",
    "Entry": "#E0E0E0",
}


class GraphVisualizer:
    """图可视化器"""
    
    def to_visjs(self, nodes: List[Node], edges: List[Edge]) -> Dict[str, Any]:
        """转换为 Vis.js 格式"""
        vis_nodes = []
        vis_edges = []
        
        for node in nodes:
            node_type = node.node_type.value
            vis_nodes.append({
                "id": node.id,
                "label": node.name,
                "group": node_type,
                "title": self._create_tooltip(node),
                "color": {
                    "background": NODE_COLORS.get(node_type, "#999999"),
                    "border": "#2C3E50"
                },
                "shape": "dot" if node_type == "Person" else "box"
            })
        
        for edge in edges:
            vis_edges.append({
                "id": edge.id,
                "from": edge.source_id,
                "to": edge.target_id,
                "label": edge.rel_type.value,
                "arrows": "" if edge.direction == "undirected" else "to",
                "color": {"color": "#888888"}
            })
        
        return {"nodes": vis_nodes, "edges": vis_edges}
    
    def to_cytoscape(self, nodes: List[Node], edges: List[Edge]) -> List[Dict[str, Any]]:
        """转换为 Cytoscape.js 格式"""
        elements = []
        
        for node in nodes:
            node_type = node.node_type.value
            elements.append({
                "data": {
                    "id": node.id,
                    "label": node.name,
                    "type": node_type,
                    "color": NODE_COLORS.get(node_type, "#999999")
                }
            })
        
        for edge in edges:
            elements.append({
                "data": {
                    "id": edge.id,
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "label": edge.rel_type.value
                }
            })
        
        return elements
    
    def to_networkx_format(self, nodes: List[Node], edges: List[Edge]) -> Dict[str, Any]:
        """转换为 NetworkX 格式"""
        return {
            "nodes": [{"id": n.id, **n.to_dict()} for n in nodes],
            "links": [
                {
                    "source": e.source_id,
                    "target": e.target_id,
                    "type": e.rel_type.value
                }
                for e in edges
            ]
        }
    
    def generate_html(self, nodes: List[Node], edges: List[Edge], 
                      title: str = "知识图谱") -> str:
        """生成 Vis.js HTML 页面"""
        data = self.to_visjs(nodes, edges)
        
        # 确保 JSON 字符串正确转义
        nodes_json = json.dumps(data['nodes'], ensure_ascii=False)
        edges_json = json.dumps(data['edges'], ensure_ascii=False)
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ 
            width: 100%; 
            height: 100%; 
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        #mynetwork {{ 
            width: 100%; 
            height: 100%; 
            background: #fafafa;
        }}
        #info {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255,255,255,0.95);
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 14px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            z-index: 100;
        }}
        #info h3 {{
            margin: 0 0 4px 0;
            font-size: 16px;
            color: #333;
        }}
        #info p {{
            margin: 0;
            color: #666;
        }}
        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 16px;
            color: #999;
        }}
    </style>
</head>
<body>
    <div id="info">
        <h3>{title}</h3>
        <p>节点: {len(nodes)} | 关系: {len(edges)}</p>
    </div>
    <div id="mynetwork">
        <div class="loading">正在加载图谱...</div>
    </div>
    <script>
        // 等待页面加载完成
        document.addEventListener('DOMContentLoaded', function() {{
            var container = document.getElementById('mynetwork');
            
            if (!container) {{
                console.error('Container element not found');
                return;
            }}
            
            try {{
                var nodesData = {nodes_json};
                var edgesData = {edges_json};
                
                // 检查并去重节点和边
                var nodeIds = new Set();
                var uniqueNodes = nodesData.filter(function(n) {{
                    if (nodeIds.has(n.id)) return false;
                    nodeIds.add(n.id);
                    return true;
                }});
                
                var edgeIds = new Set();
                var uniqueEdges = edgesData.filter(function(e) {{
                    if (edgeIds.has(e.id)) return false;
                    edgeIds.add(e.id);
                    return true;
                }});
                
                var nodes = new vis.DataSet(uniqueNodes);
                var edges = new vis.DataSet(uniqueEdges);
                
                var networkData = {{nodes: nodes, edges: edges}};
                
                var options = {{
                    nodes: {{
                        font: {{ size: 14, face: 'Arial' }},
                        borderWidth: 2,
                        shadow: true,
                        size: 25
                    }},
                    edges: {{
                        width: 2,
                        smooth: {{ 
                            type: 'continuous',
                            roundness: 0.2
                        }},
                        font: {{ size: 11, align: 'middle' }},
                        color: {{ color: '#848484', highlight: '#2B7CE9' }}
                    }},
                    physics: {{
                        enabled: true,
                        stabilization: {{
                            enabled: true,
                            iterations: 100,
                            updateInterval: 25
                        }},
                        barnesHut: {{
                            gravitationalConstant: -8000,
                            springConstant: 0.04,
                            springLength: 150,
                            damping: 0.09
                        }}
                    }},
                    interaction: {{ 
                        hover: true,
                        tooltipDelay: 200,
                        hideEdgesOnDrag: false
                    }},
                    layout: {{
                        randomSeed: 2
                    }}
                }};
                
                var network = new vis.Network(container, networkData, options);
                
                // 添加点击事件
                network.on("click", function(params) {{
                    if (params.nodes.length > 0) {{
                        console.log('Clicked node:', params.nodes[0]);
                    }}
                }});
                
                console.log('Network visualization loaded successfully');
            }} catch (error) {{
                console.error('Error loading visualization:', error);
                if (container) {{
                    container.innerHTML = '<div style="padding: 20px; color: red;">加载失败: ' + error.message + '</div>';
                }}
            }}
        }});
    </script>
</body>
</html>'''
        return html
    
    def _create_tooltip(self, node: Node) -> str:
        """创建节点提示信息"""
        lines = [f"<b>{node.name}</b>", f"类型: {node.node_type.value}"]
        
        if node.aliases:
            lines.append(f"别名: {', '.join(node.aliases)}")
        
        if node.category:
            lines.append(f"类别: {node.category}")
        
        if node.birth_year or node.death_year:
            lines.append(f"生卒: {node.birth_year or '?'} - {node.death_year or '?'}")
        
        if node.start_time or node.end_time:
            lines.append(f"时间: {node.start_time or '?'} - {node.end_time or '?'}")
        
        return "<br>".join(lines)


# 全局实例
_visualizer = None


def get_visualizer() -> GraphVisualizer:
    """获取可视化器实例"""
    global _visualizer
    if _visualizer is None:
        _visualizer = GraphVisualizer()
    return _visualizer
