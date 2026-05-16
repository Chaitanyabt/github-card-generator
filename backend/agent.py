import os
import asyncio
import sys
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams
from mcp.client.stdio import StdioServerParameters
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.sessions.vertex_ai_session_service import VertexAiSessionService
from google.adk.memory.vertex_ai_memory_bank_service import VertexAiMemoryBankService
from google.adk.apps import App
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = "us-central1"
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID")

print(f"DEBUG: Starting Agent. Project: {PROJECT_ID}, Engine: {AGENT_ENGINE_ID}")

# Define the MCP Server connection
mcp_server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")

# Use 'python3' for Cloud Run (Linux)
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python3",
            args=[mcp_server_path],
            env=os.environ.copy()
        ),
        timeout=60.0
    )
)

# Define the ADK Agent
github_card_agent = Agent(
    name="github_card_agent",
    model="gemini-2.5-flash-lite",
    instruction="""You are a GitHub profile analyst and dev card generator. 
    When a user gives you a GitHub username, you ALWAYS follow this exact sequence: 
    1. Call scrape_github.
    2. Call analyze_profile with the results of scrape_github.
    3. Call generate_card_html with the username, results of scrape_github, and results of analyze_profile.
    4. Call save_card with the username and the generated HTML.
    
    CRITICAL: Your final response MUST be ONLY the raw HTML string returned by generate_card_html. 
    Do not add any explanations, markdown formatting (like ```html), or conversational text. 
    Check for any previous user preferences (theme, color, languages) stored in memory and respect them.
    Never skip steps.""",
    tools=[mcp_toolset, PreloadMemoryTool()]
)

# Initialize Services
if AGENT_ENGINE_ID:
    print(f"DEBUG: Using Vertex AI Persistent Memory with Engine: {AGENT_ENGINE_ID}")
    session_service = VertexAiSessionService(
        project=PROJECT_ID,
        location=LOCATION,
        agent_engine_id=AGENT_ENGINE_ID
    )
    memory_service = VertexAiMemoryBankService(
        project=PROJECT_ID,
        location=LOCATION,
        agent_engine_id=AGENT_ENGINE_ID
    )
else:
    print("DEBUG: Using In-Memory Session Service (Non-persistent)")
    session_service = InMemorySessionService()
    memory_service = None

async def run_agent(username: str):
    """Orchestrates the card generation process using the ADK Agent."""
    app_name = "github_card_app"
    app = App(name=app_name, root_agent=github_card_agent)
    
    runner = Runner(
        app=app, 
        session_service=session_service,
        memory_service=memory_service
    )
    
    user_id = "default_user"
    session_id = f"session_{username}"
    
    print(f"DEBUG: Processing request for {username}. Session: {session_id}")
    
    # Force create session to avoid "not found" error
    try:
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        print(f"DEBUG: Created new session {session_id}")
    except Exception as e:
        print(f"DEBUG: Session {session_id} might already exist or failed: {str(e)}")
    
    final_text = ""
    new_message = types.Content(
        parts=[types.Part(text=f"Generate a GitHub dev card for user: {username}")],
        role="user"
    )
    
    try:
        async for event in runner.run_async(
            user_id=user_id, 
            session_id=session_id, 
            new_message=new_message
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        final_text += part.text
        
        print(f"DEBUG: Agent finished for {username}")
    except Exception as e:
        print(f"DEBUG: Error during run_async: {str(e)}")
        raise e
    
    return {"message": final_text, "username": username}

if __name__ == "__main__":
    async def main():
        result = await run_agent("torvalds")
        print(result["message"])

    asyncio.run(main())
