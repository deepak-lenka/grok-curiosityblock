import requests
import json

def get_research(primary_topic, intent_topic, previous_topics=None):
    """
    Function to get initial research output from the API
    """
    # API endpoint for research
    api_url = "http://localhost:8001/research/"
    
    # Prepare request data
    request_data = {
        "primary_topic": primary_topic,
        "intent_topic": intent_topic
    }
    
    # Add previous topics if provided
    if previous_topics and len(previous_topics) > 0:
        request_data["previous_topics"] = previous_topics
    
    # Make the API request
    print(f"Sending research request to {api_url}...")
    response = requests.post(api_url, json=request_data)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        research_data = response.json()
        
        # Print the connection path
        print(f"\nConnection Path: {research_data['connection_path']}")
        
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
        
        # Extract topics from connection path
        topics = research_data['connection_path'].split(' → ')
        return research_data, topics
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None, None

def continue_research(topics, next_topic):
    """
    Function to continue research by adding a new topic
    """
    # API endpoint for continuing research
    api_url = "http://localhost:8001/continue-research/"
    
    # Prepare request data
    request_data = {
        "topics": topics,
        "next_topic": next_topic
    }
    
    # Make the API request
    print(f"\nContinuing research with new topic: {next_topic}")
    print(f"Sending continue-research request to {api_url}...")
    response = requests.post(api_url, json=request_data)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        research_data = response.json()
        
        # Print the updated connection path
        print(f"\nUpdated Connection Path: {research_data['connection_path']}")
        
        # Print the research output
        print("\n" + "="*80)
        print(f"RESEARCH TITLE: {research_data['research_output']['title']}")
        print("="*80)
        print(f"\nINTRODUCTION:\n{research_data['research_output']['introduction']}")
        
        # Print connections by discipline (just the first two for brevity)
        print("\nCONNECTIONS BY DISCIPLINE (sample):")
        for connection in research_data['research_output']['connections'][:2]:
            print(f"\n{connection['discipline']}:")
            print(f"  {connection['explanation'][:150]}...")
        
        # Save the full response to a file
        with open('continued_research_output.json', 'w') as f:
            json.dump(research_data, f, indent=2)
            
        print("\nFull continued research output saved to 'continued_research_output.json'")
        
        # Extract updated topics from connection path
        updated_topics = research_data['connection_path'].split(' → ')
        return research_data, updated_topics
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None, None

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
        return related_topics_data['related_topics']
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def main():
    """
    Example client script to demonstrate how to use the Multidisciplinary Research Explorer API
    """
    print("=== MULTIDISCIPLINARY RESEARCH EXPLORER API DEMO ===")
    print("This script demonstrates the complete research flow with multiple topics")
    
    # Step 1: Initial Research with two topics
    primary_topic = "Coffee"
    intent_topic = "Politics"
    print(f"\n1. STARTING RESEARCH: {primary_topic} and {intent_topic}")
    research_data, topics = get_research(primary_topic, intent_topic)
    
    if not topics:
        print("Initial research failed. Exiting.")
        return
    
    # Step 2: Get related topics for the initial research
    print("\n2. GETTING RELATED TOPICS FOR INITIAL RESEARCH")
    related_topics = get_related_topics(topics)
    
    if not related_topics:
        print("Failed to get related topics. Exiting.")
        return
    
    # Step 3: Continue research with a third topic (Gender)
    third_topic = "Gender"
    print(f"\n3. CONTINUING RESEARCH WITH: {third_topic}")
    # We can either use the continue_research function or directly call get_research with previous_topics
    # Option 1: Using continue_research (unchanged)
    continued_data, updated_topics = continue_research(topics, third_topic)
    
    # Option 2 (alternative): Using get_research with previous_topics
    # previous_topics = [third_topic]
    # continued_data, updated_topics = get_research(primary_topic, intent_topic, previous_topics)
    
    if not updated_topics:
        print("Failed to continue research. Exiting.")
        return
    
    # Step 4: Get related topics for the continued research
    print("\n4. GETTING RELATED TOPICS FOR CONTINUED RESEARCH")
    updated_related_topics = get_related_topics(updated_topics)
    
    if not updated_related_topics:
        print("Failed to get updated related topics. Exiting.")
        return
    
    # Step 5: Continue research with a fourth topic (Colonialism)
    fourth_topic = "Colonialism"
    print(f"\n5. CONTINUING RESEARCH WITH: {fourth_topic}")
    final_data, final_topics = continue_research(updated_topics, fourth_topic)
    
    if not final_topics:
        print("Failed to continue research with fourth topic. Exiting.")
        return
    
    print("\n" + "="*80)
    print("COMPLETE RESEARCH JOURNEY SUMMARY")
    print("="*80)
    print(f"Final Connection Path: {' → '.join(final_topics)}")
    print(f"Total Topics Connected: {len(final_topics)}")
    print("\nThe API successfully maintained connections between all topics throughout the research journey.")
    print("All research outputs and related topics have been saved to JSON files.")
    print("="*80)

if __name__ == "__main__":
    main()
