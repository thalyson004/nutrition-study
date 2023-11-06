from PapaGraph.PapaGraph.PapaGraph import *
from PapaGraph.sample import handmande
from queue import Queue

def components_number(graph:PapaGraph)->int:
    '''Number of components of the graph `graph`

    Input
    ----
    `graph`: Papagraph

    Output
    ----
    `number`: Number of components of the graph
    '''

    components = [None]*graph.nodes_number
    number = 0
    for node in range(graph.nodes_number):
        if components[node] == None:
            number += 1
            components[node]= number
            bfs = Queue()
            bfs.put(node)

            while not bfs.empty():
                actual_node = bfs.get()
                
                for next_node, edge_index in graph.neighbors(actual_node):
                    if components[next_node]==None:
                        components[next_node] = number
                        bfs.put(next_node) 

    return number

if __name__=='__main__':
    graph = handmande.handmade_sample()

    print(components_number(graph))