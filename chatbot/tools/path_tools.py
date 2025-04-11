# from langchain.tools import BaseTool
# from typing import List, Optional, Type, Dict, Any
# from pydantic import BaseModel, Field
# import database
# import heapq
# import math
# from collections import defaultdict

# class OptimizePickingPathInput(BaseModel):
#     order_id: str = Field(..., description="ID of the order to optimize picking path for")
#     worker_location: Optional[str] = Field(None, description="Current location ID of the worker (starting point)")
#     algorithm: Optional[str] = Field("nearest_neighbor", description="Path optimization algorithm to use: nearest_neighbor, cluster, or optimal")

# class GetPathInput(BaseModel):
#     start_location: str = Field(..., description="Starting location ID")
#     end_location: str = Field(..., description="Destination location ID")

# class LocationDistanceInput(BaseModel):
#     location_id1: str = Field(..., description="First location ID")
#     location_id2: str = Field(..., description="Second location ID")

# class PathOptimizationTool(BaseTool):
#     name = "optimize_picking_path"
#     description = "Optimize the path for picking items in an order"
#     args_schema: Type[BaseModel] = OptimizePickingPathInput
    
#     async def _run(self, order_id: str, worker_location: Optional[str] = None, algorithm: Optional[str] = "nearest_neighbor"):
#         # Get necessary collections
#         order_collection = await database.get_orders_collection()
#         order_detail_collection = await database.get_order_detail_collection()
#         inventory_collection = await database.get_inventory_collection()
#         location_collection = await database.get_location_collection()
        
#         # Get order details
#         order = await order_collection.find_one({"_id": order_id})
#         if not order:
#             return {"success": False, "message": f"Order {order_id} not found"}
            
#         # Get order items
#         order_details_cursor = order_detail_collection.find({"order_id": order_id})
#         order_items = await order_details_cursor.to_list(length=100)
        
#         if not order_items:
#             return {"success": False, "message": f"No items found for order {order_id}"}
        
#         # Get location for each item
#         locations_to_visit = []
        
#         for item in order_items:
#             inventory_item = await inventory_collection.find_one({"_id": item["item_id"]})
#             if not inventory_item:
#                 continue
                
#             location_id = inventory_item.get("location_id")
#             if not location_id:
#                 continue
                
#             location = await location_collection.find_one({"_id": location_id})
#             if not location:
#                 continue
                
#             locations_to_visit.append({
#                 "location_id": location_id,
#                 "item_id": item["item_id"],
#                 "quantity": item["quantity"],
#                 "section": location.get("section"),
#                 "row": location.get("row"),
#                 "shelf": location.get("shelf"),
#                 "bin": location.get("bin"),
#                 "coordinates": location.get("coordinates", {"x": 0, "y": 0, "z": 0})  # Fallback if no coordinates
#             })
        
#         if not locations_to_visit:
#             return {"success": False, "message": f"No valid locations found for items in order {order_id}"}
        
#         # If worker location is provided, get its coordinates
#         start_coordinates = {"x": 0, "y": 0, "z": 0}  # Default to origin
#         if worker_location:
#             worker_loc = await location_collection.find_one({"_id": worker_location})
#             if worker_loc and "coordinates" in worker_loc:
#                 start_coordinates = worker_loc["coordinates"]
        
#         # Optimize path based on selected algorithm
#         if algorithm == "nearest_neighbor":
#             optimized_path = self._nearest_neighbor_algorithm(locations_to_visit, start_coordinates)
#         elif algorithm == "cluster":
#             optimized_path = self._cluster_algorithm(locations_to_visit, start_coordinates)
#         elif algorithm == "optimal":
#             optimized_path = self._optimal_algorithm(locations_to_visit, start_coordinates)
#         else:
#             optimized_path = self._nearest_neighbor_algorithm(locations_to_visit, start_coordinates)
        
#         # Calculate total distance
#         total_distance = 0
#         prev_coords = start_coordinates
        
#         for location in optimized_path:
#             coords = location["coordinates"]
#             distance = self._calculate_distance(prev_coords, coords)
#             total_distance += distance
#             prev_coords = coords
        
#         # Return optimized path
#         return {
#             "success": True,
#             "order_id": order_id,
#             "starting_point": worker_location or "Default entrance",
#             "algorithm_used": algorithm,
#             "optimized_path": optimized_path,
#             "total_distance": round(total_distance, 2),
#             "estimated_time_minutes": round(total_distance / 50 * 60, 2),  # Assuming 50 distance units per hour
#             "item_count": len(optimized_path)
#         }
    
#     def _calculate_distance(self, coords1, coords2):
#         """Calculate Euclidean distance between two points"""
#         return math.sqrt(
#             (coords1["x"] - coords2["x"]) ** 2 +
#             (coords1["y"] - coords2["y"]) ** 2 +
#             (coords1["z"] - coords2["z"]) ** 2
#         )
    
#     def _nearest_neighbor_algorithm(self, locations, start_coords):
#         """Implement nearest neighbor algorithm for path optimization"""
#         unvisited = locations.copy()
#         path = []
#         current_coords = start_coords
        
#         while unvisited:
#             # Find nearest unvisited location
#             nearest_idx = 0
#             nearest_distance = float('inf')
            
#             for i, location in enumerate(unvisited):
#                 distance = self._calculate_distance(current_coords, location["coordinates"])
#                 if distance < nearest_distance:
#                     nearest_distance = distance
#                     nearest_idx = i
            
#             # Add to path and update current position
#             nearest_location = unvisited.pop(nearest_idx)
#             path.append(nearest_location)
#             current_coords = nearest_location["coordinates"]
        
#         return path
    
#     def _cluster_algorithm(self, locations, start_coords):
#         """Implement section-based clustering algorithm for path optimization"""
#         # Group locations by section
#         sections = defaultdict(list)
#         for location in locations:
#             sections[location["section"]].append(location)
        
#         # Sort sections by distance from start
#         section_distances = {}
#         for section, locs in sections.items():
#             # Take average position of items in section
#             avg_x = sum(loc["coordinates"]["x"] for loc in locs) / len(locs)
#             avg_y = sum(loc["coordinates"]["y"] for loc in locs) / len(locs)
#             avg_z = sum(loc["coordinates"]["z"] for loc in locs) / len(locs)
#             avg_coords = {"x": avg_x, "y": avg_y, "z": avg_z}
            
#             # Calculate distance from start to section
#             distance = self._calculate_distance(start_coords, avg_coords)
#             section_distances[section] = distance
        
#         # Sort sections by distance
#         sorted_sections = sorted(sections.keys(), key=lambda s: section_distances[s])
        
#         # Build path by visiting each section and using nearest neighbor within section
#         path = []
#         current_coords = start_coords
        
#         for section in sorted_sections:
#             section_locs = sections[section]
#             # Use nearest neighbor within each section
#             while section_locs:
#                 # Find nearest location in current section
#                 nearest_idx = 0
#                 nearest_distance = float('inf')
                
#                 for i, location in enumerate(section_locs):
#                     distance = self._calculate_distance(current_coords, location["coordinates"])
#                     if distance < nearest_distance:
#                         nearest_distance = distance
#                         nearest_idx = i
                
#                 # Add to path and update current position
#                 nearest_location = section_locs.pop(nearest_idx)
#                 path.append(nearest_location)
#                 current_coords = nearest_location["coordinates"]
        
#         return path
    
#     def _optimal_algorithm(self, locations, start_coords):
#         """
#         Implement a more optimal algorithm (approximate TSP solution)
#         Uses 2-opt local search improvement on nearest neighbor solution
#         """
#         # Start with nearest neighbor solution
#         path = self._nearest_neighbor_algorithm(locations, start_coords)
        
#         # Apply 2-opt improvement
#         improved = True
#         while improved:
#             improved = False
#             for i in range(len(path) - 2):
#                 for j in range(i + 2, len(path)):
#                     # Calculate current distance
#                     if i == 0:
#                         d1 = self._calculate_distance(start_coords, path[i]["coordinates"])
#                     else:
#                         d1 = self._calculate_distance(path[i-1]["coordinates"], path[i]["coordinates"])
                    
#                     d2 = self._calculate_distance(path[i]["coordinates"], path[i+1]["coordinates"])
#                     d3 = self._calculate_distance(path[j-1]["coordinates"], path[j]["coordinates"])
                    
#                     if j == len(path) - 1:
#                         d4 = 0  # No next location after last one
#                     else:
#                         d4 = self._calculate_distance(path[j]["coordinates"], path[j+1]["coordinates"])
                    
#                     current_distance = d1 + d2 + d3 + d4
                    
#                     # Calculate new distance if we swap
#                     if i == 0:
#                         new_d1 = self._calculate_distance(start_coords, path[j-1]["coordinates"])
#                     else:
#                         new_d1 = self._calculate_distance(path[i-1]["coordinates"], path[j-1]["coordinates"])
                    
#                     new_d2 = self._calculate_distance(path[j-1]["coordinates"], path[i]["coordinates"])
#                     new_d3 = self._calculate_distance(path[i+1]["coordinates"], path[j]["coordinates"])
                    
#                     if j == len(path) -