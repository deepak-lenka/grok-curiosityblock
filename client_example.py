import requests
import json

def main():
    """
    Example client script to demonstrate how to use the Multidisciplinary Research Explorer API
    """
    # API endpoint
    api_url = "http://localhost:8000/research/"
    
    # Example request data
    request_data = {
        "primary_topic": "Coffee",
        "intent_topic": "Politics",
        "third_topic": "Gender"  # Optional, can be omitted
    }
    
    # Make the API request
    print(f"Sending request to {api_url}...")
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
        
        # Print related topics
        print("\nRELATED TOPICS:")
        for topic in research_data['related_topics']:
            print(f"  - {topic['topic']}")
        
        print("\nFull JSON response saved to 'research_output.json'")
        
        # Save the full response to a file
        with open('research_output.json', 'w') as f:
            json.dump(research_data, f, indent=2)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()
