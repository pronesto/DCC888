from lang import Env, Inst, BinOp, Bt, Add, Read, Mul, Lth, Geq, Phi
from abc import ABC, abstractmethod
from functools import reduce


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
    def name(self):
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
        by the `eval_aux` method, which is abstract.
        """
        old_abs_val = data_flow_env.get(self.name(), 'UNDEF')
        data_flow_env[self.name()] = self.eval_aux(data_flow_env)
        return True if data_flow_env[self.name()] != old_abs_val else False


class ConstantPropagationEq(DataFlowEq):
    """
    These data-flow equations simply return the name of the variable they define
    as the name of the equation.
    """
    def name(self):
        """
        The name of a constant-propagation equation is always the name of the
        variable that is defined by the instruction that they encode.
        Example:
            >>> i0 = Add('x', 'ZERO', 'ONE')
            >>> df0 = AddEq(i0)
            >>> df0.name()
            'x'
        """
        if not hasattr(self.inst, "dst"):
            raise AttributeError(f"Instruction without def: {self.inst}")
        return self.inst.dst


class AddEq(ConstantPropagationEq):
    def eval_aux(self, abs_env: Env):
        """
        Example:
            >>> i0 = Add('x', 'ZERO', 'ONE')
            >>> i1 = Add('z', 'x', 'ONE')
            >>> df0 = AddEq(i0)
            >>> df1 = AddEq(i1)
            >>> abs_env = {'ZERO': 0, 'ONE': 1}
            >>> _ = df0.eval(abs_env)
            >>> _ = df1.eval(abs_env)
            >>> sorted(abs_env.items())
            [('ONE', 1), ('ZERO', 0), ('x', 1), ('z', 2)]
        """
        if abs_env[self.inst.src0] == 'NAC' or abs_env[self.inst.src1] == 'NAC':
            return 'NAC'
        return abs_env[self.inst.src0] + abs_env[self.inst.src1]


class MulEq(ConstantPropagationEq):
    def eval_aux(self, abs_env: Env):
        """
        Example:
            >>> i0 = Mul('x', 'ONE', 'ONE')
            >>> i1 = Mul('z', 'x', 'ONE')
            >>> df0 = MulEq(i0)
            >>> df1 = MulEq(i1)
            >>> abs_env = {'ONE': 1}
            >>> _ = df0.eval(abs_env)
            >>> _ = df1.eval(abs_env)
            >>> sorted(abs_env.items())
            [('ONE', 1), ('x', 1), ('z', 1)]
        """
        if abs_env[self.inst.src0] == 'NAC' or abs_env[self.inst.src1] == 'NAC':
            return 'NAC'
        return abs_env[self.inst.src0] * abs_env[self.inst.src1]


class LthEq(ConstantPropagationEq):
    def eval_aux(self, abs_env: Env):
        """
        Example:
            >>> i0 = Lth('x', 'ONE', 'ONE')
            >>> df0 = LthEq(i0)
            >>> abs_env = {'ONE': 1}
            >>> _ = df0.eval(abs_env)
            >>> sorted(abs_env.items())
            [('ONE', 1), ('x', False)]
        """
        if abs_env[self.inst.src0] == 'NAC' or abs_env[self.inst.src1] == 'NAC':
            return 'NAC'
        return abs_env[self.inst.src0] < abs_env[self.inst.src1]


class GeqEq(ConstantPropagationEq):
    def eval_aux(self, abs_env: Env):
        """
        Example:
            >>> i0 = Geq('x', 'ONE', 'ONE')
            >>> df0 = GeqEq(i0)
            >>> abs_env = {'ONE': 1}
            >>> _ = df0.eval(abs_env)
            >>> sorted(abs_env.items())
            [('ONE', 1), ('x', True)]
        """
        if abs_env[self.inst.src0] == 'NAC' or abs_env[self.inst.src1] == 'NAC':
            return 'NAC'
        return abs_env[self.inst.src0] >= abs_env[self.inst.src1]


class ReadEq(ConstantPropagationEq):
    def eval_aux(self, data_flow_env: Env):
        """
        Example:
            >>> i = Read('x')
            >>> d = ReadEq(i)
            >>> e = {}
            >>> _ = d.eval(e)
            >>> e['x']
            'NAC'
        """
        return 'NAC'


class PhiEq(ConstantPropagationEq):
    def eval_aux(self, env: Env):
        """
        Example:
            >>> Inst.next_index = 0
            >>> i = Phi('x', ['const1', 'const2'])
            >>> d = PhiEq(i)
            >>> e = {'const1': 2, 'const2': 2}
            >>> _ = d.eval(e)
            >>> sorted(e.items())
            [('const1', 2), ('const2', 2), ('x', 2)]

            >>> Inst.next_index = 0
            >>> i = Phi('x', ['const1', 'const2'])
            >>> d = PhiEq(i)
            >>> e = {'const1': 1, 'const2': 2}
            >>> _ = d.eval(e)
            >>> sorted(e.items())
            [('const1', 1), ('const2', 2), ('x', 'NAC')]
        """
        def meet(c0, c1):
            if c0 == 'NAC' or c1 == 'NAC':
                return 'NAC'
            elif c0 == 'UNDEF':
                return c1;
            elif c1 == 'UNDEF':
                return c0;
            elif c1 == c0:
                return c0
            else:
                return 'NAC'
        return reduce(lambda acc, a: meet(acc, env[a]), self.inst.args, 'UNDEF')


def constant_prop_constraint_gen(instructions: list[Inst]):
    """
    This function converts a list of instructions to a list of data-flow
    equations.

    Notice that we don't need to generate equations for branches, as these
    instructions do not define SSA-form names.
    """
    eqMap = {
        Add:    AddEq,
        Mul:    MulEq,
        Lth:    LthEq,
        Geq:    GeqEq,
        Read:   ReadEq,
        Phi:    PhiEq,
    }
    return [eqMap[type(i)](i) for i in instructions if not isinstance(i, Bt)]


def abstract_interp(eq, abs_env: Env):
    """
    This function iterates on the equations, solving them in the order in which
    they appear. It returns an environment with the solution to the data-flow
    analysis.

    Example for reaching-definition analysis:
        >>> env = {'zero': 0, 'one': 1}
        >>> i0 = Add('a0', 'one', 'zero')
        >>> i1 = Read('b0')
        >>> i2 = Mul('c0', 'a0', 'b0')
        >>> i3 = Add('a1', 'a0', 'a0')
        >>> i4 = Add('a2', 'a1', 'c0')
        >>> eqs = constant_prop_constraint_gen([i0, i1, i2, i3, i4])
        >>> sol = abstract_interp(eqs, env)
        >>> sorted(sol.items())
        [('a0', 1), ('a1', 2), ('a2', 'NAC'), ('b0', 'NAC'), ('c0', 'NAC'), ('one', 1), ('zero', 0)]

    """
    changed = True
    while changed:
        changed = reduce(lambda acc, eq: eq.eval(abs_env) or acc, eq, False)
    return abs_env
