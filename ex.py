
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
def xmap (proc, *args):
    """
    返回经过proc处理后的map迭代器。
    """
    
    if len(args) == 0:
        if type(proc) == list:
            def xmapn (*argsn):
                return map(proc,*argsn)
            return xmapn
        else:
            def xmap1 (*args1):
                return map(proc, *args1)
            return xmap1
    else:
        return map(proc,*args)

#=================================================================================================================
#====  xseq
#=================================================================================================================
class xseq(list):
    def __init__ ( self, lst = [] ):
        self.extend( lst )
    def map (self, proc, *args): return map(proc,*args, self)


#=================================================================================================================
#====  xreduce
#=================================================================================================================
def xreduce_args_map(args, arg):
    if arg == "%1": return args[0]
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

    argNum = len(lists)

    if argNum == 0:
        def xreduce1(*lists):
            return xreduce(proc, *lists, init=init, xargs=xargs, when=when)
        return xreduce1
        
    if type(proc) == list:
        return map(lambda p: xreduce(p, *lists, init=init, xargs=xargs, when=when), proc)

    if argNum == 1:
        lstSize = len(lists[0])
    else:
        lstSize = min(*tuple([len(lst) for lst in lists]))
    
    st = 0
    if init == None:
        init = lists[0][0]
        st = 1
        
    lists = [[lists[j][i] for j in range(argNum)] for i in range(st, lstSize)]
    
    for lst in lists:
        if xargs == None:
            args = tuple(lst)
        else:
            args = tuple([xreduce_args_map(lst,arg) for arg in args])
            
        if when==None or when(*args):
            init = proc(init, *args)
            
    return init


#def list_map (proc, lst, *args): map(proc, *args.append(lst))
#list.set_instance_method(list_map)

# def add8 (a,b,c,d,e,f,g,h): return a+b+c+d+e+f+g+h
# print(xapply(add8, 1,2,3,[4,5,6,7,8]))
# print(xapply(add8,xapply_json,1,2,[3,4],5,6,[7,8]))
# print(xapply(add8, xapply_scalar, 1,2,3,4, xapply_sequence, [5,6], xapply_scalar, 7, 8))