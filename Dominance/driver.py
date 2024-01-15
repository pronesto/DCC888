import sys
import lang
import parser
import dataflow

from lang import interp


def print_instructions(instructions):
    for inst in instructions:
        print(inst)


if __name__ == "__main__":
    """
    If you want to see the program, you can use the function call
    `print_instructions(program)`
        >>> l0 = '{"a": 1, "b": 3, "x": 42, "z": 0}'
        >>> l1 = 'bt a 2'
        >>> l2 = 'x = add a b'
        >>> l3 = 'x = add x z'
        >>> _, program = file2cfg_and_env([l0, l1, l2, l3])
        >>> print_instructions(program)
    """
    lang.Inst.next_index = 0
    lines = sys.stdin.readlines()
    env, program = parser.file2cfg_and_env(lines)
    equations = dataflow.dominance_constraint_gen(program)
    dom_tree = dataflow.abstract_interp(equations)
    for ID in sorted(dom_tree):
        print(f"D({ID}): {sorted(dom_tree[str(ID)])}")
