from PapaGraph.PapaGraph.PapaGraph import PapaGraph
from PapaGraph.algorithm.shortest_path import steps_from
from PapaGraph.sample.handmande import handmade_sample
from joblib import Parallel, delayed
import random

# TODO: If i'm on node with no neighbors, actual algorithm not work properly
def random_walk(graph:PapaGraph, start:int, lenght:int, p:float=1.0, q:float=1.0):
    '''Generate a random walk starting from `start`

    Input
    ----
    `start`: Start node
    `lenght`: Lenght of the walk
    `p`: Return paramenter
    `q`: In-Out paramenter

    Output
    ----
    `walk`: A list of nodes representing a random walk
    '''
    assert start>=0 and start<graph.nodes_number, "node is not in graph"
    assert isinstance(p, float), "p parameter must by float32"
    assert isinstance(q, float), "q parameter must by float32"
    
    walk:list = [start]
    prev:int = None
    actual:int = start

    steps_distance:list = steps_from(graph=graph, start=start) 

    for step in range(lenght):
        neighbors:list[tuple] = graph.neighbors(actual)
        probability_sum:float = 0.0
        probabilities:list[float] = []

        for neighbor_index, edge_index in neighbors:
            if neighbor_index == prev:
                probabilities.append(1.0/p)
            elif steps_distance[neighbor_index] > steps_distance[actual]:
                probabilities.append(1.0/q)
            else: 
                probabilities.append(1.0)

        probability_sum:float = sum(probabilities)

        probability_remain:float = random.uniform(0,probability_sum)
        prev = actual
        for i, (neighbor_index, edge_index) in enumerate(neighbors):
            if probability_remain <= probabilities[i]:
                actual = neighbor_index
                break
            else:
                probability_remain = probability_remain - probabilities[i]
        
        walk.append(actual)

    return walk   

def random_walk_r(graph:PapaGraph, start:int, r:int=3, lenght:int=10, p:float=1.0, q:float=1.0): 
    '''Generate ``r`` random walks starting from `start`.
    
    Input
    ----
    `graph`: A PapaGraph
    `start`: Start node
    `lenght`: Lenght of the walk
    `r`: Quantity of random walks
    `p`: Return paramenter
    `q`: In-Out paramenter

    Output
    ----
    `walks`: A list of lists of nodes representing random walks
    '''
    assert start>=0 and start<graph.nodes_number, "node is not in graph"
    assert isinstance(p, float), "p parameter must by float32"
    assert isinstance(q, float), "q parameter must by float32"

    walks = []
    for i in range(r):
        walks.append(random_walk(graph, start, lenght, p, q))
    return walks

def random_walk_r_all(graph:PapaGraph, lenght:int=10, r:int=3, p:float=1.0, q:float=1.0): 
    '''Generate ``r`` random walks per node.
    
    Input
    ----
    `graph`: A PapaGraph
    `lenght`: Lenght of the walk
    `r`: Quantity of random walks
    `p`: Return paramenter
    `q`: In-Out paramenter

    Output
    ----
    `walks`: A list of lists of nodes representing random walks
    '''
    assert isinstance(p, float), "p parameter must by float32"
    assert isinstance(q, float), "q parameter must by float32"

    walks = []
    for node in range(graph.nodes_number):
        fromNode = random_walk_r(graph, node, r, lenght=lenght, p=p, q=q)
        for walk in fromNode:
            walks.append(walk)
            
    return walks

def probability_matrix(graph:PapaGraph, r:int=10, lenght:int=10, p:float=1.0, q:float=1.0):
    '''Returns a matrix `probabilities` that cell ``[u][v]``
    represents the probability to reach node `v` from node `u`
    by a random walk.

    Input
    ----
    `graph`: A PapaGraph
    `r`: Quantity of random walks
    `lenght`: Lenght of the walk
    `p`: Return paramenter
    `q`: In-Out paramenter

    Output
    ----
    `probabilities`: Probability matrix
    '''
    probabilities = [[ 0.0 for i in range(graph.nodes_number) ] for j in range(graph.nodes_number)]
    for u in range(graph.nodes_number):
        walks = random_walk_r(graph, u, r, lenght, p, q)
        for walk in walks:
            in_path:set = set(walk)

            for v in in_path:
                probabilities[u][v] = probabilities[u][v] + 1/r

    return probabilities

if __name__ == '__main__':
    graph = handmade_sample()
    # print(random_walk(graph, 0, 5))
    print(random_walk_r(graph, 0, 5, 4))