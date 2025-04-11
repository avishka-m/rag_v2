from fastapi import FastAPI#, HTTPException, Depends
from pydantic import BaseModel
import getpass
from dotenv import load_dotenv
# from typing import Dict, Optional, List
import uvicorn
import os

# Import agents
from agents.base_agent import BaseWarehouseAgent
from agents.picker_agent import PickerAgent
# Import other role-specific agents as needed


load_dotenv()


# Create FastAPI app
app = FastAPI(title="Warehouse Management Chatbot")

# Define models
class ChatMessage(BaseModel):
    message: str
    user_id: str
    role: str  # Role of the user (picker, packer, driver, etc.)

class ChatResponse(BaseModel):
    response: str
    role: str
    user_id: str

# Store agents by role
agents = {}

@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup"""
    # Create agents for each role
    # ---------------langsmith------------------

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





    agents["picker"] = PickerAgent()
    # Add other agents here as they are implemented
    
    # For demonstration, we'll use the base agent for other roles
    from tools.inventory_tools import InventoryQueryTool
    from tools.order_tools import CreatePackingTaskTool, UpdatePackingStatusTool
    
    agents["packer"] = BaseWarehouseAgent(
        role="packer", 
        tools=[InventoryQueryTool(), CreatePackingTaskTool(), UpdatePackingStatusTool()]
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Process a chat message from a warehouse worker"""
    # Get the appropriate agent for the user's role
    # if message.role not in agents:
    #     # If we don't have a specific agent for this role yet, use a basic one
    #     from tools.inventory_tools import InventoryQueryTool
    #     agents[message.role] = BaseWarehouseAgent(
    #         role=message.role,
    #         tools=[InventoryQueryTool()]  # Limited tools for unknown roles
    #     )
    
    agent = agents[message.role]
    
    # Process the message
    response = await agent.process_message(message.message, message.user_id)
    
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)