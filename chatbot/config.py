import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Vector DB configuration
CHROMA_PERSIST_DIRECTORY = os.path.join(os.path.dirname(__file__), "data")

# Role definitions and permissions
ROLES = {
    "receiving_clerk": {
        "description": "Adds items from pre-approved list and handles returns",
        "allowed_tools": ["inventory_add", "process_return", "inventory_query"]
    },
    "picker": {
        "description": "Places received items in the right location and fulfills orders",
        "allowed_tools": ["inventory_query", "create_picking_task", "update_picking_status", "path_optimize"]
    },
    "packer": {
        "description": "Verifies order completeness and creates sub-orders if necessary",
        "allowed_tools": ["inventory_query", "create_packing_task", "update_packing_status", "create_sub_order"]
    },
    "driver": {
        "description": "Selects vehicles and updates order status to Shipped",
        "allowed_tools": ["create_shipping_task", "update_shipping_status", "vehicle_select"]
    },
    "manager": {
        "description": "Full control over inventory, workers, and system management",
        "allowed_tools": ["inventory_query", "inventory_approve", "inventory_update", "worker_manage", 
                         "system_manage", "all_tasks_query"]
    }
}

# Agent configuration
AGENT_TEMPERATURE = 0.0  # Low temperature for more predictable responses
AGENT_MODEL = "gpt-4o-mini"  # Use appropriate model based on your needs