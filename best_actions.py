'''Module for playing the network centrality game with greedy strategies.'''

import itertools
import networkx as nx
from collections import namedtuple

def addEdge(i, j):
        return {'i': i,
                'j': j,
                'test': (lambda graph : graph.add_edge(i, j)),
                'ignore': (lambda graph : graph.has_edge(i, j) or i == j),
                'reset':  (lambda graph : graph.remove_edge(i, j))
                }


def removeEdge(i, j):
    return {'i': i,
            'j': j,
            'test': lambda graph : graph.add_edge(i, j),
            'ignore': (lambda graph : not graph.has_edge(i, j) or i == j),
            'reset': lambda graph : graph.remove_edge(i, j)
            }


def best_addition(graph, player):
    '''Determines the edge that when added to graph produces greatest improvement in betweenness
    centrality. If opponent is present, computes best improvement minus opponent's change.
    '''

    best = best_strategy(graph, player,
                         [addEdge(i, j) for i, j in
                          itertools.product(range(0, len(graph)), repeat=2)])
                         
    return { 'improvement': best['improvement'],
             'edge': (best['action']['i'], best['action']['j']) }


def best_strategy(graph, agent, actions):
    original_centrality = nx.betweenness_centrality(graph)[agent]
    return max(((
        {'action': action,
         'improvement': compute_improvement(graph, action, agent, original_centrality)
        }
    ) for action in actions), key=(lambda pair : pair['improvement']))


def compute_improvement(graph, action, agent, original_centrality=-1):
    '''Computes the change (improvement) in betweenness centrality for player if the given edge is
    added to the graph. If opponent is present, computes best improvement minus opponent's change.
    '''
    if original_centrality == -1:
        original_centrality = nx.betweenness_centrality(graph)[agent]

    if 'ignore' in action and action['ignore'](graph):
        return 0

    action['test'](graph)
    new_centrality = nx.betweenness_centrality(graph)[agent]
    improvement = new_centrality - original_centrality

    action['reset'](graph)

    return improvement


# Tests


def test_compute_improvement_graph_left_alone():
    '''Tests that compute_improvement does not modify graph when finished.'''
    graph = nx.empty_graph(4)
    compute_improvement(graph, action=addEdge(0, 1), agent=0)
    assert graph.adj == nx.empty_graph(4).adj


def test_best_addition_connect_three_nodes():
    '''Tests that if player and 1 are connected, player will connect to 2.'''
    graph = nx.empty_graph(3)
    graph.add_edge(0, 1)
    best = best_addition(graph=graph, player=0)
    assert best['edge'] == (0,2)

def test_best_addition_two_stars_will_kiss():
    star = nx.star_graph(3) # size 4
    star.remove_edge(0,1) # 1 is now disconnected from star
    best = best_addition(graph=star, player=0)
    assert best['edge'] == (0,1)




#test_compute_improvement_graph_left_alone()
#test_best_addition_connect_three_nodes()
test_best_addition_two_stars_will_kiss()
