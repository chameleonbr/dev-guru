import asyncio
import json
from src.server import call_guru
from src.config import settings

async def main():
    # My current thinking about the project
    my_thinking = (
        "I have successfully implemented the Developer Guru MCP server. "
        "I refactored the providers into a unified factory for better reuse and implemented a multi-stage Docker build. "
        "One concern is whether mounting the FastMCP app at the root ('/') in FastAPI might shadow the "
        "explicitly defined root route in main.py, although FastMCP usually handles its SSE path distinctly."
    )
    
    context = (
        "Project: Dev Guru MCP Server\n"
        "State: Refactored, Dockerized, Tests Passing.\n"
        "Task: Use the tool to self-reflect on the implementation."
    )
    
    print("--- 🧘 Dev Guru Self-Consultation 🧘 ---")
    print(f"Thinking: {my_thinking}\n")
    
    try:
        # We use 'expert' to get the best reasoning
        result = await call_guru(
            level="expert",
            technologies="python, fastapi, mcp, agno, docker, openrouter",
            context=context,
            thinking=my_thinking
        )
        
        print("--- 💡 Guru Response 💡 ---")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error calling Guru: {e}")
        print("\nNote: Ensure API Keys (OPENAI_API_KEY or OPENROUTER_API_KEY) are set in .env")

if __name__ == "__main__":
    asyncio.run(main())
