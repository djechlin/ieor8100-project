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

def best_addition_2p_zero_sum(graph, player, opponent):
    '''Determines the edge that produces the greatest additive improvement.'''
    original_centralities = nx.betweenness_centrality(graph)
    player_original = original_centralities[player]
    opponent_original = original_centralities[opponent]
    best = {}
    for i, j in itertools.product(range(0, len(graph)), repeat=2):
        if i == j:
            continue
        if graph.has_edge(i, j):
            continue
        [player_improvement, opponent_improvement] = compute_improvements(
            graph, (i, j), (player, opponent), (player_original, opponent_original))
        zero_sum_improvement = player_improvement - opponent_improvement
        if not best or zero_sum_improvement > best['zero_sum_improvement']:
            best = {"zero_sum_improvement": zero_sum_improvement,
                    "edge": (i, j),
                    "player_improvement": player_improvement,
                    "opponent_improvement": opponent_improvement}
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


def test_best_addition_2p_zero_sum_little_kisses_big():
    star = nx.star_graph(10) # 0; 1,2,...,10
    # Free up the last three nodes and make a path
    star.remove_edge(0, 8)
    star.remove_edge(0, 9)
    star.remove_edge(0, 10)
    star.add_edge(8, 9)
    star.add_edge(9, 10)

    # make a singleton
    star.remove_edge(0, 7)

    # without zero sum, the star node prefers the matchstick (all matchstick nodes are equivalent)
    best = best_addition(graph=star, player=0)
    assert best['edge'] == (0, 8)

    # if node 8 is an opponent, the star node must connect away from it
    best = best_addition_2p_zero_sum(graph=star, player=0, opponent=8)
    assert best['edge'] == (0, 9)


test_compute_improvement_nilpotent_throws_error()
test_compute_improvement_graph_left_alone()
test_best_addition_connect_three_nodes()
test_best_addition_two_stars_will_kiss()
test_best_addition_2p_zero_sum_little_kisses_big()
