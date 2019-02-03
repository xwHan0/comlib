
import types

class Proc:
    
    #def __init__(self):
    #    
    
    def pre(self, result, *datum, stack=[]): pass
    def post(self, result, *datum, stack=[]): pass
    def pre_yield(self): return False
    def post_yield(self): return False
    def is_yield(self): return self.pre_yield() or self.post_yield()
        

class ProcIter(Proc):
    
    #def __init__(self):
    #    
    
    def pre(self, result, *datum, stack=[]):
        if len(datum) == 1:
            result.rst = datum[0]
        else:
            result.rst = datum
            
    def pre_yield(self): return True
        
        
class ProcMap(Proc):
    def __init__(self, func):
        if isinstance(func, ProcMap):
            self = func
        else:
            self.func = func
        
    def pre(self, result, *datum, stack=[]):
        if self.func.__code__.co_argcount == 1:
            result.rst = self.func(datum[0])
        elif self.func.__code__.co_argcount == 0:
            result.rst = self.func(*datum, stack=stack)
        
    
class ProcReduce(Proc):
    def __init__(self, proc):
        if isinstance(proc, ProcReduce):
            self = proc
        elif isinstance(proc, types.FunctionType):
            self.proc = proc
            
    def pre(self, result, *datum, stack=[]): pass
            
    def post(self, result, *datum, stack=[]):
        if self.proc.__code__.co_argcount == 2:
            result.rst = self.proc(result.rst, datum[0])
        elif self.proc.__code__.co_argcount == 0:
            result.rst = self.proc(result.rst, *datum, stack=stack)
        
    def pre_yield(self): return False
        