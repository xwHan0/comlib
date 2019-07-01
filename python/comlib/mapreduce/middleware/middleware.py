class MiddleWare:

    def bind(self, qmar): 
        self.qmar = qmar

    def __iter__(self):
        self.qmar.__iter__()
        return self

    def __next__(self):
        return self.qmar.__next__()

    def wm(self, *args):
        args[0].bind_qmar(self)
        return args[0]