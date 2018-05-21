import numpy as np
from scipy.sparse import lil_matrix


def simulated_parameters(m=2,
                         n=10,
                         o=0.5,
                         degs=[2],
                         dist=np.random.normal,
                         dist_par=(0.0, 1.0 / np.sqrt(m * n))):

    mn = m * n
    mm = m * np.arange(n)

    degs = degs[degs <= n]

    degs1 = degs[degs > 0]
    degs2 = degs[degs > 1]

    max_deg = np.max(degs)

    m_idx = {deg: {} for deg in degs}
    q = {deg: 0 for deg in degs}
    q[0] = 1

    for deg in degs1:

        # base mn number with deg digits
        idx = np.zeros(deg, dtype=int)

        for _ in range(mn**deg):

            var = [j / m for j in idx]
            state = [j % m for j in idx]
            same_var = len(set(var)) == 1
            diff_var = len(set(var)) == deg
            same_state = len(set(state)) == 1
            nondecreasing = np.all(np.diff(idx) >= 0)
            increasing = np.all(np.diff(idx) > 0)

            # if (diff_var or (same_var and same_state)) and nondecreasing:
            if diff_var and increasing:

                # top dict
                d = m_idx[deg]
                for j, k in enumerate(idx):
                    try:
                        # descend into dict
                        d = d[k]
                    except:
                        if j == deg - 1:
                            # if at leaf, store flat index
                            d[k] = q[deg]
                        else:
                            # add new layer and descend
                            d[k] = {}
                            d = d[k]
                q[deg] += 1

            # increment multiindex
            j = deg - 1
            idx[j] += 1
            while idx[j] == mn:
                j -= 1
                idx[j] += 1
            idx[j + 1:] = 0

    # number of model parameters
    par = mn * np.sum(q.values())

    # number of observations
    l = int(o * par)

    # model parameters
    f = {deg: dist(*dist_par, size=(mn, q[deg])) for deg in degs}
    for deg in degs:
        f[deg] = np.vstack([fi - fi.mean(0) for fi in np.split(f[deg], n)])
    for deg in degs1:
        f[deg] -= f[deg].mean(1)[:, np.newaxis]

    return f
