import networkx as nx
from math import radians, cos, sin, sqrt, atan2

def distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

def build_graph(locations):
    G = nx.Graph()

    for i in range(len(locations)):
        for j in range(i+1, len(locations)):
            d = distance(
                locations[i].latitude, locations[i].longitude,
                locations[j].latitude, locations[j].longitude
            )
            G.add_edge(i, j, weight=d)

    return G

def tsp_route(locations):
    if len(locations) < 2:
        return list(range(len(locations)))
    G = build_graph(locations)
    path = nx.approximation.traveling_salesman_problem(G, cycle=True)
    return path