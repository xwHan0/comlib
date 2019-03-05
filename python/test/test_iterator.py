import sys, os
sys.path.append( (os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) )

from comlib import Index, ChildSub, ChildAttr, Query
from comlib import Pred, Proc


class node:
    def __init__(self, v, sub=[]):
        self.sub = sub
        self.val = v

def children(node, idx):
    if len(idx) == 1:
        return node.sub
    else:
        return node

class TestIterator:
    def test_1d_array(self):
        """简单数组测试"""
        a = [10,20,30,40]
        que = Query(a).skip()
        r =[]
        for i in range(5):
            r += [x for x in que]
        assert r == [10,20,30,40]*5

    def test_func_pred(self):
        """Test """
        a = [1,2,3,4,5,6,7]
        que = Query(a, query=lambda x:x%2==0).skip()
        r = []
        for i in range(3):
            r += [x for x in que]
        assert r == [2,4,6]*3
        
    def test_1d_array_index(self):
        """简单数组+Index测试"""
        a = [10,20,30,40]
        que = Query(a, Index()).skip()
        r = []
        for i in range(3):
            r += [(idx.idx(), x) for x,idx in que]
        assert r == [([0],10),([1],20),([2],30),([3],40)]*3

    def test_3d_array_index(self):
        """多维数组+Index+简单Filter测试"""
        a = [10, [20, 30], [40, [[50,60], 70, 80], 90]]
        r = [(idx.idx(), x) for x,idx in Query(a, Index(), query='int').skip()]
        assert r == [([0], 10), ([1,0], 20), ([1,1], 30), ([2,0], 40), ([2,1,0,0], 50), 
            ([2,1,0,1], 60), ([2,1,1], 70), ([2,1,2], 80), ([2,2], 90)]

    def test_2d_list(self):
        """简单树+ChildSub测试"""
        n1 = node(1000)
        n2 = node(2000)
        n0 = node(100, [n1, n2])
        que = Query(n0, children={node : ChildAttr('sub')})
        r =[]
        for i in range(3):
            r += [x.val for x in que]
        assert r == [100, 1000, 2000]*3

    def test_hybrid(self):
        """数组+树复合数据 + Index"""
        n0 = node(100)
        n0.sub = [100,200,300]
        n1 = node(200)
        n1.sub = [1000,2000,3000]
        a = [n0, n1]
        r = [(idx.idx(), x) for x,idx in Query(a, Index(), children={node:ChildAttr('sub')} ) if isinstance(x, int)]
        assert r == [([0,0], 100), ([0,1], 200), ([0,2], 300), ([1,0], 1000), ([1,1], 2000), ([1,2], 3000)]

    def test_select_object(self):
        """数组+树复合数据 + 简单Filter字符串"""
        n0 = node(100)
        n0.sub = [100,200,300]
        n1 = node(200)
        n1.sub = [1000,2000,3000]
        a = [n0, n1]
        r = [x.val for x in Query(a, children={node: ChildAttr('sub')}, query='node' )]
        assert r == [100,200]
        
    def test_select_condition(self):
        """复杂数据 + 复杂Filter字符串 + 字符串下一跳"""
        n1, n2 = (node(200), node(300))
        n0 = node(100, [n1, n2])
        r = [x.val for x,i in Query(n0, Index(), children={node:'sub'}, query='*[not (#0.val==300)]')]
        assert r == [100,200]


class TestMap:
    def test_map_commom(self):
        rst = [x for x in Query([1,2,3,4]).map(lambda x:x+10).skip()]
        assert rst == [11,12,13,14]


def reduce_proc(last, next): 
    if last:
        return last + next.val
    else:
        return next.val


class TestReduce:
    def test_reduce_common(self):
        n1, n2 = (node(1000), node(2000))
        n0 = node(3000, [n1, n2])
        r = Query(n0, children='sub').reduce(reduce_proc, None)
        assert r == 6000


#########################################################################################
class MyQMar(Pred, Proc):
    def __init__(self, v, sub=[]):
        self.v = v
        self.sub = sub

    def match(self,*datum):
        return 1 if datum[0].v % 2 == 0 else 0

    def pre(self, result, *datum, stack=[]):
        result.rst = datum[0].v + 100

    def pre_yield(self): return True


# class TestQMar:
#     def test_common_qmar(self):
#         node = MyQMar(0, sub=[MyQMar(i) for i in range(1,5)])
#         r = [x for x in Query(node, children='sub').clear_pred().append_qmar(MyQMar)]
#         assert r == [100,102,104]