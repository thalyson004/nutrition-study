
from PapaGraph.PapaGraph.PapaGraph import PapaGraph
from ogb.io.read_graph_raw import read_csv_graph_raw

def convert_from_ogb(ogb_graph:dict):
    try:
        nodes_number = ogb_graph['num_nodes']
        nodes_features = ogb_graph['node_feat']

        edges = ogb_graph['edge_index']
        edges_features = ogb_graph['edge_feat']
    except:
        print("The input is not a OGB Raw Graph")
        return None

    ans = PapaGraph()

    # TODO: Change nodes_features from list[list] to list[dict]
    ans.add_nodes(nodes_number, nodes_features)

    # print(len(edges_features))
    # print(edges_features)
    # print(ans.nodes_number, edges[0][0], edges[1][0])

    # TODO: Change edges_features from list[list] to list[dict]
    for i in range(len(edges_features)):
        # print(edges_features[i])
        ans.add_edge( edges[0][i], edges[1][i], features=edges_features[i], bidirectional=True) 

    return ans

if __name__ == '__main__':
    graphs = read_csv_graph_raw("E:/Projetos/Doctorate/MLG/Machine-Learning-with-Graphs/data/homework02/ogbg_molhiv/raw")
    graph = convert_from_ogb(graphs[0])

    print("Nodes =", graph.nodes_number)
    print("Edges =", graph.edges_number)
    #print(graph.edges_features, "\n")
    #print(graph.nodes_features, "\n")