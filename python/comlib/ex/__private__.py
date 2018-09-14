def gcd(a,b):
    if a < b:
        a,b = b,a
    remainder = a % b
    if remainder == 0:
        return b
    else:
        return gcd(remainder,b)
        
def flatten(ite):
    r = []
    for e in ite:
        if isinstance(e,Iterable):
            r += flatten(e)
        else:
            r.append(e)
    return r