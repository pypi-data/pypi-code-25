from yuna import masternodes as mn

def label_series_nodes(g):
    remove = list()
    for n in g.nodes():
        if g.node[n]['label'].id[0] in ['b', 'v']:
            if len([i for i in g[n]]) == 2:
                remove.append(n)
    return remove


def series_node_removal(g):
    """  """
    remove = label_series_nodes(g)

    for n in g.nodes():
        if g.node[n]['label'].id[0] in ['b', 'v']:
            if len([i for i in g[n]]) == 2:
                e = [i for i in g[n]]
                g.add_edge(e[0], e[1])

    g.remove_nodes_from(remove)


def is_node_grounded(g, n):
    # TODO: We have to update the ground terminal connections.
    # if g.node[n]['label'].datatype == 1:
    if 'label' in g.node[n]:
        if isinstance(g.node[n]['label'], mn.Via):
            if len([i for i in g.neighbors(n)]) == 1:
                return True
            else:
                return False


def graph_to_netlist(g, name):
    G = g.copy()

    mfile = open(name + '.cir', 'w')

    mfile.write('* Inductances\n')
    for i, e in enumerate(G.edges()):
        # G[e[0]][e[1]]['label'] = 'L' + str(i)

        print(e)

        n1, n2 = None, None
        if is_node_grounded(G, e[0]):
            n1 = '0'
        else:
            n1 = str(e[0])

        if is_node_grounded(G, e[1]):
            n2 = '0'
        else:
            n2 = str(e[1])

        if n1 == '0':
            mfile.write('L' + str(i) + '\t' + n2 + '\t' + n1 + '\n')
        elif n2 == '0':
            mfile.write('L' + str(i) + '\t' + n1 + '\t' + n2 + '\n')
        else:
            mfile.write('L' + str(i) + '\t' + n1 + '\t' + n2 + '\n')

    num = 0
    mfile.write('\n* Ports\n')
    for n in G.nodes():
        if 'label' in g.node[n]:
            if isinstance(g.node[n]['label'], mn.Terminal):
                portname = g.node[n]['label'].text
                mfile.write(portname + '\t' + str(n) + '\t' + '0' + '\n')
                num += 1

    mfile.write('.end')
    mfile.close()

    return G
