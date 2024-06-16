#!/usr/bin/env python3
import sys
import lang
import parser

if __name__ == "__main__":
    lang.Inst.next_index = 0
    lines = sys.stdin.readlines()
    env, program = parser.file2cfg_and_env(lines)
    try:
        lang.type_check(program[0], lang.TypeEnv.from_env(env))
        print("The program type checks.")
    except lang.InstTypeErr as e:
        print(e)
