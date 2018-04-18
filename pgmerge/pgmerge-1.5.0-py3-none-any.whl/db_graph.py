#!/usr/bin/env python3
"""
pgmerge - a PostgreSQL data import and merge utility

Copyright 2018 Simon Muller (samullers@gmail.com)
"""
import logging
import networkx as nx

_log = logging.getLogger(__name__)


def get_cycles(graph):
    return list(nx.simple_cycles(graph))


def break_cycles(graph):
    edges_removed = []
    for cycle in nx.simple_cycles(graph):
        # Only remove one direction of dependency and also remove self-references
        graph.remove_edge(cycle[0], cycle[-1])
        edges_removed.append([cycle[0], cycle[-1]])
    return edges_removed


def convert_to_dag(directed_graph):
    """
    Convert graph to directed acyclic graph by breaking cycles.
    """
    edges_removed = break_cycles(directed_graph)
    return edges_removed


def get_dependents(directed_acyclic_graph, node):
    assert nx.is_directed_acyclic_graph(directed_acyclic_graph), "Graph contains cycles."
    return nx.descendants(directed_acyclic_graph, node)


def get_fks_for_direct_cycles(table_graph, direct_cycles):
    fks = [table_graph.get_edge_data(cycle[0], cycle[1])['name'] for cycle in direct_cycles if len(cycle) == 2]
    fks.extend([table_graph.get_edge_data(cycle[1], cycle[0])['name'] for cycle in direct_cycles if len(cycle) == 2])
    return fks


def get_insertion_order(table_graph):
    copy_of_graph = table_graph.copy()
    convert_to_dag(copy_of_graph)
    return nx.topological_sort(copy_of_graph, reverse=True)


def build_fk_dependency_graph(inspector, schema, tables=None):
    table_graph = nx.DiGraph()
    if tables is None:
        tables = sorted(inspector.get_table_names(schema))
    for table in tables:
        fks = inspector.get_foreign_keys(table, schema)
        table_graph.add_node(table)
        for fk in fks:
            assert fk['referred_schema'] == schema, 'Remote tables not supported'
            other_table = fk['referred_table']
            if other_table in tables:
                table_graph.add_edge(table, other_table, name=fk['name'])
    return table_graph


def get_direct_cycle_fks_per_table(table_graph):
    cycles = get_cycles(table_graph)
    cycles = [cycle for cycle in cycles if len(cycle) > 1]

    from collections import defaultdict
    cycle_fks_per_table = defaultdict(list)
    for table_a, table_b in cycles:
        cycle_fks_per_table[table_a].append(table_graph.get_edge_data(table_a, table_b)['name'])
        cycle_fks_per_table[table_b].append(table_graph.get_edge_data(table_b, table_a)['name'])

    return cycle_fks_per_table


def get_all_dependent_tables(table_graph, tables):
    """
    Find all the tables on which the given set of tables depends. I.e. if the table has a foreign key dependency on
    a table and that table has a dependency on 2 other tables, then we'll get all 3 tables. We return all referenced
    tables as well as the given set of tables.
    """
    # dependent_tables = set()
    # print('Also including the following dependent tables:\n')
    # for table in sorted(tables):
    #     dependency_tree = nx.dfs_successors(table_graph, table)
    #     dependent_tables.update({table})
    #     dependent_tables.update(set(dependency_tree.keys()))
    #     dependent_tables.update({node for dependents in dependency_tree.values() for node in dependents})
    #     for node in sorted(dependency_tree.keys(), key=lambda x: '' if x == table else x):
    #         indent = '\t' if node == table else '\t  '
    #         print(indent + '{} -> {}'.format(node, ', '.join(sorted(dependency_tree[node]))))
    # print('')
    dependent_tables = {}
    print('Also including the following dependent tables:\n')
    for table in sorted(tables):
        dependency_tree = nx.dfs_successors(table_graph, table)
        dependents = set(dependency_tree.keys())
        dependents.update({node for dependents in dependency_tree.values() for node in dependents})
        dependent_tables[table] = dependents

    for main_table in sorted(dependent_tables.keys()):
        for dep_table in sorted(dependent_tables[main_table], key=lambda x: '' if x == main_table else x):
            indent = '\t' if dep_table == main_table else '\t  '
            print(indent + '{} -> {}'.format(dep_table, ', '.join(sorted(dependency_tree[node]))))
        print('')
    # dependent_tables.update(set())

    return dependent_tables
