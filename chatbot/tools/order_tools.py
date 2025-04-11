from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    SUB_ORDER_CREATED = "Sub-Order Created"

class PickingTaskInput(BaseModel):
    worker_id: str = Field(..., description="ID of the worker performing the picking")
    order_id: str = Field(..., description="ID of the order to pick")
    item_id: str = Field(..., description="ID of the item to pick")

class UpdatePickingStatusInput(BaseModel):
    task_id: str = Field(..., description="ID of the picking task to update")
    status: str = Field(..., description="New status (Pending, In Progress, Completed, Sub-Order Created)")

class PackingTaskInput(BaseModel):
    worker_id: str = Field(..., description="ID of the worker performing the packing")
    order_id: str = Field(..., description="ID of the order to pack")

class UpdatePackingStatusInput(BaseModel):
    task_id: str = Field(..., description="ID of the packing task to update")
    status: str = Field(..., description="New status (Pending, In Progress, Completed)")

class ShippingTaskInput(BaseModel):
    worker_id: str = Field(..., description="ID of the driver")
    order_id: str = Field(..., description="ID of the order to ship")
    vehicle_id: str = Field(..., description="ID of the vehicle to use")

class UpdateShippingStatusInput(BaseModel):
    task_id: str = Field(..., description="ID of the shipping task to update")
    status: str = Field(..., description="New status (Pending, In Progress, Shipped)")

class CreatePickingTaskTool(BaseTool):
    name:str = "create_picking_task"
    description:str = "Create a new picking task for an order"
    args_schema: Type[BaseModel] = PickingTaskInput
    
    async def _run(self, worker_id, order_id, item_id):
        # In a real implementation, you would connect to your MongoDB here
        return {
            "success": True,
            "task_id": "pick_12345",
            "message": f"Created picking task for order {order_id}, item {item_id}, assigned to worker {worker_id}"
        }
            
    def _arun(self, worker_id, order_id, item_id):
        # Async implementation would go here
        return self._run(worker_id, order_id, item_id)

class UpdatePickingStatusTool(BaseTool):
    name:str = "update_picking_status"
    description:str = "Update the status of a picking task"
    args_schema: Type[BaseModel] = UpdatePickingStatusInput
    
    async def _run(self, task_id, status):
        # In a real implementation, you would connect to your MongoDB here
        return {
            "success": True,
            "message": f"Updated picking task {task_id} status to {status}"
        }
            
    def _arun(self, task_id, status):
        # Async implementation would go here
        return self._run(task_id, status)

class CreatePackingTaskTool(BaseTool):
    name:str = "create_packing_task"
    description:str = "Create a new packing task for an order"
    args_schema: Type[BaseModel] = PackingTaskInput
    
    async def _run(self, worker_id, order_id):
        # In a real implementation, you would connect to your MongoDB here
        return {
            "success": True,
            "task_id": "pack_12345",
            "message": f"Created packing task for order {order_id}, assigned to worker {worker_id}"
        }
            
    def _arun(self, worker_id, order_id):
        # Async implementation would go here
        return self._run(worker_id, order_id)

class UpdatePackingStatusTool(BaseTool):
    name:str = "update_packing_status"
    description:str = "Update the status of a packing task"
    args_schema: Type[BaseModel] = UpdatePackingStatusInput
    
    def _run(self, task_id, status):
        # In a real implementation, you would connect to your MongoDB here
        return {
            "success": True,
            "message": f"Updated packing task {task_id} status to {status}"
        }
            
    def _arun(self, task_id, status):
        # Async implementation would go here
        return self._run(task_id, status)

class CreateShippingTaskTool(BaseTool):
    name:str = "create_shipping_task"
    description:str = "Create a new shipping task for an order"
    args_schema: Type[BaseModel] = ShippingTaskInput
    
    def _run(self, worker_id, order_id, vehicle_id):
        # In a real implementation, you would connect to your MongoDB here
        return {
            "success": True,
            "task_id": "ship_12345",
            "message": f"Created shipping task for order {order_id}, assigned to driver {worker_id} with vehicle {vehicle_id}"
        }
            
    def _arun(self, worker_id, order_id, vehicle_id):
        # Async implementation would go here
        return self._run(worker_id, order_id, vehicle_id)

class UpdateShippingStatusTool(BaseTool):
    name:str = "update_shipping_status"
    description:str = "Update the status of a shipping task"
    args_schema: Type[BaseModel] = UpdateShippingStatusInput
    
    def _run(self, task_id, status):
        # In a real implementation, you would connect to your MongoDB here
        return {
            "success": True,
            "message": f"Updated shipping task {task_id} status to {status}"
        }
            
    def _arun(self, task_id, status):
        # Async implementation would go here
        return self._run(task_id, status)