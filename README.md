# Multidisciplinary Research Explorer

A Streamlit application that generates comprehensive multidisciplinary research outputs connecting diverse academic topics. The app uses the Grok API to create rich, interconnected analyses across various disciplines, maintaining connections between topics as you progressively add more to your research journey.

## Features

- **Unlimited Topic Connections**: Start with two topics and add as many additional topics as you want
- **Progressive Research Journey**: Each new topic connects to all previous topics
- **Rich Multidisciplinary Analysis**: Explore connections through sociology, economics, history, anthropology, and more
- **Detailed Subtopics**: Get specific subtopics under each disciplinary lens
- **Research Questions**: Generate relevant research questions spanning all connected topics
- **Related Topics**: Discover new topics to expand your research
- **Mind Map Structure**: Visualize central themes and key connections between topics

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your Grok API key:
   ```
   XAI_API_KEY=your_api_key_here
   ```
4. Run the app:
   ```
   streamlit run simplified_app.py
   ```

## Usage

1. **Start Your Research**: Enter two initial topics (e.g., "Coffee" and "Politics")
2. **Generate Research**: Click the "Generate Research" button to create a multidisciplinary analysis
3. **Add More Topics**: After viewing the research, add a third topic to connect with the previous ones
4. **Continue Your Journey**: Keep adding more topics to build a comprehensive research map
5. **Start Fresh**: Use the "Start New Research" button when you want to begin a new exploration

## Example Research Path

Try this research journey to see how the app maintains connections between topics:

1. Start with "Coffee" and "Politics"
2. Add "Gender" as a third topic
3. Continue by adding "Colonialism"
4. See how each new topic connects to all previous ones

## Environment Variables

This application requires a Grok API key to function. Create a `.env` file with the following:

```
XAI_API_KEY=your_api_key_here
```

You can obtain a Grok API key by signing up at https://api.x.ai/

## Notes

The application is designed to follow a structured approach to connecting topics, ensuring that all connections are maintained throughout the user's exploration. The research outputs are comprehensive and academic in tone, highlighting meaningful connections between the topics across multiple disciplines.
