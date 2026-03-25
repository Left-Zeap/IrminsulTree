# -*- coding: utf-8 -*-
"""
Streamlit GUI 主应用
无需 Neo4j，纯本地运行的知识图谱管理系统
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import json
import base64

from core.models import Node, Edge, NodeType, RelationType, PersonCategory, MiscCategory
from core.storage import get_storage
from core.visualizer import get_visualizer
import config

# 初始化
storage = get_storage()
visualizer = get_visualizer()

# 页面标题使用配置
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .node-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """主函数"""
    # 侧边栏导航
    with st.sidebar:
        st.title("🌐 知识图谱管理")
        
        page = st.radio(
            "选择功能",
            ["📊 概览", "➕ 添加节点", "🔗 添加关系", "📋 节点列表", "🔗 查看/删除关系", "🔍 搜索", "🕸️ 可视化", "💾 数据管理"]
        )
        
        st.divider()
        
        # 统计信息
        stats = storage.get_statistics()
        st.metric("总节点数", stats["total_nodes"])
        st.metric("总关系数", stats["total_edges"])
    
    # 页面路由
    if "概览" in page:
        show_overview()
    elif "添加节点" in page:
        show_add_node()
    elif "添加关系" in page:
        show_add_relation()
    elif "节点列表" in page:
        show_node_list()
    elif "查看/删除关系" in page:
        show_manage_relations()
    elif "搜索" in page:
        show_search()
    elif "可视化" in page:
        show_visualization()
    elif "数据管理" in page:
        show_data_management()


def show_overview():
    """概览页面"""
    st.markdown('<div class="main-header">📊 知识图谱概览</div>', unsafe_allow_html=True)
    
    stats = storage.get_statistics()
    
    # 统计卡片
    cols = st.columns(4)
    with cols[0]:
        st.metric("总节点", stats["total_nodes"])
    with cols[1]:
        st.metric("总关系", stats["total_edges"])
    with cols[2]:
        person_count = stats["nodes_by_type"].get("Person", 0)
        st.metric("人物", person_count)
    with cols[3]:
        event_count = stats["nodes_by_type"].get("Event", 0)
        st.metric("事件", event_count)
    
    st.divider()
    
    # 节点类型分布
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 节点类型分布")
        if stats["nodes_by_type"]:
            df = pd.DataFrame([
                {"类型": k, "数量": v}
                for k, v in stats["nodes_by_type"].items()
            ])
            st.bar_chart(df.set_index("类型"))
        else:
            st.info("暂无数据")
    
    with col2:
        st.subheader("🕸️ 快速操作")
        
        if st.button("➕ 添加人物"):
            st.session_state.page = "添加节点"
            st.rerun()
        
        if st.button("🔗 添加关系"):
            st.session_state.page = "添加关系"
            st.rerun()
        
        if st.button("🔍 搜索节点"):
            st.session_state.page = "搜索"
            st.rerun()
    
    # 最近添加
    st.divider()
    st.subheader("🕐 最近添加的节点")
    
    nodes = storage.get_all_nodes()
    nodes.sort(key=lambda x: x.created_at, reverse=True)
    
    if nodes:
        recent = nodes[:5]
        for node in recent:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**{node.name}**")
                with col2:
                    st.write(f"类型: {node.node_type.value}")
                with col3:
                    if st.button("查看", key=f"view_{node.id}"):
                        show_node_detail(node.id)
    else:
        st.info("还没有节点，快去添加吧！")


def show_add_node():
    """添加节点页面"""
    st.markdown('<div class="main-header">➕ 添加节点</div>', unsafe_allow_html=True)
    
    node_type = st.selectbox(
        "选择节点类型",
        options=[
            ("Person", "👤 人物"),
            ("Event", "📅 事件"),
            ("Location", "📍 地点"),
            ("Quest", "📜 任务"),
            ("Organization", "🏛️ 团体"),
            ("Misc", "📦 杂项"),
            ("Entry", "📖 普通词条")
        ],
        format_func=lambda x: x[1]
    )[0]
    
    with st.form("add_node_form"):
        # 基础信息
        name = st.text_input("名称 *", placeholder="输入名称")
        aliases = st.text_input("别名", placeholder="多个别名用逗号分隔")
        
        # 类型特有字段
        if node_type == "Person":
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox("类别", ["自机", "npc", "未出现"])
            with col2:
                birth_year = st.number_input("出生年份", value=None, step=1)
            death_year = st.number_input("去世年份", value=None, step=1)
        
        elif node_type in ["Event", "Location", "Quest", "Organization"]:
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.number_input("起始时间", value=None, step=1)
            with col2:
                end_time = st.number_input("终止时间", value=None, step=1)
            
            if node_type == "Location":
                poi_codes = st.text_input("POI编码", placeholder="多个编码用逗号分隔")
        
        elif node_type == "Misc":
            misc_category = st.selectbox("杂项类别", ["书籍", "圣遗物", "翅膀", "武器", "大世界文本"])
        
        # 所有节点类型都有的字段
        st.divider()
        version = st.text_input("版本", placeholder="例如：1.0, 2.0, 3.0, 4.0, 5.0...")
        
        # 检查同名节点
        existing_node = storage.get_node_by_name(node_type, name)
        if existing_node:
            st.warning(f"⚠️ 已存在同名节点：**{existing_node.name}** (ID: {existing_node.id})")
            st.info("请前往「节点列表」页面修改现有节点，或使用不同的名称。")
        
        submitted = st.form_submit_button("✅ 创建节点")
        
        if submitted:
            if not name:
                st.error("名称不能为空！")
                return
            
            # 检查同名节点
            existing_node = storage.get_node_by_name(node_type, name)
            if existing_node:
                st.error(f"❌ 无法创建：已存在同名节点 **{name}** (ID: {existing_node.id})")
                st.info("提示：您可以前往「节点列表」页面搜索该节点并进行修改。")
                return
            
            # 构建节点
            node_data = {
                "name": name,
                "node_type": node_type,
                "aliases": [a.strip() for a in aliases.split(",") if a.strip()]
            }
            
            if node_type == "Person":
                node_data.update({
                    "category": category,
                    "birth_year": birth_year,
                    "death_year": death_year
                })
            elif node_type in ["Event", "Location", "Quest", "Organization"]:
                node_data.update({
                    "start_time": start_time,
                    "end_time": end_time
                })
                if node_type == "Location" and 'poi_codes' in locals():
                    node_data["poi_codes"] = [p.strip() for p in poi_codes.split(",") if p.strip()]
            elif node_type == "Misc":
                node_data["misc_category"] = misc_category
            
            # 所有节点类型都有的字段
            node_data["version"] = version if version else None
            
            node = Node(**node_data)
            node_id = storage.create_node(node)
            
            st.success(f"✅ 节点创建成功！ID: {node_id}")


def show_add_relation():
    """添加关系页面"""
    st.markdown('<div class="main-header">🔗 添加关系</div>', unsafe_allow_html=True)
    
    nodes = storage.get_all_nodes()
    
    if len(nodes) < 2:
        st.warning("节点数量不足，请先添加至少两个节点")
        return
    
    # 选择模式：单个添加或批量添加
    add_mode = st.radio(
        "添加模式",
        ["单个添加", "批量添加（一个源节点连接多个目标节点）"],
        horizontal=True
    )
    
    if "单个添加" in add_mode:
        show_add_single_relation(nodes)
    else:
        show_add_batch_relations(nodes)


def show_add_single_relation(nodes):
    """单个添加关系"""
    # 搜索选择节点
    col1, col2 = st.columns(2)
    
    # 源节点选择
    with col1:
        st.subheader("源节点")
        source_search = st.text_input("搜索源节点", placeholder="输入名称或别名...", key="source_search")
        
        # 筛选匹配的节点
        if source_search:
            source_matches = [n for n in nodes if source_search.lower() in n.name.lower() 
                             or any(source_search.lower() in a.lower() for a in n.aliases)]
        else:
            source_matches = nodes
        
        # 显示可选节点（最多20个）
        if source_matches:
            source_options = {f"[{n.node_type.value}] {n.name} ({n.id})": n for n in source_matches[:20]}
            source_key = st.radio("选择源节点", options=list(source_options.keys()), key="source_select")
            source_node = source_options[source_key]
            st.success(f"已选择: **{source_node.name}** ({source_node.node_type.value})")
        else:
            st.warning("未找到匹配的节点")
            return
    
    # 目标节点选择
    with col2:
        st.subheader("目标节点")
        target_search = st.text_input("搜索目标节点", placeholder="输入名称或别名...", key="target_search")
        
        # 筛选匹配的节点（排除已选的源节点）
        if target_search:
            target_matches = [n for n in nodes if n.id != source_node.id 
                             and (target_search.lower() in n.name.lower() 
                                  or any(target_search.lower() in a.lower() for a in n.aliases))]
        else:
            target_matches = [n for n in nodes if n.id != source_node.id]
        
        # 显示可选节点（最多20个）
        if target_matches:
            target_options = {f"[{n.node_type.value}] {n.name} ({n.id})": n for n in target_matches[:20]}
            target_key = st.radio("选择目标节点", options=list(target_options.keys()), key="target_select")
            target_node = target_options[target_key]
            st.success(f"已选择: **{target_node.name}** ({target_node.node_type.value})")
        else:
            st.warning("未找到匹配的节点")
            return
    
    # 关系类型
    st.divider()
    
    rel_type = st.selectbox(
        "关系类型",
        options=[
            (RelationType.MEMBER_OF, "👤 成员关系 (Person->Organization)"),
            (RelationType.PARTICIPATED_IN, "🎭 参与事件 (Person->Event)"),
            (RelationType.RELATED_TO, "🤝 人物关系 (Person<->Person)"),
            (RelationType.LOCATED_AT, "📍 居住/位于 (Person->Location)"),
            (RelationType.ASSIGNED_TO, "📋 分配任务 (Person->Quest)"),
            (RelationType.EVENT_AT, "📅 事件发生 (Event->Location)"),
            (RelationType.SUB_EVENT_OF, "📖 子事件 (Event->Event)"),
            (RelationType.SUB_LOCATION_OF, "🏠 子地点 (Location->Location)"),
            (RelationType.ASSOCIATED_WITH, "🔗 关联 (任意->Misc/Entry)"),
        ],
        format_func=lambda x: x[1],
        key="single_rel_type"
    )[0]
    
    # 方向
    direction = "undirected" if rel_type == RelationType.RELATED_TO else "directed"
    if rel_type != RelationType.RELATED_TO:
        st.info(f"关系方向: **{'无向' if direction == 'undirected' else '有向'}** (源 → 目标)")
    
    # 标签（可选）
    label = st.text_input("关系标签（可选）", placeholder="例如：朋友、参与、属于...", key="single_label")
    
    # 时间范围（可选）
    if rel_type in [RelationType.MEMBER_OF, RelationType.LOCATED_AT]:
        st.subheader("⏰ 时间范围（可选）")
        col1, col2 = st.columns(2)
        with col1:
            start_year = st.number_input("起始年份", value=None, step=1, key="single_rel_start")
        with col2:
            end_year = st.number_input("终止年份", value=None, step=1, key="single_rel_end")
        if start_year is not None or end_year is not None:
            label = (start_year, end_year)
    
    # 检查是否已存在相同关系
    existing_edge = None
    for edge in storage.edges.values():
        if (edge.source_id == source_node.id and 
            edge.target_id == target_node.id and 
            edge.rel_type == rel_type):
            existing_edge = edge
            break
    
    if existing_edge:
        st.warning(f"⚠️ 已存在相同关系：**{source_node.name}** → **{target_node.name}** ({rel_type.value})")
        st.info("该关系已存在，如需修改请前往「查看/删除关系」页面。")
    
    if st.button("✅ 创建关系"):
        try:
            # 检查是否已存在相同关系
            for edge in storage.edges.values():
                if (edge.source_id == source_node.id and 
                    edge.target_id == target_node.id and 
                    edge.rel_type == rel_type):
                    st.error(f"❌ 无法创建：已存在相同关系 **{source_node.name}** → **{target_node.name}** ({rel_type.value})")
                    st.info("提示：该关系已存在，如需修改请前往「查看/删除关系」页面。")
                    return
            
            edge = Edge(
                source_id=source_node.id,
                target_id=target_node.id,
                rel_type=rel_type,
                direction=direction,
                label=label if label else None
            )
            edge_id = storage.create_edge(edge)
            st.success(f"✅ 关系创建成功！ID: {edge_id}")
        except Exception as e:
            st.error(f"❌ 创建失败: {e}")


def show_add_batch_relations(nodes):
    """批量添加关系"""
    st.info("📌 批量添加模式：选择一个源节点，然后筛选并批量选择多个目标节点，统一设置关系类型和标签。")
    
    # 步骤1：选择源节点
    st.divider()
    st.subheader("步骤 1：选择源节点")
    
    source_search = st.text_input("搜索源节点", placeholder="输入名称或别名...", key="batch_source_search")
    
    if source_search:
        source_matches = [n for n in nodes if source_search.lower() in n.name.lower() 
                         or any(source_search.lower() in a.lower() for a in n.aliases)]
    else:
        source_matches = nodes
    
    if not source_matches:
        st.warning("未找到匹配的节点")
        return
    
    source_options = {f"[{n.node_type.value}] {n.name} ({n.id})": n for n in source_matches[:20]}
    source_key = st.radio("选择源节点", options=list(source_options.keys()), key="batch_source_select")
    source_node = source_options[source_key]
    st.success(f"已选择源节点: **{source_node.name}** ({source_node.node_type.value})")
    
    # 步骤2：筛选目标节点
    st.divider()
    st.subheader("步骤 2：筛选目标节点")
    
    # 筛选条件
    col1, col2 = st.columns(2)
    with col1:
        target_name_filter = st.text_input("按名称筛选", placeholder="输入关键词...", key="batch_target_name")
    with col2:
        target_type_filter = st.selectbox(
            "按类型筛选",
            options=["全部"] + [t.value for t in NodeType],
            key="batch_target_type"
        )
    
    # 应用筛选
    filtered_targets = [n for n in nodes if n.id != source_node.id]
    
    if target_name_filter:
        filtered_targets = [n for n in filtered_targets 
                          if target_name_filter.lower() in n.name.lower()
                          or any(target_name_filter.lower() in a.lower() for a in n.aliases)]
    
    if target_type_filter != "全部":
        filtered_targets = [n for n in filtered_targets if n.node_type.value == target_type_filter]
    
    if not filtered_targets:
        st.warning("没有符合条件的节点")
        return
    
    st.write(f"筛选结果：**{len(filtered_targets)}** 个节点")
    
    # 步骤3：批量选择目标节点
    st.divider()
    st.subheader("步骤 3：选择目标节点（可多选）")
    
    # 使用多选框
    target_options = {f"[{n.node_type.value}] {n.name} ({n.id})": n for n in filtered_targets}
    
    # 全选/全不选按钮
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("☑️ 全选"):
            st.session_state.batch_selected_targets = list(target_options.keys())
    with col2:
        if st.button("⬜ 全不选"):
            st.session_state.batch_selected_targets = []
    
    # 多选框
    selected_target_keys = st.multiselect(
        "选择要添加关系的目标节点",
        options=list(target_options.keys()),
        default=st.session_state.get("batch_selected_targets", []),
        key="batch_target_multiselect"
    )
    
    if not selected_target_keys:
        st.info("请至少选择一个目标节点")
        return
    
    selected_targets = [target_options[k] for k in selected_target_keys]
    st.success(f"已选择 **{len(selected_targets)}** 个目标节点")
    
    # 显示预览
    with st.expander("📋 查看已选节点"):
        for t in selected_targets:
            st.write(f"- {t.name} ({t.node_type.value})")
    
    # 步骤4：设置关系类型和标签
    st.divider()
    st.subheader("步骤 4：设置关系类型和标签")
    
    rel_type = st.selectbox(
        "关系类型",
        options=[
            (RelationType.MEMBER_OF, "👤 成员关系 (Person->Organization)"),
            (RelationType.PARTICIPATED_IN, "🎭 参与事件 (Person->Event)"),
            (RelationType.RELATED_TO, "🤝 人物关系 (Person<->Person)"),
            (RelationType.LOCATED_AT, "📍 居住/位于 (Person->Location)"),
            (RelationType.ASSIGNED_TO, "📋 分配任务 (Person->Quest)"),
            (RelationType.EVENT_AT, "📅 事件发生 (Event->Location)"),
            (RelationType.SUB_EVENT_OF, "📖 子事件 (Event->Event)"),
            (RelationType.SUB_LOCATION_OF, "🏠 子地点 (Location->Location)"),
            (RelationType.ASSOCIATED_WITH, "🔗 关联 (任意->Misc/Entry)"),
        ],
        format_func=lambda x: x[1],
        key="batch_rel_type"
    )[0]
    
    # 方向
    direction = "undirected" if rel_type == RelationType.RELATED_TO else "directed"
    if rel_type != RelationType.RELATED_TO:
        st.info(f"关系方向: **{'无向' if direction == 'undirected' else '有向'}** (源 → 目标)")
    
    # 标签
    label = st.text_input("关系标签（可选）", placeholder="例如：朋友、参与、属于...", key="batch_label")
    
    # 时间范围（可选）
    if rel_type in [RelationType.MEMBER_OF, RelationType.LOCATED_AT]:
        st.subheader("⏰ 时间范围（可选）")
        col1, col2 = st.columns(2)
        with col1:
            start_year = st.number_input("起始年份", value=None, step=1, key="batch_rel_start")
        with col2:
            end_year = st.number_input("终止年份", value=None, step=1, key="batch_rel_end")
        if start_year is not None or end_year is not None:
            label = (start_year, end_year)
    
    # 步骤5：确认并批量创建
    st.divider()
    st.subheader("步骤 5：确认并批量创建")
    
    # 检查哪些关系已存在
    existing_count = 0
    new_count = 0
    for target in selected_targets:
        exists = any(e.source_id == source_node.id and 
                    e.target_id == target.id and 
                    e.rel_type == rel_type for e in storage.edges.values())
        if exists:
            existing_count += 1
        else:
            new_count += 1
    
    st.write(f"📊 预览：**{len(selected_targets)}** 个目标节点")
    st.write(f"- ✅ 将新建关系：**{new_count}** 个")
    if existing_count > 0:
        st.write(f"- ⚠️ 已存在将跳过：**{existing_count}** 个")
    
    if st.button("🚀 批量创建关系", type="primary"):
        try:
            success_count = 0
            skip_count = 0
            error_count = 0
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, target in enumerate(selected_targets):
                progress = (i + 1) / len(selected_targets)
                progress_bar.progress(progress)
                status_text.text(f"正在处理 {i+1}/{len(selected_targets)}: {target.name}")
                
                # 检查是否已存在
                exists = any(e.source_id == source_node.id and 
                            e.target_id == target.id and 
                            e.rel_type == rel_type for e in storage.edges.values())
                
                if exists:
                    skip_count += 1
                    continue
                
                try:
                    edge = Edge(
                        source_id=source_node.id,
                        target_id=target.id,
                        rel_type=rel_type,
                        direction=direction,
                        label=label if label else None
                    )
                    storage.create_edge(edge)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    logger.error(f"创建关系到 {target.name} 失败: {e}")
            
            progress_bar.empty()
            status_text.empty()
            
            # 显示结果
            if success_count > 0:
                st.success(f"✅ 成功创建 **{success_count}** 个关系！")
            if skip_count > 0:
                st.info(f"⏭️ 跳过 **{skip_count}** 个已存在的关系")
            if error_count > 0:
                st.error(f"❌ **{error_count}** 个关系创建失败")
            
            if success_count > 0:
                st.balloons()
        
        except Exception as e:
            st.error(f"❌ 批量创建失败: {e}")


def show_node_list():
    """节点列表页面"""
    st.markdown('<div class="main-header">📋 节点列表</div>', unsafe_allow_html=True)
    
    # 搜索框
    search_keyword = st.text_input("🔍 搜索节点", placeholder="输入名称或别名筛选...")
    
    # 类型筛选
    filter_type = st.selectbox(
        "筛选类型",
        options=["全部"] + [t.value for t in NodeType]
    )
    
    # 获取节点
    if filter_type == "全部":
        nodes = storage.get_all_nodes()
    else:
        nodes = storage.get_all_nodes(node_type=filter_type)
    
    # 根据关键词进一步筛选
    if search_keyword:
        nodes = [n for n in nodes if search_keyword.lower() in n.name.lower() 
                 or any(search_keyword.lower() in a.lower() for a in n.aliases)]
    
    # 显示
    st.write(f"共 **{len(nodes)}** 个节点")
    
    if nodes:
        # 转换为 DataFrame
        data = []
        for n in nodes:
            data.append({
                "ID": n.id,
                "名称": n.name,
                "类型": n.node_type.value,
                "别名": ", ".join(n.aliases) if n.aliases else "-",
                "创建时间": n.created_at[:19] if n.created_at else "-"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, hide_index=True)
        
        # 详细操作
        st.divider()
        st.subheader("🔍 查看/编辑节点")
        
        # 搜索选择节点
        detail_search = st.text_input("搜索要查看的节点", placeholder="输入名称...", key="detail_search")
        
        if detail_search:
            detail_matches = [n for n in nodes if detail_search.lower() in n.name.lower()]
            if detail_matches:
                detail_options = {f"{n.name} ({n.id})": n.id for n in detail_matches[:10]}
                selected_key = st.radio("选择节点", options=list(detail_options.keys()), key="detail_select")
                selected_id = detail_options[selected_key]
                
                # 显示详情和编辑
                show_node_detail_edit(selected_id)
            else:
                st.warning("未找到匹配的节点")
    else:
        st.info("暂无节点")


def show_node_detail(node_id: str):
    """显示节点详情"""
    node = storage.get_node(node_id)
    if not node:
        st.error("节点不存在")
        return
    
    with st.container():
        st.markdown(f"### {node.name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**类型:** {node.node_type.value}")
            st.write(f"**ID:** {node.id}")
            if node.aliases:
                st.write(f"**别名:** {', '.join(node.aliases)}")
            
            if node.category:
                st.write(f"**类别:** {node.category}")
            if node.birth_year or node.death_year:
                st.write(f"**生卒:** {node.birth_year or '?'} - {node.death_year or '?'}")
            if node.start_time or node.end_time:
                st.write(f"**时间:** {node.start_time or '?'} - {node.end_time or '?'}")
        
        with col2:
            # 相关关系
            edges = storage.get_node_edges(node_id)
            st.write(f"**关系数:** {len(edges)}")
            
            for edge in edges[:5]:
                if edge.source_id == node_id:
                    other = storage.get_node(edge.target_id)
                    direction = "→"
                else:
                    other = storage.get_node(edge.source_id)
                    direction = "←"
                
                if other:
                    st.write(f"{direction} [{edge.rel_type.value}] {other.name}")
            
            if len(edges) > 5:
                st.write(f"... 还有 {len(edges) - 5} 个关系")
        
        # 操作按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ 删除节点", key=f"del_{node_id}"):
                if storage.delete_node(node_id):
                    st.success("节点已删除")
                    st.rerun()
        with col2:
            if st.button("🕸️ 查看子图", key=f"sub_{node_id}"):
                st.session_state['subgraph_node_id'] = node_id
                st.session_state.page = "可视化"


def show_node_detail_edit(node_id: str):
    """显示节点详情并支持编辑"""
    node = storage.get_node(node_id)
    if not node:
        st.error("节点不存在")
        return
    
    with st.container():
        st.markdown(f"### 📄 节点详情: {node.name}")
        
        # 显示基本信息
        with st.expander("📊 查看当前数据", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**类型:** {node.node_type.value}")
                st.write(f"**ID:** {node.id}")
                if node.version:
                    st.write(f"**版本:** {node.version}")
                if node.aliases:
                    st.write(f"**别名:** {', '.join(node.aliases)}")
                
                if node.category:
                    st.write(f"**类别:** {node.category}")
                if node.birth_year or node.death_year:
                    st.write(f"**生卒:** {node.birth_year or '?'} - {node.death_year or '?'}")
                if node.start_time or node.end_time:
                    st.write(f"**时间:** {node.start_time or '?'} - {node.end_time or '?'})")
            
            with col2:
                # 相关关系
                edges = storage.get_node_edges(node_id)
                st.write(f"**关系数:** {len(edges)}")
                
                for edge in edges[:10]:
                    if edge.source_id == node_id:
                        other = storage.get_node(edge.target_id)
                        direction = "→"
                    else:
                        other = storage.get_node(edge.source_id)
                        direction = "←"
                    
                    if other:
                        st.write(f"{direction} [{edge.rel_type.value}] {other.name}")
                
                if len(edges) > 10:
                    st.write(f"... 还有 {len(edges) - 10} 个关系")
        
        # 编辑表单
        st.divider()
        st.markdown("### ✏️ 编辑节点")
        
        with st.form("edit_node_form"):
            # 基础字段
            new_name = st.text_input("名称", value=node.name)
            new_aliases = st.text_input("别名", value=", ".join(node.aliases))
            
            # 所有节点类型都有的字段
            new_version = st.text_input("版本", value=node.version if node.version else "", placeholder="例如：1.0, 2.0, 3.0...")
            
            # 类型特有字段
            updates = {}
            
            if node.node_type.value == "Person":
                new_category = st.selectbox("类别", ["自机", "npc", "未出现"], 
                                           index=["自机", "npc", "未出现"].index(node.category) if node.category else 0)
                new_birth = st.number_input("出生年份", value=node.birth_year, step=1)
                new_death = st.number_input("去世年份", value=node.death_year, step=1)
                updates["category"] = new_category
                updates["birth_year"] = new_birth if new_birth != 0 else None
                updates["death_year"] = new_death if new_death != 0 else None
            
            elif node.node_type.value in ["Event", "Location", "Quest", "Organization"]:
                new_start = st.number_input("起始时间", value=node.start_time, step=1)
                new_end = st.number_input("终止时间", value=node.end_time, step=1)
                updates["start_time"] = new_start if new_start != 0 else None
                updates["end_time"] = new_end if new_end != 0 else None
                
                if node.node_type.value == "Location":
                    new_poi = st.text_input("POI编码", value=", ".join(node.poi_codes))
                    updates["poi_codes"] = [p.strip() for p in new_poi.split(",") if p.strip()]
            
            elif node.node_type.value == "Misc":
                new_misc_cat = st.selectbox("杂项类别", 
                                           ["书籍", "圣遗物", "翅膀", "武器", "大世界文本"],
                                           index=["书籍", "圣遗物", "翅膀", "武器", "大世界文本"].index(node.misc_category) if node.misc_category else 0)
                updates["misc_category"] = new_misc_cat
            
            col1, col2 = st.columns(2)
            with col1:
                save_btn = st.form_submit_button("💾 保存修改")
            with col2:
                delete_btn = st.form_submit_button("🗑️ 删除节点")
            
            if save_btn:
                # 更新基础字段
                updates["name"] = new_name
                updates["aliases"] = [a.strip() for a in new_aliases.split(",") if a.strip()]
                updates["version"] = new_version if new_version else None
                
                # 执行更新
                if storage.update_node(node_id, updates):
                    st.success("✅ 节点已更新并保存到文件！")
                    st.rerun()
                else:
                    st.error("❌ 更新失败")
            
            if delete_btn:
                if storage.delete_node(node_id):
                    st.success("✅ 节点已删除！")
                    st.rerun()
                else:
                    st.error("❌ 删除失败")


def show_manage_relations():
    """查看/删除关系页面"""
    st.markdown('<div class="main-header">🔗 查看/删除关系</div>', unsafe_allow_html=True)
    
    # 搜索方式选择
    search_method = st.radio(
        "查找方式",
        ["按节点查找", "按关系类型查找", "查看所有关系"],
        horizontal=True
    )
    
    edges_to_show = []
    
    if search_method == "按节点查找":
        # 搜索节点
        node_search = st.text_input("搜索节点", placeholder="输入节点名称...")
        
        if node_search:
            matching_nodes = [n for n in storage.get_all_nodes() 
                            if node_search.lower() in n.name.lower()
                            or any(node_search.lower() in a.lower() for a in n.aliases)]
            
            if matching_nodes:
                node_options = {f"{n.name} ({n.node_type.value})": n for n in matching_nodes[:10]}
                selected = st.radio("选择节点", options=list(node_options.keys()))
                selected_node = node_options[selected]
                
                # 获取该节点的一层关联关系
                edges_to_show = storage.get_node_edges(selected_node.id, direction="both")
                
                st.info(f"节点 **{selected_node.name}** 的关联关系（共 {len(edges_to_show)} 条）")
            else:
                st.warning("未找到匹配的节点")
                return
        else:
            st.info("请输入节点名称进行搜索")
            return
    
    elif search_method == "按关系类型查找":
        # 选择关系类型
        rel_type = st.selectbox(
            "选择关系类型",
            options=[
                (RelationType.MEMBER_OF, "👤 成员关系"),
                (RelationType.PARTICIPATED_IN, "🎭 参与事件"),
                (RelationType.RELATED_TO, "🤝 人物关系"),
                (RelationType.LOCATED_AT, "📍 居住/位于"),
                (RelationType.ASSIGNED_TO, "📋 分配任务"),
                (RelationType.EVENT_AT, "📅 事件发生"),
                (RelationType.SUB_EVENT_OF, "📖 子事件"),
                (RelationType.SUB_LOCATION_OF, "🏠 子地点"),
                (RelationType.ASSOCIATED_WITH, "🔗 关联"),
            ],
            format_func=lambda x: x[1]
        )[0]
        
        edges_to_show = [e for e in storage.edges.values() if e.rel_type == rel_type]
        st.info(f"关系类型 **{rel_type.value}** 的所有关系（共 {len(edges_to_show)} 条）")
    
    else:  # 查看所有关系
        edges_to_show = list(storage.edges.values())
        st.info(f"所有关系（共 {len(edges_to_show)} 条）")
    
    # 显示关系列表
    if edges_to_show:
        st.divider()
        
        # 转换为表格数据
        edge_data = []
        for edge in edges_to_show:
            source = storage.get_node(edge.source_id)
            target = storage.get_node(edge.target_id)
            
            if source and target:
                edge_data.append({
                    "ID": edge.id,
                    "源节点": source.name,
                    "源类型": source.node_type.value,
                    "关系": edge.rel_type.value,
                    "目标节点": target.name,
                    "目标类型": target.node_type.value,
                    "方向": "无向" if edge.direction == "undirected" else "有向",
                    "标签": str(edge.label) if edge.label else "-"
                })
        
        if edge_data:
            df = pd.DataFrame(edge_data)
            st.dataframe(df, hide_index=True)
            
            # 删除关系功能
            st.divider()
            st.subheader("🗑️ 删除关系")
            
            edge_options = {f"{e['源节点']} → {e['关系']} → {e['目标节点']} (ID: {e['ID']})": e['ID'] 
                          for e in edge_data}
            
            selected_edge_key = st.selectbox("选择要删除的关系", options=list(edge_options.keys()))
            selected_edge_id = edge_options[selected_edge_key]
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("🗑️ 删除选中关系", type="primary"):
                    if storage.delete_edge(selected_edge_id):
                        st.success("✅ 关系已删除！")
                        st.rerun()
                    else:
                        st.error("❌ 删除失败")
            with col2:
                st.warning("⚠️ 删除后无法恢复，请谨慎操作！")
        else:
            st.info("没有找到完整的关系数据")
    else:
        st.info("没有找到关系")


def show_search():
    """搜索页面"""
    st.markdown('<div class="main-header">🔍 搜索节点</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        keyword = st.text_input("搜索关键词", placeholder="输入名称或别名...")
    
    with col2:
        search_type = st.selectbox(
            "类型筛选",
            options=["全部"] + [t.value for t in NodeType]
        )
    
    if keyword:
        node_type = None if search_type == "全部" else search_type
        results = storage.search_nodes(node_type=node_type, name_pattern=keyword, limit=50)
        
        st.write(f"找到 **{len(results)}** 个结果")
        
        for node in results:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**{node.name}**")
                    if node.aliases:
                        st.caption(f"别名: {', '.join(node.aliases)}")
                with col2:
                    st.write(f"类型: {node.node_type.value}")
                with col3:
                    if st.button("查看", key=f"search_view_{node.id}"):
                        show_node_detail(node.id)
    else:
        st.info("输入关键词开始搜索")


def show_visualization():
    """可视化页面"""
    st.markdown('<div class="main-header">🕸️ 图谱可视化</div>', unsafe_allow_html=True)
    
    # 选择可视化模式
    mode = st.radio(
        "可视化模式",
        options=["完整图谱", "子图（从某节点展开）", "路径查找"],
        horizontal=True
    )
    
    nodes = []
    edges = []
    
    if mode == "完整图谱":
        all_nodes = storage.get_all_nodes()
        if len(all_nodes) > 200:
            st.warning(f"节点数量过多 ({len(all_nodes)})，只显示前200个")
            all_nodes = all_nodes[:200]
        node_ids = [n.id for n in all_nodes]
        nodes, edges = storage.get_subgraph(node_ids, depth=1)
    
    elif mode == "子图（从某节点展开）":
        all_nodes = storage.get_all_nodes()
        if all_nodes:
            options = {f"{n.name} ({n.node_type.value})": n for n in all_nodes}
            selected = st.selectbox("选择中心节点", options=list(options.keys()))
            center_node = options[selected]
            
            depth = st.slider("展开深度", min_value=1, max_value=3, value=2)
            
            nodes, edges = storage.get_subgraph([center_node.id], depth=depth)
            st.write(f"子图包含 {len(nodes)} 个节点，{len(edges)} 条边")
        else:
            st.warning("没有节点")
            return
    
    elif mode == "路径查找":
        all_nodes = storage.get_all_nodes()
        if len(all_nodes) < 2:
            st.warning("节点数量不足")
            return
        
        options = {f"{n.name} ({n.node_type.value})": n for n in all_nodes}
        
        col1, col2 = st.columns(2)
        with col1:
            source_key = st.selectbox("起始节点", options=list(options.keys()), key="path_source")
            source = options[source_key]
        with col2:
            target_key = st.selectbox("目标节点", options=list(options.keys()), key="path_target")
            target = options[target_key]
        
        if source.id != target.id:
            path_edges = storage.find_path(source.id, target.id)
            if path_edges:
                st.success(f"找到路径，包含 {len(path_edges)} 个关系")
                node_ids = {source.id, target.id}
                for e in path_edges:
                    node_ids.add(e.source_id)
                    node_ids.add(e.target_id)
                nodes = [storage.get_node(nid) for nid in node_ids if storage.get_node(nid)]
                edges = path_edges
            else:
                st.warning("未找到路径")
        else:
            st.info("请选择不同的节点")
    
    # 渲染可视化
    if nodes and edges:
        # 显示统计
        st.write(f"📊 正在显示 {len(nodes)} 个节点，{len(edges)} 条边")
        
        # 生成 Vis.js HTML
        html_content = visualizer.generate_html(nodes, edges, title="知识图谱")
        
        # 使用 iframe 显示，确保 Vis.js 能正常加载
        import base64
        b64_html = base64.b64encode(html_content.encode('utf-8')).decode()
        iframe_src = f"data:text/html;base64,{b64_html}"
        
        iframe_html = f'<iframe src="{iframe_src}" width="100%" height="600px" frameborder="0"></iframe>'
        st.components.v1.html(iframe_html, height=620)
        
        # 导出选项
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 导出为 HTML"):
                # 保存文件
                filename = f"viz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                st.success(f"已保存: {filename}")
                
                # 提供下载按钮
                with open(filename, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="⬇️ 下载 HTML 文件",
                        data=f.read(),
                        file_name=filename,
                        mime="text/html"
                    )
        
        with col2:
            if st.button("📊 查看数据"):
                st.json({
                    "nodes": [{"id": n.id, "name": n.name, "type": n.node_type.value} for n in nodes],
                    "edges": [{"source": e.source_id, "target": e.target_id, "type": e.rel_type.value} for e in edges]
                })
    else:
        st.info("没有数据可显示")


def show_data_management():
    """数据管理页面"""
    st.markdown('<div class="main-header">💾 数据管理</div>', unsafe_allow_html=True)
    
    # 显示存储信息
    stats = storage.get_statistics()
    total_nodes = stats["total_nodes"]
    total_edges = stats["total_edges"]
    
    # 估算数据大小
    sample_data = {"nodes": [n.to_dict() for n in list(storage.nodes.values())[:10]], 
                   "edges": [e.to_dict() for e in list(storage.edges.values())[:10]]}
    avg_node_size = len(json.dumps(sample_data["nodes"])) / max(len(sample_data["nodes"]), 1)
    avg_edge_size = len(json.dumps(sample_data["edges"])) / max(len(sample_data["edges"]), 1)
    estimated_size = (total_nodes * avg_node_size + total_edges * avg_edge_size) / (1024 * 1024)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总节点", total_nodes)
    with col2:
        st.metric("总关系", total_edges)
    with col3:
        st.metric("估算大小", f"{estimated_size:.2f} MB")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 导出数据")
        
        if st.button("导出为 JSON"):
            data = {
                "nodes": [n.to_dict() for n in storage.get_all_nodes()],
                "edges": [e.to_dict() for e in storage.edges.values()],
                "export_time": datetime.now().isoformat()
            }
            
            filename = f"kg_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            st.success(f"数据已导出: {filename}")
            
            # 提供下载
            with open(filename, 'r', encoding='utf-8') as f:
                st.download_button(
                    label="下载 JSON 文件",
                    data=f.read(),
                    file_name=filename,
                    mime="application/json"
                )
        
        # 备份功能
        st.divider()
        st.subheader("💾 创建备份")
        if st.button("创建备份"):
            backup_file = storage.create_backup()
            st.success(f"备份已创建: {backup_file}")
    
    with col2:
        st.subheader("📥 导入数据")
        
        uploaded_file = st.file_uploader("选择 JSON 文件", type=['json'])
        
        if uploaded_file is not None:
            try:
                data = json.loads(uploaded_file.read())
                
                # 显示预览
                st.write(f"文件包含: {len(data.get('nodes', []))} 个节点, "
                        f"{len(data.get('edges', []))} 条边")
                
                if st.button("确认导入"):
                    with st.spinner("正在导入数据..."):
                        # 导入节点
                        node_count = 0
                        for node_data in data.get('nodes', []):
                            try:
                                node = Node(**node_data)
                                storage.create_node(node)
                                node_count += 1
                            except Exception as e:
                                logger.error(f"导入节点失败: {e}")
                        
                        # 导入边
                        edge_count = 0
                        for edge_data in data.get('edges', []):
                            try:
                                if 'label' in edge_data and isinstance(edge_data['label'], list):
                                    edge_data['label'] = tuple(edge_data['label'])
                                edge = Edge(**edge_data)
                                storage.create_edge(edge)
                                edge_count += 1
                            except Exception as e:
                                logger.error(f"导入边失败: {e}")
                        
                        st.success(f"导入完成: {node_count} 个节点, {edge_count} 条边")
                        st.rerun()
            
            except Exception as e:
                st.error(f"导入失败: {e}")


if __name__ == "__main__":
    main()
