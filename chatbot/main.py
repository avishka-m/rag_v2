from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import getpass
import os
import uvicorn

# Import agents
from agents.base_agent import BaseWarehouseAgent
from agents.picker_agent import PickerAgent

# Import tools
from tools.inventory_tools import InventoryQueryTool
from tools.order_tools import CreatePackingTaskTool, UpdatePackingStatusTool

load_dotenv()

# Store agents globally
agents = {}

# Use FastAPI lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources before the app starts"""
    
    # Set up LangSmith and OpenAI API keys
    os.environ["LANGSMITH_TRACING"] = "true"

    if "LANGSMITH_API_KEY" not in os.environ:
        os.environ["LANGSMITH_API_KEY"] = getpass.getpass(
            prompt="Enter your LangSmith API key (optional): "
        )

    if "LANGSMITH_PROJECT" not in os.environ:
        os.environ["LANGSMITH_PROJECT"] = getpass.getpass(
            prompt='Enter your LangSmith Project Name (default = "default"): '
        )
        if not os.environ.get("LANGSMITH_PROJECT"):
            os.environ["LANGSMITH_PROJECT"] = "default"

    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = getpass.getpass(
            prompt="Enter your OpenAI API key (required if using OpenAI): "
        )

    # Initialize agents
    agents["picker"] = PickerAgent()
    agents["packer"] = BaseWarehouseAgent(
        role="packer",
        tools=[InventoryQueryTool(), CreatePackingTaskTool(), UpdatePackingStatusTool()]
    )

    print("Agents initialized.")

    yield  # App runs here

    # Optional cleanup logic goes here after app shutdown
    print("Shutting down...")

# Create FastAPI app
app = FastAPI(title="Warehouse Management Chatbot", lifespan=lifespan)

# Request and Response Models
class ChatMessage(BaseModel):
    message: str
    user_id: str
    role: str

class ChatResponse(BaseModel):
    response: str
    role: str
    user_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Process a chat message from a warehouse worker"""

    if message.role not in agents:
        return JSONResponse(status_code=400, content={"error": f"No agent defined for role '{message.role}'"})

    agent = agents[message.role]
    response = await agent.process_message(message.message, message.user_id)

    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
