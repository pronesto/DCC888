from lang import Env, Inst, BinOp, Bt
from abc import ABC, abstractmethod


class DataFlowEq(ABC):
    """
    A class that implements a data-flow equation. The key trait of a data-flow
    equation is an `eval` method, which evaluates that equation. The evaluation
    of an equation might change the environment that associates data-flow facts
    with identifiers.

    Attributes:
        num_evals the number of times that constraints have been evaluated.
            Remember to zero this attribute once you start a new static
            analysis, so that you can correctly count how many times each
            equation had to be evaluated to solve the analysis.
    """

    num_evals = 0

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
    def deps(self) -> list:
        """
        A list with the name of all the constraints that this equation depends
        upon. For instance, if the equation is like:

        "OUT[p] = (v, p) + (IN[p] - (v, _))"

        Then, self.deps() == ['IN_p']
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
        DataFlowEq.num_evals += 1
        old_env = data_flow_env[self.name()]
        data_flow_env[self.name()] = self.eval_aux(data_flow_env)
        return True if data_flow_env[self.name()] != old_env else False


def name_in(ID):
    """
    The name of an IN set is always ID + _IN. Eg.:
        >>> Inst.next_index = 0
        >>> add = Add('x', 'a', 'b')
        >>> name_in(add.ID)
        'IN_0'
    """
    return f"IN_{ID}"


class IN_Eq(DataFlowEq):
    """
    This abstract class represents all the equations that affect the IN set
    related to some program point.
    """

    def name(self):
        return name_in(self.inst.ID)


def name_out(ID):
    """
    The name of an OUT set is always ID + _OUT. Eg.:
        >>> Inst.next_index = 0
        >>> add = Add('x', 'a', 'b')
        >>> name_out(add.ID)
        'OUT_0'
    """
    return f"OUT_{ID}"


class OUT_Eq(DataFlowEq):
    """
    This abstract class represents all the equations that affect the OUT set
    related to some program point.
    """

    def name(self):
        return name_out(self.inst.ID)


class ReachingDefs_Bin_OUT_Eq(OUT_Eq):
    """
    This concrete class implements the equations that affect OUT facts of the
    reaching-definitions analysis for binary instructions. These instructions
    have three fields: dst, src0 and src1; however, only the former is of
    interest for these equations.
    """

    def eval_aux(self, data_flow_env):
        """
        Evaluates this equation, where:
        OUT[p] = (v, p) + (IN[p] - (v, _))

        Example:
            >>> Inst.next_index = 0
            >>> i0 = Add('x', 'a', 'b')
            >>> df = ReachingDefs_Bin_OUT_Eq(i0)
            >>> sorted(df.eval_aux({'IN_0': {('x', 1), ('y', 2)}}))
            [('x', 0), ('y', 2)]
        """
        in_set = data_flow_env[name_in(self.inst.ID)]
        new_set = {(v, p) for (v, p) in in_set if v != self.inst.dst}
        return new_set.union([(self.inst.dst, self.inst.ID)])

    def deps(self):
        """
        The list of dependencies of this equation. Ex.:
            >>> Inst.next_index = 0
            >>> add = Add('x', 'a', 'b')
            >>> df = ReachingDefs_Bin_OUT_Eq(add)
            >>> df.deps()
            ['IN_0']
        """
        return [name_in(self.inst.ID)]

    def __str__(self):
        """
        A string representation of a reaching-defs equation representing
        a binary instruction. Eg.:
            >>> Inst.next_index = 0
            >>> add = Add('x', 'a', 'b')
            >>> df = ReachingDefs_Bin_OUT_Eq(add)
            >>> str(df)
            'OUT_0: (x, 0) + (IN_0 - (x, _))'
        """
        kill_set = f" + ({name_in(self.inst.ID)} - ({self.inst.dst}, _))"
        gen_set = f"({self.inst.dst}, {self.inst.ID})"
        return f"{self.name()}: {gen_set}{kill_set}"


class ReachingDefs_Bt_OUT_Eq(OUT_Eq):
    """
    This concrete class implements the equations that affect OUT facts of the
    reaching-definitions analysis for branch instructions. These instructions
    do not affect reaching definitions at all. Therefore, their equations are
    mostly treated as identity functions.
    """

    def eval_aux(self, data_flow_env):
        """
        Evaluates this equation. Notice that the reaching definition equation
        for a branch instruction is simply the identity function.
        OUT[p] = IN[p]

        Example:
            >>> Inst.next_index = 0
            >>> i0 = Bt('x')
            >>> df = ReachingDefs_Bt_OUT_Eq(i0)
            >>> sorted(df.eval_aux({'IN_0': {('x', 1), ('y', 2)}}))
            [('x', 1), ('y', 2)]
        """
        return data_flow_env[name_in(self.inst.ID)]

    def deps(self):
        """
        The list of dependencies of this equation. Ex.:
            >>> Inst.next_index = 0
            >>> i = Bt('x')
            >>> df = ReachingDefs_Bt_OUT_Eq(i)
            >>> df.deps()
            ['IN_0']
        """
        return [name_in(self.inst.ID)]

    def __str__(self):
        """
        A string representation of a reaching-defs equation representing a
        branch. Eg.:
            >>> Inst.next_index = 0
            >>> i = Bt('x')
            >>> df = ReachingDefs_Bt_OUT_Eq(i)
            >>> str(df)
            'OUT_0: IN_0'
        """
        kill_set = f"{name_in(self.inst.ID)}"
        gen_set = f""
        return f"{self.name()}: {gen_set}{kill_set}"


class ReachingDefs_IN_Eq(IN_Eq):
    """
    This concrete class implements the meet operation for reaching-definition
    analysis. The meet operation produces the IN set of a program point. This
    IN set is the union of the OUT set of the predecessors of this point.
    """

    def eval_aux(self, data_flow_env):
        """
        The evaluation of the meet operation over reaching definitions is the
        union of the OUT sets of the predecessors of the instruction.

        Example:
            >>> Inst.next_index = 0
            >>> i0 = Add('x', 'a', 'b')
            >>> i1 = Add('x', 'c', 'd')
            >>> i2 = Add('y', 'x', 'x')
            >>> i0.add_next(i2)
            >>> i1.add_next(i2)
            >>> df = ReachingDefs_IN_Eq(i2)
            >>> sorted(df.eval_aux({'OUT_0': {('x', 0)}, 'OUT_1': {('x', 1)}}))
            [('x', 0), ('x', 1)]
        """
        solution = set()
        for inst in self.inst.preds:
            solution = solution.union(data_flow_env[name_out(inst.ID)])
        return solution

    def deps(self) -> list[str]:
        """
        The list of dependencies of this equation. Ex.:
            >>> Inst.next_index = 0
            >>> i0 = Add('x', 'a', 'b')
            >>> i1 = Add('x', 'c', 'd')
            >>> i2 = Add('y', 'x', 'x')
            >>> i0.add_next(i2)
            >>> i1.add_next(i2)
            >>> df = ReachingDefs_IN_Eq(i2)
            >>> sorted(df.deps())
            ['OUT_0', 'OUT_1']
        """
        # TODO: Implement this method
        return []

    def __str__(self):
        """
        The name of an IN set is always ID + _IN.

        Example:
            >>> Inst.next_index = 0
            >>> i0 = Add('x', 'a', 'b')
            >>> i1 = Add('x', 'c', 'd')
            >>> i2 = Add('y', 'x', 'x')
            >>> i0.add_next(i2)
            >>> i1.add_next(i2)
            >>> df = ReachingDefs_IN_Eq(i2)
            >>> str(df)
            'IN_2: Union( OUT_0, OUT_1 )'
        """
        succs = ", ".join([name_out(pred.ID) for pred in self.inst.preds])
        return f"{self.name()}: Union( {succs} )"


def reaching_defs_constraint_gen(insts):
    """
    Builds a list of equations to solve Reaching-Definition Analysis for the
    given set of instructions.

    Example:
        >>> Inst.next_index = 0
        >>> i0 = Add('c', 'a', 'b')
        >>> i1 = Mul('d', 'c', 'a')
        >>> i2 = Lth('e', 'c', 'd')
        >>> i0.add_next(i2)
        >>> i1.add_next(i2)
        >>> insts = [i0, i1, i2]
        >>> sol = [str(eq) for eq in reaching_defs_constraint_gen(insts)]
        >>> sol[0] + " " + sol[-1]
        'OUT_0: (c, 0) + (IN_0 - (c, _)) IN_2: Union( OUT_0, OUT_1 )'
    """
    in0 = [ReachingDefs_Bin_OUT_Eq(i) for i in insts if isinstance(i, BinOp)]
    in1 = [ReachingDefs_Bt_OUT_Eq(i) for i in insts if isinstance(i, Bt)]
    out = [ReachingDefs_IN_Eq(i) for i in insts]
    return in0 + in1 + out


def abstract_interp(equations):
    """
    This function iterates on the equations, solving them in the order in which
    they appear. It returns an environment with the solution to the data-flow
    analysis.

    Example for reaching-definition analysis:
        >>> Inst.next_index = 0
        >>> i0 = Add('c', 'a', 'b')
        >>> i1 = Mul('d', 'c', 'a')
        >>> i0.add_next(i1)
        >>> eqs = reaching_defs_constraint_gen([i0, i1])
        >>> (sol, num_evals) = abstract_interp(eqs)
        >>> f"OUT_0: {sorted(sol['OUT_0'])}, Num Evals: {num_evals}"
        "OUT_0: [('c', 0)], Num Evals: 12"
    """
    from functools import reduce

    DataFlowEq.num_evals = 0
    env = {eq.name(): set() for eq in equations}
    changed = True
    while changed:
        changed = reduce(lambda acc, eq: eq.eval(env) or acc, equations, False)
    return (env, DataFlowEq.num_evals)


def build_dependence_graph(equations) -> dict[str, list[DataFlowEq]]:
    """
    This function builds the dependence graph of equations.

    Example:
        >>> Inst.next_index = 0
        >>> i0 = Add('c', 'a', 'b')
        >>> i1 = Mul('d', 'c', 'a')
        >>> i0.add_next(i1)
        >>> eqs = reaching_defs_constraint_gen([i0, i1])
        >>> deps = build_dependence_graph(eqs)
        >>> [eq.name() for eq in deps['IN_0']]
        ['OUT_0']
    """
    # TODO: implement this method
    dep_graph = {eq.name(): [] for eq in equations}
    return dep_graph


def abstract_interp_worklist(equations) -> tuple[Env, int]:
    """
    This function solves the system of equations using a worklist. Once an
    equation E is evaluated, and the evaluation changes the environment, only
    the dependencies of E are pushed onto the worklist.

    Example for reaching-definition analysis:
        >>> Inst.next_index = 0
        >>> i0 = Add('c', 'a', 'b')
        >>> i1 = Mul('d', 'c', 'a')
        >>> i0.add_next(i1)
        >>> eqs = reaching_defs_constraint_gen([i0, i1])
        >>> (sol, num_evals) = abstract_interp_worklist(eqs)
        >>> f"OUT_0: {sorted(sol['OUT_0'])}"
        "OUT_0: [('c', 0)]"
    """
    # TODO: implement this method
    from collections import defaultdict

    DataFlowEq.num_evals = 0
    env = defaultdict(list)
    return (env, DataFlowEq.num_evals)
