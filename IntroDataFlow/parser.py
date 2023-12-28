"""
This file implements a parser: a function that reads a text file, and returns
a control-flow graph of instructions plus an environment mapping variables to
integer values.
"""

from lang import *

def line2Inst(line):
    """
    Converts a line to an instruction.

    Example:
        >>> line2Inst('count = add zero three').definition()
        {'count'}
    """
    if "add" in line:
        return line2BinOp(line, lambda dst, src0, src1: Add(dst, src0, src1))
    elif "mul" in line:
        return line2BinOp(line, lambda dst, src0, src1: Mul(dst, src0, src1))
    elif "lth" in line:
        return line2BinOp(line, lambda dst, src0, src1: Lth(dst, src0, src1))
    elif "geq" in line:
        return line2BinOp(line, lambda dst, src0, src1: Geq(dst, src0, src1))
    elif "bt" in line:
        return line2Bt(line)
    else:
        raise ValueError(f"Invalid instruction: {line}")

def line2BinOp(line, creator):
    """
    Converts a line that contains the structure 'x = op a b' to an instruction.

    Example:
        >>> i = line2BinOp('a = lth x y', lambda d, s0, s1: Lth(d, s0, s0))
        >>> i.definition()
        {'a'}
    """
    (dst, _, _, src0, src1) = line.split()
    return creator(dst, src0, src1)

def line2Bt(line):
    """
    Converts a line to a branch. This method will add a field, 'offset' to the
    branch instruction. We will need that field later on, when creating the
    control-flow graph.

    Example:
        >>> line2Bt('bt a 3').uses()
        {'a'}

        >>> line2Bt('bt a 3').offset
        3
    """
    (_, cond, offset) = line.split()
    bt = Bt(cond)
    bt.offset = int(offset)
    return bt

def line2env(line):
    """
    Maps a string (the line) to a dictionary in python.

    Example
        >>> line2env('{"zero": 0, "one": 1, "three": 3, "iter": 9}').get('one')
        1
    """
    import json
    env_dict = json.loads(line)
    env_lang = Env()
    for k, v in env_dict.items():
        env_lang.set(k, v)
    return env_lang

def file2cfg_and_env(lines):
    """
    Builds a control-flow graph representation for the strings stored in
    `lines`. The first string represents the environment. The other strings
    represent instructions.

    Example:
        >>> l0 = '{"a": 0, "b": 3}'
        >>> l1 = 'bt a 1'
        >>> l2 = 'x = add a b'
        >>> env, prog = file2cfg_and_env([l0, l1, l2])
        >>> interp(prog[0], env).get("x")
        3

        >>> l0 = '{"a": 1, "b": 3, "x": 42, "z": 0}'
        >>> l1 = 'bt a 2'
        >>> l2 = 'x = add a b'
        >>> l3 = 'x = add x z'
        >>> env, prog = file2cfg_and_env([l0, l1, l2, l3])
        >>> interp(prog[0], env).get("x")
        42

        >>> l0 = '{"a": 1, "b": 3, "c": 5}'
        >>> l1 = 'x = add a b'
        >>> l2 = 'x = add x c'
        >>> env, prog = file2cfg_and_env([l0, l1, l2])
        >>> interp(prog[0], env).get("x")
        9
    """
    env = line2env(lines[0])
    insts = [line2Inst(line) for line in lines[1:]]
    for i in range(len(insts)-1):
        insts[i].add_next(insts[i+1])
    for b in insts:
        if hasattr(b, 'offset'):
            b.nexts[0] = insts[b.offset]
    return (env, insts)
