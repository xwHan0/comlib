"""
* Qmar：树遍历引擎
* 常用迭代器
"""


from comlib.iterators import  CommonIterator, Counter, LinkList, interpose
from comlib.iterator_operator import *

from comlib.mapreduce.pred import Pred
from comlib.mapreduce.proc import Proc, ProcMap, ProcReduce, ProcIter

from comlib.mapreduce.qmar import Qmar


from comlib.ex.math import xmin,xmax,xceil

from comlib.allreduce import xmap,xrange
from comlib.allreduce import xapply

