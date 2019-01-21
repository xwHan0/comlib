__all__ = [
    'ReduceBase',
    'ReduceInit',
    'ReduceFunction',
]

class ReduceBase:
    pass


class ReduceInit(ReduceBase):
    def __init__(self, proc, initial):
        self.proc = proc
        self.init = initial

    def reduce(self, last, next): return self.proc(last, next)
    def initial(self, *nodes): return self.init(*nodes)
    def post(self, last, *nodes): return last


class ReduceFunction(ReduceBase):
    def __init__(self, proc, initial=None, post=None):
        self.proc = proc

        if initial == None:
            def init_none(self, *nodes):
                return nodes[0]
            self.initial = init_none
        else:
            def init_func(self, *nodes):
                return initial(*nodes)
            self.initial = init_func

        if post == None:
            def post_none(self, last, *nodes):
                return last
            self.post = post_none
        else:
            def post_func(self, last, *nodes):
                return post(self, last, *nodes)
            self.post = post_func 


    def reduce(self, next, last):
        return self.proc( last, next )

    