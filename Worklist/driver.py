import sys
import lang
import parser
import dataflow

from lang import interp


def chaotic_solver(program):
    equations = dataflow.reaching_defs_constraint_gen(program)
    return dataflow.abstract_interp(equations)


def worklist_solver(program):
    equations = dataflow.reaching_defs_constraint_gen(program)
    return dataflow.abstract_interp(equations)


if __name__ == "__main__":
    """
    This function reads a program, and solves reaching definition analysis
    for it, using either chaotic iterations or the worklist-based algorithm.
    """
    lang.Inst.next_index = 0
    lines = sys.stdin.readlines()
    env, program = parser.file2cfg_and_env(lines)
    (env_chaotic, n_chaotic) = chaotic_solver(program)
    (env_worklist, n_worklist) = worklist_solver(program)
    print(f"Are the environments the same? {env_chaotic == env_worklist}")
    print(f"Used less than {n_chaotic} iterations? {n_worklist <= n_chaotic}")
