import numpy as np


def chinese_whispers(weights, n_iter=10):

    n_items, _ = weights.shape

    ordered_items = np.array(range(n_items))

    # one cluster per item
    labels = np.array(range(n_items))

    for i in range(n_iter):

        n_changes = 0

        # iterate over all items in random order
        items = ordered_items.copy()
        np.random.shuffle(items)
        for item in items:

            best_cluster = labels[item]
            best_weight = -np.inf

            clusters = np.unique(labels)
            # this is to ensure that ties are not always in favor
            # the smaller cluster identifier...
            np.random.shuffle(clusters)

            for cluster in clusters:

                # compute total weight to cluster
                w = weights[item, (item != ordered_items) * (labels == cluster)]
                cluster_weight = np.sum(w)

                # keep track of best cluster
                if len(w) and cluster_weight > best_weight:
                    best_cluster = cluster
                    best_weight = cluster_weight

            # update cluster for current item
            if best_cluster != labels[item]:
                labels[item] = best_cluster
                # keep track of number of changes
                n_changes += 1

        _, labels = np.unique(labels, return_inverse=True)

        msg = 'iteration #{i} - {n_clusters} clusters - {n_changes} changes'
        print(msg.format(i=i, n_clusters=len(np.unique(labels)), n_changes=n_changes))

        if n_changes < 1:
            break

    return labels
