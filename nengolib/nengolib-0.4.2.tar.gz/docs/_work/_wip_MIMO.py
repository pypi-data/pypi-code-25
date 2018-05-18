def _normalize(nums, den):
    # Normalize all numerator rows against same denominator
    r_nums, r_den = np.empty_like(nums), None
    for i in range(len(nums)):
        r_nums[i], new_den = scipy.signal.normalize(nums[i], den)
        if r_den is None:
            r_den = new_den
        assert np.allclose(r_den, new_den)
    return r_nums, r_den


def _ss2tf(A, B, C, D):
    nums = []
    den = None
    for i in range(len(B)):
        #print i
        num, new_den = scipy.signal.ss2tf(A, B, C, D, input=i)
        nums.append(num)
        if den is None:
            den = new_den
        #print den, new_den
        assert np.allclose(den, new_den)
    #print nums
    #raise
    return np.asarray(nums), den


def _tf2ss(nums, den):
    #_normalize
    size_out, size_in = nums.shape[:2]
    order = len(den) - 1
    #print size_out, size_in, order
    init = False
    A = np.empty((order, order))
    B = np.zeros((order, size_in))
    C = np.zeros((size_out, order))
    D = np.empty((size_out, size_in))
    for i in range(size_out):
        for j in range(size_in):
            #print nums[i, j], den
            a, b, c, d = scipy.signal.tf2ss(nums[i, j], den)
            if not init:
                init = True
                A[...] = a
                #B[...] = b
                #C[i, ]
                D[i, j] = d
            else:
                assert np.allclose(A, a)
                #assert np.allclose(B, b)
            #print a, b, c, d
            # this isn't going to work!! knowing den is the same doesn't help us. need to create larger system and then do balanced reduction
            B[:, j] += b[:, 0]
            C[i, :] += c[0, :]
    return (A, B, C, D)

A = [[1, 0], [0, 1]]
B = [[1, 2], [2, 4]]
C = [[1, -1], [-1, 1]]
D = [[0, 1], [0, 1]]

tf = _ss2tf(A, B, C, D)
print tf
ss = _tf2ss(*tf)
print _ss2tf(*ss)
