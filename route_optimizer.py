from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math

def calculate_distance(coord1, coord2):
    """Calculate simple scaled Euclidean distance to use as cost."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return int(math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 100000)

# Static Municipality Hub Coordinates (Tirupati Municipal Corporation)
MUNICIPALITY_HUB = [13.6288, 79.4192]

def get_optimized_route(locations):
    """
    locations: list of [lat, lng] (user reported waste locations)
    Returns an optimized route order of [lat, lng] starting and ending at the municipality hub.
    """
    # Always include the municipal hub at index 0
    full_locations = [MUNICIPALITY_HUB] + locations
    
    if len(full_locations) <= 2:
        # If no reports, or just one report, route is just out and back
        return full_locations + [MUNICIPALITY_HUB] if len(full_locations) > 1 else full_locations

    # Create the routing index manager
    # len(full_locations) nodes, 1 vehicle, start at node 0 (Municipality)
    manager = pywrapcp.RoutingIndexManager(len(full_locations), 1, 0)

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        # Convert from routing variable Index to distance matrix NodeIndex
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return calculate_distance(full_locations[from_node], full_locations[to_node])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        ordered_locations = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            ordered_locations.append(full_locations[node_index])
            index = solution.Value(routing.NextVar(index))
        
        # Add start node to complete loop (Return to Municipality Hub)
        node_index = manager.IndexToNode(index)
        ordered_locations.append(full_locations[node_index])
        
        return ordered_locations
    else:
        return full_locations + [MUNICIPALITY_HUB] if len(full_locations) > 1 else full_locations
