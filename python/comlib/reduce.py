
def reduce(proc, *iters, init=None):
    """
    """
   
    # Parity闭包处理
    if len(iters) == 0:
        def parity_func(*iters):
            return reduce(proc,*iters,init)
        return parity_func

    # 多reduce并发处理
    if isinstance(proc, list):
        rst = []
        for p in proc:
            rst.append(reduce(p,init[0],*iters))
            if len(init) > 1: init = init[1:]
        return rst
            
    inner_iter = zip(*iters)
    
    # 初始参数处理
    if init==None: init = next(inner_iter)[0]
    
    for v in inner_iter:
        init = proc(init, *v)
        
    return init