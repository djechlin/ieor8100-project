'''Module for playing the network centrality game with greedy strategies.'''

import itertools
import networkx as nx
from collections import namedtuple

from betweenness_centrality_cache import betweenness_centrality


def toggle_edge(graph, i, j):
    if graph.has_edge(i, j):
        graph.remove_edge(i, j)
    else:
        graph.add_edge(i, j)

neighbors = []

def make_assassination(i):
        neighbors = []
        def test(graph):
                for n in graph.neighbors(i):
                    neighbors.append(n)
                    graph.remove_edge(i, n)

        def reset(graph):
                for n in neighbors:
                   graph.add_edge(n, i)


        return {'test': test, 'reset': reset, 'strategy': lambda : 'assassinate(%d)' % len(neighbors)}


def make_toggle(i, j):
        return {'edge': (i, j),
                'strategy': lambda : '',
                'test': lambda graph : toggle_edge(graph, i, j),
                'reset': lambda graph : toggle_edge(graph, i, j)
                }
def make_two_toggles(edge1, edge2):
        toggle1 = make_toggle(*edge1)
        toggle2 = make_toggle(*edge2)
        def test(graph):
            toggle1['test'](graph)
            toggle2['test'](graph)
        def reset(graph):
            toggle2['reset'](graph)
            toggle1['reset'](graph)
        return {
                'test': test,
                'reset': reset,
                'strategy': lambda :'double'
                }

def all_edges_such_that(graph, test=None, node_list=None):
        if node_list is None:
            node_list = range(0, len(graph));
        return [(i, j) for i, j in
                itertools.product(node_list, repeat=2)
                if i != j
                and (test is None or test(graph, i, j))];

def all_present_edges(graph):
        return all_edges_such_that(graph, (lambda g, i, j : g.has_edge(i, j)))

def all_absent_edges(graph):
        return all_edges_such_that(graph, (lambda g, i, j: not g.has_edge(i, j)))


def best_addition(graph, score, player, opponent=None):
    return best_strategy(graph=graph,
                         player=player,
                         opponent=opponent,
                         actions=[make_toggle(*edge) for edge in all_absent_edges(graph)],
                         score=score)


def best_removal(graph, player, score, opponent=None):
    return best_strategy(graph=graph,
                         player=player,
                         opponent=opponent,
                         actions=[make_toggle(*edge) for edge in all_present_edges(graph)],
                         score=score)

def best_addition_or_removal(graph, player, score, node_list=None, opponent=None):
    return best_strategy(graph=graph,
                         player=player,
                         opponent=opponent,
                         actions=[make_toggle(*edge)
                                  for edge in all_edges_such_that(graph, node_list=node_list)],
                         score=score)


def best_strategy(graph, player, actions, score, opponent):
    if len(actions) == 0:
        return None
    return max(((
        {
                'action': action,
                'improvement': compute_improvement(graph=graph,
                                                   action=action,
                                                   player=player,
                                                   opponent=opponent,
                                                   score=score)
        }
    ) for action in actions),
               key=(lambda pair : pair['improvement']))


def compute_improvement(graph, action, player, opponent, score, diff=(lambda a, b : a - b)):
    old_player_score = score(graph, player)
    if opponent is not None:
            old_opponent_score = score(graph, opponent)


    action['test'](graph)
    new_player_score = score(graph, player)
    if opponent is not None:
            new_opponent_score = score(graph, opponent)

    action['reset'](graph)

    player_improvement = diff(new_player_score, old_player_score)
    if opponent is not None:
            opponent_improvement = diff(new_opponent_score, old_opponent_score)

    if opponent is None:
            return player_improvement
    else:
            return player_improvement - opponent_improvement


# Tests


def test_compute_improvement_graph_left_alone():
    graph = nx.empty_graph(4)
    compute_improvement(graph=graph,
                        action=make_toggle(0, 1),
                        player=0,
                        opponent=None,
                        score=betweenness_centrality)
    assert graph.adj == nx.empty_graph(4).adj


def test_best_addition_connect_three_nodes():
    graph = nx.empty_graph(3)
    graph.add_edge(0, 1)
    best = best_addition(graph=graph,
                         player=0,
                         score=betweenness_centrality)
    assert best['action']['edge'] == (0,2)

def test_best_addition_two_stars_will_kiss():
    star = nx.star_graph(3) # size 4
    star.remove_edge(0,1) # 1 is now disconnected from star
    best = best_addition(graph=star,
                         player=0,
                         score=betweenness_centrality)
    assert best['action']['edge'] == (0,1)


def test_best_addition_adds_to_empty():
    graph = nx.empty_graph(2)
    best = best_addition(graph=graph,
                         player=0,
                         score=betweenness_centrality)
    assert best['action']['edge'] == (0,1)


def test_best_removal_hurts_opponent():
        graph = nx.empty_graph(7)
        # make node 0 have betweenness for a large star
        graph.add_edge(0,1)
        graph.add_edge(0,2)
        graph.add_edge(0,3)
        # make rival node 3 have betweenness for a small star
        graph.add_edge(4,5)
        graph.add_edge(4,6)
        # connect the two competitors
        graph.add_edge(0, 4)

        best = best_removal(graph=graph,
                            player=0,
                            opponent=3,
                            score=betweenness_centrality)
        # big star wants the connection or is at least indifferent
        # so would rather just hurt the small star
        assert best['action']['edge'] == (4,5)


test_compute_improvement_graph_left_alone()
test_best_addition_connect_three_nodes()
test_best_addition_two_stars_will_kiss()
test_best_addition_adds_to_empty()
test_best_removal_hurts_opponent()
