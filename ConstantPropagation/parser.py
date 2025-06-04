from lang import Env, Inst, Add, Mul, Lth, Geq, Read, Phi, Bt

"""
This file implements a parser: a function that reads a text file, and returns
a control-flow graph of instructions plus an environment mapping variables to
integer values. The text file has the following format:

    [First line] A dictionary describing the environment
    [n-th line] The n-th instruction in our program.

As an example, the program below sums up the numbers a, b and c:

    {"a": 1, "b": 3, "c": 5}
    x = add a b
    x = add x c
"""


def file2cfg_and_env(lines):
    """
    Builds a control-flow graph representation for the strings stored in
    `lines`. The first string represents the environment. The other strings
    represent instructions.
    """
    # TODO: Implement the parser.
    env = dict()
    insts = []
    return (env, insts)
