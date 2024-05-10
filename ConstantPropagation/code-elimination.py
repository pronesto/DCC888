from dataflow import abstract_interp, constant_prop_constraint_gen
from lang import Env, Inst, Add, Mul, Lth, Geq, Phi

def constant_to_env(instructions: list[Inst],
                    constant_env: Env) -> (list[Inst], dict):
    if len(instructions) == 0:
        return [], dict()

    head = instructions[0]
    definition = head.definition().pop()
    value = constant_env.get(definition)
    if type(value) is int:
        patch = {definition:  value}
        program_head = []
    else:
        patch = dict()
        program_head = [head]

    program, patches = constant_to_env(instructions[1:], constant_env)
    return program_head + program, patch.update(patches)

def eliminate_constant_assignments(instructions: list[Inst], program_env: Env) -> (list[Inst], Env):
    constant_prop = constant_prop_constraint_gen(instructions)
    constant_env = abstract_interp(constant_prop, program_env)
    new_program, env_patches = constant_to_env(instructions,
                                               constant_env)

    new_env = program_env.to_dict()
    new_env.update(env_patches)
    return [] + constant_to_env(instructions[0], constant_env), Env(new_env)
