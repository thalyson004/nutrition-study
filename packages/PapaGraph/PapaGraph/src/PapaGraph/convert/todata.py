from PapaGraph.PapaGraph.PapaGraph import PapaGraph
from PapaGraph.sample import handmade_sample
from PapaGraph.feature.node2vec import graph2vec

from pandas import DataFrame

import pandas as pd
import numpy as np


def toDataFrame(graphs: list[PapaGraph]) -> DataFrame:
    """Return a DataFrame with the graph features


    Input
    ----
    `graphs`: List of PapaGraphs

    Output
    ----
    `df`: DataFrame with the graph features

    """
    # TODO: Check if all graphs have the same features

    df = DataFrame(
        [list(graph.graph_features.values()) for graph in graphs],
        columns=list(graphs[0].graph_features),
    )

    return df


if __name__ == "__main__":
    graphs = [handmade_sample()] * 5

    for graph in graphs:
        graph2vec(graph, d=5, add_feature=True)

    print(print(toDataFrame(graphs)))
