'''Module for playing the network centrality game with greedy strategies.'''

import itertools
import networkx as nx
from collections import namedtuple

def addEdge(i, j):
        return {'i': i,
                'j': j,
                'test': (lambda graph : graph.add_edge(i, j)),
                'reset':  (lambda graph : graph.remove_edge(i, j))
                }


def removeEdge(i, j):
    return {'i': i,
            'j': j,
            'test': lambda graph : graph.remove_edge(i, j),
            'reset': lambda graph : graph.add_edge(i, j)
            }



def best_addition(graph, player):
    if graph.degree(player) == 0:
        other = 1 if player == 0 else 0
        return {'improvement': 0.001, 'action': addEdge(player, other),
                'edge': (player, other) }
    best = best_strategy(graph, player,
                         [addEdge(i, j) for i, j in
                          itertools.product(range(0, len(graph)), repeat=2)
                          if i != j
                          and not graph.has_edge(i, j)
                         ])
    if best == None:
        return None

    return { 'improvement': best['improvement'], 'action': best['action'],
             'edge': (best['action']['i'], best['action']['j']) }


def best_removal(graph, player):
    best = best_strategy(graph, player,
                         [removeEdge(i, j) for i, j in
                          itertools.product(range(0, len(graph)), repeat=2)
                          if i != j
                          and graph.has_edge(i, j)
                         ])

    if best == None:
        return None

    return { 'improvement': best['improvement'], 'action': best['action'],
             'edge': (best['action']['i'], best['action']['j']) }


def best_strategy(graph, agent, actions):
    if len(actions) == 0:
        return None
    original_centrality = nx.betweenness_centrality(graph)[agent]
    return max(((
        {'action': action,
         'improvement': compute_improvement(graph, action, agent, original_centrality)
        }
    ) for action in actions), key=(lambda pair : pair['improvement']))


def compute_improvement(graph, action, agent, original_centrality=None):
    if original_centrality is None:
        original_centrality = nx.betweenness_centrality(graph)[agent]

    action['test'](graph)
    new_centrality = nx.betweenness_centrality(graph)[agent]
    improvement = new_centrality - original_centrality

    action['reset'](graph)

    return improvement



# Tests


def test_compute_improvement_graph_left_alone():
    graph = nx.empty_graph(4)
    compute_improvement(graph, action=addEdge(0, 1), agent=0)
    assert graph.adj == nx.empty_graph(4).adj


def test_best_addition_connect_three_nodes():
    graph = nx.empty_graph(3)
    graph.add_edge(0, 1)
    best = best_addition(graph=graph, player=0)
    assert best['edge'] == (0,2)

def test_best_addition_two_stars_will_kiss():
    star = nx.star_graph(3) # size 4
    star.remove_edge(0,1) # 1 is now disconnected from star
    best = best_addition(graph=star, player=0)
    assert best['edge'] == (0,1)


def test_best_addition_adds_to_empty():
    graph = nx.empty_graph(2)
    best = best_addition(graph=graph, player=0)



test_compute_improvement_graph_left_alone()
test_best_addition_connect_three_nodes()
test_best_addition_two_stars_will_kiss()
test_best_addition_adds_to_empty()
