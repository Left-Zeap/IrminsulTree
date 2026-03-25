# Helper script to create app.py with proper encoding
content = '''# -*- coding: utf-8 -*-
"""
Streamlit GUI Main Application
No Neo4j required, pure local knowledge graph management system
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Page configuration (must be first)
st.set_page_config(
    page_title="Genshin Knowledge Graph Manager",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

from core.models import Node, Edge, NodeType, RelationType, PersonCategory, MiscCategory
from core.storage import get_storage
from core.visualizer import get_visualizer

# Initialize
storage = get_storage()
visualizer = get_visualizer()

# CSS Styles
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main function"""
    with st.sidebar:
        st.title("🌐 Knowledge Graph Manager")
        
        page = st.radio(
            "Select Function",
            ["📊 Overview", "➕ Add Node", "🔗 Add Relation", "📋 Node List", "🔍 Search", "🕸️ Visualization", "💾 Data Management"]
        )
        
        st.divider()
        
        stats = storage.get_statistics()
        st.metric("Total Nodes", stats["total_nodes"])
        st.metric("Total Relations", stats["total_edges"])
    
    if "Overview" in page:
        show_overview()
    elif "Add Node" in page:
        show_add_node()
    elif "Add Relation" in page:
        show_add_relation()
    elif "Node List" in page:
        show_node_list()
    elif "Search" in page:
        show_search()
    elif "Visualization" in page:
        show_visualization()
    elif "Data Management" in page:
        show_data_management()


def show_overview():
    """Overview page"""
    st.markdown("<div class='main-header'>📊 Knowledge Graph Overview</div>", unsafe_allow_html=True)
    
    stats = storage.get_statistics()
    
    cols = st.columns(4)
    with cols[0]:
        st.metric("Total Nodes", stats["total_nodes"])
    with cols[1]:
        st.metric("Total Relations", stats["total_edges"])
    with cols[2]:
        st.metric("Persons", stats["nodes_by_type"].get("Person", 0))
    with cols[3]:
        st.metric("Events", stats["nodes_by_type"].get("Event", 0))
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Node Type Distribution")
        if stats["nodes_by_type"]:
            df = pd.DataFrame([
                {"Type": k, "Count": v}
                for k, v in stats["nodes_by_type"].items()
            ])
            st.bar_chart(df.set_index("Type"))
        else:
            st.info("No data yet")
    
    with col2:
        st.subheader("🕸️ Quick Actions")
        
        if st.button("➕ Add Person"):
            st.session_state.page = "Add Node"
            st.rerun()
        
        if st.button("🔗 Add Relation"):
            st.session_state.page = "Add Relation"
            st.rerun()


def show_add_node():
    """Add node page"""
    st.markdown("<div class='main-header'>➕ Add Node</div>", unsafe_allow_html=True)
    
    node_type = st.selectbox(
        "Select Node Type",
        options=[
            ("Person", "👤 Person"),
            ("Event", "📅 Event"),
            ("Location", "📍 Location"),
            ("Quest", "📜 Quest"),
            ("Organization", "🏛️ Organization"),
            ("Misc", "📦 Misc"),
            ("Entry", "📖 Entry"),
        ],
        format_func=lambda x: x[1]
    )[0]
    
    with st.form("add_node_form"):
        name = st.text_input("Name *", placeholder="Enter name")
        aliases = st.text_input("Aliases", placeholder="Separate with commas")
        
        if node_type == "Person":
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox("Category", ["自机", "npc", "未出现"])
            with col2:
                birth_year = st.number_input("Birth Year", value=None, step=1)
            death_year = st.number_input("Death Year", value=None, step=1)
        
        elif node_type in ["Event", "Location", "Quest", "Organization"]:
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.number_input("Start Time", value=None, step=1)
            with col2:
                end_time = st.number_input("End Time", value=None, step=1)
            
            if node_type == "Location":
                poi_codes = st.text_input("POI Codes", placeholder="Separate with commas")
        
        elif node_type == "Misc":
            misc_category = st.selectbox("Misc Category", ["书籍", "圣遗物", "翅膀", "武器", "大世界文本"])
        
        submitted = st.form_submit_button("✅ Create Node")
        
        if submitted:
            if not name:
                st.error("Name is required!")
                return
            
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
            
            node = Node(**node_data)
            node_id = storage.create_node(node)
            
            st.success(f"✅ Node created! ID: {node_id}")


def show_add_relation():
    """Add relation page"""
    st.markdown("<div class='main-header'>🔗 Add Relation</div>", unsafe_allow_html=True)
    
    nodes = storage.get_all_nodes()
    
    if len(nodes) < 2:
        st.warning("Need at least 2 nodes")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Source Node")
        source_options = {f"[{n.node_type.value}] {n.name} ({n.id})": n for n in nodes}
        source_key = st.selectbox("Select source", options=list(source_options.keys()), key="source")
        source_node = source_options[source_key]
    
    with col2:
        st.subheader("Target Node")
        target_options = {f"[{n.node_type.value}] {n.name} ({n.id})": n for n in nodes if n.id != source_node.id}
        if target_options:
            target_key = st.selectbox("Select target", options=list(target_options.keys()), key="target")
            target_node = target_options[target_key]
        else:
            st.error("No other nodes available")
            return
    
    st.divider()
    
    rel_type = st.selectbox(
        "Relation Type",
        options=[
            (RelationType.MEMBER_OF, "👤 Member Of"),
            (RelationType.PARTICIPATED_IN, "🎭 Participated In"),
            (RelationType.RELATED_TO, "🤝 Related To"),
            (RelationType.LOCATED_AT, "📍 Located At"),
            (RelationType.EVENT_AT, "📅 Event At"),
            (RelationType.SUB_EVENT_OF, "📖 Sub Event Of"),
            (RelationType.SUB_LOCATION_OF, "🏠 Sub Location Of"),
            (RelationType.ASSOCIATED_WITH, "🔗 Associated With"),
        ],
        format_func=lambda x: x[1]
    )[0]
    
    direction = "undirected" if rel_type == RelationType.RELATED_TO else "directed"
    
    label = st.text_input("Relation Label (optional)", placeholder="e.g., friend, participated...")
    
    if rel_type in [RelationType.MEMBER_OF, RelationType.LOCATED_AT]:
        st.subheader("⏰ Time Range (optional)")
        col1, col2 = st.columns(2)
        with col1:
            start_year = st.number_input("Start Year", value=None, step=1, key="rel_start")
        with col2:
            end_year = st.number_input("End Year", value=None, step=1, key="rel_end")
        if start_year is not None or end_year is not None:
            label = (start_year, end_year)
    
    if st.button("✅ Create Relation"):
        try:
            edge = Edge(
                source_id=source_node.id,
                target_id=target_node.id,
                rel_type=rel_type,
                direction=direction,
                label=label if label else None
            )
            edge_id = storage.create_edge(edge)
            st.success(f"✅ Relation created! ID: {edge_id}")
        except Exception as e:
            st.error(f"❌ Failed: {e}")


def show_node_list():
    """Node list page"""
    st.markdown("<div class='main-header'>📋 Node List</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        filter_type = st.selectbox(
            "Filter Type",
            options=["All"] + [t.value for t in NodeType]
        )
    
    if filter_type == "All":
        nodes = storage.get_all_nodes()
    else:
        nodes = storage.get_all_nodes(node_type=filter_type)
    
    st.write(f"Total **{len(nodes)}** nodes")
    
    if nodes:
        data = []
        for n in nodes:
            data.append({
                "ID": n.id,
                "Name": n.name,
                "Type": n.node_type.value,
                "Aliases": ", ".join(n.aliases) if n.aliases else "-",
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, hide_index=True)


def show_search():
    """Search page"""
    st.markdown("<div class='main-header'>🔍 Search Nodes</div>", unsafe_allow_html=True)
    
    keyword = st.text_input("Search keyword", placeholder="Enter name or alias...")
    
    if keyword:
        results = storage.search_nodes(name_pattern=keyword, limit=50)
        
        st.write(f"Found **{len(results)}** results")
        
        for node in results:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{node.name}** ({node.node_type.value})")
                with col2:
                    st.button("View", key=f"search_view_{node.id}")
    else:
        st.info("Enter keyword to search")


def show_visualization():
    """Visualization page"""
    st.markdown("<div class='main-header'>🕸️ Graph Visualization</div>", unsafe_allow_html=True)
    
    mode = st.radio(
        "Mode",
        options=["Full Graph", "Subgraph", "Path Find"],
        horizontal=True
    )
    
    nodes = []
    edges = []
    
    if mode == "Full Graph":
        all_nodes = storage.get_all_nodes()
        if len(all_nodes) > 200:
            st.warning(f"Too many nodes ({len(all_nodes)}), showing first 200")
            all_nodes = all_nodes[:200]
        node_ids = [n.id for n in all_nodes]
        nodes, edges = storage.get_subgraph(node_ids, depth=1)
    
    elif mode == "Subgraph":
        all_nodes = storage.get_all_nodes()
        if all_nodes:
            options = {f"{n.name} ({n.node_type.value})": n for n in all_nodes}
            selected = st.selectbox("Center node", options=list(options.keys()))
            center_node = options[selected]
            
            depth = st.slider("Depth", min_value=1, max_value=3, value=2)
            
            nodes, edges = storage.get_subgraph([center_node.id], depth=depth)
    
    if nodes and edges:
        html_content = visualizer.generate_html(nodes, edges, title="Knowledge Graph")
        st.components.v1.html(html_content, height=600, scrolling=True)
    else:
        st.info("No data to display")


def show_data_management():
    """Data management page"""
    st.markdown("<div class='main-header'>💾 Data Management</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Export Data")
        
        if st.button("Export as JSON"):
            data = {
                "nodes": [n.to_dict() for n in storage.get_all_nodes()],
                "edges": [e.to_dict() for e in storage.edges.values()],
            }
            
            filename = "export_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            st.success(f"Exported: {filename}")
    
    with col2:
        st.subheader("📥 Import Data")
        
        uploaded_file = st.file_uploader("Select JSON file", type=['json'])
        
        if uploaded_file is not None:
            try:
                data = json.loads(uploaded_file.read())
                
                if st.button("Confirm Import"):
                    for node_data in data.get('nodes', []):
                        node = Node(**node_data)
                        storage.create_node(node)
                    
                    for edge_data in data.get('edges', []):
                        if 'label' in edge_data and isinstance(edge_data['label'], list):
                            edge_data['label'] = tuple(edge_data['label'])
                        edge = Edge(**edge_data)
                        storage.create_edge(edge)
                    
                    st.success("Import completed!")
            except Exception as e:
                st.error(f"Import failed: {e}")
    
    st.divider()
    
    st.subheader("⚠️ Danger Zone")
    
    if st.button("🗑️ Clear All Data", type="primary"):
        confirm = st.checkbox("I confirm to delete all data")
        if confirm:
            storage.nodes.clear()
            storage.edges.clear()
            storage.node_name_index.clear()
            storage.adjacency.clear()
            storage.save()
            st.success("All data cleared")
            st.rerun()


if __name__ == "__main__":
    main()
'''

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('File created successfully')
