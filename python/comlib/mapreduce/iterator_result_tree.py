
from comlib.mapreduce import CommonIterator

class ResultTree(CommonIterator):
    def __init__(self):
        self.sub = []

    def sub(self, *node):
        self.sub.append(ResultTree())
        return self.sub[-1]

    def __iter__(self):
        return self.sub