"""
数据模型定义
"""
from typing import List, Optional, Dict, Any, Union, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import uuid


class NodeType(str, Enum):
    """节点类型"""
    PERSON = "Person"
    EVENT = "Event"
    LOCATION = "Location"
    QUEST = "Quest"
    ORGANIZATION = "Organization"
    MISC = "Misc"
    ENTRY = "Entry"


class PersonCategory(str, Enum):
    """人物类别"""
    PLAYABLE = "自机"
    NPC = "npc"
    UNSEEN = "未出现"


class MiscCategory(str, Enum):
    """杂项类别"""
    BOOK = "书籍"
    ARTIFACT = "圣遗物"
    WING = "翅膀"
    WEAPON = "武器"
    WORLD_TEXT = "大世界文本"


class RelationType(str, Enum):
    """关系类型"""
    SUB_EVENT_OF = "SUB_EVENT_OF"
    SUB_ORGANIZATION_OF = "SUB_ORGANIZATION_OF"
    SUB_LOCATION_OF = "SUB_LOCATION_OF"
    SUB_QUEST_OF = "SUB_QUEST_OF"
    MEMBER_OF = "MEMBER_OF"
    PARTICIPATED_IN = "PARTICIPATED_IN"
    RELATED_TO = "RELATED_TO"
    LOCATED_AT = "LOCATED_AT"
    ASSIGNED_TO = "ASSIGNED_TO"
    EVENT_AT = "EVENT_AT"
    EVENT_TRIGGER = "EVENT_TRIGGER"
    QUEST_AT = "QUEST_AT"
    ORG_QUEST = "ORG_QUEST"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"


class Node(BaseModel):
    """节点模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    node_type: NodeType
    aliases: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # 类型特有字段
    category: Optional[str] = None  # Person
    birth_year: Optional[int] = None  # Person
    death_year: Optional[int] = None  # Person
    
    sub_events: List[str] = Field(default_factory=list)  # Event
    sub_locations: List[str] = Field(default_factory=list)  # Location
    sub_quests: List[str] = Field(default_factory=list)  # Quest
    sub_organizations: List[str] = Field(default_factory=list)  # Organization
    
    start_time: Optional[int] = None  # Event/Location/Quest/Organization
    end_time: Optional[int] = None
    
    poi_codes: List[str] = Field(default_factory=list)  # Location
    
    misc_category: Optional[str] = None  # Misc
    
    # 通用字段 - 所有节点类型都有
    version: Optional[str] = None  # 版本，例如：1.0, 2.0, 3.0, 4.0, 5.0
    
    # 扩展属性
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class Edge(BaseModel):
    """边（关系）模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_id: str  # 源节点ID
    target_id: str  # 目标节点ID
    rel_type: RelationType
    direction: str = "directed"  # directed / undirected
    # label 可以是字符串或时间范围元组（允许None值）
    label: Optional[Union[str, Tuple[Optional[int], Optional[int]]]] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        # 处理 tuple 类型的 label
        if isinstance(self.label, tuple):
            data['label'] = list(self.label)
        # 处理 None 值，确保输出为 null 而不是省略
        for key, value in data.items():
            if value is None:
                data[key] = None
        return data


class GraphData(BaseModel):
    """图数据容器"""
    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges]
        }
