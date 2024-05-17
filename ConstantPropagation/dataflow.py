from lang import Env, Inst, BinOp, Bt, Add, Read, Mul, Lth, Geq, Phi
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


class SparseConstantPropagationEq(DataFlowEq):
    """
    When dealing with SSA-Form programs a classical data-flow analysis is
    somewhat cumbersome. Since every variable is associated with a single
    information during their whole lifetime, the analysis state can be shared
    across all program points. Thus, each instruction contributes to this state
    by defining the state of their own involved variable.

    This class implements the sparse analysis for Constant
    Propagation. Since we assume an input program is in SSA Form, 
    there is no further need for IN and OUT sets for each instruction.
    Instead, each variable is associated with one state by the end of the
    Analysis.
    """

    def eval_aux(self, data_flow_env: Env):
        """
        The evaluation of the meet operation over constant propagation follows
        the lattice:
                Not-a-constant (NAC)
              /   /   /  | \  \  \ 
            ... -c2 -c1 c0 c1 c2 ... 
              \   \   \  | /  /  /  
                Undefined (UNDEF)

        Whereby variables start UNDEF untill value assignment, operations with
        constants do not move them up the lattice and operations with NACs turn
        them into NACs as well.

        """
        raise NotImplementedError

    def eval(self, data_flow_env: Env) -> bool:
        """
        This method implements the abstract evaluation of a data-flow equation.
        Notice that the actual semantics of this evaluation will be implemented
        by the `eval_aux` method, which is abstract.
        """
        DataFlowEq.num_evals += 1
        old_env = data_flow_env.to_dict()
        self.eval_aux(data_flow_env)
        if data_flow_env.to_dict() != old_env:
            # debugging
            # set1 = set(old_env.items())
            # set2 = set(data_flow_env.to_dict().items())
            # print(set1 ^ set2)
            return True
        else:
            return False

    def deps(self):
        return {}

    def name(self):
        return '' 


class BranchEq(SparseConstantPropagationEq):
    def eval_aux(self, data_flow_env: Env):
        return


class BinOpEq(SparseConstantPropagationEq):
    def eval_aux(self, data_flow_env: Env):
        """
        Example:
            >>> Inst.next_index = 0
            >>> i0 = Add('x', 'x', 'ONE')
            >>> i1 = Add('z', 'ONE', 'ONE')
            >>> i2 = Mul('a', 'z', 'y')
            >>> i3 = Lth('b', 'z', 'x')

            >>> i0.add_next(i1)
            >>> i1.add_next(i2)
            >>> i2.add_next(i3)

            >>> df0 = BinOpEq(i0)
            >>> df1 = BinOpEq(i1)
            >>> df2 = BinOpEq(i2)
            >>> df3 = BinOpEq(i3)

            >>> env = Env({'ZERO': 0, 'ONE': 1, 'x': 5, 'y': 'NAC'})
            >>> _ = df0.eval(env)
            >>> _ = df1.eval(env)
            >>> _ = df2.eval(env)
            >>> _ = df3.eval(env)
            >>> sorted(env.to_dict().items())
            [('ONE', 1), ('ZERO', 0), ('a', 'NAC'), ('b', 1), ('x', 6), ('y', 'NAC'), ('z', 2)]
        """
        # TODO
        pass


class ReadEq(SparseConstantPropagationEq):
    def eval_aux(self, data_flow_env: Env):
        """
        Example:
            >>> Inst.next_index = 0
            >>> i0 = Add('x', 'ZERO', 'ZERO')
            >>> i1 = Read('y')
            >>> i2 = Add('z', 'x', 'y')

            >>> i0.add_next(i1)
            >>> i1.add_next(i2)

            >>> df = ReadEq(i1)
            >>> env = Env({'ZERO': 0, 'x': 0})
            >>> df.eval_aux(env)
            >>> sorted(env.to_dict().items())
            [('ZERO', 0), ('x', 0), ('y', 'NAC')]
        """
        # TODO
        pass


class PhiEq(SparseConstantPropagationEq):
    def eval_aux(self, data_flow_env: Env):
        """
        Example:
            >>> Inst.next_index = 0
            >>> i0 = Phi('x', 'const1', 'const2')
            >>> i1 = Phi('y', 'const1', 'notconst')
            >>> i2 = Phi('z', 'const1', 'const3')

            >>> df0 = PhiEq(i0)
            >>> df1 = PhiEq(i1)
            >>> df2 = PhiEq(i2)
            >>> env = Env({'const1': 0, 'const2': 0, 'const3': 1, 'notconst': 'NAC'})
            >>> _ = df0.eval(env)
            >>> _ = df1.eval(env)
            >>> _ = df2.eval(env)
            >>> sorted(env.to_dict().items())
            [('const1', 0), ('const2', 0), ('const3', 1), ('notconst', 'NAC'), ('x', 0), ('y', 'NAC'), ('z', 'NAC')]
        """
        # TODO
        pass


def constant_prop_constraint_gen(instructions: list[Inst]):
    equationMap = {
        Add:    BinOpEq,
        Mul:    BinOpEq,
        Lth:    BinOpEq,
        Geq:    BinOpEq,
        Bt:     BranchEq,
        Read:   ReadEq,
        Phi:    PhiEq,
    }
 
    equations = []
    for i in instructions:
        equations.append(equationMap[type(i)](i))
    return equations


def abstract_interp(equations, program_env: Env):
    """
    This function iterates on the equations, solving them in the order in which
    they appear. It returns an environment with the solution to the data-flow
    analysis.

    Example for reaching-definition analysis:
        >>> Inst.next_index = 0
        >>> env = Env({'zero': 0, 'one': 1})
        >>> i0 = Add('a0', 'one', 'zero')
        >>> i1 = Read('b0')
        >>> i2 = Mul('c0', 'a0', 'b0')
        >>> i3 = Add('a1', 'a0', 'a0')
        >>> i4 = Add('a2', 'a1', 'c0')
        >>> i0.add_next(i1)
        >>> i1.add_next(i2)
        >>> i2.add_next(i3)
        >>> i3.add_next(i4)
        >>> eqs = constant_prop_constraint_gen([i0, i1, i2, i3, i4])
        >>> (sol, num_evals) = abstract_interp(eqs, env)
        >>> sorted(sol.to_dict().items())
        [('a0', 1), ('a1', 2), ('a2', 'NAC'), ('b0', 'NAC'), ('c0', 'NAC'), ('one', 1), ('zero', 0)]

    """
    from functools import reduce

    copy_env = Env(program_env.to_dict())
    DataFlowEq.num_evals = 0
    changed = True
    while changed:
        changed = reduce(lambda acc, eq: eq.eval(copy_env) or acc, equations, False)
    return (copy_env, DataFlowEq.num_evals)
