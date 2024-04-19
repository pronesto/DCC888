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

if __name__ == "__main__":
    lines = sys.stdin.readlines()
    env, program = parser.file2cfg_and_env(lines)
    run_abstract_semantics(program)
