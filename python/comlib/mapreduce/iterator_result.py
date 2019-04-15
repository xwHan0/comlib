
from comlib.mapreduce import Child

class Result(Child):
    def __init__(self, **keys):
        for k,v in keys.items():
            setattr(self, k, v)

