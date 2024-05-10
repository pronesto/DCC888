from dataflow import abstract_interp, constant_prop_constraint_gen
from lang import Env, Inst, Add, Mul, Lth, Geq, Phi, Bt
from copy import deepcopy


def relink(removed_instruction: Inst):
    preds = removed_instruction.preds
    nexts = removed_instruction.nexts
    for pred in preds:
        pred.nexts.remove(removed_instruction)
        for nxt in nexts:
            nxt.preds.remove(removed_instruction)
            if type(pred) is Bt:
                if removed_instruction == pred.nexts[0]:
                    pred.add_true_next(nxt)
            else:
                pred.add_next(nxt)



def constant_to_env(instructions: list[Inst],
                    constant_env: Env) -> (list[Inst], dict):
    if len(instructions) == 1:
        return instructions, dict()

    head = instructions[0]
    patch = dict()
    program_head = [head]

    if type(head) is not Bt:
        definition = head.definition().pop()
        value = constant_env.get(definition)
        if type(value) is int:
            patch = {definition: value}
            program_head = []
            relink(head)

    program, patches = constant_to_env(instructions[1:], constant_env)
    return program_head + program, patch | patches

def eliminate_constant_assignments(instructions: list[Inst], program_env: Env) -> (list[Inst], Env):
    constant_prop = constant_prop_constraint_gen(instructions)
    constant_env, _ = abstract_interp(constant_prop, program_env)
    new_program, env_patches = constant_to_env(deepcopy(instructions),
                                               constant_env)

    new_env = program_env.to_dict()
    new_env.update(env_patches)
    return new_program, Env(new_env)
