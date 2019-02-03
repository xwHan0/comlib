
import types


class Proc:
        
    def pre(self,  *datum, node=None):
        if len(datum) == 1:
            return datum[0]
        else:
            return datum
            
    def post(self, result, *datum, node=None):
        if len(datum) == 1:
            return datum[0]
        else:
            return datum
            
    def pre_yield(self): return True
    def post_yield(self): return False
    def is_yield(self): return True
        
        
class ProcMap(Proc):
    def __init__(self, func):
        if isinstance(func, ProcMap):
            self = func
        else:
            self.func = func
        
    def pre(self, *datum, node=None):
        if self.func.__code__.co_argcount == 1:
            return self.func(datum[0])
        elif self.func.__code__.co_argcount == 0:
            return self.func(*datum, node=node)
        
    
class ProcReduce(Proc):
    def __init__(self, proc):
        if isinstance(proc, ProcReduce):
            self = proc
        elif isinstance(proc, types.FunctionType):
            self.proc = proc
            
    def post(self, result, *datum, node=None):
        if self.proc.__code__.co_argcount == 1:
            return self.proc(result, datum[0])
        elif self.proc.__code__.co_argcount == 0:
            return self.proc(result, *datum, node=node)
        
    def pre_yield(self): return False
    def is_yield(self): return False
        