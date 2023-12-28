import sys
import todo

from lang import interp

if __name__ == "__main__":
    lines = sys.stdin.readlines()
    env, program = todo.file2cfg_and_env(lines)
    final_env = interp(program[0], env)
    final_env.dump()
