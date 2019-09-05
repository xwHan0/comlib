import sys, os
sys.path.append( (os.path.abspath(os.path.join(os.path.dirname(__file__), './'))) )

print(sys.path)


from comlib.iterator import tree,index

class TestTree:

    def test_tree_basic(self):
        """数组全遍历"""
        a = [10,20,30]
        rst = []
        for _ in range(5):
            rst += [n.value[0] for n in tree(a)]
        assert rst == [[10,20,30], 10, 10, 20, 20, 30, 30, [10,20,30]]*5

    def test_array_basic(self):
        """基本数据遍历"""
        a = [10,20,30]
        rst = []
        for _ in range(5):
            rst += [n.value[0] for n in tree(a) if n.status==0][1:]
        assert rst == [10, 20, 30]*5


class TestIndex:
    def test_index_basic(self):
        """基本的index测试"""
        a = [10,20,[30,40],50]
        rst = [n.value[1].idx for n in tree(a, index()) if n.status==0]
        assert rst == [[], [0], [1],[2],[2,0],[2,1],[3]]


from comlib import Qmar
from comlib import Pred, Proc
from comlib.mapreduce import Match, Child
from comlib.mapreduce import ResultTree
from comlib.mapreduce.tree import Index


class node:
    def __init__(self, v, sub=[]):
        self.sub = sub
        self.val = v

def children(node, idx):
    if len(idx) == 1:
        return node.sub
    else:
        return node


node0 = node(100, [node(200),node(300)])


class TestBasic:
    # def test_1d_array(self):
    #     """简单数组测试"""
    #     a = [10,20,30,40]
    #     que = Qmar(a).skip().all()
    #     r =[]
    #     for _ in range(5):
    #         r += [x for x in que]
    #     assert r == [10,20,30,40]*5

    def test_func_pred(self):
        """简单条件匹配测试"""
        a = [1,2,3,4,5,6,7]
        que = Qmar(a).skip().filter(lambda x:x%2==0)
        r = []
        for _ in range(3):
            r += [x for x in que]
        assert r == [2,4,6]*3
        
    def test_1d_array_index(self):
        """简单数组+Index测试"""
        a = [10,20,30,40]
        que = Qmar(a, Index()).skip().all()
        r = []
        for _ in range(3):
            r += [(idx.idx(), x) for x,idx in que]
        assert r == [([0],10),([1],20),([2],30),([3],40)]*3

    def test_3d_array_index(self):
        """多维数组+Index+简单Filter测试"""
        a = [10, [20, 30], [40, [[50,60], 70, 80], 90]]
        r = [(idx.idx(), x) for x,idx in Qmar(a, Index()).skip().filter(lambda x: type(x)==int)]
        assert r == [([0], 10), ([1,0], 20), ([1,1], 30), ([2,0], 40), ([2,1,0,0], 50), 
            ([2,1,0,1], 60), ([2,1,1], 70), ([2,1,2], 80), ([2,2], 90)]

    def test_2d_list(self):
        """简单树+ChildSub测试"""
        n1 = node(1000)
        n2 = node(2000)
        n0 = node(100, [n1, n2])
        que = Qmar(n0).child(node,'sub').all()
        r =[]
        for _ in range(3):
            r += [x.val for x in que]
        assert r == [100, 1000, 2000]*3

    def test_hybrid(self):
        """数组+树复合数据 + Index"""
        n0 = node(100)
        n0.sub = [100,200,300]
        n1 = node(200)
        n1.sub = [1000,2000,3000]
        a = [n0, n1]
        r = [(idx.idx(), x) for x,idx in Qmar(a, Index()).child(node,'sub').all() if isinstance(x, int)]
        assert r == [([0,0], 100), ([0,1], 200), ([0,2], 300), ([1,0], 1000), ([1,1], 2000), ([1,2], 3000)]

    def test_select_object(self):
        """数组+树复合数据 + 简单Filter字符串"""
        n0 = node(100)
        n0.sub = [100,200,300]
        n1 = node(200)
        n1.sub = [1000,2000,3000]
        a = [n0, n1]
        r = [x.val for x in Qmar(a).child(node,'sub').filter(lambda x : type(x)==node)]
        assert r == [100,200]
        
    def test_select_condition(self):
        """复杂数据 + 复杂Filter字符串 + 字符串下一跳"""
        n1, n2 = (node(200), node(300))
        n0 = node(100, [n1, n2])
        r = [x.val for x,i in Qmar(n0, Index()).child(node,'sub').filter('*[not (#0.val==300)]')]
        assert r == [100,200]


def result_tree_pre(*nodes):
    nodes[1].rst = nodes[0].val + 5
    return None

class TestIterator:
    def test_result_tree(self):
        rst = Qmar(node0, ResultTree()) \
                .child(node, 'sub') \
                .match(Match(pre=result_tree_pre)) \
                .result()
        assert rst.rst==105 and rst[0].rst==205 and rst[1].rst==305


class TestMap:
    def test_map_commom(self):
        rst = [x for x in Qmar([1,2,3,4]).skip().map(lambda x:x+10)]
        assert rst == [11,12,13,14]


def reduce_proc(last, next): 
    if last:
        return last + next.val
    else:
        return next.val


# class TestReduce:
#     def test_reduce_common(self):
#         n1, n2 = (node(1000), node(2000))
#         n0 = node(3000, [n1, n2])
#         r = Query(n0, children='sub').reduce(reduce_proc, None)
#         assert r == 6000


#########################################################################################
# class MyQMar(Match, Child):
#     def __init__(self, v, sub=[]):
#         super().__init__(pred=Match.NONE, pre=Match.NONE)
#         self.v = v
#         self.subs = sub

#     def sub(self, *datum):
#         return self.subs

#     def match(self,*datum, stack=[]):
#         return datum[0].v % 2 == 0

#     def pre(self, *datum, stack=[]):
#         return datum[0].v + 100


# class TestQMar:
#     def test_common_qmar(self):
#         node = MyQMar(0, [MyQMar(i) for i in range(1,5)])
#         r = [x for x in Qmar(node).all()]
#         assert r == [100,102,104]


class TestPerformance:
    def test_1d_array(self):
        """简单数组测试"""
        a = [10,20,30,40]
        que = Qmar(a).skip().all()
        for _ in range(100000):
            r = [x for x in que]
            assert r == [10,20,30,40]

### Last 7.40 seconds
