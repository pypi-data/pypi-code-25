from ecapy import eca

def test_eca():
    f = lambda x: abs(sum(x))
    x, fx = eca(f, 5, minimize=True)

    assert abs(fx) < 1e-8
