import copy


class PapaGraph:
    def __init__(self):
        self.__nodes_number: int = 0
        self.__nodes_features: list[dict] = []
        self.__edges_number: int = 0
        self.__edges_features: list[dict] = []
        self.__edges_list: list[tuple] = []
        self.__adjacency_list: list[list[tuple]] = []
        self.__graph_features: dict = {}

    @property
    def nodes_number(self):
        return self.__nodes_number

    @property
    def nodes_features(self):
        return self.__nodes_features

    @property
    def edges_number(self):
        return self.__edges_number

    @property
    def edges_features(self):
        return self.__edges_features

    @property
    def edges_list(self):
        return self.__edges_list

    @property
    def adjacency_list(self):
        return self.__adjacency_list

    @property
    def graph_features(self):
        return self.__graph_features

    def add_feature(self, key: str, value: any):
        self.__graph_features[key] = value

    def add_edge(
        self, u: int, v: int, features: dict = {}, bidirectional: bool = False
    ):
        """Add edge from node `u` to node `v` with features `features`
        If `bidirectional` is True, it will create a edge(v,u) too.
        """
        assert u >= 0 and u < self.__nodes_number
        assert v >= 0 and v < self.__nodes_number

        if bidirectional == True:
            self.add_edge(v, u, features=features)

        self.__edges_list.append((u, v))
        self.__edges_features.append(features)
        self.__adjacency_list[u].append((v, self.__edges_number))
        self.__edges_number = self.__edges_number + 1

    def add_node(self, features: dict = {}):
        self.__nodes_number = self.__nodes_number + 1
        self.__nodes_features.append(features)
        self.__adjacency_list.append([])

    def add_nodes(self, quantity: int, features_list: list[dict] = []):
        if len(features_list) == 0:
            assert quantity > 0

            for i in range(quantity):
                self.add_node()
        else:
            assert quantity == len(features_list)

            for i in range(quantity):
                self.add_node(features=features_list[i])

    def copy(self):
        return copy.deepcopy(self)

    # TODO: neighbors of a node
    def neighbors(self, node_index: int):
        """Return a list of pairs<``neighbor_node``, ``edge_index``>"""
        return self.adjacency_list[node_index]


if __name__ == "__main__":
    graph = PapaGraph()
    """
    print(graph.nodes_number)
    print(graph.nodes_features)
    print(graph.edges_number)
    print(graph.edges_features)
    print(graph.edges_list)
    print(graph.adjacency_list)
    print(graph.graph_features)
    """
    graph.add_nodes(quantity=2, features_list=[{}, {}])
    print(graph.nodes_features, "------")

    newGraph = graph.copy()
    newGraph.add_node()

    print(graph.nodes_features)
    print(newGraph.nodes_features)
