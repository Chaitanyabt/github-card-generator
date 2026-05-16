import os
import vertexai
from vertexai import types
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = "us-central1"

if not PROJECT_ID:
    print("Error: GOOGLE_CLOUD_PROJECT environment variable not set.")
    exit(1)

vertexai.init(project=PROJECT_ID, location=LOCATION)

def deploy_agent_engine():
    """Creates a Vertex AI Agent Engine with custom memory topics for card preferences."""
    print(f"Creating Agent Engine in project {PROJECT_ID}...")

    # Define custom topic for card preferences
    custom_topic = types.MemoryBankCustomizationConfigMemoryTopic(
        custom_memory_topic=types.MemoryBankCustomizationConfigMemoryTopicCustomMemoryTopic(
            label="card_preferences",
            instructions="""Extract the user's preferences for their GitHub dev card.
Focus on:
- Preferred card theme (e.g., hacker, builder, designer).
- Favorite programming languages or skills to highlight.
- Visual preferences (e.g., preference for dark or light mode)."""
        )
    )

    # Configure Memory Bank
    memory_bank_config = types.ReasoningEngineContextSpecMemoryBankConfig(
        customization_config=types.MemoryBankCustomizationConfig(
            memory_topics=[custom_topic]
        ),
        generation_config=types.ReasoningEngineContextSpecMemoryBankConfigGenerationConfig(
            model="gemini-1.5-flash"
        )
    )

    # Create the Agent Engine
    client = vertexai.Client()
    try:
        agent_engine = client.agent_engines.create(
            display_name="github-card-memory-engine",
            memory_bank_config=memory_bank_config
        )
        # The agent_engine.name is usually in the format:
        # projects/{project}/locations/{location}/agentEngines/{id}
        agent_engine_id = agent_engine.name.split("/")[-1]
        
        print("\n✨ Agent Engine Created Successfully!")
        print(f"AGENT_ENGINE_ID={agent_engine_id}")
        print("\nAdd this ID to your .env file and restart your backend.")
        return agent_engine_id
    except Exception as e:
        print(f"Failed to create Agent Engine: {str(e)}")
        return None

if __name__ == "__main__":
    deploy_agent_engine()
