# # agents/packer_agent.py
# from .base_agent import BaseWarehouseAgent
# from typing import List, Dict, Any, Optional
# from langchain.tools import BaseTool
# from tools.inventory_tools import InventoryQueryTool
# from tools.order_tools import CreatePackingTaskTool, UpdatePackingStatusTool
# from tools.warehouse_tools import GetWarehouseLocationTool

# class PackerAgent(BaseWarehouseAgent):
#     """Agent specifically for packers in the warehouse system."""
    
#     def __init__(self):
#         """Initialize the packer agent with packer-specific tools."""
#         tools = [
#             InventoryQueryTool(),           # To check inventory details
#             CreatePackingTaskTool(),        # To create packing tasks
#             UpdatePackingStatusTool(),      # To update packing status
#             GetWarehouseLocationTool()      # To find items in the warehouse
#         ]
        
#         # Include packer-specific system instructions
#         system_message = """
#         You are a helpful assistant for packers in the warehouse management system.
#         As a packer agent, you can:
#         1. Verify order completeness before packing
#         2. Create sub-orders if necessary when items are missing
#         3. Update packing status
#         4. Find the optimal box sizes for orders
#         5. Provide packing instructions for fragile items
        
#         Always respond to requests in the context of a packer's responsibilities.
#         If a request is outside your scope, kindly redirect the user to the appropriate role.
#         """
        
#         super().__init__(role="packer", tools=tools, system_message=system_message)
    
#     async def process_message(self, message: str, user_id: str) -> Dict[str, Any]:
#         """Process messages specifically for packers."""
#         # Could add packer-specific pre-processing here
        
#         # Look up common packer-related terms and provide smart responses
#         if "verification" in message.lower() or "verify order" in message.lower():
#             return {
#                 "response": "To verify an order, scan all items in the order and confirm they match the order details. If any items are missing, you can create a sub-order through the system.",
#                 "role": "packer",
#                 "user_id": user_id
#             }
#         elif "sub-order" in message.lower() or "missing item" in message.lower():
#             return {
#                 "response": "To create a sub-order for missing items: 1) Mark the current order as partially fulfilled, 2) Create a new sub-order for the missing items, 3) Update the inventory system.",
#                 "role": "packer",
#                 "user_id": user_id
#             }
        
#         # Process using the standard agent workflow
#         return await super().process_message(message, user_id)