# # agents/manager_agent.py
# from .base_agent import BaseWarehouseAgent
# from typing import List, Dict, Any, Optional
# from langchain.tools import BaseTool
# from tools.inventory_tools import InventoryQueryTool, UpdateInventoryTool, ApproveInventoryTool
# from tools.warehouse_tools import GetWarehouseStatsTool, GetStaffPerformanceTool
# from tools.order_tools import GetOrderDetailsTool, GetOrderAnalyticsTool
# from tools.path_tools import OptimizeWarehouseLayoutTool

# class ManagerAgent(BaseWarehouseAgent):
#     """Agent specifically for managers in the warehouse system."""
    
#     def __init__(self):
#         """Initialize the manager agent with manager-specific tools."""
#         tools = [
#             InventoryQueryTool(),           # To check inventory details
#             UpdateInventoryTool(),          # To update inventory levels
#             ApproveInventoryTool(),         # To approve inventory changes
#             GetWarehouseStatsTool(),        # To get warehouse performance stats
#             GetStaffPerformanceTool(),      # To monitor staff performance
#             GetOrderDetailsTool(),          # To view order details
#             GetOrderAnalyticsTool(),        # To analyze order trends
#             OptimizeWarehouseLayoutTool()   # To optimize warehouse layout
#         ]
        
#         # Include manager-specific system instructions
#         system_message = """
#         You are a helpful assistant for managers in the warehouse management system.
#         As a manager agent, you have full control and can:
#         1. View and manage all inventory
#         2. Monitor staff performance across all roles
#         3. View and analyze order statistics
#         4. Approve inventory changes and purchases
#         5. Generate performance reports
#         6. Optimize warehouse layout and operations
        
#         Always provide data-driven insights when possible and focus on operational efficiency.
#         You have access to more sensitive data and broader system capabilities than other roles.
#         """
        
#         super().__init__(role="manager", tools=tools, system_message=system_message)
    
#     async def process_message(self, message: str, user_id: str) -> Dict[str, Any]:
#         """Process messages specifically for managers."""
#         # Could add manager-specific pre-processing here
        
#         # Look up common manager-related terms and provide smart responses
#         if "performance" in message.lower() or "stats" in message.lower() or "metrics" in message.lower():
#             return {
#                 "response": "I can generate performance reports for you. Would you like to see metrics for a specific department (picking, packing, shipping), a specific employee, or overall warehouse performance?",
#                 "role": "manager",
#                 "user_id": user_id
#             }
#         elif "approval" in message.lower() or "approve inventory" in message.lower():
#             return {
#                 "response": "You have pending inventory approval requests. I can show you items pending approval, including quantity changes and new stock requests. Would you like to see them now?",
#                 "role": "manager",
#                 "user_id": user_id
#             }
        
#         # Process using the standard agent workflow
#         return await super().process_message(message, user_id)