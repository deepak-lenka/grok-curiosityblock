import requests
import json

def get_research(primary_topic, intent_topic, third_topic=None):
    """
    Function to get research output from the API
    """
    # API endpoint for research
    api_url = "http://localhost:8001/research/"
    
    # Prepare request data
    request_data = {
        "primary_topic": primary_topic,
        "intent_topic": intent_topic
    }
    
    # Add third topic if provided
    if third_topic:
        request_data["third_topic"] = third_topic
    
    # Make the API request
    print(f"Sending research request to {api_url}...")
    response = requests.post(api_url, json=request_data)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        research_data = response.json()
        
        # Print the research output
        print("\n" + "="*80)
        print(f"RESEARCH TITLE: {research_data['research_output']['title']}")
        print("="*80)
        print(f"\nINTRODUCTION:\n{research_data['research_output']['introduction']}")
        
        # Print connections by discipline
        print("\nCONNECTIONS BY DISCIPLINE:")
        for connection in research_data['research_output']['connections']:
            print(f"\n{connection['discipline']}:")
            print(f"  {connection['explanation'][:150]}...")
            
            # Print subtopics if available
            if 'subtopics' in connection:
                print("\n  Subtopics:")
                for subtopic in connection['subtopics']:
                    print(f"    - {subtopic['name']}")
        
        # Print research questions
        print("\nRESEARCH QUESTIONS:")
        for i, question in enumerate(research_data['research_output']['research_questions'], 1):
            print(f"  {i}. {question}")
        
        # Save the full response to a file
        with open('research_output.json', 'w') as f:
            json.dump(research_data, f, indent=2)
            
        print("\nFull research output saved to 'research_output.json'")
        
        # Return the topics for related topics search
        topics = [primary_topic, intent_topic]
        if third_topic:
            topics.append(third_topic)
        return topics
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def get_related_topics(topics):
    """
    Function to get related topics from the API
    """
    # API endpoint for related topics
    api_url = "http://localhost:8001/related-topics/"
    
    # Prepare request data
    request_data = {
        "topics": topics
    }
    
    # Make the API request
    print(f"\nSending related topics request to {api_url}...")
    response = requests.post(api_url, json=request_data)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        related_topics_data = response.json()
        
        # Print related topics
        print("\n" + "="*80)
        print("RELATED TOPICS")
        print("="*80)
        
        for topic in related_topics_data['related_topics']:
            print(f"\n- {topic['topic']}")
            print(f"  {topic['relevance']}")
        
        # Save the full response to a file
        with open('related_topics.json', 'w') as f:
            json.dump(related_topics_data, f, indent=2)
            
        print("\nFull related topics saved to 'related_topics.json'")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def main():
    """
    Example client script to demonstrate how to use the Multidisciplinary Research Explorer API
    """
    # Example topics
    primary_topic = "Coffee"
    intent_topic = "Politics"
    third_topic = "Gender"  # Optional, can be None
    
    # Step 1: Get research output
    topics = get_research(primary_topic, intent_topic, third_topic)
    
    # Step 2: If research was successful, get related topics
    if topics:
        get_related_topics(topics)

if __name__ == "__main__":
    main()
