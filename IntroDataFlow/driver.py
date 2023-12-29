import sys
import lang
import parser
import dataflow

from lang import interp


def check_environment(env, init_in):
    """
    This function is an example of how liveness analysis can be used.
    It checks if the program contains any use of a variable that is not
    defined before. This very function is used, for instance, to prevent the
    compilation of invalid Java programs, or to issue warnings whenever a
    variable is used without being initialized in C.

    Parameters:
    -----------
        env: The initial environment.
        init_in: the IN set of the first instruction. If this IN set contains
            any variable V, then V must be defined in `env`; otherwise, the
            program might be considered wrong.
    """
    print(f"Initial live set: {sorted(init_in)}")
    for var in init_in:
        try:
            env.get(var)
        except LookupError:
            print(f"{var} is used without being defined")


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
    equations = dataflow.liveness_constraint_gen(program)
    df_env = dataflow.abstract_interp(equations)
    init_in = df_env[dataflow.name_in(program[0].ID)]
    check_environment(env, init_in)
