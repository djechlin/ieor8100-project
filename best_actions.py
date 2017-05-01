'''Module for playing the network centrality game with greedy strategies.'''

import itertools
import networkx as nx

def best_addition(graph, player):
    '''Determines the edge that when added to graph produces greatest improvement in betweenness
    centrality. If opponent is present, computes best improvement minus opponent's change.
    '''
    player_original = nx.betweenness_centrality(graph)[player]
    best = {}
    for i, j in itertools.product(range(0, len(graph)), repeat=2):
        if i == j:
            continue
        if graph.has_edge(i, j):
            continue
        [player_improvement] = compute_improvements(graph, (i, j), (player,), (player_original,))
        if not best or player_improvement > best['improvement']:
            best = {"improvement": player_improvement, "edge": (i, j)}
    return best


def compute_improvements(graph, edge, agents, original_centralities=None):
    '''Computes the change (improvement) in betweenness centrality for player if the given edge is
    added to the graph. If opponent is present, computes best improvement minus opponent's change.
    '''
    if graph.has_edge(*edge):
        raise ValueError("graph already has edges %s and %s" % edge)

    if original_centralities is None:
        centralities_all = nx.betweenness_centrality(graph)
        original_centralities = [centralities_all[agent] for agent in agents]

    graph.add_edge(*edge)

    centralities_all = nx.betweenness_centrality(graph)
    new_centralities = [centralities_all[agent] for agent in agents]
    improvements = [new - original for new, original in
                    zip(new_centralities, original_centralities)]

    graph.remove_edge(*edge)

    return improvements


# Tests

def test_compute_improvement_nilpotent_throws_error():
    '''Tests that compute_improvement throws error if change does nothing.'''
    caught = False
    graph = nx.empty_graph(4)
    graph.add_edge(0, 1)
    try:
        compute_improvements(graph, edge=(0, 1), agents=(0,))
    except ValueError as error:
        caught = str(error).startswith("graph already has")
    if not caught:
        raise ValueError("Failed test")


def test_compute_improvement_graph_left_alone():
    '''Tests that compute_improvement does not modify graph when finished.'''
    graph = nx.empty_graph(4)
    compute_improvements(graph, edge=(0, 1), agents=(0,))
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
    best = best_addition(graph=star, player=1)
    assert best['edge'] == (0,1)


test_compute_improvement_nilpotent_throws_error()
test_compute_improvement_graph_left_alone()
test_best_addition_connect_three_nodes()
test_best_addition_two_stars_will_kiss()
