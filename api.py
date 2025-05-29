import os
import json
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
import httpx

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Multidisciplinary Research Explorer API",
    description="API for generating multidisciplinary research outputs connecting diverse academic topics",
    version="1.0.0"
)

# Pydantic models for request and response
class ResearchRequest(BaseModel):
    primary_topic: str
    intent_topic: str
    previous_topics: Optional[List[str]] = None

class ContinueResearchRequest(BaseModel):
    topics: List[str]  # All existing topics
    next_topic: str    # New topic to connect

class RelatedTopicsRequest(BaseModel):
    topics: List[str]

class ResearchResponse(BaseModel):
    research_output: Dict[str, Any]
    related_topics: List[Dict[str, str]]
    connection_path: str

class RelatedTopicsResponse(BaseModel):
    related_topics: List[Dict[str, str]]

# Function to get Grok client
def get_grok_client():
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Grok API key not found in environment variables")
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
    )

# Function to generate multidisciplinary research
def generate_research(primary_topic: str, intent_topic: str, previous_topics: Optional[List[str]] = None):
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
    """
    
    # Construct the user prompt based on provided topics
    if previous_topics and len(previous_topics) > 0:
        # Format all previous topics as a comma-separated string
        previous_topics_str = ", ".join(previous_topics)
        user_prompt = f"Create a multidisciplinary research output connecting {primary_topic}, {intent_topic}, and the following previous topics: {previous_topics_str}. Pay special attention to the interconnections between all topics."
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
            raise HTTPException(status_code=500, detail="Failed to parse the response from Grok API")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Grok API: {str(e)}")

# Function to generate related topics based on provided topics
def generate_related_topics(topics: List[str]):
    client = get_grok_client()
    
    # Construct the prompt for related topics
    system_prompt = """
    You are a multidisciplinary research assistant specializing in connecting diverse academic topics.
    Your task is to suggest related topics that would expand the research on the provided topics.
    
    For each suggested topic, provide:
    1. The topic name
    2. A brief explanation of how it connects to the provided topics
    3. Why exploring this connection would be valuable
    
    Format your response as a JSON object with the following structure:
    {
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
    """
    
    # Construct the user prompt based on provided topics
    topics_str = ", ".join(topics[:-1]) + f", and {topics[-1]}" if len(topics) > 1 else topics[0]
    user_prompt = f"Suggest related topics that would expand research on {topics_str}. Focus on topics that create interesting interdisciplinary connections."
    
    try:
        # Call Grok API
        completion = client.chat.completions.create(
            model="grok-3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
            max_tokens=1000,
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
                
            related_topics_data = json.loads(json_str)
            return related_topics_data
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to parse the response from Grok API")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Grok API: {str(e)}")

# API endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to the Multidisciplinary Research Explorer API"}

@app.post("/research/", response_model=ResearchResponse)
async def create_research(request: ResearchRequest):
    """
    Generate multidisciplinary research connecting the provided topics.
    
    - **primary_topic**: The first topic to explore
    - **intent_topic**: The second topic to connect with the primary topic
    - **previous_topics**: Optional array of previously explored topics to connect with the first two
    """
    research_data = generate_research(
        primary_topic=request.primary_topic,
        intent_topic=request.intent_topic,
        previous_topics=request.previous_topics
    )
    
    # Create connection path string
    all_topics = [request.primary_topic, request.intent_topic]
    if request.previous_topics and len(request.previous_topics) > 0:
        all_topics.extend(request.previous_topics)
    connection_path = " → ".join(all_topics)
    
    return {
        "research_output": research_data["research_output"],
        "related_topics": research_data["related_topics"],
        "connection_path": connection_path
    }

@app.post("/continue-research/", response_model=ResearchResponse)
async def continue_research(request: ContinueResearchRequest):
    """
    Continue research by adding a new topic while maintaining all previous connections.
    
    - **topics**: List of all existing connected topics
    - **next_topic**: New topic to connect with the existing topics
    """
    # Get the current topics and the new topic to connect
    current_topics = request.topics
    next_topic = request.next_topic
    topic_count = len(current_topics)
    
    if topic_count < 2:
        raise HTTPException(status_code=400, detail="At least two existing topics are required")
    
    # Use the new approach with previous_topics parameter
    # First two topics remain as primary and intent topics
    # All other existing topics plus the new topic go into previous_topics
    previous_topics = []
    
    if topic_count > 2:
        # Add all topics from index 2 onwards to previous_topics
        previous_topics.extend(current_topics[2:])
    
    # Add the new topic to previous_topics
    previous_topics.append(next_topic)
    
    # Generate research with the new structure
    research_data = generate_research(
        primary_topic=current_topics[0],
        intent_topic=current_topics[1],
        previous_topics=previous_topics
    )
    
    # Create updated topics list and connection path
    updated_topics = current_topics + [next_topic]
    connection_path = " → ".join(updated_topics)
    
    return {
        "research_output": research_data["research_output"],
        "related_topics": research_data["related_topics"],
        "connection_path": connection_path
    }

@app.post("/related-topics/", response_model=RelatedTopicsResponse)
async def get_related_topics(request: RelatedTopicsRequest):
    """
    Generate related topics based on the provided topics.
    
    - **topics**: List of topics to find related topics for
    """
    related_topics_data = generate_related_topics(request.topics)
    
    return related_topics_data

@app.get("/health/")
async def health_check():
    """Check if the API is running properly"""
    return {"status": "healthy", "api_version": "1.0.0"}

# Run the application with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
