# from langchain.tools import BaseTool
# from typing import Optional, Type
# from pydantic import BaseModel, Field
# import database

# class WarehouseQueryInput(BaseModel):
#     warehouse_id: Optional[str] = Field(None, description="ID of the warehouse to query")
#     location_id: Optional[str] = Field(None, description="ID of the specific location to query")
#     section: Optional[str] = Field(None, description="Section code to query (e.g., 'A', 'B', 'C')")

# class StorageAvailabilityInput(BaseModel):
#     item_size: str = Field(..., description="Size of the item (small, medium, large)")
#     storage_type: str = Field(..., description="Type of storage needed (standard, refrigerated, hazardous)")
#     quantity: int = Field(..., description="Number of items to store")

# class WorkerQueryInput(BaseModel):
#     worker_id: Optional[str] = Field(None, description="ID of the worker to query")
#     role: Optional[str] = Field(None, description="Role of workers to query")
#     shift: Optional[str] = Field(None, description="Shift time to query (morning, afternoon, night)")

# class WarehouseQueryTool(BaseTool):
#     name = "warehouse_query"
#     description = "Query information about warehouses, storage locations, and capacity"
#     args_schema: Type[BaseModel] = WarehouseQueryInput
    
#     async def _run(self, warehouse_id: Optional[str] = None, location_id: Optional[str] = None, section: Optional[str] = None):
#         warehouse_collection = await database.get_warehouse_collection()
#         location_collection = await database.get_location_collection()
        
#         # Build query based on provided parameters
#         if location_id:
#             # Query specific location
#             location = await location_collection.find_one({"_id": location_id})
#             if location:
#                 return {
#                     "location_id": location_id,
#                     "section": location.get("section"),
#                     "row": location.get("row"),
#                     "shelf": location.get("shelf"),
#                     "bin": location.get("bin"),
#                     "current_items": location.get("current_items", []),
#                     "capacity": location.get("capacity"),
#                     "available_space": location.get("available_space")
#                 }
#             return "Location not found"
            
#         elif warehouse_id:
#             # Query specific warehouse
#             warehouse = await warehouse_collection.find_one({"_id": warehouse_id})
#             if warehouse:
#                 # Get summary of locations in this warehouse
#                 location_cursor = location_collection.find({"warehouse_id": warehouse_id})
#                 location_count = await location_collection.count_documents({"warehouse_id": warehouse_id})
#                 available_locations = await location_collection.count_documents(
#                     {"warehouse_id": warehouse_id, "available_space": {"$gt": 0}}
#                 )
                
#                 return {
#                     "warehouse_id": warehouse_id,
#                     "name": warehouse.get("name"),
#                     "address": warehouse.get("address"),
#                     "total_capacity": warehouse.get("capacity"),
#                     "total_locations": location_count,
#                     "available_locations": available_locations,
#                     "utilization_percentage": round(
#                         (1 - (available_locations / location_count if location_count else 0)) * 100, 2
#                     )
#                 }
#             return "Warehouse not found"
            
#         elif section:
#             # Query locations by section
#             location_cursor = location_collection.find({"section": section})
#             locations = await location_cursor.to_list(length=10)
#             if locations:
#                 return {
#                     "section": section,
#                     "location_count": len(locations),
#                     "locations": [
#                         {
#                             "location_id": loc.get("_id"),
#                             "row": loc.get("row"),
#                             "shelf": loc.get("shelf"),
#                             "available": loc.get("available_space", 0) > 0
#                         }
#                         for loc in locations
#                     ]
#                 }
#             return f"No locations found in section {section}"
            
#         else:
#             # Return summary of all warehouses
#             warehouses_cursor = warehouse_collection.find()
#             warehouses = await warehouses_cursor.to_list(length=5)
#             if warehouses:
#                 return [
#                     {
#                         "warehouse_id": wh.get("_id"),
#                         "name": wh.get("name"),
#                         "total_capacity": wh.get("capacity")
#                     }
#                     for wh in warehouses
#                 ]
#             return "No warehouses found"
    
#     async def _arun(self, warehouse_id: Optional[str] = None, location_id: Optional[str] = None, section: Optional[str] = None):
#         return await self._run(warehouse_id, location_id, section)

# class StorageAvailabilityTool(BaseTool):
#     name = "find_available_storage"
#     description = "Find available storage locations for items based on size and storage type"
#     args_schema: Type[BaseModel] = StorageAvailabilityInput
    
#     async def _run(self, item_size: str, storage_type: str, quantity: int):
#         location_collection = await database.get_location_collection()
        
#         # Define space requirements based on item size
#         space_required = {
#             "small": 1,
#             "medium": 3,
#             "large": 5
#         }.get(item_size.lower(), 1)
        
#         total_space_needed = space_required * quantity
        
#         # Find suitable locations
#         query = {
#             "available_space": {"$gte": space_required},
#             "storage_type": storage_type
#         }
        
#         # Sort by available space (ascending) to optimize space usage
#         locations_cursor = location_collection.find(query).sort("available_space", 1)
#         locations = await locations_cursor.to_list(length=20)
        
#         if not locations:
#             return f"No suitable storage locations found for {quantity} {item_size} items with {storage_type} storage type."
        
#         # Calculate how many locations needed
#         selected_locations = []
#         remaining_quantity = quantity
        
#         for loc in locations:
#             # How many items can fit in this location
#             items_can_fit = min(remaining_quantity, loc["available_space"] // space_required)
            
#             if items_can_fit > 0:
#                 selected_locations.append({
#                     "location_id": loc["_id"],
#                     "section": loc["section"],
#                     "row": loc["row"],
#                     "shelf": loc["shelf"],
#                     "bin": loc["bin"],
#                     "items_can_fit": items_can_fit
#                 })
                
#                 remaining_quantity -= items_can_fit
                
#                 if remaining_quantity <= 0:
#                     break
        
#         if remaining_quantity > 0:
#             return {
#                 "complete_solution": False,
#                 "locations_found": selected_locations,
#                 "items_placed": quantity - remaining_quantity,
#                 "items_remaining": remaining_quantity,
#                 "message": f"Partial solution found. {remaining_quantity} items cannot be stored with current availability."
#             }
        
#         return {
#             "complete_solution": True,
#             "locations_found": selected_locations,
#             "total_items": quantity,
#             "message": f"Found storage for all {quantity} {item_size} items requiring {storage_type} storage."
#         }
    
#     async def _arun(self, item_size: str, storage_type: str, quantity: int):
#         return await self._run(item_size, storage_type, quantity)

# class WorkerQueryTool(BaseTool):
#     name = "worker_query"
#     description = "Query information about warehouse workers by ID, role, or shift"
#     args_schema: Type[BaseModel] = WorkerQueryInput
    
#     async def _run(self, worker_id: Optional[str] = None, role: Optional[str] = None, shift: Optional[str] = None):
#         worker_collection = await database.get_worker_collection()
        
#         # Build query based on provided parameters
#         query = {}
#         if worker_id:
#             query["_id"] = worker_id
#         if role:
#             query["role"] = role
#         if shift:
#             query["shift"] = shift
            
#         # Execute query
#         if not query:
#             return "Please provide at least one search parameter (worker_id, role, or shift)"
            
#         if worker_id:  # Looking for a specific worker
#             worker = await worker_collection.find_one(query)
#             if worker:
#                 return {
#                     "worker_id": worker["_id"],
#                     "name": worker["name"],
#                     "role": worker["role"],
#                     "shift": worker.get("shift"),
#                     "current_tasks": worker.get("current_tasks", []),
#                     "performance_metrics": worker.get("performance_metrics", {})
#                 }
#             return "Worker not found"
#         else:  # Looking for multiple workers
#             workers_cursor = worker_collection.find(query)
#             workers = await workers_cursor.to_list(length=10)
#             if workers:
#                 return [
#                     {
#                         "worker_id": w["_id"],
#                         "name": w["name"],
#                         "role": w["role"],
#                         "shift": w.get("shift")
#                     }
#                     for w in workers
#                 ]
#             return "No workers found matching your criteria"
    
#     async def _arun(self, worker_id: Optional[str] = None, role: Optional[str] = None, shift: Optional[str] = None):
#         return await self._run(worker_id, role, shift)