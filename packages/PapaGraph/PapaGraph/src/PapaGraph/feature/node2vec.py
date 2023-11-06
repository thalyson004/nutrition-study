from PapaGraph.PapaGraph.PapaGraph import PapaGraph
from PapaGraph.sample.handmande import handmade_sample
from PapaGraph.walk.random_walk import probability_matrix, random_walk_r, random_walk_r_all
from gensim.models import Word2Vec
import random 
import math

def listOfListAny2listOfListStr(lists:list[list])->list[list[str]]:
    return [[str(w) for w in word] for word in lists]

def node2vec(   graph: PapaGraph, d:int=3, r:int=10, 
                lenght:int=10, p:float=1.0, q:float=1.0, 
                epochs:int=5, learning_rate:float=0.025) -> dict[int, list]:
    ''' Dictionary that mapping each node into a `d` dimensional space.

    Input
    ----
    `graph`: A PapaGraph
    `d`: Number of features
    `r`: Number of random walks
    `lenght`: Lenght of each random walk
    `p`: Return parameter
    `q`: In-Out paramenter
    `steps`: Number of steps using Gradiente Descent
    
    Output
    ----
    `features`: Dictionary that mapping node to features

    '''
    
    walks = random_walk_r_all(graph, r=r, lenght=lenght, p=p, q=q)
    words = listOfListAny2listOfListStr(walks)
    model = Word2Vec(   words, 
                        window=5, min_count=1, sg=1, 
                        workers=2, alpha=learning_rate,
                        epochs=epochs, vector_size=d)
    '''
        This model give features for each node
        To get features by node, use: model.wv[str(0)]
    '''

    features = dict()
    for node in range(graph.nodes_number):
        features[node] = model.wv[str(node)].copy()

    return features

def graph2vec(graph: PapaGraph, d:int=3, r:int=10, 
                lenght:int=10, p:float=1.0, q:float=1.0, 
                epochs:int=5, learning_rate:float=0.025, add_feature:bool=False) -> list:
    ''' Return a list of `d` features.

    Input
    ----
    `graph`: A PapaGraph
    `d`: Number of features
    `r`: Number of random walks
    `lenght`: Lenght of each random walk
    `p`: Return parameter
    `q`: In-Out paramenter
    `epochs`: Number of epochs using in word2vec
    `add_feature`: If is True, add the features into graph features

    Output
    ----
    `features`: List of features

    '''

    # Create a copy of the graph
    graphCopied = graph.copy()

    # Add a new node
    u = graphCopied.nodes_number
    graphCopied.add_node()

    # Add edge from the new node to all nodes
    for v in range(u):
        graphCopied.add_edge(u, v, bidirectional=False)
    
    # Call node2vec
    features = node2vec(graphCopied, d=d, r=r, 
                        lenght=lenght, p=p, q=q, 
                        epochs=epochs, learning_rate=learning_rate
                        )[u]
    

    if add_feature:
        for i, feature in enumerate(features):
            graph.add_feature("f"+str(i), feature)

    # Return features of the newnode
    return features

if __name__ == '__main__':
    graph = handmade_sample()
    
    feature = graph2vec(graph, d= 5, lenght=5, r=3, add_feature=True)

    print(graph.graph_features)


