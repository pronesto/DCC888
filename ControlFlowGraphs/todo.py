from lang import *

def test_min(m, n):
    """
    Stores in the variable 'answer' the minimum of 'm' and 'n'

    Examples:
        >>> test_min(3, 4)
        3

        >>> test_min(4, 3)
        3
    """
    env = Env({"m": m, "n": n, "x": m, "zero": 0})
    m_min = Add("answer", "m", "zero")
    n_min = Add("answer", "n", "zero")
    p = Lth("p", "n", "m")
    b = Bt("p", n_min, m_min)
    p.add_next(b)
    interp(p, env)
    return env.get("answer")

def test_min3(x, y, z):
    """
    Stores in the variable 'answer' the minimum of 'x', 'y' and 'z'

    Examples:
        >>> test_min3(3, 4, 5)
        3

        >>> test_min3(5, 4, 3)
        3
    """
    # TODO: Implement this method
    return env.get("answer")

def test_div(m, n):
    """
    Stores in the variable 'answer' the integer division of 'm' and 'n'.

    Examples:
        >>> test_div(30, 4)
        7

        >>> test_div(4, 3)
        1

        >>> test_div(1, 3)
        0
    """
    # TODO: Implement this method
    return env.get("answer")

def test_fact(n):
    """
    Stores in the variable 'answer' the factorial of 'n'.

    Examples:
        >>> test_fact(3)
        6
    """
    # TODO: Implement this method
    return env.get("answer")
