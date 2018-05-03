
class Middleware:
    """Middleware处理基类
    
    Raises:
        ValueError -- [description]
    
    Returns:
        [type] -- [description]
    """

    def __init__(self, handler=None):
        self.handler=handler
    
    def set_handler(self, handler):
        if isinstance(handler, middleware):
            self.handler=handler
        else:
            raise ValueError('Middleware handler is not a middleware instance!')

    def proc(self, *ins):
        if self.handler and type(self.handler)!=Middleware:
            return self.handler.proc(*ins)
        else:
            return ins

    def wrapper(*middlewares):
        """串联多个middlewares，返回一个统一的处理函数
        """
        L=len(middlewares)
        if L==0:         #当输入Middleware个数为0时，返回默认Middleware的处理函数
            def wrapper_inner(*ins):
                m=Middleware()
                return m.proc(*ins)
            return wrapper_inner    #返回函数
        elif L==1:       #当处理到最后一个Middleware时
            def wrapper_inner(*ins):
                m=middlewares[0]    #获取唯一一个middleware的instance。
                if isinstance(m,Middleware) and type(m)!=Middleware
                    return m.proc(*ins) #注意：middlewares成了闭包变量
                else:
                    raise ValueError('Parameter middlewares[0] is not a instance of Middleware!')
            return wrapper_inner    #返回函数
        else:
            for i in range(L-1)；#设置Middleware串联
                middlewares[i].set_handler(middlewares[i+1])
            def wrapper_inner(*ins):
                m=middlewares[0]    #获取唯一一个middleware的instance。
                if isinstance(m,Middleware) and type(m)!=Middleware
                    return m.proc(*ins) #注意：middlewares成了闭包变量
                else:
                    raise ValueError('Parameter middlewares[0] is not a instance of Middleware!')
            return wrapper_inner

