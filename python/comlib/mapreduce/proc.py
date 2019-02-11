
import types

class Proc:
    """处理动作基类。"""
    
    def pre(self, result, *datum, stack=[]): 
        """子项迭代前的处理动作函数。
        Arguments:
        - result {Result}: 保存在query实例中的处理结果。参看Result说明
        - datum {data}: 当前的处理节点集合
        - stack {list<NodeInfo>}: 当前处理堆栈。栈底为当前处理的节点。每个节点为一个NodeInfo实列。参看NodeInfo说明。
        """
        pass

    def post(self, result, *datum, stack=[]): 
        """子项迭代后的处理动作函数。参数说明参看pre函数。"""
        pass

    def pre_yield(self): 
        """成功匹配后，子项迭代前是否返回pre函数的处理结果。"""
        return False

    def post_yield(self): 
        """成功匹配后，子项迭代后是否返回pre函数的处理结果。"""
        return False

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

    def pre_yield(self): return True
        
    
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
        