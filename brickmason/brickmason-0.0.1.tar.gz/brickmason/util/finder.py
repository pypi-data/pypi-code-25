"""
find most similar name by class

util.find(G, BRICK.Zone_Temperature_Sensor, "0024")
use difflib to find most similar
"""

import json
import difflib
import numpy as np
from collections import defaultdict
np.random.seed(1)

def mean_distance(cluster, l):
    return np.mean([difflib.SequenceMatcher(None, cur, l).ratio() for cur in cluster])

def find_closest(cluster, l, prefix):
    similarities = [difflib.SequenceMatcher(None, x[len(prefix):], l).ratio() for x in cluster]
    idx = np.argmax(similarities)
    return np.max(similarities), cluster[idx]


def build_cluster(labels, THRESHOLD=.85):
    clusters = defaultdict(list)
    first = labels.pop(0)
    clusters[0].append(first)

    foundCluster = False
    for l in labels:
        for cl, cluster in clusters.items():
            if mean_distance(cluster, l) >= THRESHOLD:
                clusters[cl].append(l)
                foundCluster = True
                break
        if not foundCluster: clusters[len(clusters)].append(l)

    return clusters

def common_prefix(cluster):
    len_first = len(cluster[0])
    for i in range(len_first):
        prefixes = set([x[:i] for x in cluster])
        if len(prefixes) > 1:
            return cluster[0][:i-1]
    return ''

def find(graph, klass, name):
    q = """SELECT ?x WHERE {{
        ?x rdf:type <{0}>
    }}""".format(klass)
    res = graph.query(q)
    # pull out the name of the label from the URI
    labels = [x[0].split('#')[1] for x in res]

    # cluster all of the labels for this class
    clusters = build_cluster(labels)
    # build the common prefixes for all labels on a per-cluster basis
    prefixes = {k: common_prefix(cluster) for k, cluster in clusters.items()}
    
    #print json.dumps(clusters, indent=2)

    similarities = []
    possible_labels = []
    for clusteridx, cluster in clusters.items():
        s, possible = find_closest(cluster, name, prefixes[clusteridx])
        similarities.append(s)
        possible_labels.append(possible)
    #print similarities
    #print possible_labels
    #print name,"closest", possible_labels[np.argmax(similarities)]

    predictions = [difflib.SequenceMatcher(None, name, l).ratio() for l in labels]
    choose_similarity = -1.0
    choose_idx = -1
    for idx, similarity in enumerate(predictions):
        if similarity > choose_similarity:
            choose_similarity = similarity
            choose_idx = idx
    if choose_idx == -1:
        return name
    return labels[choose_idx]
