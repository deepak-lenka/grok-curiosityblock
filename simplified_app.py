import os
import streamlit as st
import json
from openai import OpenAI
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Multidisciplinary Research Explorer",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
    }
    .research-output {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .related-topic {
        background-color: #e9ecef;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI client with Grok API
def get_grok_client():
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        st.error("XAI_API_KEY not found. Please set it in your .env file.")
        st.stop()
    
    # Create a custom httpx client without proxies
    http_client = httpx.Client()
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
        http_client=http_client
    )

# Function to generate multidisciplinary research
def generate_research(primary_topic, intent_topic, third_topic=None):
    client = get_grok_client()
    
    # Construct the prompt based on the examples
    system_prompt = """
    You are a multidisciplinary research assistant specializing in connecting diverse academic topics.
    Your task is to create a comprehensive research output that connects the provided topics
    through various academic lenses such as sociology, economics, history, anthropology, environmental studies, cultural studies, and political science.
    
    IMPORTANT: Follow this exact structure for your analysis:
    1. Start with connecting the primary topic and intent topic
    2. Then connect those to the third topic (if provided)
    3. Maintain all previous connections when adding new topics
    
    For example, if analyzing multiple topics:
    - First analyze the connections between the first two topics in detail
    - Then show how additional topics connect to the previous ones
    - Always maintain the previous connections while adding new topics
    - Create rich, nuanced connections between all topics with specific subtopics
    - Identify cross-cutting themes that span all topics
    
    Your analysis should include:
    - Specific subtopics under each disciplinary lens
    - Detailed explanations of how topics intersect
    - Historical contexts and contemporary relevance
    - Power dynamics and structural relationships
    - Practical implications and applications
    
    Format your response as a JSON object with the following structure:
    {
        "research_output": {
            "title": "Connecting [Topics]: A Multidisciplinary Exploration",
            "introduction": "Brief introduction to the connection between the topics",
            "connections": [
                {
                    "discipline": "[Relevant Discipline]",
                    "explanation": "Detailed explanation of connections through this discipline",
                    "subtopics": [
                        {
                            "name": "[Specific Subtopic]",
                            "details": "Detailed explanation of this subtopic"
                        },
                        {
                            "name": "[Specific Subtopic]",
                            "details": "Detailed explanation of this subtopic"
                        }
                    ],
                    "themes": ["Theme 1", "Theme 2", "Theme 3"]
                }
            ],
            "research_questions": [
                "Research question 1",
                "Research question 2",
                "Research question 3"
            ],
            "cross_cutting_themes": [
                "Theme connecting all topics 1",
                "Theme connecting all topics 2",
                "Theme connecting all topics 3"
            ],
            "mind_map": {
                "central_themes": "[List of all connected topics]",
                "key_connections": [
                    {
                        "node": "[Connection Point]",
                        "connects_to": "[Related Topic]",
                        "research_angles": "[Specific research approaches]"
                    }
                ]
            }
        },
        "related_topics": [
            {
                "topic": "Related Topic 1",
                "relevance": "Explanation of how this topic connects to the current research"
            },
            {
                "topic": "Related Topic 2",
                "relevance": "Explanation of how this topic connects to the current research"
            },
            {
                "topic": "Related Topic 3",
                "relevance": "Explanation of how this topic connects to the current research"
            }
        ]
    }
    
    The research output should be comprehensive, academic in tone, and highlight meaningful connections
    between the topics across multiple disciplines. The related topics should be relevant areas that would
    expand the research in interesting directions.
    """
    
    # Construct the user prompt based on provided topics
    if third_topic:
        user_prompt = f"Create a multidisciplinary research output connecting {primary_topic}, {intent_topic}, and {third_topic}. Pay special attention to the interconnections between all three topics."
    else:
        user_prompt = f"Create a multidisciplinary research output connecting {primary_topic} and {intent_topic}. Focus on meaningful connections between these topics across different academic disciplines."
    
    try:
        # Call Grok API
        completion = client.chat.completions.create(
            model="grok-3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=4000,  # Increased token limit for more detailed outputs
        )
        
        # Extract the response
        response_text = completion.choices[0].message.content
        
        # Extract JSON from the response
        try:
            # Find JSON content (it might be wrapped in markdown code blocks)
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text
                
            research_data = json.loads(json_str)
            return research_data
        except json.JSONDecodeError:
            st.error("Failed to parse the response from Grok API. Please try again.")
            st.code(response_text)
            return None
            
    except Exception as e:
        st.error(f"Error calling Grok API: {str(e)}")
        return None

# Main application
st.title("🔍 Multidisciplinary Research Explorer")
st.markdown("""
This application generates multidisciplinary research outputs that connect different topics
across various academic disciplines, following the structure from the examples.
""")

# Initialize session state for connection flow
if "connection_stage" not in st.session_state:
    st.session_state.connection_stage = "initial"
    st.session_state.topics = []
    st.session_state.next_topic_index = 0

# Different UI based on connection stage
if st.session_state.connection_stage == "initial":
    st.markdown("### Step 1: Start with connecting two topics")
    st.markdown("Begin by connecting your first two topics (e.g., Coffee and Politics)")
    
    # Input form for initial two topics
    with st.form("initial_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            primary_topic = st.text_input("Primary Topic", value="Coffee")
        
        with col2:
            intent_topic = st.text_input("Intent Topic", value="Politics")
        
        submit_button = st.form_submit_button("Generate Research", type="primary")

elif st.session_state.connection_stage == "continue":
    # Show the current connection path
    topic_count = len(st.session_state.topics)
    
    if topic_count == 2:
        st.markdown(f"### Step 2: Connect to a third topic")
        st.markdown(f"Now connect {st.session_state.topics[0]} and {st.session_state.topics[1]} to a third topic")
    else:
        st.markdown(f"### Continue your research journey")
        topics_str = ", ".join(st.session_state.topics[:-1]) + f", and {st.session_state.topics[-1]}"
        st.markdown(f"Now connect {topics_str} to another topic")
    
    # Input form for next topic
    with st.form(f"next_topic_form_{st.session_state.next_topic_index}"):
        if topic_count == 2:
            next_topic = st.text_input("Third Topic to Connect", value="Gender")
        else:
            next_topic = st.text_input("Next Topic to Connect", value="")
        
        submit_button = st.form_submit_button("Connect Topic", type="primary")

# Initialize session state
if "research_data" not in st.session_state:
    st.session_state.research_data = None
    st.session_state.topic_history = []
    st.session_state.current_primary = None
    st.session_state.current_intent = None

# Handle form submissions based on connection stage
if st.session_state.connection_stage == "initial" and submit_button:
    with st.spinner(f"Generating research connecting {primary_topic} and {intent_topic}..."):
        st.session_state.research_data = generate_research(primary_topic, intent_topic)
        st.session_state.topics = [primary_topic, intent_topic]
        
        # Add to topic history
        history_entry = f"{primary_topic} → {intent_topic}"
        if "topic_history" not in st.session_state:
            st.session_state.topic_history = []
        if history_entry not in st.session_state.topic_history:
            st.session_state.topic_history.append(history_entry)
        
        # Move to continue stage
        st.session_state.connection_stage = "continue"
        st.experimental_rerun()

elif st.session_state.connection_stage == "continue" and submit_button:
    # Get the current topics and the new topic to connect
    current_topics = st.session_state.topics.copy()
    topic_count = len(current_topics)
    
    # Create a spinner message based on the number of topics
    if topic_count == 2:
        spinner_message = f"Generating research connecting {current_topics[0]}, {current_topics[1]}, and {next_topic}..."
    else:
        topics_str = ", ".join(current_topics[:-1]) + f", and {current_topics[-1]}"
        spinner_message = f"Generating research connecting {topics_str}, and {next_topic}..."
    
    with st.spinner(spinner_message):
        # For topics beyond the third, we'll use a special approach to maintain all connections
        if topic_count == 2:
            # Simple case for third topic
            st.session_state.research_data = generate_research(current_topics[0], current_topics[1], next_topic)
        else:
            # For additional topics, we'll pass the last topic and the new topic as the third parameter
            # This ensures we maintain all previous connections
            combined_prompt = f"{current_topics[-1]} and {next_topic}"
            st.session_state.research_data = generate_research(current_topics[0], current_topics[1], combined_prompt)
        
        # Add the new topic to the list
        st.session_state.topics.append(next_topic)
        
        # Add to topic history
        history_entry = " → ".join(st.session_state.topics)
        if history_entry not in st.session_state.topic_history:
            st.session_state.topic_history.append(history_entry)
        
        # Increment the next topic index to avoid duplicate widget keys
        st.session_state.next_topic_index += 1
        
        # Stay in continue stage
        st.experimental_rerun()

# Add a Start New Research button in the sidebar
with st.sidebar:
    st.title("Your Research Journey")
    
    # Display topic history
    if "topic_history" in st.session_state and st.session_state.topic_history:
        for entry in st.session_state.topic_history:
            st.markdown(f"- {entry}")
    
    # Always show the Start New Research button
    if st.button("Start New Research", key="new_research_sidebar"):
        st.session_state.connection_stage = "initial"
        st.session_state.topics = []
        st.session_state.next_topic_index = 0
        st.experimental_rerun()

# Display research output if available
if st.session_state.research_data:
    research_output = st.session_state.research_data.get("research_output", {})
    
    # Display title and introduction
    if len(st.session_state.topics) > 2:
        title = research_output.get("title", f"Connecting {', '.join(st.session_state.topics[:-1])}, and {st.session_state.topics[-1]}")
    else:
        title = research_output.get("title", f"Connecting {st.session_state.topics[0]} and {st.session_state.topics[1]}")
    
    st.header(title)
    st.markdown(research_output.get("introduction", ""))
    
    # Show the current connection path
    st.info(f"**Current Connection Path:** {' → '.join(st.session_state.topics)}")
    
    # Success message about the current connections
    topic_count = len(st.session_state.topics)
    if topic_count == 2:
        st.success(f"✅ Successfully connected {st.session_state.topics[0]} and {st.session_state.topics[1]}. You can now connect to more topics.")
    else:
        topics_str = ", ".join(st.session_state.topics[:-1]) + f", and {st.session_state.topics[-1]}"
        st.success(f"✅ Successfully connected {topics_str}. You can continue adding more topics.")
        
    # Add a Start New Research button in the main area too
    if st.button("Start New Research", key="new_research_main"):
        st.session_state.connection_stage = "initial"
        st.session_state.topics = []
        st.session_state.next_topic_index = 0
        st.experimental_rerun()
    
    # Display connections by discipline
    st.subheader("Disciplinary Connections")
    
    for connection in research_output.get("connections", []):
        with st.expander(f"**{connection.get('discipline')}**", expanded=True):
            st.markdown(connection.get("explanation", ""))
            
            st.markdown("**Key Themes:**")
            themes = connection.get("themes", [])
            for theme in themes:
                st.markdown(f"- {theme}")
    
    # Display research questions
    st.subheader("Research Questions")
    for question in research_output.get("research_questions", []):
        st.markdown(f"- {question}")
        
    # Display cross-cutting themes if available
    if "cross_cutting_themes" in research_output and research_output["cross_cutting_themes"]:
        st.subheader("Cross-Cutting Themes")
        st.markdown("These themes connect all the topics across multiple disciplines:")
        for theme in research_output.get("cross_cutting_themes", []):
            st.markdown(f"- {theme}")
    
    # Display related topics section for continuing research
    if st.session_state.connection_stage == "continue":
        st.header("Related Topics to Explore")
        related_topics = st.session_state.research_data.get("related_topics", [])
        
        st.markdown("**Connect to one of these topics or enter your own:**")
        
        # Show suggested topics as buttons
        cols = st.columns(3)
        for i, topic_data in enumerate(related_topics[:3]):
            topic = topic_data.get("topic", "")
            relevance = topic_data.get("relevance", "")
            
            with cols[i]:
                st.markdown(f"**{topic}**")
                st.markdown(relevance)
                if st.button(f"Connect with {topic}", key=f"connect_{i}_{st.session_state.next_topic_index}"):
                    # Get the current topics
                    current_topics = st.session_state.topics.copy()
                    topic_count = len(current_topics)
                    
                    # Create a spinner message
                    if topic_count == 2:
                        spinner_message = f"Generating research connecting {current_topics[0]}, {current_topics[1]}, and {topic}..."
                    else:
                        topics_str = ", ".join(current_topics[:-1]) + f", and {current_topics[-1]}"
                        spinner_message = f"Generating research connecting {topics_str}, and {topic}..."
                    
                    with st.spinner(spinner_message):
                        # For topics beyond the third, we'll use a special approach to maintain all connections
                        if topic_count == 2:
                            # Simple case for third topic
                            st.session_state.research_data = generate_research(current_topics[0], current_topics[1], topic)
                        else:
                            # For additional topics, we'll pass the last topic and the new topic as the third parameter
                            combined_prompt = f"{current_topics[-1]} and {topic}"
                            st.session_state.research_data = generate_research(current_topics[0], current_topics[1], combined_prompt)
                        
                        # Add the new topic to the list
                        st.session_state.topics.append(topic)
                        
                        # Add to topic history
                        history_entry = " → ".join(st.session_state.topics)
                        if history_entry not in st.session_state.topic_history:
                            st.session_state.topic_history.append(history_entry)
                        
                        # Increment the next topic index to avoid duplicate widget keys
                        st.session_state.next_topic_index += 1
                        
                        # Stay in continue stage
                        st.experimental_rerun()
    
    # Custom topic input - only show if we're in continue stage
    if st.session_state.connection_stage == "continue":
        st.subheader("Add Your Own Topic")
        custom_col1, custom_col2 = st.columns([3, 1])
        
        with custom_col1:
            # Create a dynamic prompt based on current topics
            current_topics = st.session_state.topics.copy()
            if len(current_topics) == 2:
                prompt = f"Enter a topic to connect with {current_topics[0]} and {current_topics[1]}"
            else:
                topics_str = ", ".join(current_topics[:-1]) + f", and {current_topics[-1]}"
                prompt = f"Enter a topic to connect with {topics_str}"
                
            custom_topic = st.text_input(prompt, key=f"custom_topic_{st.session_state.next_topic_index}")
        
        with custom_col2:
            if st.button("Connect", type="primary", key=f"connect_custom_{st.session_state.next_topic_index}") and custom_topic:
                # Get the current topics
                current_topics = st.session_state.topics.copy()
                topic_count = len(current_topics)
                
                # Create a spinner message
                if topic_count == 2:
                    spinner_message = f"Generating research connecting {current_topics[0]}, {current_topics[1]}, and {custom_topic}..."
                else:
                    topics_str = ", ".join(current_topics[:-1]) + f", and {current_topics[-1]}"
                    spinner_message = f"Generating research connecting {topics_str}, and {custom_topic}..."
                
                with st.spinner(spinner_message):
                    # For topics beyond the third, we'll use a special approach to maintain all connections
                    if topic_count == 2:
                        # Simple case for third topic
                        st.session_state.research_data = generate_research(current_topics[0], current_topics[1], custom_topic)
                    else:
                        # For additional topics, we'll pass the last topic and the new topic as the third parameter
                        combined_prompt = f"{current_topics[-1]} and {custom_topic}"
                        st.session_state.research_data = generate_research(current_topics[0], current_topics[1], combined_prompt)
                    
                    # Add the new topic to the list
                    st.session_state.topics.append(custom_topic)
                    
                    # Add to topic history
                    history_entry = " → ".join(st.session_state.topics)
                    if history_entry not in st.session_state.topic_history:
                        st.session_state.topic_history.append(history_entry)
                    
                    # Increment the next topic index to avoid duplicate widget keys
                    st.session_state.next_topic_index += 1
                    
                    # Stay in continue stage
                    st.experimental_rerun()
    
    # Topic history is already displayed in the sidebar
else:
    # Display instructions
    st.info("👆 Enter a primary topic and an intent topic, then click 'Generate Research' to create a multidisciplinary research output.")
    
    # Example topics
    st.subheader("Example Topics to Try")
    st.markdown("""
    - Primary: Coffee, Intent: Politics
    - Primary: Gender, Intent: Economics
    - Primary: Technology, Intent: Society
    - Primary: Climate Change, Intent: Migration
    """)
