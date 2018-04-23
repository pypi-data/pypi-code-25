from math_131_numerics import bisection_method

def test1():
    result = bisection_method(lambda x: x-2, 0, 3, 1e-5, 100)
    assert result == (2.0000038146972656, 5.7220458984375e-06, 17)
    
def test_not_print(capfd):
    result = bisection_method(lambda x: x-2, 0, 3, 1e-5, 100)
    out, err = capfd.readouterr()
    assert out == 'Convergence in 17 steps\n'
    