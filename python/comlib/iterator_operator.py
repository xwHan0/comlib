def deq(it, n=1): 
    it = iter(it)
    return [next(it) for i in range(n)]

