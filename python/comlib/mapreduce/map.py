
__all__ = [
    'MapFunction',
    'MapBypass',
]
    

#### 定义直接透传关系
class MapBypass:
    def map(self,*node):
        return node[0]


class MapFunction:
    def __init__(self,func):
        self.func = func
        
    def map(self,*node):
        return self.func(*node)







 

