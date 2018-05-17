from ecapy.optimizer import eca

def test_eca():
    f = lambda x, d: abs(sum(x[:d]))
    x, fx = eca(f, 10, minimize=True)

    assert abs(fx) < 1e-8
