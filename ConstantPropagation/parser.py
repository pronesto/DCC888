import json
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
    l2 = x = add x c
"""


def file2cfg_and_env(lines):
    """
    Builds a control-flow graph representation for the strings stored in
    `lines`. The first string represents the environment. The other strings
    represent instructions.
    """

    match_op = {
        "add":  Add,
        "mul":  Mul,
        "lth":  Lth,
        "geq":  Geq,
        "rd":  Read,
    }

    env = json.loads(lines[0])
    insts = []
    bt_list = []
    i = 0
    for line in lines[1:]:
        tokens = line.split()
        if tokens[0] == "bt":
            inst = Bt(tokens[1])
            bt_list.append((inst, tokens[2], i))
        else:
            op_str = tokens[2]
            if op_str == "phi":
                inst = Phi(tokens[0], tokens[3:])
            else:
                op = match_op[tokens[2]]
                inst = op(tokens[0], *tokens[3:])
        insts.append(inst)

    for bt_tuple in bt_list:
        bt = bt_tuple[0] 
        bt.add_true_next(insts[int(bt_tuple[1])])

    for i in range(len(insts)-1):
        insts[i].add_next(insts[i+1])
    return (env, insts)
