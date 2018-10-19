import ex.__private__ as lib

def xmin(*args):
    """寻找{args}列表中的最小值。

    特殊情况：当列表为空列表时，返回0；当列表为单元素列表时，返回该元素。
    
    Returns:
        [type] -- [description]
    """

    l = len(args)
    
    if l==0: return 0
    if l==1:
        arg0 = args[0]
        if type(arg0)==list:
           return min(*tuple(arg0))
        else:
           return arg0
    
    return min(*args)
    
def xmax(*args):
    """寻找{args}列表中的最大值。

    特殊情况：当列表为空列表时，返回0；当列表为单元素列表时，返回该元素。
    
    Returns:
        [type] -- [description]
    """
    l = len(args)
    
    if l==0: return 0
    if l==1: 
        arg0 = args[0]
        if type(arg0)==list:
            return max(*tuple(arg0))
        else:
            return args[0]
    
    return max(*args)
    
def xgcd(*args):
    """计算args的最大公约数。args元素需为integer类型
    
    Returns:
        int -- 最大公约数
    """
    args = lib.flatten(args)
    
    l = len(args)

    if l == 0: return 0
    if l == 1: return args[0]

    gcdv = args[0]
    for b in args[1:]:
        gcdv = lib.gcd( gcdv, b )

    return gcdv
    

def xlcm(*args):
    """计算args最小公倍数。args元素需为integer类型
    
    Returns:
        int -- 最小公倍数
    """
    args = lib.flatten(args)
    
    l = len(args)
    if l == 0: return 0
    if l == 1: return args[0]
    
    lcmv = args[0]
    for b in args[1:]:
        if lcmv * b == 0: return 0
        lcmv = int( lcmv * b / lib.gcd( lcmv, b ) )

    return lcmv
    

