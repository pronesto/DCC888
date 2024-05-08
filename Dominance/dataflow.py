from lang import Inst
from abc import ABC, abstractmethod


class DataFlowEq(ABC):
    """
    A class that implements a data-flow equation. The key trait of a data-flow
    equation is an `eval` method, which evaluates that equation. The evaluation
    of an equation might change the environment that associates data-flow facts
    with identifiers.
    """

    def __init__(self, instruction):
        """
        Every data-flow equation is produced out of a program instruction. The
        initialization of the data-flow equation verifies if, indeed, the input
        object is an instruction.
        """
        assert isinstance(instruction, Inst)
        self.inst = instruction

    @classmethod
    @abstractmethod
    def name(self) -> str:
        """
        The name of a data-flow equation is used to retrieve the data-flow
        facts associated with that equation in the environment. For instance,
        imagine that we have an equation like this one below:

        "OUT[p] = (v, p) + (IN[p] - (v, _))"

        This equation affects OUT[p]. We store OUT[p] in a dictionary. The name
        of the equation is used as the key in this dictionary. For instance,
        the name of the equation could be 'OUT_p'.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def eval_aux(self, data_flow_env) -> set:
        """
        This method determines how each concrete equation evaluates itself.
        In a way, this design implements the 'template method' pattern. In other
        words, the DataFlowEq class implements a concrete method eval, which
        calls the abstract method eval_aux. It is the concrete implementation of
        eval_aux that determines how the environment is affected by the
        evaluation of a given equation.
        """
        raise NotImplementedError

    def eval(self, data_flow_env) -> bool:
        """
        This method implements the abstract evaluation of a data-flow equation.
        Notice that the actual semantics of this evaluation will be implemented
        by the `èval_aux` method, which is abstract.
        """
        old_env = data_flow_env[self.name()]
        data_flow_env[self.name()] = self.eval_aux(data_flow_env)
        return True if data_flow_env[self.name()] != old_env else False


class Dominance_Eq(DataFlowEq):
    """
    This concrete class implements the meet operation for the dominance
    analysis. The dominators of data-flow vertex v is the intersection of the
    dominators of the predecessors of v.
    """

    def eval_aux(self, env: dict[str, set[int]]) -> set[int]:
        """
        The evaluation of the meet operation for the dominance relation.
        Basically: D[n] = {n} U Intersection(D[p], for p in n.preds)

        Example:
            >>> Inst.next_index = 0
            >>> i0 = Add('x', 'a', 'b')
            >>> df = Dominance_Eq(i0)
            >>> sorted(df.eval_aux({}))
            [0]

            >>> Inst.next_index = 0
            >>> i0 = Add('x', 'a', 'b')
            >>> i1 = Add('y', 'x', 'a')
            >>> i2 = Add('y', 'x', 'b')
            >>> i3 = Add('z', 'x', 'y')
            >>> i0.add_next(i1)
            >>> i0.add_next(i2)
            >>> i1.add_next(i3)
            >>> i2.add_next(i3)
            >>> df = Dominance_Eq(i3)
            >>> sorted(df.eval_aux({'1': {0, 1}, '2': {0, 2}}))
            [0, 3]
        """
        # TODO: Implement this method.
        return set()

    def name(self):
        """
        The name of this dataflow equation. Ex.:
            >>> Inst.next_index = 0
            >>> add = Add('x', 'a', 'b')
            >>> eq = Dominance_Eq(add)
            >>> eq.name()
            '0'
        """
        return str(self.inst.ID)


    def __str__(self):
        """
        The name of a dominance equation is always in the format:
        D(n) = set(n) U Intersection( D(p1), D(p2), ... D(pn) )
        where each pi is a predecessor of n.

        Example:
            >>> Inst.next_index = 0
            >>> i0 = Add('w', 'a', 'b')
            >>> i1 = Add('x', 'a', 'a')
            >>> i2 = Add('y', 'b', 'b')
            >>> i3 = Add('z', 'x', 'y')
            >>> i0.add_next(i3)
            >>> i1.add_next(i3)
            >>> i2.add_next(i3)
            >>> df = Dominance_Eq(i3)
            >>> str(df)
            'D(3) = set(3) U Intersection( D(0), D(1), D(2) )'
        """
        ps = ", ".join(sorted([f"D({pred.ID})" for pred in self.inst.preds]))
        return f"D({self.name()}) = set({self.inst.ID}) U Intersection( {ps} )"


def dominance_constraint_gen(insts: list[Inst]) -> list[Dominance_Eq]:
    """
    Builds a list of equations to solve Dominance Analysis for the given set of
    instructions.

    Example:
        >>> Inst.next_index = 0
        >>> i0 = Add('w', 'a', 'b')
        >>> i1 = Add('x', 'a', 'a')
        >>> i2 = Add('y', 'b', 'b')
        >>> i3 = Add('z', 'x', 'y')
        >>> i0.add_next(i3)
        >>> i1.add_next(i3)
        >>> i2.add_next(i3)
        >>> insts = [i0, i1, i2, i3]
        >>> sol = [str(eq) for eq in dominance_constraint_gen(insts)]
        >>> sol[3]
        'D(3) = set(3) U Intersection( D(0), D(1), D(2) )'
    """
    # TODO: Implement this function.
    return []


class UniversalSet(set):
    """
    This class implements a 'set of everything'. Basically, the intersection of
    a universal set with any other set is always the other set. We use this
    set of everything to simulate the TOP of a JOIN semi-lattice. The TOP is
    the element that, once joined with any other element, will be the other
    element. We initialize the set of dominators with the TOP, for instance.
    """
    def __and__(self, other):
        """
        The AND operation of a universal set and any set is always the other
        set. Ex.:
            >>> sorted(set([1, 2, 3]) & UniversalSet())
            [1, 2, 3]
            >>> set() & UniversalSet()
            set()
        """
        return other

    def __rand__(self, other):
        """
        The AND operation of any set and a universal set is always the other
        set. Ex.:
            >>> UniversalSet() & set()
            set()
            >>> sorted(UniversalSet() & set(['a', 'b']))
            ['a', 'b']
        """
        return other


def abstract_interp(equations: list[Dominance_Eq]) -> dict[str, set[int]]:
    """
    This function iterates on the equations, solving them in the order in which
    they appear. It returns an environment with the solution to the data-flow
    analysis.

    Example for liveness analysis:
        >>> Inst.next_index = 0
        >>> i0 = Add('w', 'a', 'b')
        >>> i1 = Add('x', 'a', 'a')
        >>> i2 = Add('y', 'b', 'b')
        >>> i3 = Add('z', 'x', 'y')
        >>> i0.add_next(i3)
        >>> i1.add_next(i3)
        >>> i2.add_next(i3)
        >>> insts = [i0, i1, i2, i3]
        >>> eqs = dominance_constraint_gen(insts)
        >>> sol = abstract_interp(eqs)
        >>> f"D(0): {sorted(sol['0'])}, D(1): {sorted(sol['3'])}"
        'D(0): [0], D(1): [3]'

        >>> Inst.next_index = 0
        >>> i0 = Add('w', 'a', 'b')
        >>> i1 = Add('x', 'a', 'a')
        >>> i2 = Add('y', 'b', 'b')
        >>> i3 = Add('z', 'x', 'y')
        >>> i0.add_next(i3)
        >>> i1.add_next(i3)
        >>> i2.add_next(i3)
        >>> i0.add_next(i1)
        >>> i0.add_next(i2)
        >>> insts = [i0, i1, i2, i3]
        >>> eqs = dominance_constraint_gen(insts)
        >>> sol = abstract_interp(eqs)
        >>> f"D(0): {sorted(sol['0'])}, D(1): {sorted(sol['3'])}"
        'D(0): [0], D(1): [0, 3]'

        >>> Inst.next_index = 0
        >>> c0 = Add('c', 'zero', 'zero')
        >>> repeat = Lth('repeat', 'c', 'N')
        >>> bt = Bt('repeat')
        >>> c1 = Add('c', 'c', 'one')
        >>> answer = Add('answer', 'c', 'zero')
        >>> c0.add_next(repeat)
        >>> repeat.add_next(bt)
        >>> bt.add_next(answer)
        >>> bt.add_true_next(c1)
        >>> c1.add_next(repeat)
        >>> insts = [c0, repeat, bt, c1, answer]
        >>> eqs = dominance_constraint_gen(insts)
        >>> s = abstract_interp(eqs)
        >>> f"D(0): {sorted(s['0'])}, D(1): {sorted(s['1'])}"
        'D(0): [0], D(1): [0, 1]'
    """
    # TODO: Implement this function.
    env = {eq.name(): UniversalSet() for eq in equations}
    return env
