'''Module for playing the network centrality game with greedy strategies.'''

import itertools
import networkx as nx
import numpy as np

from best_actions import *
from betweenness_centrality_cache import betweenness_centrality

def play_one_player_on_graph(graph, player):
    for i in xrange(20):
        best = best_addition(graph, player)
        print(best)
        if best['improvement'] >= 0:
            graph.add_edge(*best['action']['edge'])
        else:
            print('No more improvements')
            return

def play_one_player_on_empty_graph():
    graph = nx.empty_graph(20)
    play_one_player_on_graph(graph, 0)


def play_one_player_on_ring():
    graph = nx.empty_graph(20)
    for i in xrange(19):
        graph.add_edge(i, i+1)
    graph.add_edge(19, 0)
    play_one_player_on_graph(graph, 0)

def play_one_player_on_matchsticks():
    graph = nx.empty_graph()
    for i in xrange(10):
        graph.add_edge(2*i, 2*i+1)
    play_one_player_on_graph(graph, 0)

def parallel_graph_play_is_plus_or_minus_better():

    for turn in range(0,5):
        print('N   p      add    remove')
        for N in [20]:
            for p in np.arange(0,1.0,0.02):
                graph_add = nx.erdos_renyi_graph(N, p)
                graph_remove = graph_add.copy()
                add_done = False
                remove_done = False
                for rounds in xrange(2000):
                    if not add_done:
                        best_a = best_addition(graph=graph_add,
                                               player=0,
                                               score=betweenness_centrality)
                        if best_a is not None and best_a['improvement'] >= 0:
                            graph_add.add_edge(*best_a['action']['edge'])
                        else:
                            add_done = True

                    if not remove_done:
                        best_r = best_removal(graph=graph_remove,
                                              player=0,
                                              score=betweenness_centrality)
                        if best_r is not None and best_r['improvement'] >= 0:
                            graph_remove.remove_edge(*best_r['action']['edge'])
                        else:
                            remove_done = True
                print('%d  %.2f | %.3f  %.3f' %
                      (N, p,
                       betweenness_centrality(graph_add, 0),
                       betweenness_centrality(graph_remove, 0)))



def score_degree(graph, node):
    return graph.degree(node)


def same_graph_degree_competition():
    N = 20
    p = 0.25
    graph = nx.erdos_renyi_graph(N, p)
    p1 = 0
    p2 = 1

    for rounds in xrange(200):
        # player 1
        best_a = best_addition(graph=graph_add,
                               player=p1,
                               score=score_degree,
                               opponent=p2)


parallel_graph_play_is_plus_or_minus_better()

