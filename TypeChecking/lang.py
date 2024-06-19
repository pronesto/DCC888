"""
This file contains the implementation of a simple interpreter of low-level
instructions. The interpreter takes a program, represented as its first
instruction, plus an environment, which is a stack of bindings. Bindings are
pairs of variable names and values. New bindings are added to the stack
whenever new variables are defined. Bindings are never removed from the stack.
In this way, we can inspect the history of state transformations caused by the
interpretation of a program.

In contrast to the other files of same name in previous labs, this file contains
special code to implement a simple type-checking enginee. You must fill up the
missing parts of this type checking engine.

This file uses doctests all over. To test it, just run python 3 as follows:
"python3 -m doctest main.py". The program uses syntax that is excluive of
Python 3. It will not work with standard Python 2.
"""

from collections import deque
from abc import ABC, abstractmethod
from enum import Enum


class LangType(Enum):
    NUM = 1
    BOOL = 2


class Env:
    """
    A table that associates variables with values. The environment is
    implemented as a stack, so that previous bindings of a variable V remain
    available in the environment if V is overassigned.

    Example:
        >>> e = Env()
        >>> e.set("a", 2)
        >>> e.set("a", 3)
        >>> e.get("a")
        3

        >>> e = Env({"b": 5})
        >>> e.set("a", 2)
        >>> e.get("a") + e.get("b")
        7
    """

    def __init__(s, initial_args={}):
        s.env = deque()
        for var, value in initial_args.items():
            s.env.appendleft((var, value))

    def get(self, var):
        """
        Finds the first occurrence of variable 'var' in the environment stack,
        and returns the value associated with it.
        """
        val = next((value for (e_var, value) in self.env if e_var == var), None)
        if val is not None:
            return val
        else:
            raise LookupError(f"Absent key {var}")

    def get_from_list(self, vars):
        """
        Finds the first occurrence of any variable 'vr' in the list 'vars' that
        has a binding in the environment, and returns the associated value.

        Example:
            >>> e = Env()
            >>> e.set("b", 1)
            >>> e.set("a", 2)
            >>> e.set("b", 3)
            >>> e.get_from_list(["b", "a"])
            3

            >>> e = Env()
            >>> e.set("b", 1)
            >>> e.set("a", 2)
            >>> e.set("b", 3)
            >>> e.set("a", 4)
            >>> e.get_from_list(["b", "a"])
            4
        """
        # TODO: Implement this method
        raise NotImplementedError

    def set(s, var, value):
        """
        This method adds 'var' to the environment, by placing the binding
        '(var, value)' onto the top of the environment stack.
        """
        s.env.appendleft((var, value))

    def dump(s):
        """
        Prints the contents of the environment. This method is mostly used for
        debugging purposes.
        """
        for var, value in s.env:
            print(f"{var}: {value}")

    def to_dict(s):
        d = dict()
        for var, value in reversed(s.env):
            d[var] = value
        return d


class TypeEnvErr(Exception):
    pass


class TypeEnv(Env):
    @classmethod
    def from_env(cls, env: Env):
        d = env.to_dict()
        type_d = dict()
        for k, v in d.items():
            t = type(v)
            if t is int:
                type_d[k] = LangType.NUM
            elif t is bool:
                type_d[k] = LangType.BOOL
            else:
                raise TypeEnvErr
        return TypeEnv(type_d)

    def set(s, var, value: LangType):
        """
        This method wraps the inherited set(var, value) method, making
        sure only LangType values are accepted.
        """
        if type(value) is not LangType:
            raise TypeEnvErr
        else:
            s.env.appendleft((var, value))


class Inst(ABC):
    """
    The representation of instructions. All that an instruction has, that is
    common among all the instructions, is the next_inst attribute. This
    attribute determines the next instruction that will be fetched after this
    instruction runs. Also, every instruction has an index, which is always
    different. The index is incremented whenever a new instruction is created.
    """

    next_index = 0

    def __init__(self):
        self.nexts = []
        self.preds = []
        self.ID = Inst.next_index
        Inst.next_index += 1

    def add_next(self, next_inst):
        self.nexts.append(next_inst)
        next_inst.preds.append(self)

    @classmethod
    @abstractmethod
    def definition(self):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def uses(self):
        raise NotImplementedError

    def get_next(self):
        if len(self.nexts) > 0:
            return self.nexts[0]
        else:
            return None


class InstTypeErr(Exception):
    def __init__(s, inst: Inst, expected: LangType, found: LangType):
        s.inst = inst
        s.expected = expected
        s.found = found
        message = (
            f"Type error in instruction {inst.ID}\n"
            f"Expected: {expected}, found: {found}"
        )
        super().__init__(message)


class Phi(Inst):
    """
    A Phi-Function is an abstract notation used to facilitate the implementation
    of static analyses. They were not really conceived to have a dynamic
    semantics. Nevertheless, we can still interpret programs containing
    phi-functions. A possible semantics of 'a = phi(a0, a1, a2)' is to
    recover, from the environment, the first binding of either a0, a1 or a2.
    If our program were in the so-called "Conventional-SSA Form", this
    semantics would be perfect. But our program is not in such a format, and
    we might have issues with swaps, for instance. That's why we shall use
    phi-blocks to implement phi-functions. All the same, you can still write
    programs using phi-functions without using phi-blocks, as long as variables
    that are related by phi-functions do not have overlapping live ranges.

    Example:
        >>> a = Phi("a", "b0", "b1", "b2")
        >>> e = Env()
        >>> e.set("b0", 1)
        >>> e.set("b1", 3)
        >>> a.eval(e)
        >>> e.get("a")
        3

        >>> a = Phi("a", "b0", "b1")
        >>> e = Env()
        >>> e.set("b1", 3)
        >>> e.set("b0", 1)
        >>> a.eval(e)
        >>> e.get("a")
        1
    """

    def __init__(s, dst, *args):
        s.dst = dst
        s.args = list(args)
        super().__init__()

    def definition(s):
        return set([s.dst])

    def uses(s):
        return s.args

    def eval(s, env):
        """
        If the program were in Conventional-SSA form, then we could correctly
        implement the semantics of phi-functions simply retrieving the first
        occurrence of each variable in the list of uses. However, notice what
        would happen with swaps:

        >>> a0 = Phi("a0", "a1", "a0")
        >>> a1 = Phi("a1", "a0", "a1")
        >>> e = Env()
        >>> e.set("a0", 1)
        >>> e.set("a1", 3)
        >>> a0.eval(e)
        >>> a1.eval(e)
        >>> e.get("a0") - e.get("a1")
        0

        In the example above, we would like to evaluate the two phi-functions in
        parallel, e.g.: (a0, a1) = (a0:1, a1:3). In this way, after the
        evaluation, we would like to have a0 == 3 and a1 == 1. However, there is
        no way we can do it: our phi-functions are evaluated once at a time! The
        problem is that variables a0 and a1 are defined by different
        phi-functions, but they have overlapping live ranges. So, this
        program is not in conventional SSA-form (as per Definition 1 in the
        paper 'SSA Elimination after Register Allocation' - 2009).
        """
        env.set(s.dst, env.get_from_list(s.uses()))

    def type_eval(s, type_env):
        """
        Assume that our language does not allow for type changes in variables.
        Thus, all arguments in a Phi-Function must belong to the same type.
        Example:

            >>> Inst.next_index = 0
            >>> i0 = Phi("a", "b0", "b1")
            >>> e = TypeEnv()
            >>> e.set("b0", LangType.NUM)
            >>> e.set("b1", LangType.BOOL)
            >>> i0.type_eval(e)
            Traceback (most recent call last):
             ...
            lang.InstTypeErr: Type error in instruction 0
            Expected: LangType.NUM, found: LangType.BOOL
        """
        # TODO: implement this method
        raise NotImplementedError

    def __str__(self):
        use_list = ", ".join(self.uses())
        inst_s = f"{self.ID}: {self.dst} = phi[{use_list}]"
        pred_s = f"\n  P: {', '.join([str(inst.ID) for inst in self.preds])}"
        next_s = f"\n  N: {self.nexts[0].ID if len(self.nexts) > 0 else ''}"
        return inst_s + pred_s + next_s


class ReadNum(Inst):
    """
    The ReadNum instruction introduces non-constant values to the program.
    This blocking instruction requests a numerical input from the user.
    """

    def __init__(s, dst):
        s.dst = dst
        super().__init__()

    def definition(s):
        return {s.dst}

    def uses(s):
        return set()

    def eval(s, env):
        """
        For simplicity, ReadNum fails with any value other than ints
        """
        input_value = input(f"value for {s.dst}: ")
        if type(input_value) is not int:
            raise InstTypeErr(s, int, type(input_value))
        env.set(s.dst, int(input_value))

    def type_eval(s, type_env):
        type_env.set(s.dst, LangType.NUM)

    def __str__(self):
        inst_s = f"{self.ID}: {self.dst} = INPUT"
        pred_s = f"\n  P: {', '.join([str(inst.ID) for inst in self.preds])}"
        next_s = f"\n  N: {self.nexts[0].ID if len(self.nexts) > 0 else ''}"
        return inst_s + pred_s + next_s


class ReadBool(Inst):
    """
    The ReadNum instruction introduces non-constant values to the program.
    This blocking instruction requests a numerical input from the user.
    """

    def __init__(s, dst):
        s.dst = dst
        super().__init__()

    def definition(s):
        return {s.dst}

    def uses(s):
        return set()

    def eval(s, env):
        """
        For simplicity, ReadBool fails with any value other than bool
        """
        input_value = input(f"value for {s.dst}: ")
        if type(input_value) is not bool:
            raise InstTypeErr(s, bool, type(input_value))
        env.set(s.dst, int(input_value))

    def type_eval(s, type_env):
        type_env.set(s.dst, LangType.BOOL)

    def __str__(self):
        inst_s = f"{self.ID}: {self.dst} = INPUT"
        pred_s = f"\n  P: {', '.join([str(inst.ID) for inst in self.preds])}"
        next_s = f"\n  N: {self.nexts[0].ID if len(self.nexts) > 0 else ''}"
        return inst_s + pred_s + next_s


class PhiBlock(Inst):
    """
    PhiBlocks implement a correct semantics for groups of phi-functions. A
    phi-block groups a number of phi-functions as a matrix. Once a phi-block
    is evaluated, all the values in a given column of this matrix are read and
    saved, and then the definitions are updated --- all in parallel. To see a
    more detailed explanation of this semantics, please, refer to Section 3 of
    the paper 'SSA Elimination after Register Allocation'. In particular, take
    a look into Figure 1 of that paper.

    Example:
        >>> a0 = Phi("a0", "a0", "a1")
        >>> a1 = Phi("a1", "a1", "a0")
        >>> aa = PhiBlock([a0, a1], [10, 31])
        >>> e = Env()
        >>> e.set("a0", 1)
        >>> e.set("a1", 3)
        >>> aa.eval(e, 10)
        >>> e.get("a0") - e.get("a1")
        -2

        >>> a0 = Phi("a0", "a0", "a1")
        >>> a1 = Phi("a1", "a1", "a0")
        >>> aa = PhiBlock([a0, a1], [10, 31])
        >>> e = Env()
        >>> e.set("a0", 1)
        >>> e.set("a1", 3)
        >>> aa.eval(e, 31)
        >>> e.get("a0") - e.get("a1")
        2
    """

    def __init__(self, phis, selector_IDs):
        """
        A phi-block represents an M*N matrix, where each one of the M lines is
        a phi-function, and each phi-function reads from N different parameters.
        Each one of these N columns is associated with a 'selector', which is
        the ID of the instruction that leads to that parallel assignment.

        Examples:
            >>> a0 = Phi("a0", ["a0", "a1"])
            >>> a1 = Phi("a1", ["a1", "a0"])
            >>> aa = PhiBlock([a0, a1], [10, 31])
            >>> sorted(aa.selectors.items())
            [(10, 0), (31, 1)]

            >>> a0 = Phi("a0", ["a0", "a1"])
            >>> a1 = Phi("a1", ["a1", "a0"])
            >>> aa = PhiBlock([a0, a1], [10, 31])
            >>> sorted([phi.definition().pop() for phi in aa.phis])
            ['a0', 'a1']
        """
        self.phis = phis
        # TODO: implement the rest of this method
        # here...
        #########################################
        super().__init__()

    def definition(self):
        """
        We consider that a phi-block defines multiple variables. These are the
        variables assignment by the phi-functions that the phi-block contains.

        Example:
            >>> a0 = Phi("a0", ["a0", "a1"])
            >>> a1 = Phi("a1", ["a1", "a0"])
            >>> aa = PhiBlock([a0, a1], [10, 31])
            >>> sorted(aa.definition())
            ['a0', 'a1']
        """
        return [phi.definition().pop() for phi in self.phis]

    def uses(self):
        """
        The uses of a phi-block are all the variables used by the phi-functions
        that it contains. Notice that we don't need this method for anything; it
        is here rather to help understand the structure of phi-blocks.

        Example:
            >>> a0 = Phi("a0", "a0", "x")
            >>> a1 = Phi("a1", "y", "a0")
            >>> aa = PhiBlock([a0, a1], [10, 31])
            >>> sorted(aa.uses())
            ['a0', 'a0', 'x', 'y']
        """
        return sum([phi.uses() for phi in self.phis], [])

    def eval(self, env: Env, PC: int):
        # TODO: Read all the definitions
        # TODO: Assign all the uses:
        raise NotImplementedError

    def type_eval(s, type_env):
        """
        To type check a block of phi-functions, just type check each phi
        function individually. Notice that the phi-functions within a phi
        block don't need to have the same types.

        Example:
            >>> Inst.next_index = 0
            >>> a0 = Phi("a0", "a0", "a1")
            >>> a1 = Phi("a1", "a1", "a0")
            >>> aa = PhiBlock([a0, a1], [10, 31])
            >>> e = TypeEnv({"a0": LangType.NUM, "a1": LangType.BOOL})
            >>> aa.type_eval(e)
            Traceback (most recent call last):
             ...
            lang.InstTypeErr: Type error in instruction 0
            Expected: LangType.NUM, found: LangType.BOOL

            >>> Inst.next_index = 0
            >>> a = Phi("a0", "a1", "a2")
            >>> b = Phi("b0", "b1", "b2")
            >>> aa = PhiBlock([a, b], [10, 31])
            >>> e = TypeEnv({"a1": LangType.NUM, "b1": LangType.BOOL})
            >>> aa.type_eval(e)
        """
        for phi in s.phis:
            phi.type_eval(type_env)

    def __str__(self):
        block_str = "\n".join([str(phi) for phi in self.phis])
        return f"PHI_BLOCK [\n{block_str}\n]"


class BinOp(Inst):
    """
    The general class of binary instructions. These instructions define a
    value, and use two values. As such, it contains a routine to extract the
    defined value, and the list of used values.
    """

    def __init__(s, dst, src0, src1):
        s.dst = dst
        s.src0 = src0
        s.src1 = src1
        super().__init__()

    @classmethod
    @abstractmethod
    def get_opcode(self):
        raise NotImplementedError

    def definition(s):
        return set([s.dst])

    def uses(s):
        return set([s.src0, s.src1])

    def __str__(self):
        op = self.get_opcode()
        inst_s = f"{self.ID}: {self.dst} = {self.src0}{op}{self.src1}"
        pred_s = f"\n  P: {', '.join([str(inst.ID) for inst in self.preds])}"
        next_s = f"\n  N: {self.nexts[0].ID if len(self.nexts) > 0 else ''}"
        return inst_s + pred_s + next_s


class Add(BinOp):
    """
    Example:
        >>> a = Add("a", "b0", "b1")
        >>> e = Env({"b0":2, "b1":3})
        >>> a.eval(e)
        >>> e.get("a")
        5

        >>> a = Add("a", "b0", "b1")
        >>> a.get_next() == None
        True
    """

    def eval(self, env):
        env.set(self.dst, env.get(self.src0) + env.get(self.src1))

    def type_eval(s, type_env):
        """
        Additions will always require and result in a numerical value:
            >>> Inst.next_index = 0
            >>> a = Add("a", "b0", "b1")
            >>> e = TypeEnv({"b0": LangType.NUM, "b1": LangType.BOOL})
            >>> a.type_eval(e)
            Traceback (most recent call last):
             ...
            lang.InstTypeErr: Type error in instruction 0
            Expected: LangType.NUM, found: LangType.BOOL

            >>> a = Add("a", "b0", "b1")
            >>> e = TypeEnv({"b0": LangType.NUM, "b1": LangType.NUM})
            >>> a.type_eval(e)
            >>> print(e.get("a"))
            LangType.NUM
        """
        # TODO: implement this method
        raise NotImplementedError

    def get_opcode(self):
        return "+"


class Mul(BinOp):
    """
    Example:
        >>> a = Mul("a", "b0", "b1")
        >>> e = Env({"b0":2, "b1":3})
        >>> a.eval(e)
        >>> e.get("a")
        6
    """

    def eval(s, env):
        env.set(s.dst, env.get(s.src0) * env.get(s.src1))

    def type_eval(s, type_env):
        """
        Multiplications will always require and result in a numerical value:
            >>> Inst.next_index = 0
            >>> a = Mul("a", "b0", "b1")
            >>> e = TypeEnv({"b0": LangType.NUM, "b1": LangType.BOOL})
            >>> a.type_eval(e)
            Traceback (most recent call last):
             ...
            lang.InstTypeErr: Type error in instruction 0
            Expected: LangType.NUM, found: LangType.BOOL

            >>> a = Mul("a", "b0", "b1")
            >>> e = TypeEnv({"b0": LangType.NUM, "b1": LangType.NUM})
            >>> a.type_eval(e)
            >>> print(e.get("a"))
            LangType.NUM
        """
        # TODO: implement this method
        raise NotImplementedError

    def get_opcode(self):
        return "*"


class Lth(BinOp):
    """
    Example:
        >>> a = Lth("a", "b0", "b1")
        >>> e = Env({"b0":2, "b1":3})
        >>> a.eval(e)
        >>> e.get("a")
        True
    """

    def eval(s, env):
        env.set(s.dst, env.get(s.src0) < env.get(s.src1))

    def type_eval(s, type_env):
        """
        Comparisons will always require numerical values and output booleans:
            >>> Inst.next_index = 0
            >>> a = Lth("a", "b0", "b1")
            >>> e = TypeEnv({"b0": LangType.NUM, "b1": LangType.BOOL})
            >>> a.type_eval(e)
            Traceback (most recent call last):
             ...
            lang.InstTypeErr: Type error in instruction 0
            Expected: LangType.NUM, found: LangType.BOOL

            >>> a = Lth("a", "b0", "b1")
            >>> e = TypeEnv({"b0": LangType.NUM, "b1": LangType.NUM})
            >>> a.type_eval(e)
            >>> print(e.get("a"))
            LangType.BOOL
        """
        # TODO: implement this method
        raise NotImplementedError

    def get_opcode(self):
        return "<"


class Geq(BinOp):
    """
    Example:
        >>> a = Geq("a", "b0", "b1")
        >>> e = Env({"b0":2, "b1":3})
        >>> a.eval(e)
        >>> e.get("a")
        False
    """

    def eval(s, env):
        env.set(s.dst, env.get(s.src0) >= env.get(s.src1))

    def type_eval(s, type_env):
        """
        Comparisons will always require numerical values and output booleans:
            >>> Inst.next_index = 0
            >>> a = Geq("a", "b0", "b1")
            >>> e = TypeEnv({"b0": LangType.NUM, "b1": LangType.BOOL})
            >>> a.type_eval(e)
            Traceback (most recent call last):
             ...
            lang.InstTypeErr: Type error in instruction 0
            Expected: LangType.NUM, found: LangType.BOOL

            >>> a = Geq("a", "b0", "b1")
            >>> e = TypeEnv({"b0": LangType.NUM, "b1": LangType.NUM})
            >>> a.type_eval(e)
            >>> print(e.get("a"))
            LangType.BOOL
        """
        # TODO: implement this method
        raise NotImplementedError

    def get_opcode(self):
        return ">="


class Bt(Inst):
    """
    This is a Branch-If-True instruction, which diverts the control flow to the
    'true_dst' if the predicate 'pred' is true, and to the 'false_dst'
    otherwise.

    Example:
        >>> e = Env({"t": True, "x": 0})
        >>> a = Add("x", "x", "x")
        >>> m = Mul("x", "x", "x")
        >>> b = Bt("t", a, m)
        >>> b.eval(e)
        >>> b.get_next() == a
        True
    """

    def __init__(s, cond, true_dst=None, false_dst=None):
        super().__init__()
        s.cond = cond
        s.nexts = [true_dst, false_dst]
        s.next_iter = 1  # By default, perform no jump
        if true_dst != None:
            true_dst.preds.append(s)
        if false_dst != None:
            false_dst.preds.append(s)

    def definition(s):
        return set()

    def uses(s):
        return set([s.cond])

    def add_true_next(s, true_dst):
        s.nexts[0] = true_dst
        true_dst.preds.append(s)

    def add_next(s, false_dst):
        s.nexts[1] = false_dst
        false_dst.preds.append(s)

    def eval(s, env):
        """
        The evaluation of the condition sets the next_iter to the instruction.
        This value determines which successor instruction is to be evaluated.
        Any values greater than 0 are evaluated as True, while 0 corresponds to
        False.
        """
        if env.get(s.cond):
            s.next_iter = 0
        else:
            s.next_iter = 1

    def type_eval(s, type_env):
        """
        Branch instructions require boolean conditions:
            >>> Inst.next_index = 0
            >>> a = Add("x", "x", "x")
            >>> m = Mul("x", "x", "x")
            >>> b = Bt("t", a, m)
            >>> e = TypeEnv({"t": LangType.NUM})
            >>> b.type_eval(e)
            Traceback (most recent call last):
             ...
            lang.InstTypeErr: Type error in instruction 2
            Expected: LangType.BOOL, found: LangType.NUM
        """
        # TODO: implement this method
        raise NotImplementedError

    def get_next(s):
        return s.nexts[s.next_iter]

    def __str__(self):
        inst_s = f"{self.ID}: bt {self.cond}"
        pred_s = f"\n  P: {', '.join([str(inst.ID) for inst in self.preds])}"
        next_s = f"\n  NT:{self.nexts[0].ID} NF:{self.nexts[1].ID}"
        return inst_s + pred_s + next_s


def interp(instruction: Inst, environment: Env, PC=0):
    """
    This function evaluates a program until there is no more instructions to
    evaluate. Notice that, in contrast to the previous labs, the interpreter
    now receives three arguments. The third argument is necessary to implement
    the correct semantics of phi-functions using phi-blocks. This argument can
    be used to select the correct parallel copy that a PhiBlock implements.

    Parameters:
    -----------
        instruction: the instruction that will be interpreted
        environment: the list that associates variable names with their values
        PC: the identifier of the last instruction that was interpreted.

    Example:
        >>> env = Env({"m": 3, "n": 2, "zero": 0})
        >>> m_min = Add("answer", "m", "zero")
        >>> n_min = Add("answer", "n", "zero")
        >>> p = Lth("p", "n", "m")
        >>> b = Bt("p", n_min, m_min)
        >>> p.add_next(b)
        >>> interp(p, env).get("answer")
        2
    """
    if instruction:
        if isinstance(instruction, PhiBlock):
            instruction.eval(environment, PC)
        else:
            instruction.eval(environment)
        return interp(instruction.get_next(), environment, instruction.ID)
    else:
        return environment


def type_check(inst: Inst, tp_env: TypeEnv, phi_queue: list[Inst] = []):
    """
    This function runs a simple type checking engine on the program that is
    headed by instruction `inst`. Types are stored in the type environment
    `tp_env`. The function type checks the program in two phases. Normal
    instructions are checked right away. Phi-functions are checked into two
    moments. They are checked once, the first time they are met, in order to
    determine their types. Then, afterwards, they are checked again, to ensure
    that all the parameters have the same type. To perform this two-phase
    approach, this function uses a queue of phi-functions.
    """
    if inst:
        if isinstance(inst, PhiBlock) or isinstance(inst, Phi):
            phi_queue.append(inst)
        inst.type_eval(tp_env)
        type_check(inst.get_next(), tp_env)
    else:
        for phi in phi_queue:
            phi.type_eval(tp_env)
