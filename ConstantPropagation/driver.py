#!/usr/bin/env python3
import sys
import lang
import parser
import dataflow

if __name__ == "__main__":
    lang.Inst.next_index = 0
    lines = sys.stdin.readlines()
    env, program = parser.file2cfg_and_env(lines)
    equations = dataflow.constant_prop_constraint_gen(program)
    result_env, _ = dataflow.abstract_interp(equations, env)
    print(result_env.to_dict())
