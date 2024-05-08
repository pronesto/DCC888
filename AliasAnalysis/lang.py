"""
This file contains the implementation of a simple interpreter of low-level
instructions. The interpreter contains instructions to manipulate a language
with variables and memory references.

This file uses doctests all over. To test it, just run python 3 as follows:
"python3 -m doctest main.py". The program uses syntax that is excluive of
Python 3. It will not work with standard Python 2.
"""

from collections import deque
from abc import ABC, abstractmethod


class Storage:
    """
    This class simulates a memory environment. It is a set of memory locations.
    The memory locations are named with a counter that determines the order
    when they were created.
    Example:
        >>> s = Storage()
        >>> x = s.alloca(0)
        >>> s.store(x, 1)
        >>> s.load(x)
        1
    """

    def stc_loc_name(site_id):
        """
        Informs the static name of the memory location identified with id.

        Every memory location has two names: a static name  and a dynamic name.
        The static name is unique based on the allocation site. The allocation
        site is determined by the ID of the Alloca instruction. The dynamic
        name varies: a new name is created whenever that Alloca instruction
        runs.

        Example:
            >>> Inst.next_index = 0
            >>> i0 = Alloca('v')
            >>> Storage.stc_loc_name(i0.ID)
            'ref_0'
        """
        return f"ref_{site_id}"

    def dyn_loc_name(self, site_id):
        """
        The dynamic name of a memory allocation depends on how often that
        alloca instruction was interpreted. Whenever it runs, a new allocation
        is created (imagine whenever you run a new malloc statement in C).

        Example:
            >>> Inst.next_index = 0
            >>> i = Alloca('v')
            >>> s = Storage()
            >>> e = Env({})
            >>> i.eval(e, s)
            >>> st_name_0 = Storage.stc_loc_name(i.ID)
            >>> dy_name_0 = s.dyn_loc_name(i.ID)
            >>> i.eval(e, s)
            >>> st_name_1 = Storage.stc_loc_name(i.ID)
            >>> dy_name_1 = s.dyn_loc_name(i.ID)
            >>> [st_name_0, dy_name_0, st_name_1, dy_name_1]
            ['ref_0', 'ref_0_1', 'ref_0', 'ref_0_2']
        """
        name = Storage.stc_loc_name(site_id) + f"_{self.location_counter}"
        return name

    def __init__(self, initial_args={}):
        self.storage = {}
        self.location_counter = 0

    def alloca(self, loc_site):
        """
        Creates a new memory location and returns it.
        """
        ref = self.dyn_loc_name(loc_site)
        self.location_counter += 1
        self.storage[ref] = None
        return ref

    def store(self, ref, value):
        """
        This method stores the contents of value into the location pointed out
        by ref
        """
        self.storage[ref] = value

    def load(self, ref):
        """
        This method stores the contents of value into the location pointed out
        by ref
        """
        return self.storage[ref]

    def dump(self):
        """
        Prints the contents of the storage. This method is mostly used for
        debugging purposes.
        """
        for loc, value in self.storage.items():
            print(f"{loc}: {value}")


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


class Store(Inst):
    """
    This instruction stores a new value in the storage environment. These
    instructions have the structure *ref = src.

    Example:
        >>> e = Env({"x": 1})
        >>> s = Storage()
        >>> a = Alloca("v")
        >>> i = Store("v", "x")
        >>> a.eval(e, s)
        >>> i.eval(e, s)
        >>> s.load(e.get("v"))
        1
    """

    def __init__(self, ref, src):
        super().__init__()
        self.ref = ref
        self.src = src

    def definition(self):
        return set()

    def uses(self):
        return set([self.src])

    def __str__(self):
        inst_s = f"{self.ID}: {self.ref} = store {self.src}"
        pred_s = f"\n  P: {', '.join([str(inst.ID) for inst in self.preds])}"
        next_s = f"\n  N: {self.nexts[0].ID if len(self.nexts) > 0 else ''}"
        return inst_s + pred_s + next_s

    def eval(self, env, storage):
        ref = env.get(self.ref)
        val = env.get(self.src)
        storage.store(ref, val)


class Load(Inst):
    """
    This instruction loads a value from the storage environment.

    Example:
        >>> e = Env({"x": 1})
        >>> s = Storage()
        >>> a = Alloca("v")
        >>> i = Store("v", "x")
        >>> l = Load("w", "v")
        >>> a.eval(e, s)
        >>> i.eval(e, s)
        >>> l.eval(e, s)
        >>> e.get("w")
        1
    """

    def __init__(self, dst, ref):
        super().__init__()
        self.dst = dst
        self.ref = ref

    def definition(self):
        return set([self.dst])

    def uses(self):
        return set([self.ref])

    def __str__(self):
        inst_s = f"{self.ID}: {self.dst} = load {self.ref}"
        pred_s = f"\n  P: {', '.join([str(inst.ID) for inst in self.preds])}"
        next_s = f"\n  N: {self.nexts[0].ID if len(self.nexts) > 0 else ''}"
        return inst_s + pred_s + next_s

    def eval(self, env, storage):
        ref = env.get(self.ref)
        val = storage.load(ref)
        env.set(self.dst, val)


class Alloca(Inst):
    """
    This instruction creates a new location in the storage.

    Example:
        >>> Inst.next_index = 0
        >>> e = Env({})
        >>> s = Storage()
        >>> a = Alloca("v")
        >>> a.eval(e, s)
        >>> e.get("v")
        'ref_0_0'

        >>> Inst.next_index = 0
        >>> e = Env({})
        >>> s = Storage()
        >>> a = Alloca("v")
        >>> a.eval(e, s)
        >>> s.load(e.get("v")) == None
        True
    """

    def __init__(self, name):
        super().__init__()
        self.name = name

    def definition(self):
        return set([self.name])

    def uses(self):
        return set()

    def __str__(self):
        inst_s = f"{self.ID}: {self.name} = Alloca"
        pred_s = f"\n  P: {', '.join([str(inst.ID) for inst in self.preds])}"
        next_s = f"\n  N: {self.nexts[0].ID if len(self.nexts) > 0 else ''}"
        return inst_s + pred_s + next_s

    def eval(self, env, storage):
        ref = storage.alloca(self.ID)
        env.set(self.name, ref)


class Move(Inst):
    """
    This instruction copies the contents of the source operand into the
    destination operand.

    Example:
        >>> e = Env({"src": True})
        >>> a = Move("dst", "src")
        >>> a.eval(e, None)
        >>> e.get("dst")
        True
    """

    def __init__(self, dst, src):
        super().__init__()
        self.dst = dst
        self.src = src

    def definition(self):
        return set([self.dst])

    def uses(self):
        return set([self.src])

    def __str__(self):
        inst_s = f"{self.ID}: {self.dst} = {self.src}"
        pred_s = f"\n  P: {', '.join([str(inst.ID) for inst in self.preds])}"
        next_s = f"\n  N: {self.nexts[0].ID if len(self.nexts) > 0 else ''}"
        return inst_s + pred_s + next_s

    def eval(self, env, _):
        env.set(self.dst, env.get(self.src))


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
        >>> a.eval(e, None)
        >>> e.get("a")
        5

        >>> a = Add("a", "b0", "b1")
        >>> a.get_next() == None
        True
    """

    def eval(self, env, _):
        env.set(self.dst, env.get(self.src0) + env.get(self.src1))

    def get_opcode(self):
        return "+"


class Mul(BinOp):
    """
    Example:
        >>> a = Mul("a", "b0", "b1")
        >>> e = Env({"b0":2, "b1":3})
        >>> a.eval(e, None)
        >>> e.get("a")
        6
    """

    def eval(s, env, _):
        env.set(s.dst, env.get(s.src0) * env.get(s.src1))

    def get_opcode(self):
        return "*"


class Lth(BinOp):
    """
    Example:
        >>> a = Lth("a", "b0", "b1")
        >>> e = Env({"b0":2, "b1":3})
        >>> a.eval(e, None)
        >>> e.get("a")
        True
    """

    def eval(s, env, _):
        env.set(s.dst, env.get(s.src0) < env.get(s.src1))

    def get_opcode(self):
        return "<"


class Geq(BinOp):
    """
    Example:
        >>> a = Geq("a", "b0", "b1")
        >>> e = Env({"b0":2, "b1":3})
        >>> a.eval(e, None)
        >>> e.get("a")
        False
    """

    def eval(s, env, _):
        env.set(s.dst, env.get(s.src0) >= env.get(s.src1))

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
        >>> b.eval(e, None)
        >>> b.get_next() == a
        True
    """

    def __init__(s, cond, true_dst=None, false_dst=None):
        super().__init__()
        s.cond = cond
        s.nexts = [true_dst, false_dst]
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

    def eval(s, env, _):
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

    def get_next(s):
        return s.nexts[s.next_iter]

    def __str__(self):
        inst_s = f"{self.ID}: bt {self.cond}"
        pred_s = f"\n  P: {', '.join([str(inst.ID) for inst in self.preds])}"
        next_s = f"\n  NT:{self.nexts[0].ID} NF:{self.nexts[1].ID}"
        return inst_s + pred_s + next_s


def interp(instruction, environment, storage):
    """
    This function evaluates a program until there is no more instructions to
    evaluate. The interpreter takes as input three parameters:

    instruction: lang.Inst
        The current instruction that must be interpreted.
    environment: lang.Env
        A table that associates variable names with the values they hold.
    storage: lang.Storage
        A table that associate memory references with the values they hold.

    Notice that the environment is a stack of bindings. Bindings are pairs of
    variable names and values. New bindings are added to the stack whenever new
    variables are defined. Bindings are never removed from the stack. In this
    way, we can inspect the history of state transformations caused by the
    interpretation of a program.

    Example:
        >>> env = Env({"m": 3, "n": 2, "zero": 0})
        >>> m_min = Add("answer", "m", "zero")
        >>> n_min = Add("answer", "n", "zero")
        >>> p = Lth("p", "n", "m")
        >>> b = Bt("p", n_min, m_min)
        >>> p.add_next(b)
        >>> interp(p, env, None).get("answer")
        2
    """
    if instruction:
        instruction.eval(environment, storage)
        return interp(instruction.get_next(), environment, storage)
    else:
        return environment
