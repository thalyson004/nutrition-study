from PapaGraph.PapaGraph.PapaGraph import PapaGraph

samples:list[PapaGraph] = []

graph = PapaGraph()
graph.add_nodes(quantity=8)
graph.add_edge(0,1, bidirectional=True)
graph.add_edge(0,2, bidirectional=True)
graph.add_edge(0,3, bidirectional=True)
graph.add_edge(1,2, bidirectional=True)
graph.add_edge(1,7, bidirectional=True)
graph.add_edge(2,3, bidirectional=True)
graph.add_edge(3,4, bidirectional=True)
graph.add_edge(4,7, bidirectional=True)
graph.add_edge(4,5, bidirectional=True)
graph.add_edge(4,6, bidirectional=True)
graph.add_edge(5,6, bidirectional=True)
samples.append(graph)

def handmade_sample(index:int = 0):
    return samples[index]

