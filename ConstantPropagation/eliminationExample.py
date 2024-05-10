import parser
import lang
import codeElimination
import dataflow

with open('tests/fib.txt', 'r') as f:
    lines = f.readlines()

env, prog = parser.file2cfg_and_env(lines)
newprog, newenv = codeElimination.eliminate_constant_assignments(prog,
                                                                 env)

result = lang.interp(prog[0], env)
newresult = lang.interp(newprog[0], newenv)

print(f'Original prog size: {len(prog)}')
print(f'New prog size: {len(newprog)}')
print('equal results?')
print(result.to_dict() == newresult.to_dict())
