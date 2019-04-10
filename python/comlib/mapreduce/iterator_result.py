
from comlib.mapreduce import CommonIterator

class Result(CommonIterator):
    def __init__(self, **keys):
        for k,v in keys.items():
            setattr(self, k, v)


class ResultTree(CommonIterator):
    def __init__(self):
        self.subs = []

    def sub(self, *node):
        self.subs.append(ResultTree())
        return self.subs[-1]

    def __iter__(self):
        return iter(self.subs)