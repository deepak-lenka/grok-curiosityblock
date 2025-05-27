import os
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import tempfile
from pathlib import Path
import json
import html
from dotenv import load_dotenv
from grok_api import get_grok_client, generate_mind_map

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Multidisciplinary Research Mind Map",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
    }
    .node-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Function to create a network visualization
def create_network_visualization(mind_map_data, primary_topic, secondary_topics):
    if not mind_map_data:
        return None
    
    # Create a pyvis network
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
    
    # Add the nodes
    discipline_colors = {
        "sociology": "#4285F4",  # Blue
        "economics": "#34A853",  # Green
        "history": "#FBBC05",    # Yellow
        "anthropology": "#EA4335",  # Red
        "political science": "#8E24AA",  # Purple
        "primary": "#1E3A8A",    # Dark Blue
        "secondary": "#3B82F6",  # Light Blue
        "interdisciplinary": "#6B7280"  # Gray
    }
    
    # Process nodes
    for node in mind_map_data.get("nodes", []):
        group = node.get("group", "interdisciplinary").lower()
        color = discipline_colors.get(group, discipline_colors["interdisciplinary"])
        
        # Determine node size based on importance
        size = 25
        if node["id"] == primary_topic.lower().replace(" ", "_") or node.get("label", "").lower() == primary_topic.lower():
            size = 40
        elif secondary_topics and node.get("label", "").lower() in [t.lower() for t in secondary_topics]:
            size = 35
            
        net.add_node(
            node["id"], 
            label=node["label"], 
            title=html.escape(node.get("description", "")),
            color=color,
            size=size
        )
    
    # Process edges
    for edge in mind_map_data.get("edges", []):
        net.add_edge(
            edge["from"],
            edge["to"],
            title=html.escape(edge.get("description", "")),
            label=edge.get("label", "")
        )
    
    # Set physics layout
    net.barnes_hut(spring_length=200, spring_strength=0.01, damping=0.09)
    
    # Generate the HTML file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
        path = tmp_file.name
        net.save_graph(path)
    
    return path

# Function to display node information
def display_node_info(mind_map_data, selected_node=None):
    if not mind_map_data or not selected_node:
        return
    
    # Find the selected node
    node_info = None
    for node in mind_map_data.get("nodes", []):
        if node["id"] == selected_node or node.get("label", "") == selected_node:
            node_info = node
            break
    
    if node_info:
        st.subheader(f"📍 {node_info.get('label', selected_node)}")
        st.markdown(f"**Discipline:** {node_info.get('group', 'Interdisciplinary')}")
        st.markdown(f"**Description:** {node_info.get('description', 'No description available.')}")
        
        # Find connections
        connections = []
        for edge in mind_map_data.get("edges", []):
            if edge["from"] == node_info["id"]:
                target_node = next((n for n in mind_map_data.get("nodes", []) if n["id"] == edge["to"]), None)
                if target_node:
                    connections.append({
                        "target": target_node.get("label", edge["to"]),
                        "relationship": edge.get("label", "related to"),
                        "description": edge.get("description", "")
                    })
            elif edge["to"] == node_info["id"]:
                source_node = next((n for n in mind_map_data.get("nodes", []) if n["id"] == edge["from"]), None)
                if source_node:
                    connections.append({
                        "target": source_node.get("label", edge["from"]),
                        "relationship": edge.get("label", "related to"),
                        "description": edge.get("description", "")
                    })
        
        if connections:
            st.subheader("🔗 Connections")
            for conn in connections:
                with st.expander(f"{conn['target']} ({conn['relationship']})"):
                    st.markdown(conn["description"])

# Main application
st.title("🧠 Multidisciplinary Research Mind Map")
st.markdown("""
This application generates interactive mind maps showing connections between different topics
across various academic disciplines. Enter a primary topic and optional secondary topics to explore
how they interconnect through the lenses of sociology, economics, history, anthropology, and political science.
""")

# Sidebar for inputs
with st.sidebar:
    st.header("📊 Mind Map Configuration")
    
    primary_topic = st.text_input("Primary Topic", value="Coffee")
    
    # Allow multiple secondary topics
    st.subheader("Secondary Topics")
    st.markdown("Add topics to connect with the primary topic")
    
    secondary_topics = []
    for i in range(3):  # Allow up to 3 secondary topics
        topic = st.text_input(f"Topic {i+1}", key=f"topic_{i}")
        if topic:
            secondary_topics.append(topic)
    
    # Default examples
    if not secondary_topics and primary_topic.lower() == "coffee":
        st.info("Tip: Try adding 'Politics', 'Gender', or 'Colonialism' as secondary topics!")
    
    # Generate button
    generate_button = st.button("Generate Mind Map", type="primary")
    
    # Example selector
    st.subheader("📚 Examples")
    example_option = st.selectbox(
        "Load example mind map",
        ["None", "Coffee and Politics", "Coffee, Gender, and Colonialism"]
    )

# Main content area
if "mind_map_data" not in st.session_state:
    st.session_state.mind_map_data = None
    st.session_state.selected_node = None
    st.session_state.related_topics = []
    st.session_state.topic_history = []

# Handle example selection
if example_option != "None":
    if example_option == "Coffee and Politics":
        primary_topic = "Coffee"
        secondary_topics = ["Politics"]
        generate_button = True
    elif example_option == "Coffee, Gender, and Colonialism":
        primary_topic = "Coffee"
        secondary_topics = ["Gender", "Colonialism"]
        generate_button = True

# Generate mind map if button is clicked
if generate_button:
    with st.spinner(f"Generating mind map for {primary_topic}..."):
        st.session_state.mind_map_data = generate_mind_map(primary_topic, secondary_topics)
        st.session_state.selected_node = None  # Reset selected node

# Display the mind map if data is available
if st.session_state.mind_map_data:
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Mind Map Visualization", "Data Explorer", "Related Topics"])
    
    with tab1:
        # Generate and display the network visualization
        html_path = create_network_visualization(
            st.session_state.mind_map_data, 
            primary_topic, 
            secondary_topics
        )
        
        if html_path:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            st.components.v1.html(html_content, height=600)
            st.caption("**Tip:** Click on nodes to see details. Drag nodes to rearrange the network.")
            
            # Clean up the temporary file
            try:
                os.unlink(html_path)
            except:
                pass
    
    with tab2:
        # Node selector
        st.subheader("🔍 Explore Nodes")
        
        # Get all node labels
        node_options = ["Select a node..."] + [
            node.get("label", node["id"]) 
            for node in st.session_state.mind_map_data.get("nodes", [])
        ]
        
        selected_node = st.selectbox("Select a node to view details", node_options)
        
        if selected_node != "Select a node...":
            st.session_state.selected_node = selected_node
        
        # Display node information
        if st.session_state.selected_node:
            display_node_info(st.session_state.mind_map_data, st.session_state.selected_node)
        
        # Display raw data (collapsible)
        with st.expander("View Raw JSON Data"):
            st.json(st.session_state.mind_map_data)
    
    with tab3:
        st.subheader("🔍 Related Topics")
        st.markdown("These topics are related to your current mind map and might be interesting to explore next.")
        
        # Extract related topics from the mind map data
        related_topics = st.session_state.mind_map_data.get("related_topics", [])
        
        if related_topics:
            # Store related topics in session state if not already there
            if not st.session_state.related_topics:
                st.session_state.related_topics = related_topics
            
            # Display related topics as clickable buttons
            st.subheader("Suggested Topics to Explore")
            cols = st.columns(3)
            
            for i, topic_data in enumerate(st.session_state.related_topics[:3]):
                topic = topic_data.get("topic")
                relevance = topic_data.get("relevance")
                
                with cols[i % 3]:
                    st.markdown(f"**{topic}**")
                    st.caption(relevance)
                    if st.button(f"Connect with {topic}", key=f"connect_{i}"):
                        # Add this topic to secondary topics and regenerate mind map
                        if topic not in secondary_topics:
                            secondary_topics.append(topic)
                            # Add to topic history
                            if primary_topic not in st.session_state.topic_history:
                                st.session_state.topic_history.append(primary_topic)
                            # Regenerate mind map
                            st.session_state.mind_map_data = generate_mind_map(primary_topic, secondary_topics)
                            st.experimental_rerun()
        
        # Allow user to add custom topic
        st.subheader("Add Your Own Topic")
        custom_topic = st.text_input("Enter a new topic to connect")
        if st.button("Add Connection", type="primary") and custom_topic:
            if custom_topic not in secondary_topics:
                secondary_topics.append(custom_topic)
                # Add to topic history
                if primary_topic not in st.session_state.topic_history:
                    st.session_state.topic_history.append(primary_topic)
                # Regenerate mind map
                st.session_state.mind_map_data = generate_mind_map(primary_topic, secondary_topics)
                st.experimental_rerun()
        
        # Show topic history
        if st.session_state.topic_history:
            st.subheader("Your Topic History")
            st.markdown("Topics you've explored:")
            history_list = ", ".join(st.session_state.topic_history)
            st.info(history_list)
else:
    # Display instructions when no mind map is generated
    st.info("👈 Enter a topic in the sidebar and click 'Generate Mind Map' to create a visualization.")
    
    # Display example images
    st.subheader("📊 Example Mind Maps")
    st.markdown("""
    The application will generate interactive mind maps showing connections between topics across various academic disciplines.
    
    **Example topics to try:**
    - Coffee and its connections to Politics
    - Gender studies and its relationship with Economics
    - Climate Change and its impact on various disciplines
    - Technology and its influence on Society
    """)
