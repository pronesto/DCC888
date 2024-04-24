import sys
import parser
import alias

from lang import interp, Storage


def run_concrete_semantics(env, program):
    """
    Calls the interpreter on the input program with the given input environemnt.
    """
    storage = Storage()
    interp(program[0], env, storage)
    env.dump()
    storage.dump()


def run_abstract_semantics(program):
    """
    Runs Andersen-Style points-to analysis on the input program
    """
    abstract_env = alias.abstract_interp(program)
    if abstract_env:
        for name in sorted(abstract_env):
            print(f"{name}, {sorted(abstract_env[name])}")
    else:
        print("The program has no memory allocation.")


def check_pointers(program):
    """
    Runs Andersen-Style points-to analysis on the input program, and check the
    abstract state of six variable names: p0, p1, p2, ref_0, ref_1 and ref_2.
    This method is ony used to automatically grade the assignment.
    """
    abstract_env = alias.abstract_interp(program)
    if abstract_env:
        print(f"Alias(p0): {sorted(abstract_env.setdefault('p0', set()))}")
        print(f"Alias(p1): {sorted(abstract_env.setdefault('p1', set()))}")
        print(f"Alias(p2): {sorted(abstract_env.setdefault('p2', set()))}")
        print(f"Alias(ref0): {sorted(abstract_env.setdefault('ref_0', set()))}")
        print(f"Alias(ref1): {sorted(abstract_env.setdefault('ref_1', set()))}")
        print(f"Alias(ref2): {sorted(abstract_env.setdefault('ref_2', set()))}")
    else:
        print("The program has no memory allocation.")


if __name__ == "__main__":
    lines = sys.stdin.readlines()
    env, program = parser.file2cfg_and_env(lines)
    check_pointers(program)
