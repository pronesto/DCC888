from lang import Inst, Add, Mul, Lth, Geq, Bt, Phi, Env
from dataflow import abstract_interp, liveness_constraint_gen
from collections import defaultdict


class InterferenceGraph:
    def __init__(s, program: list[Inst]):
        liveness = abstract_interp(liveness_constraint_gen(program))
        s.graph = defaultdict(lambda: set())
        s.mcsgraph = defaultdict(lambda: set())
        s.weights = dict()
        s.maxweight = 0
        # build intersection graph
        for values in liveness.values():
            for var in values:
                s.graph[var] |= set(values) - set([var])
                s.mcsgraph[var] |= set(values) - set([var])
        for var in s.graph.keys():
            s.weights[var] = 0
        # Sort graph vertices (variables) according to weight
        s.weightedVs = sorted(s.weights.keys(), key=lambda x: s.weights[x])

    def N(s, v: str) -> set[str]:
        return s.graph[v]

    def size(s):
        return len(s.mcsgraph)

    def greedy_coloring(s, sequence: list[str]) -> tuple[dict[str, int], int]:
        # TODO: implement this method

    def maximum_cardinality_search(s):
        # TODO: implement this method


def register_allocation(prog: list[Inst]):
    """
    TODO: add descricao de phi aqui
        >>> prog, env = new_euclid()
        >>> coloring, num_registers = register_allocation(prog)
        >>> num_registers
        5
    """
    iGraph = InterferenceGraph(prog)
    return iGraph.greedy_coloring(iGraph.maximum_cardinality_search())
