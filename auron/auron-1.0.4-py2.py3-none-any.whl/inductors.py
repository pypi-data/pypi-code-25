import networkx as nx

from auron import tools
from auron import filters

from yuna import masternodes as mn


def _device(g, n):
    if 'device' in g.node[n]:
        if tools.is_master(g.node[n]['device']):
            return True
    return False


def _label(g, n):
    if 'label' in g.node[n]:
        if tools.is_master(g.node[n]['label']):
            return True
    return False


class ConductingPath:
    """  """

    def __init__(self, g):
        self.g = g
        self.ix = []

        for n in g.nodes():
            if _device(self.g, n) or _label(self.g, n):
                self.ix.append(n)

        self.subgraph_branches = []

    def add_path_to_branch(self, path):
        ix = True

        """ Test if path contains masternodes. """
        for n in path[1:-1]:
            if _device(self.g, n) or _label(self.g, n):
                ix = False

        """ Test if path already exists. """
        be = [path[0], path[-1]]
        for bp in self.subgraph_branches:
            if set(be).issubset(bp):
                ix = False

        if len(path) == 2:
            self.subgraph_branches.append(path)
        if ix is True:
            self.subgraph_branches.append(path)

    def ground_master(self):
        for n in self.g.nodes():
            self.subgraph_branches.append([n])

    def branch_master(self):
        """ Get the branches between masternodes without
        any other masternodes inbetween. """

        for source in self.ix:
            targets = filter(lambda x: x not in [source], self.ix)

            for target in targets:
                for path in nx.all_shortest_paths(self.g, source=source, target=target):
                    if (path[0] in self.ix) or (path[-1] in self.ix):
                        self.add_path_to_branch(path)


class Branch(object):
    _ID = 0

    def __init__(self, path):
        self.path = path

        self.id = 'b{}'.format(Branch._ID)
        Branch._ID += 1

    def update_nodes(self, g):
        """
        All nodes in a specific conducting branch is labeled
        with a the BranchNode object.

        Parameters
        ----------
        g : NetworkX graph object
            Graph nodes are updated with labels
        branches : dict()
            {i: []} - Dictionary containing the branch key and
            a list of the nodes present in the branch.
        """

        for n in self.path:
            if 'label' in g.node[n]:
                if tools.is_master(g.node[n]['label']) is False:
                    poly = g.node[n]['poly']
                    g.node[n]['label'] = mn.Remove(poly.text,
                                                   poly.position,
                                                   poly.layer,
                                                   id0=Branch._ID)
        return g


def branches(g, gds):
    """ Branch must have atleast 2 masternodes, otherwise just save
    the masternode, master = get_master_nodes(sg) """

    sub_graphs = nx.connected_component_subgraphs(g, copy=True)

    for sg in sub_graphs:
        cpaths = ConductingPath(sg)

        if len(cpaths.ix) > 1:
            cpaths.branch_master()
        elif len(cpaths.ix) == 1:
            cpaths.ground_master()

        if cpaths.subgraph_branches is not None:
            for path in cpaths.subgraph_branches:
                branch = Branch(path)
                g = branch.update_nodes(g)

    return g

