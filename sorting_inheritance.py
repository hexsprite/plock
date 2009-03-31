class C(object):
    pass

class B(C):
    pass

class A(B):
    pass

d = {
    A: B,
    B: C,
    C: None,
    }

l = [A, B, C]

def f(x, y):
    if x is y:
        return 0
    if inherits(x, y):
        return 1
    else:
        return -1

def inherits(x, y):
    if x is y:
        return True
    potential_base = d[x]
    if potential_base is None:
        return False
    if potential_base is y:
        return True
    return inherits(potential_base, y)

print sorted(l, cmp=f)
