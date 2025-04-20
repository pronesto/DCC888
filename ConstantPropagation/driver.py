#!/usr/bin/env python3
import sys
import lang
import parser
import dataflow

def dump_environment(env):
    for key in sorted(env):
        print(f"{key}: {env[key]}")

def dump_program(program):
    for inst in program:
        print(inst)

if __name__ == "__main__":
    lang.Inst.next_index = 0
    lines = sys.stdin.readlines()
    env, program = parser.file2cfg_and_env(lines)
    equations = dataflow.constant_prop_constraint_gen(program)
    result_env = dataflow.abstract_interp(equations, env)
    dump_environment(env)
