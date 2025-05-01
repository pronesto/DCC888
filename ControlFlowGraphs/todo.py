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


def test_fib(n):
    """
    Stores in the variable 'answer' the n-th number of the Fibonacci sequence.

    Examples:
        >>> test_fib(2)
        2
        >>> test_fib(3)
        3
        >>> test_fib(6)
        13
    """
    env = Env({"c": 0, "N": n, "fib0": 0, "fib1": 1, "zero": 0, "one": 1})
    i0 = Lth("p", "c", "N")
    i2 = Add("aux", "fib1", "zero")
    i3 = Add("fib1", "aux", "fib0")
    i4 = Add("fib0", "aux", "zero")
    i5 = Add("c", "c", "one")
    i6 = Add("answer", "fib1", "zero")
    i1 = Bt("p", i2, i6)
    i0.add_next(i1)
    i2.add_next(i3)
    i3.add_next(i4)
    i4.add_next(i5)
    i5.add_next(i0)
    interp(i0, env)
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
    env = Env({"x": x, "y": y, "z": z, "zero": 0})

    # Compare x and y
    x_min = Add("answer", "x", "zero")  # x is min
    y_min = Add("answer", "y", "zero")  # y is min

    xy_min = Lth("xy_min", "y", "x")  # true if y is min
    bt_xy = Bt("xy_min", y_min, x_min)  # go to y if it is min
    xy_min.add_next(bt_xy)

    # comparing xy_min and z
    z_min = Add("answer", "z", "zero")

    xyz_min = Lth("xyz_min", "z", "answer")  # true if z min
    bt_xyz = Bt("xyz_min", z_min, None)
    xyz_min.add_next(bt_xyz)

    # connect x and y
    x_min.add_next(xyz_min)
    y_min.add_next(xyz_min)

    interp(xy_min, env)
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
    env = Env(
        {
            "m": m,
            "n": n,  # keep original positive n for comparison
            "neg_n": -n,  # use for subtracting
            "one": 1,
            "count": 0,
            "zero": 0,
        }
    )

    # Set answer = count when done
    done = Add("answer", "count", "zero")

    # m = m - n; count += 1
    step1 = Add("m", "m", "neg_n")
    step2 = Add("count", "count", "one")
    step1.add_next(step2)

    # Condition: m >= n
    cond = Geq("cond", "m", "n")
    step2.add_next(cond)

    # Branch: loop if m >= n, else done
    branch = Bt("cond", step1, done)
    cond.add_next(branch)

    interp(cond, env)

    return env.get("answer")


def test_fact(n):
    """
    Stores in the variable 'answer' the factorial of 'n'.

    Examples:
        >>> test_fact(3)
        6
    """
    # TODO: Implement this method
    env = Env({"n": n, "one": 1, "count": 1, "i": 1, "zero": 0})

    # Set answer when done
    done = Add("answer", "i", "zero")

    # i = i * count; count += 1
    step1 = Mul("i", "i", "count")
    step2 = Add("count", "count", "one")
    step1.add_next(step2)

    # Condition
    cond = Geq("cond", "n", "count")
    step2.add_next(cond)

    # Branch
    branch = Bt("cond", step1, done)
    cond.add_next(branch)

    interp(cond, env)

    return env.get("answer")
