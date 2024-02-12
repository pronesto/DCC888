from lang import *


def print_instructions(instructions):
    for inst in instructions:
        print(inst)


def test_min(m, n):
    """
    Stores in the variable 'answer' the minimum of 'm' and 'n'

    Examples:
        >>> test_min(3, 4)
        3

        >>> test_min(4, 3)
        3
    """
    env = Env({"m": m, "n": n, "x0": m, "zero": 0})
    p = Lth("p", "n", "x0")
    x1 = Add("x1", "n", "zero")
    answer = Phi("answer", ["x0", "x1"])
    b = Bt("p", x1, answer)
    p.add_next(b)
    x1.add_next(answer)
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
    env = Env({"min0": x, "y": y, "z": z, "zero": 0})
    p0 = Lth("p0", "y", "min0")
    min1 = Add("min1", "y", "zero")
    min2 = Phi("min2", ["min1", "min0"])
    p1 = Lth("p1", "z", "min2")
    min3 = Add("min3", "z", "zero")
    answer = Phi("answer", ["min3", "min2"])
    b0 = Bt("p0", min1, min2)
    p0.add_next(b0)
    min1.add_next(min2)
    min2.add_next(p1)
    b1 = Bt("p1", min3, answer)
    p1.add_next(b1)
    min3.add_next(answer)
    interp(p0, env)
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
    env = Env({"d0": 0, "m0": m, "one": 1, "n": n, "minus_n": -n, "zero": 0})
    d1 = Phi("d1", ["d0", "d2"])
    m1 = Phi("m1", ["m0", "m2"])
    p = Geq("p", "m1", "n")
    m2 = Add("m2", "m1", "minus_n")
    d2 = Add("d2", "d1", "one")
    answer = Add("answer", "d1", "zero")
    b = Bt("p", m2, answer)
    d1.add_next(m1)
    m1.add_next(p)
    p.add_next(b)
    m2.add_next(d2)
    d2.add_next(d1)
    interp(d1, env)
    return env.get("answer")


def test_fact(n):
    """
    Stores in the variable 'answer' the factorial of 'n'.

    Examples:
        >>> test_fact(3)
        6
    """
    env = Env({"two": 2, "n0": n, "f0": 1, "m_one": -1, "zero": 0})
    n1 = Phi("n1", ["n0", "n2"])
    f1 = Phi("f1", ["f0", "f2"])
    p = Geq("p", "n1", "two")
    f2 = Mul("f2", "f1", "n1")
    n2 = Add("n2", "n1", "m_one")
    answer = Add("answer", "f1", "zero")
    b = Bt("p", f2, answer)
    n1.add_next(f1)
    f1.add_next(p)
    p.add_next(b)
    f2.add_next(n2)
    n2.add_next(n1)
    interp(n1, env)
    return env.get("answer")


def test_fib(n):
    """
    Stores in the variable 'answer' the n-th number of the Fibonacci sequence,
    considering that the sequence is 0, 1, 1, 2, 3, 5, ...

    Examples:
        >>> test_fib(2)
        1
        >>> test_fib(3)
        2
        >>> test_fib(6)
        8
    """
    env = Env({"N": n, "zero": 0, "one": 1})
    a = Phi("a", ["zero", "b"])
    b = Phi("b", ["one", "sum"])
    c1 = Phi("c1", ["zero", "c2"])
    p = Lth("p", "c1", "N")
    answer = Add("answer", "a", "zero")
    sum_ = Add("sum", "a", "b")
    c2 = Add("c2", "c1", "one")
    b_aux = Add("b_aux", "b", "zero")
    branch = Bt("p", sum_, answer)
    a.add_next(b)
    b.add_next(c1)
    c1.add_next(p)
    p.add_next(branch)
    sum_.add_next(c2)
    c2.add_next(b_aux)
    b_aux.add_next(a)
    interp(a, env)
    return env.get("answer")


def test_fib_swap_problem(n):
    """
    This implementation of the Fibonacci Sequence illustrates the so-called
    swap problem. If we do not evaluate the phi-functions in blocks, then we
    might get wrong results.

    Examples:
        >>> test_fib_swap_problem(2)
        4
        >>> test_fib_swap_problem(3)
        8
        >>> test_fib_swap_problem(6)
        64
    """
    env = Env({"N": n, "zero": 0, "one": 1})
    b = Phi("b", ["one", "sum"])
    a = Phi("a", ["zero", "b"])
    c1 = Phi("c1", ["zero", "c2"])
    p = Lth("p", "c1", "N")
    answer = Add("answer", "a", "zero")
    sum_ = Add("sum", "a", "b")
    c2 = Add("c2", "c1", "one")
    branch = Bt("p", sum_, answer)
    b.add_next(a)
    a.add_next(c1)
    c1.add_next(p)
    p.add_next(branch)
    sum_.add_next(c2)
    c2.add_next(b)
    interp(b, env)
    return env.get("answer")


def test_fib_swap_problem_fixed_with_phi_blocks(n):
    """
    This implementation of the Fibonacci Sequence illustrates the so-called
    swap problem. If we do not evaluate the phi-functions in blocks, then we
    might get wrong results.

    Examples:
        >>> test_fib_swap_problem_fixed_with_phi_blocks(2)
        1
        >>> test_fib_swap_problem_fixed_with_phi_blocks(3)
        2
        >>> test_fib_swap_problem_fixed_with_phi_blocks(6)
        8
    """
    env = Env({"N": n, "zero": 0, "one": 1})
    b = Phi("b", ["one", "sum"])
    a = Phi("a", ["zero", "b"])
    c1 = Phi("c1", ["zero", "c2"])
    p = Lth("p", "c1", "N")
    answer = Add("answer", "a", "zero")
    sum_ = Add("sum", "a", "b")
    c2 = Add("c2", "c1", "one")
    branch = Bt("p", sum_, answer)
    phi_block = PhiBlock([b, a, c1], [0, c2.ID])
    phi_block.add_next(p)
    p.add_next(branch)
    sum_.add_next(c2)
    c2.add_next(phi_block)
    interp(phi_block, env)
    return env.get("answer")
