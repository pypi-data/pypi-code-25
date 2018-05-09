import networkx as nx
import collections
import math
import pickle

def get_graph(DIR, FILENAME):
    print("Get Graph")
    with open(DIR+FILENAME+ '.pkl', 'rb') as f:
        G = pickle.load(f)
    return G

def order(G):
    return G.order()

def gamma_estimation(G):
    degrees = nx.degree(G).values()
    # print(degrees)
    total_nodes = len(degrees)
    counter=collections.Counter(degrees)
    # print(counter)
    gamma_dict = dict()
    for k, count in counter.items():
        # print(k, count/total_nodes)
        if k!=1:
            gamma_dict[k] = -math.log(count/total_nodes)/math.log(k)

    return gamma_dict

def number_connected_components(G):
    print("Connected Components")
    return nx.number_connected_components(G)

def clustering_coefficient(G):
    print("Clustering Coefficient")
    # print(nx.clustering(G))
    return nx.average_clustering(G)

def degree_correlation(G):
    degree_correlation = nx.degree_pearson_correlation_coefficient(G)
    return degree_correlation

def largest_connected_component(G):
    largest_cc = max(nx.connected_component_subgraphs(G), key=len)
    return largest_cc

def algebraic_connectivity(G):
    algebraic_connectivity = nx.algebraic_connectivity(G)
    return algebraic_connectivity

def edge_connectivity(G):
    return nx.edge_connectivity(G)

def node_connectivity(G):
    return nx.node_connectivity(G)

def diameter(G):
    return nx.diameter(G)

def average_shortest_path_length(G):
    return nx.average_shortest_path_length(G)

def centrality(G):
    degree = nx.degree_centrality(G)
    closeness = nx.closeness_centrality(G)
    betweenness = nx.betweenness_centrality(G)
    return degree, closeness, betweenness


FUNCTION_DICT = dict()
FUNCTION_DICT['Order'] = order
FUNCTION_DICT['Gamma'] = gamma_estimation
FUNCTION_DICT['Number_of_Connected_Components'] = number_connected_components
FUNCTION_DICT['Clustering_Coefficient'] = clustering_coefficient
FUNCTION_DICT['Degree_Correlation'] = degree_correlation
FUNCTION_DICT['Order_of_Largest_Connected_Component'] = order
FUNCTION_DICT['Algebraic_Connectivity_of_Largest_Connected_Component'] = algebraic_connectivity
FUNCTION_DICT['Edge_Connectivity_of_Largest_Connected_Component'] = edge_connectivity
FUNCTION_DICT['Vertex_Connectivity_of_Largest_Connected_Component'] = node_connectivity
FUNCTION_DICT['Diameter_of_Largest_Connected_Component'] = diameter
FUNCTION_DICT['Average_Shortest_Path_of_Largest_Connected_Component'] = average_shortest_path_length

def get_network_metrics(G, metrics_list, metrics_dict):
    metric_results_dict = dict()
    largest_cc = None
    for metric in metrics_list:
        if metrics_dict[metric]:
            print(metric)
            if metric.endswith('Largest_Connected_Component'):
                if largest_cc is None:
                    largest_cc = largest_connected_component(G)
                metric_results_dict[metric] = FUNCTION_DICT[metric](largest_cc)
            else:
                metric_results_dict[metric] = FUNCTION_DICT[metric](G)

    print(metric_results_dict)
    return metric_results_dict

