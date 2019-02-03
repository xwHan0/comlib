
import types


class Proc:
    
    #def __init__(self):
    #    
    
    def pre(self, result, *datum, node=None):
        if len(datum) == 1:
            result.rst = datum[0]
        else:
            result.rst = datum
            
    def post(self, result, *datum, node=None):
        if len(datum) == 1:
            result.rst = datum[0]
        else:
            result.rst = datum
            
    def pre_yield(self): return True
    def post_yield(self): return False
    def is_yield(self): return True
        
        
class ProcMap(Proc):
    def __init__(self, func):
        if isinstance(func, ProcMap):
            self = func
        else:
            self.func = func
        
    def pre(self, result, *datum, node=None):
        if self.func.__code__.co_argcount == 1:
            result.rst = self.func(datum[0])
        elif self.func.__code__.co_argcount == 0:
            result.rst = self.func(*datum, node=node)
        
    
class ProcReduce(Proc):
    def __init__(self, proc):
        if isinstance(proc, ProcReduce):
            self = proc
        elif isinstance(proc, types.FunctionType):
            self.proc = proc
            
    def pre(self, result, *datum, node=None): pass
            
    def post(self, result, *datum, node=None):
        if self.proc.__code__.co_argcount == 2:
            result.rst = self.proc(result, datum[0])
        elif self.proc.__code__.co_argcount == 0:
            result.rst = self.proc(result, *datum, node=node)
        
    def pre_yield(self): return False
    def is_yield(self): return False
        