
#=================================================================================================================
#====  Common
#=================================================================================================================
doc = help      #重命名help函数

#=================================================================================================================
#====  xmin xmax
#=================================================================================================================
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
    


#=================================================================================================================
#====  xapply
#=================================================================================================================
class xapply_scalar_c: pass
class xapply_sequence_c: pass
class xapply_json_c: pass

xapply_scalar = xapply_scalar_c()
xapply_sequence = xapply_sequence_c()
xapply_json = xapply_json_c()

def xapply (func, *args, **xargs):
    """Execute function <func> with parameters *args and **xargs.
    
    There are three work modes through args[0]:
    1) Common mode: args[0] is not xapply_scalar, xapply_sequence and xapply_json
        In this mode, if args[-1] is a list, we concat args[-1] into args list and form a new tuple.
        If args[-1] is not a list, we just bypass args to <func>
    2) Custom mode: args[0] is either xapply_scalar or xapply_sequence
        In this mode, parameters after xapply_scalar are treated as salar, and after xapply_sequence as list.
    3) Auto mode: args[0] is xapply_json
        In this mode, we flatten and concat all list type parameters into a new tuple.

    Arguments:
        func {function} -- Executed function
        args {tuple} -- Position parameters list
    """
    status = 0      #0: IDLE; 1: scalar; 2: sequence; 3: json;

    if args[0] == xapply_scalar:
        status = 1
        args = args[1:]
    elif args[0] == xapply_sequence:
        status = 2
        args = args[1:]
    elif args[0] == xapply_json:
        status = 3
        args = args[1:]

    if status == 0:
        if type(args[-1]) == list:
            args = args[:-1] + tuple(args[-1])
    elif status == 3:
        new_args = []
        for arg in args:
            if type(arg) == list:
                new_args.extend(arg)
            else:
                new_args.append(arg)
        args = new_args
    else:
        new_args = []
        for arg in args:
            if arg == xapply_scalar:
                status = 1
            elif arg == xapply_sequence:
                status = 2
            elif status == 1:
                new_args.append(arg)
            elif status == 2:
                new_args.extend(arg)
        args = new_args

    return func(*args, **xargs)


#=================================================================================================================
#====  xmap
#=================================================================================================================
def xmap (proc, *lists, args = None, when = None):
    """返回经过proc处理后的map迭代器。
    
    Arguments:
        proc {func or func_vector} -- 处理函数或者处理函数列表
            * proc的格式为：proc(p1,p2,...,pN)。其中p1,...,pN由xargs参数决定
            * 当proc为处理函数列表时，xmap对列表中的每个处理函数进行xmap迭代，然后返回每个迭代结果的迭代器。
        lists {([object])} -- 被处理的数据列表。
            * 当该列表为空时，返回一个支持proc的延时函数，该函数接收一个列表参数。
    
    Keyword Arguments:
        xargs {[string]} -- proc和when函数的参数映射表。 (default: {None})
            * None: 参数映射规则为: (lists[0]的当前值, ..., lists[N-1]的当前值)
            * 非None: 按照xargs列表内容的顺序作为proc和when的参数。xargs的每个值为一个字符串，"%1"表示lists[0]的当前值，
                ..., "%N"表示lists[N-1]的当前值。
        when {function} -- lists数据参与xmap处理的条件判断函数 (default: {None})
            * None表示无条件处理。
            * when的格式为: bool when(p1,p2,...,pN)。其中p1,..,pN由xargs参数决定。
    
    Returns:
        Iterator -- 处理结果迭代器
    """

    if len(lists) == 0:
        if type(proc) == list:
            def xmapn (*argsn):
                return map(proc,*argsn)
            return xmapn
        else:
            def xmap1 (*args1):
                return map(proc, *args1)
            return xmap1
    else:
        return map(proc,*lists)

#=================================================================================================================
#====  xseq
#=================================================================================================================
class xseq(list):
    """列表扩展类。
    
    Arguments:
        list {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """

    def __init__ ( self, lst = [] ):
        self.extend( lst )
    def map (self, proc, *args): return xmap(proc,*args, self)


#=================================================================================================================
#====  xreduce
#=================================================================================================================
def xreduce_args_map(args, arg, init):
    if arg == "%0": return init
    elif arg == "%1": return args[0]
    elif arg == "%2": return args[1]
    elif arg == "%3": return args[2]
    elif arg == "%4": return args[3]
    elif arg == "%5": return args[4]
    elif arg == "%6": return args[5]
    elif arg == "%7": return args[6]
    elif arg == "%8": return args[7]
    elif arg == "%9": return args[8]
    else: return arg

def xreduce(proc, *lists, init=None, xargs=None, when=None):
    """[summary]
    
    Arguments:
        proc {function or function vector} -- 处理函数或者处理函数列表。
            * proc的格式为：object proc(p1,p2,...,pN)。其中p1,...,pN由xargs参数决定
            * 当proc为处理函数列表时，xreduce对列表中的每个处理函数进行xreduce迭代，然后返回每个迭代结果的迭代器。
        lists {([object])} -- 被处理的列表集合tuple。
            * 若lists中各个列表长度不等，则统一截短对齐到最小列表的长度
            * 若lists为空，返回一个延时函数，该延时函数接收一个lists为参数。
    
    Keyword Arguments:
        init {object} -- 迭代的初始值。若为None则使用lists中第一个列表的第一个值作为初始值 (default: {None})
        xargs {[string]} -- proc和when函数的参数映射表。 (default: {None})
            * None: 参数映射规则为: (上一次计算的结果或者init, lists[0]的当前值, ..., lists[N-1]的当前值)
            * 非None: 按照xargs列表内容的顺序作为proc和when的参数。xargs的每个值为一个字符串，"%0"表示上一次计算的结果，"%1"表示lists[0]的当前值，
                ..., "%N"表示lists[N-1]的当前值。
        when {function} -- lists数据参与xreduce处理的条件判断函数 (default: {None})
            * None表示无条件处理。
            * when的格式为: bool when(p1,p2,...,pN)。其中p1,..,pN由xargs参数决定。
    
    Returns:
        [type] -- [description]

    *** Issue ***
    1. 当lists为迭代器时，如何处理

    """

    
    argNum = len(lists)

    if argNum == 0:  #没有输入数据，返回延时函数
        def xreduce1(*lists):
            return xreduce(proc, *lists, init=init, xargs=xargs, when=when)
        return xreduce1
        
    if type(proc) == list: #proc为列表，返回每个子proc的迭代器
        return map(lambda p: xreduce(p, *lists, init=init, xargs=xargs, when=when), proc)

    lstSize = xmin(*tuple([len(lst) for lst in lists]))
    
    st = 0
    if init == None:
        init = lists[0][0]
        st = 1
        
    lists = [[lists[j][i] for j in range(argNum)] for i in range(st, lstSize)]
    
    for lst in lists:
        if xargs == None:
            args = (init,) + tuple(lst)
        else:
            args = tuple([xreduce_args_map(lst,arg,init) for arg in args])
            
        if when==None or when(*args):
            init = proc(*args)
            
    return init


#def list_map (proc, lst, *args): map(proc, *args.append(lst))
#list.set_instance_method(list_map)

# def add8 (a,b,c,d,e,f,g,h): return a+b+c+d+e+f+g+h
# print(xapply(add8, 1,2,3,[4,5,6,7,8]))
# print(xapply(add8,xapply_json,1,2,[3,4],5,6,[7,8]))
# print(xapply(add8, xapply_scalar, 1,2,3,4, xapply_sequence, [5,6], xapply_scalar, 7, 8))