
def add(a=0, b=0, *args):
    rst = a + b
    for v in args:
        rst += v
    return rst

def sub(a=0, b=0, *args):
    rst = a - b
    for v in args:
        rst -= v
    return rst

def mul(a=0, b=0, *args):
    rst = a * b
    for v in args:
        rst *= v
    return rst

def lt(a=0, b=0, *args):
    if a >= b: return False
    for v in args:
        if b >= v: return False
        b = v
    return True

def le(a=0, b=0, *args):
    if a > b: return False
    for v in args:
        if b > v: return False
        b = v
    return True

def eq(a=0, b=0, *args):
    if a != b: return False
    for v in args:
        if b != v: return False
        b = v
    return True

def ne(a=0, b=0, *args):
    if a == b: return False
    for v in args:
        if b == v: return False
        b = v
    return True

def ge(a=0, b=0, *args):
    if a < b: return False
    for v in args:
        if b < v: return False
        b = v
    return True

def gt(a=0, b=0, *args):
    if a < b: return False
    for v in args:
        if b < v: return False
        b = v
    return True