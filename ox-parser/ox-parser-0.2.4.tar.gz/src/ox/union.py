import sidekick as sk

SKIP = object()
opt = sk.opt


class Union(sk.Union, is_abstract=True):
    def iter_nodes(self):
        """
        Visit all elements in tree.
        """
        node_type = type(self).mro()[1]
        return iter_dfs(self, node_type)

    def transform_nodes(self, function):
        """
        Apply function to all nodes on tree.

        The function should return the transformed node or None. If it return
        None, it will remove the node from any list, tuple, set or dict
        container.
        """
        node_type = type(self).mro()[1]
        new_args = []
        changed = False

        for arg in self.args:
            if isinstance(arg, node_type):
                new = function(arg)
            elif isinstance(arg, (list, tuple, set)):
                new = transform_list(function, arg, node_type)
            elif isinstance(arg, dict):
                new = transform_dict(function, arg, node_type)
            else:
                new = arg

            new_args.append(new)
            changed = (new is not arg) or changed

        return type(self)(*new_args) if changed else self

    def filter_nodes(self, predicate):
        """
        Return all sub-nodes that obbey the predicate. If predicate is a list
        or class, filter all nodes within the given class.
        """
        if isinstance(predicate, (list, tuple)):
            classes = tuple(predicate)
            predicate = (lambda x: isinstance(x, classes))
        elif isinstance(predicate, type):
            cls = predicate
            predicate = (lambda x: isinstance(x, cls))
        return filter(predicate, self.iter_nodes())

    def visit_nodes(self, function, acc=None):
        """

        Args:
            function:
            acc:

        Returns:

        """
        node_type = type(self).mro()[1]
        acc = [] if acc is None else acc
        visit_node(self, function, acc, node_type)
        return acc


def iter_dfs(node, node_type):  # noqa: C901
    yield node

    for arg in node.args:
        # Node types
        if isinstance(arg, node_type):
            yield from iter_dfs(arg, node_type)

        # Iterate over sequences
        elif isinstance(arg, (tuple, list, set)):
            for sub_node in arg:
                if isinstance(sub_node, node_type):
                    yield from iter_dfs(sub_node, node_type)

        # Iterate over dicts
        elif isinstance(arg, dict):
            for item in arg.items():
                for sub_node in item:
                    if isinstance(sub_node, node_type):
                        yield from iter_dfs(sub_node, node_type)


def visit_node(node, func, acc, node_type):  # noqa: C901
    if func(node, acc) is False:
        return

    for arg in node.args:
        # Node types
        if isinstance(arg, node_type):
            visit_node(arg, func, acc, node_type)

        # Iterate over sequences
        elif isinstance(arg, (tuple, list, set)):
            for sub_node in arg:
                if isinstance(sub_node, node_type):
                    visit_node(sub_node, func, acc, node_type)


        # Iterate over dicts
        elif isinstance(arg, dict):
            for item in arg.items():
                for sub_node in item:
                    if isinstance(sub_node, node_type):
                        visit_node(sub_node, func, acc, node_type)


def transform_node(func, node, node_type=None):
    result = func(node)
    return result if result is not None else node


def transform_safe(func, node, node_type):
    if isinstance(node, node_type):
        result = func(node)
        if result is None:
            return SKIP
        return result
    return node


def transform_list(function, lst, node_type):
    changed = False
    new = []
    for sub in lst:
        result = transform_safe(function, sub, node_type)
        changed = (result is not sub) or changed
        if result is not SKIP:
            new.append(result)

    # Convert sets and tuples to the right value
    if changed and not isinstance(lst, list):
        return type(lst)(new)
    return new if changed else lst


def transform_dict(function, map, node_type):
    changed = False
    new = []
    for item in map.items():
        new_item = []
        inner_changed = False

        for sub in item:
            result = transform_safe(function, sub, node_type)
            inner_changed = (result is not sub) or inner_changed
            if result is SKIP:
                break
            new_item.append(result)
        else:
            new.append(tuple(new_item) if inner_changed else item)

        changed = inner_changed or changed

    return dict(new) if changed else map
