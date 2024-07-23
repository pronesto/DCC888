from lang import interp, Inst, Add, Mul, Lth, Geq, Bt, Phi, Env
from graph import register_allocation


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


def ssa_big_branch() -> list[Inst]:
    env = Env()
    i0 = Add('sub', 3, -2)
    i1 = Lth('pred', 'sub', 1)
    i3 = Add('prod0', 0, 1)
    i4 = Add('count0', 0, 1)
    i5 = Phi('prod1', 'prod0', 'prod2')
    i6 = Phi('count1', 'count0', 'count2')
    i7 = Mul('prod2', 'prod1', 2)
    i8 = Add('count2', 'count1', 1)
    i9 = Geq('repeat0', 3, 'count2')
    i10 = Bt('repeat0', i5)
    i12 = Add('fib0', 0, 1)
    i13 = Add('count3', 0, 1)
    i14 = Phi('count4', 'count3', 'count5')
    i15 = Phi('fib1', 'fib0', 'fib2')
    i16 = Add('nextfib', 'fib1', 1)
    i17 = Add('fib2', 'fib1', 'nextfib')
    i18 = Add('count5', 'count4', 1)
    i19 = Geq('repeat1', 3, 'count5')
    i20 = Bt('repeat1', i13)
    i21 = Add('end', 0, 0)
    i11 = Bt(True, i21)
    i2 = Bt('pred', i11)
    prog = [
        i0, i1, i2, i3, i4,
        i5, i6, i7, i8, i9,
        i10, i11, i12, i13, i14,
        i15, i16, i17, i18, i19,
        i20, i21
    ]
    for i in range(21):
        prog[i].add_next(prog[i+1])
    return prog, env


def ssa_loop() -> list[Inst]:
    env = Env()
    i0 = Add('count0', 0, 1)
    i1 = Add('sum0', 0, 0)
    i2 = Phi('count1', 'count0', 'count2')
    i3 = Phi('sum1', 'sum0', 'sum2')
    i4 = Add('sum2', 'sum1', 1)
    i5 = Add('count2', 'count1', 1)
    i6 = Geq('repeat', 5, 'count2')
    i7 = Bt('repeat', i2)
    i8 = Add('end', 0, 0)
    prog = [
        i0, i1, i2, i3, i4,
        i5, i6, i7, i8,
    ]
    for i in range(8):
        prog[i].add_next(prog[i+1])
    return prog, env


def ssa_is_even() -> list[Inst]:
    env = Env({'num0': 9})
    i0 = Phi('num1', 'num0', 'num2')
    i1 = Lth('l', 'num1', 2)
    i3 = Add('num2', 'num1', -2)
    i4 = Bt(True, i0)
    i5 = Geq('isone', 'num1', 1)
    i6 = Mul('nisone', -1, 'isone')
    i7 = Add('iseven', 1, 'nisone')
    i2 = Bt('l', i5)
    prog = [
        i0, i1, i2, i3, i4,
        i5, i6, i7
    ]
    for i in range(7):
        prog[i].add_next(prog[i+1])
    return prog, env


def ssa_small_branch() -> list[Inst]:
    env = Env({'a': 0, 'b': 3})
    i1 = Add('x', 'a', 'b')
    i2 = Add('y', 'x', 'b')
    i3 = Mul('z', 'a', 'b')
    i0 = Bt(True, i3)
    prog = [i0, i1, i2, i3]
    for i in range(3):
        prog[i].add_next(prog[i+1])
    return prog, env


print(f'euclid: {register_allocation(ssa_euclid()[0])[1]}')
print(f'big_branch: {register_allocation(ssa_big_branch()[0])[1]}')
print(f'loop: {register_allocation(ssa_loop()[0])[1]}')
print(f'is_even: {register_allocation(ssa_is_even()[0])[1]}')
print(f'small_branch: {register_allocation(ssa_small_branch()[0])[1]}')
