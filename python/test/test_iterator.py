import sys, os
sys.path.append( (os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) )

from comlib import iterator, Index, ChildSub, ChildAttr

class node:
    def __init__(self, v, sub=[]):
        self.sub = sub
        self.val = v

def gnxt(node, idx):
    if len(idx) == 1:
        return node.sub
    else:
        return node

class TestIterator:
    def test_1d_array(self):
        """简单数组测试"""
        a = [10,20,30,40]
        r = [x for x in iterator(a)]
        assert r == [10,20,30,40]

    def test_1d_array_index(self):
        """简单数组+Index测试"""
        a = [10,20,30,40]
        r = [(idx.idx(), x) for x,idx in iterator(a).assist(Index())]
        assert r == [([0],10),([1],20),([2],30),([3],40)]

    def test_3d_array_index(self):
        """多维数组+Index+简单Filter测试"""
        a = [10, [20, 30], [40, [[50,60], 70, 80], 90]]
        r = [(idx.idx(), x) for x,idx in iterator(a,'int').assist(Index())]
        assert r == [([0], 10), ([1,0], 20), ([1,1], 30), ([2,0], 40), ([2,1,0,0], 50), 
            ([2,1,0,1], 60), ([2,1,1], 70), ([2,1,2], 80), ([2,2], 90)]

    def test_2d_list(self):
        """简单树+ChildSub测试"""
        n1 = node(1000)
        n2 = node(2000)
        n0 = node(100, [n1, n2])
        r = [x.val for x in iterator(n0, gnxt={node : ChildAttr('sub')})]
        assert r == [100, 1000, 2000]

    def test_hybrid(self):
        """数组+树复合数据 + Index"""
        n0 = node(100)
        n0.sub = [100,200,300]
        n1 = node(200)
        n1.sub = [1000,2000,3000]
        a = [n0, n1]
        r = [(idx.idx(), x) for x,idx in iterator(a, gnxt={node:ChildAttr('sub')} ).assist(Index()) if isinstance(x, int)]
        assert r == [([0,0], 100), ([0,1], 200), ([0,2], 300), ([1,0], 1000), ([1,1], 2000), ([1,2], 3000)]

    def test_select_object(self):
        """数组+树复合数据 + 简单Filter字符串"""
        n0 = node(100)
        n0.sub = [100,200,300]
        n1 = node(200)
        n1.sub = [1000,2000,3000]
        a = [n0, n1]
        r = [x.val for x in iterator(a, gnxt={node: ChildAttr('sub')}, sSelect='node' )]
        assert r == [100,200]
        
    def test_select_condition(self):
        """复杂数据 + 复杂Filter字符串 + 字符串下一跳"""
        n1, n2 = (node(200), node(300))
        n0 = node(100, [n1, n2])
        r = [x.val for x,i in iterator(n0, gnxt={node:'sub'}, sSelect='*[not (#0.val==300)]').assist(Index())]
        assert r == [100,200]