import os
import streamlit as st
import json
from openai import OpenAI
import httpx

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

# Function to generate mind map data using Grok API
def generate_mind_map(primary_topic, secondary_topics=None):
    client = get_grok_client()
    
    # Construct the prompt
    system_prompt = """
    You are a multidisciplinary research assistant specialized in creating comprehensive mind maps.
    Your task is to analyze the provided topics and generate a detailed mind map showing connections
    across various academic disciplines including sociology, economics, history, anthropology, and political science.
    
    For each connection, provide:
    1. A brief explanation of how the topics relate
    2. The academic discipline(s) relevant to this connection
    3. Key themes or concepts that bridge these topics
    
    Format your response as a JSON object with the following structure:
    {
        "nodes": [
            {"id": "unique_id", "label": "Node Label", "group": "discipline", "description": "detailed description"}
        ],
        "edges": [
            {"from": "source_node_id", "to": "target_node_id", "label": "relationship", "description": "explanation"}
        ],
        "related_topics": [
            {"topic": "Related Topic 1", "relevance": "Brief explanation of relevance"},
            {"topic": "Related Topic 2", "relevance": "Brief explanation of relevance"},
            {"topic": "Related Topic 3", "relevance": "Brief explanation of relevance"}
        ]
    }
    
    The 'related_topics' should contain 3 topics that are not already in the mind map but are highly relevant to the existing topics.
    These should be topics that would be interesting to explore next and would add valuable connections to the mind map.
    
    Be comprehensive but concise. Focus on academic connections and ensure all relationships are substantiated.
    """
    
    # Construct the user prompt based on provided topics
    if secondary_topics and len(secondary_topics) > 0:
        topics_list = ", ".join(secondary_topics)
        user_prompt = f"Create a multidisciplinary research mind map for the primary topic '{primary_topic}' and how it connects with {topics_list}. Include connections across sociology, economics, history, anthropology, and political science."
    else:
        user_prompt = f"Create a multidisciplinary research mind map for the topic '{primary_topic}'. Include connections across sociology, economics, history, anthropology, and political science."
    
    try:
        # Call Grok API
        completion = client.chat.completions.create(
            model="grok-3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
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
                
            mind_map_data = json.loads(json_str)
            return mind_map_data
        except json.JSONDecodeError:
            st.error("Failed to parse the response from Grok API. Please try again.")
            st.code(response_text)
            return None
            
    except Exception as e:
        st.error(f"Error calling Grok API: {str(e)}")
        return None
