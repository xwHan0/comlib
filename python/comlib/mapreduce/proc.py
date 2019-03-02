
import types

class Proc:
    """处理动作基类。

    * result: 保存于Query中的处理结果Result类实例。其内容由用户自己在pre和post函数中定义。
        -- rst: 初始化和最终返回结果变量

    * datum: 当前处理的树结构节点集合。

    * stack: 当前遍历堆栈。其每一个节点内容包含：
        -- datum: datum的影子；
        -- sta: 节点遍历状态<PRE|POST|DONE>。赋值DONE状态将导致迭代终止。
        -- pred_idx: 节点对应的Pred序号
        -- children: 子元素迭代器。该域为None表示当前节点为叶子节点
        -- pred: 匹配条件对象
      stack中最后一个元素为当前遍历的元素；倒数第二个元素为当前节点的父元素; ...; 第一个节点为根节点。
    """
    
    def pre(self, result, *datum, stack=[]): 
        """子项迭代前的处理动作函数。"""
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

    def actions(self,result):
        """按照result的结果返回处理动作：(is_pre, is_pre_yield, is_post, is_post_yield)"""
        return (False, False, False, False)
        

class ProcQMar(Proc):
    def pre(self, result, *datum, stack=[]): 
        return datum[0].pre(result, *datum, stack=stack)

    def post(self, result, *datum, stack=[]): 
        return datum[0].post(result, *datum, stack=stack)


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
        