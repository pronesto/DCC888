"""
This file implements a parser: a function that reads a text file, and returns
a control-flow graph of instructions plus an environment mapping variables to
integer values.
"""

import re
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
    elif "move" in line:
        return line2MoveOp(line, lambda dst, src: Move(dst, src))
    elif "load" in line:
        return line2MoveOp(line, lambda dst, src: Load(dst, src))
    elif store := parse_store(line):
        return store
    elif load := parse_load(line):
        return load
    elif "alloca" in line:
        return line2Alloca(line, lambda dst: Alloca(dst))
    else:
        raise ValueError(f"Invalid instruction: {line}")


def parse_load(line):
    """
    Converts a line that contains the structure '*p = s' into a store.

    Example:
        >>> load = parse_load('d = *p')
        >>> f"{load.dst} = memory[{load.ref}]"
        'd = memory[p]'

        >>> load = parse_load('d = *   p')
        >>> f"{load.dst} = memory[{load.ref}]"
        'd = memory[p]'
    """
    pattern = r"([a-zA-Z][a-zA-Z0-9]*)\s*=\s*\*\s*([a-zA-Z][a-zA-Z0-9]*)"
    match = re.search(pattern, line)
    return Load(match.group(1), match.group(2)) if match else None


def parse_store(line):
    """
    Converts a line that contains the structure '*p = s' into a store.

    Example:
        >>> store = parse_store('*p = s')
        >>> f"memory[{store.ref}] = {store.src}"
        'memory[p] = s'

        >>> store = parse_store(' *  p = s')
        >>> f"memory[{store.ref}] = {store.src}"
        'memory[p] = s'
    """
    pattern = r"\s*\*\s*([a-zA-Z][a-zA-Z0-9]*)\s*=\s*([a-zA-Z][a-zA-Z0-9]*)"
    match = re.search(pattern, line)
    return Store(match.group(1), match.group(2)) if match else None


def line2MoveOp(line, creator):
    """
    Converts a line that contains the structure 'd = op s' to an instruction.

    Example:
        >>> i = line2MoveOp('a = move x', lambda d, s: Move(d, s))
        >>> i.definition()
        {'a'}

        >>> i = line2MoveOp('a = load x', lambda d, s: Load(d, s))
        >>> i.definition()
        {'a'}
    """
    (dst, _, _, src) = line.split()
    return creator(dst, src)


def line2Alloca(line, creator):
    """
    Converts a line that contains the structure 'alloca d' to an instruction.

    Example:
    """
    (dst, _, _) = line.split()
    return creator(dst)


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
        >>> interp(prog[0], env, None).get("x")
        3

        >>> l0 = '{"a": 1, "b": 3, "x": 42, "z": 0}'
        >>> l1 = 'bt a 2'
        >>> l2 = 'x = add a b'
        >>> l3 = 'x = add x z'
        >>> env, prog = file2cfg_and_env([l0, l1, l2, l3])
        >>> interp(prog[0], env, None).get("x")
        42

        >>> l0 = '{"a": 1, "b": 3, "c": 5}'
        >>> l1 = 'x = add a b'
        >>> l2 = 'x = add x c'
        >>> env, prog = file2cfg_and_env([l0, l1, l2])
        >>> interp(prog[0], env, None).get("x")
        9

        >>> l0 = '{"a": 1}'
        >>> l1 = 'b = move a'
        >>> env, prog = file2cfg_and_env([l0, l1])
        >>> interp(prog[0], env, None).get("b")
        1
    """
    env = line2env(lines[0])
    insts = [line2Inst(line) for line in lines[1:]]
    for i in range(len(insts) - 1):
        insts[i].add_next(insts[i + 1])
    for b in insts:
        if hasattr(b, "offset"):
            b.add_true_next(insts[b.offset])
    return (env, insts)
