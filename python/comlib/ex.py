
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
#====  Special functions
#=================================================================================================================
def transport(x): return x

#=================================================================================================================
#====  args process
#=================================================================================================================

def _args_map(args, arg, init = None):
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

#=================================================================================================================
#====  xapply
#=================================================================================================================
class xapply_scalar_c: pass
class xapply_sequence_c: pass
class xapply_json_c: pass
class xapply_extend_c: pass

xapply_scalar = xapply_scalar_c()
xapply_sequence = xapply_sequence_c()
xapply_json = xapply_json_c()
xapply_extend = xapply_extend_c()

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
            * 当func为函数列表时，返回由列表中各个子处理函数的处理结果组成的迭代器(Process Function List特性)。
            * 当func=None时，返回由*args参数形成的list。即不执行func，把func的参数当作列表返回。
        args {tuple} -- Position parameters list
            * 若args为空，则返回一个延时函数(Delay Executr特性)
            * xapply_scalar: 表示随后的参数都作为一个scalar元素添加到最终的参数列表中。直到遇到其它xapply_*标识符
            * xapply_sequence: 表示随后的参数都作为一个sequence链接到最终的参数列表中。直到遇到其它xapply_*标识符
            * xapply_json: 表示随后的参数按照数据类型加入最终参数列表
                - 若参数类型为list实例，则作为sequence链接到最终参数列表
                - 若参数类型非list实例，则作为scalar追加到最终参数列表
            * xapply_extend: 表示随后的一个参数为一个列表。列表中的元素将和xapply中的args一样进行解析。xapply函数会递归解析该列表，然后把
                生产的新列表展开到当前args中，作为最后传递给func的参数使用。
                - 若随后的一个参数不是列表实例，则把该参数当作普通scalar参数添加到最终的参数列表中。
                - 若args中第一个参数就是xapply_extend，则xapply进入Custom mode

    Return:
        若func==None, 则返回由args作为参数，按xapply规则生产的列表
        若func!=None，则把生成的参数列表作为func函数的参数，然后返回func的结果
    """
    status = 0      #工作状态。0: IDLE(Common Mode); 1: scalar(Custom Mode); 2: sequence(Custom Mode); 3: json(Auto Mode);

    if isinstance(func, list):  #Process Function List特性支持
        map(lambda p : xapply(p, *args, **xargs), func)

    if len(args) == 0:  #Delay Execute特性支持
        def xapply_delay_execute(*args, **xargs):   #定义延时函数
            return xapply(func, *args, **xargs)
        return xapply_delay_execute     #返回延时函数

    if args[0] == xapply_scalar:
        status = 1
        args = args[1:]
    elif args[0] == xapply_sequence:
        status = 2
        args = args[1:]
    elif args[0] == xapply_json:
        status = 3
        args = args[1:]
    elif args[0] == xapply_extend and isinstance(args[1],list):
        status = 1
        args = args[1] + args[2:] 


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
        isExtend = False
        for arg in args:
            if arg == xapply_scalar:
                status = 1
            elif arg == xapply_sequence:
                status = 2
            elif arg == xapply_extend:  #xapply_extend参数模式进入条件
                isExtend = True         #进入extend参数模式
            elif isExtend == True:      #xapply_extend参数的下一个参数
                if isinstance(arg, list):   #若xapply_extend随后参数为列表实例
                    new_args += xapply(None, *tuple(arg))
                else:  #原则上，xapply_extend后的参数应该为列表实例。当前情况是个“非法”的corner
                    new_args.extend(arg)
                isExtend = False    #退出extend参数模式
            elif status == 1:
                new_args.append(arg)
            elif status == 2:
                new_args.extend(arg)
        args = new_args

    if func == None:
        return args
    else:
        return func(*args, **xargs)


#=================================================================================================================
#====  xmap
#=================================================================================================================
def xmap (proc, *lists, args = None, when = None):
    """返回经过proc处理后的map迭代器。
    
    Arguments:
        proc {func or func_vector} -- 处理函数或者处理函数列表
            * 当proc==None时，proc=transport
            * proc的格式为：proc(p1,p2,...,pN)。其中p1,...,pN由xargs参数决定
            * 当proc为处理函数列表时，xmap对列表中的每个处理函数进行xmap迭代，然后返回每个迭代结果的迭代器。
        lists {([object])} -- 被处理的数据列表。若为tuple，则转化为列表
            * 当该列表为空时，返回一个支持proc的延时函数，该函数接收一个列表参数。(Delay Execute特性)
    
    Keyword Arguments:
        xargs {[string]} -- proc和when函数的参数映射表。 (default: {None})
            * None: 参数映射规则为: (lists[0]的当前值, ..., lists[N-1]的当前值)
            * 非None: 按照xargs列表内容的顺序作为proc和when的参数。xargs的每个值为一个字符串，"%1"表示lists[0]的当前值，
                ..., "%N"表示lists[N-1]的当前值。
        when {function} -- lists数据参与xmap处理的条件判断函数 (default: {None})
            * None表示无条件处理。
            * when的格式为: bool when(p1,p2,...,pN)。其中p1,..,pN由xargs参数决定。
    
    Returns:
        Iterator -- 处理结果迭代器。
        注意：返回的是迭代器，需要使用list(return-value)来转化为链表。
    """

    if proc == None:
        proc = transport

    if len(lists) == 0:     #Delay Execute特性
        def xmap1 (*args1): #Delay Execute函数定义
            return map(proc, *args1)
        return xmap1    #返回Delay Execute函数
    else:
        lists = [list(lst) if isinstance(lst,tuple) else lst for lst in lists ]
        
    if args == None and when == None:
        return map(proc,*lists)

    elif when == None:
        def proc_inner(*args_inner):
            args_out = [_args_map(args_inner, arg) for arg in args]
            return proc(*tuple(args_out))
        return map(proc_inner, lists)

    else:
        argNum = len(lists)     #获取proc需要处理的参数个数
        lstSize = xmin(*tuple([len(lst) for lst in lists]))     #循环列表的最小长度，截取

        lists1 = [[]]
        for i in range(lstSize):   #循环处理列表长度
            args1 = [lists[j][i] for j in range(argNum)]     #循环处理列表个数

            if args != None:    #处理参数映射
                args1 = [_args_map(args1, arg) for arg in args]

            if when != None:    #处理过滤列表
                if when(*tuple(args1)):
                    lists1.append(args1)
            else:
                lists1.append(args1)

        return map(lambda args : proc(*tuple(args)), lists1)

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
            args = tuple([_args_map(lst,arg,init) for arg in args])
            
        if when==None or when(*args):
            init = proc(*args)
            
    return init


#def list_map (proc, lst, *args): map(proc, *args.append(lst))
#list.set_instance_method(list_map)

# def add8 (a,b,c,d,e,f,g,h): return a+b+c+d+e+f+g+h
# print(xapply(add8, 1,2,3,[4,5,6,7,8]))
# print(xapply(add8,xapply_json,1,2,[3,4],5,6,[7,8]))
# print(xapply(add8, xapply_scalar, 1,2,3,4, xapply_sequence, [5,6], xapply_scalar, 7, 8))