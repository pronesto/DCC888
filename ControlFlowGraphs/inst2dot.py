from __future__ import annotations

import sys
from os import PathLike
from typing import final


def _indent(depth=1, spaces=4):
    one_level = f'{" " * spaces}'
    return f"{one_level * depth}"


@final
class DotMaker:
    _dot_new_graph = f"digraph cfg {{\n{_indent()}node [shape=box];\n\n"
    _node_cnt = 0
    _is_active = False
    _ofile = "/dev/null"
    dot = ""
    indent_width = 4

    def __new__(self):
        raise RuntimeError("This class only contains static methods.")

    def __init__(self):
        raise RuntimeError("This class only contains static methods.")

    def __init_subclass__(cls, *args, **kwargs):
        raise TypeError(f"{cls.__name__} cannot be subclassed.")

    @staticmethod
    def enable(output_file: int | str | bytes | PathLike[str] | PathLike[bytes] | None):
        """
        Enables the generation of dot code from instructions and functions like
        `my_inst.add_next(...)`. No code will be generated while DotMaker is
        disabled, which is the default starting state.

        An optional `output_file` may be provided to this function, to be used
        by `DotMaker.write()`. However, if a different file path is passed to
        `DotMaker.write()`, that one takes precedence over this one.
        """
        if output_file is not None:
            DotMaker._ofile = output_file

        DotMaker._is_active = True

    @staticmethod
    def disable():
        """
        Disables the generation of dot code from instructions and functions.
        See `DotMaker.enable()`
        """
        DotMaker._is_active = False

    @staticmethod
    def is_enabled():
        """
        Returns whether dot code generation is enabled.
        See `DotMaker.is_enabled()`
        """
        return DotMaker._is_active == True

    @staticmethod
    def inc_node_cnt():
        DotMaker._node_cnt += 1

    @staticmethod
    def num_nodes():
        return DotMaker._node_cnt

    @staticmethod
    def write(
        output_file: int | str | bytes | PathLike[str] | PathLike[bytes] | None = None,
    ):
        """
        If an output_file was passed to `DotMaker.enable()`, the `output_file`
        arg this function accepts takes precedence over it.
        """
        if output_file is None:
            output_file = DotMaker._ofile
        with open(output_file, "w") as ofile:
            ofile.write(DotMaker._dot_new_graph + DotMaker.dot + "\n}\n")
        DotMaker.dot = ""
        DotMaker._node_cnt = 0

    @staticmethod
    def clear(reset_output_file: bool = False):
        """
        Clears the content (dot code) stored by DotMaker so far, as well as the
        node count. Optionally, also resets the output_file (if one was
        provided to enable()). An output_file can also be passed to
        `DotMaker.write()`, so there's no need to worry about resetting it.
        """
        DotMaker.dot = ""
        DotMaker._node_cnt = 0
        if reset_output_file:
            DotMaker._ofile = "/dev/null"


def _append_dot(content: str, depth: int = 1):
    DotMaker.dot += f"{_indent(depth=depth)}{content}"


def dotgen(func):
    """
    This decorator allows dot code generation for a CFG. The state is stored in
    private attributes of DotMaker and the state is only altered (i.e., dot
    code is only generated) while DotMaker is enabled (see `DotMaker.enable()`,
    `DotMaker.disable()` and `DotMaker.is_enabled()`).
    """

    def wrapper(*args, **kwargs):
        # Call the original function
        result = func(*args, **kwargs)

        # Don't generate dot code if DotMaker is not enabled
        if not DotMaker.is_enabled():
            return result

        # We use this to determine whether we're decorating a member fn or
        # a standalone one (which doesn't have a "self").
        # WARNING: this does not work for dynamically attached methods - in
        # that scenario, the __qualname__ has no '.' and the result will be
        # returned as if it were a standalone function
        if "." not in func.__qualname__:
            # Decorating standalone functions is not supported
            return result

        # args[0] is the instance (self) of the class.
        instance = args[0]

        # This is done because there was an issue trying to match types using,
        # for instance, `if type(instance) == lang.Bt: ...`. I couldn't trace
        # the exact cause, but the way the imports are resolved is a strong
        # suspect, especially considering this module had workarounds to deal
        # with circular imports (related to lang)
        itype = f"{instance.__class__.__module__}.{instance.__class__.__name__}"

        if func.__qualname__.endswith(".add_next"):
            # add_next on branch (Bt) does nothing
            if itype == "lang.Bt":
                return result

            nxt = instance.NEXTS[-1]
            _append_dot(f"{instance.id} -> {nxt.id};\n")

            return result

        # We increase the node count since at this point, we know we're
        # wrapping a node instantiation (most likely the __init__ of an Inst)
        DotMaker.inc_node_cnt()

        if itype == "lang.Bt":
            dstTrue, dstFalse = instance.NEXTS
            _append_dot(f'{instance.id} [label="bt {instance.cond}"];\n')
            _append_dot(f"{instance.id} -> {dstTrue.id};\n")
            _append_dot(f"{instance.id} -> {dstFalse.id};\n")

        # We assume a BinOp can't have Bt as one of its sources (src0, src1)
        elif itype == "lang.Add":
            _append_dot(
                f'{instance.id} [label="{instance.dst} = '
                f'{instance.src0} + {instance.src1}"];\n'
            )

        elif itype == "lang.Mul":
            _append_dot(
                f'{instance.id} [label="{instance.dst} = '
                f'{instance.src0} * {instance.src1}"];\n'
            )

        elif itype == "lang.Lth":
            _append_dot(
                f'{instance.id} [label="{instance.dst} = '
                f'{instance.src0} < {instance.src1} ? True : False"];\n'
            )

        elif itype == "lang.Geq":
            _append_dot(
                f'{instance.id} [label="{instance.dst} = '
                f'{instance.src0} >= {instance.src1} ? True : False"];\n'
            )

        return result

    return wrapper
