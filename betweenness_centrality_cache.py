import networkx as nx

cache = {}

def betweenness_centrality(graph, player=None):
    if graph.degree(player) == 0:
        return -0.001
    
    adj = graph.adj
    key = repr(adj)
    if key not in cache:
        cache[key] = nx.betweenness_centrality(graph)
    if player is None:
        return cache[key]
    else:
        return cache[key][player]

