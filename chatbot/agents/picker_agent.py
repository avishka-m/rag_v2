from .base_agent import BaseWarehouseAgent
from tools.inventory_tools import InventoryQueryTool
from tools.order_tools import CreatePickingTaskTool, UpdatePickingStatusTool
from typing import Dict, Any

class PickerAgent(BaseWarehouseAgent):
    """Agent for Picker role in the warehouse"""
    
    def __init__(self):
        # Initialize with picker-specific tools
        tools = [
            InventoryQueryTool(),
            CreatePickingTaskTool(),
            UpdatePickingStatusTool()
        ]
        
        # Initialize the base agent with 'picker' role
        super().__init__(role="picker", tools=tools)
    
    async def optimize_picking_path(self, order_id: str) -> Dict[str, Any]:
        """Special method to optimize picking path for an order"""
        # In a full implementation, this would connect to path optimization microservice
        return {
            "order_id": order_id,
            "optimized_path": [
                {"location": "A1-B2-C3", "item_id": "12345", "quantity": 2},
                {"location": "D4-E5-F6", "item_id": "67890", "quantity": 1}
            ],
            "estimated_time": "5 minutes"
        }
