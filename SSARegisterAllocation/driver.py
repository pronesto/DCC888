from lang import interp, Inst, Add, Mul, Lth, Geq, Bt, Phi, Env
from graph import new_euclid

prog, env = new_euclid()
res = interp(prog[0], env)
res.dump()


def ssa_euclid() -> list[Inst]:
    env = Env({
        'n0': 16, 'd': 5
    })
    i0 = Lth('z', 'n0', 'd')
    i2 = Mul('negd', 'd', -1)
    i3 = Phi('result1', 0, 'result2')
    i4 = Phi('n1', 'n0', 'n2')
    i5 = Add('result2', 'result1', 1)
    i6 = Add('n2', 'n1', 'negd')
    i7 = Geq('l', 'n2', 'd')
    i9 = Add('remainder', 0, 'n2')
    i10 = Add('end', 0, 0)
    i1 = Bt('z', i10)
    i8 = Bt('l', i3)
    prog = [i0, i1, i2, i3, i4, i5, i6, i7, i8, i9, i10]
    for i in range(9):
        prog[i].add_next(prog[i+1])
    return prog, env


def ssa_fibonacci() -> list[Inst]:
    env = Env({'iter': 9})
    i0 = Add('count0', 0, 3)
    i1 = Add('pred0', 0, 1)
    i2 = Add('fib0', 0, 1)
    i3 = Phi('count1', 'count0', 'count2')
    i4 = Phi('pred1', 'pred0', 'pred2')
    i5 = Phi('fib1', 'fib0', 'fib2')
    i6 = Add('aux', 0, 'fib1')
    i7 = Add('fib2', 'pred1', 'fib1')
    i8 = Add('pred2', 0, 'aux')
    i9 = Add('count2', 'count1', 1)
    i10 = Geq('repeat', 'iter', 'count2')
    i11 = Bt('repeat', i3)
    i12 = Add('end', 0, 0)
    prog = [i0, i1, i2, i3, i4, i5, i6, i7, i8, i9, i10, i11, i12]
    for i in range(12):
        prog[i].add_next(prog[i+1])
    return prog, env
