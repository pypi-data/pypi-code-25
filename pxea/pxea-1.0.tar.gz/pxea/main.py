from __future__ import print_function

from utilities import set_enrichment
from utilities import network
import networkx

def main():
    ranked_list = ["d", "a", "e", "c", "b"]
    candidates = ["b", "c"]
    g = networkx.path_graph(10)
    n_random = 10000
    # Proximity
    z, d = network.calculate_proximity(g, [1,2], [8,9], n_random=n_random)
    print(z, d)
    z, d = network.calculate_proximity(g, [2], [2,3], n_random=n_random)
    print(z, d)
    # PxEA
    score, pval = set_enrichment.get_enrichment_score_and_pval(ranked_list, candidates, n_random=n_random, alternative="greater")
    print(score, pval)
    return


if __name__ == "__main__":
    main()

