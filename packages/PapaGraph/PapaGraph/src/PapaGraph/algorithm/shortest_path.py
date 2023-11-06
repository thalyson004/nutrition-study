from PapaGraph.PapaGraph.PapaGraph import *
from PapaGraph.sample import handmande
from queue import Queue

def steps_from(graph:PapaGraph, start:int)->list[int]:
    '''Given a graph and a start node, return a list of steps from 
    the start node to all nodes

    Input
    ----
    `graph`: Papagraph
    `start`: Initial node

    Output
    ----
    `distances`: List of steps from the start node to all nodes
    '''
    
    distances = [None]*graph.nodes_number
    distances[start] = 0

    bfs = Queue()
    bfs.put(start)

    while not bfs.empty():
        actual_node = bfs.get()

        for next_node, edge_index in graph.neighbors(actual_node):
            if distances[next_node]==None:
                distances[next_node] = distances[actual_node]+1
                bfs.put(next_node) 

    return distances

if __name__=='__main__':
    graph = handmande.handmade_sample()

    print(steps_from(graph, 0))