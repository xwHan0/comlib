import sys, os
sys.path.append( (os.path.abspath(os.path.join(os.path.dirname(__file__), './'))) )

print(sys.path)

from comlib.utilis.argument import SeriesElement, SeriesIter, SeriesMixElement, SeriesMixIter, SeriesAuto
from comlib.utilis.argument import series_argument_proc, flatten

class TestSeriesArgument:

    def test_bypass(self):
        """输入参数Bypass测试"""
        assert series_argument_proc( [1,2,3,4,5] ) == [1,2,3,4,5]

    def test_element(self):
        """元素输入测试"""
        assert series_argument_proc( [SeriesElement, 1,2,3,4,5] ) == [1,2,3,4,5]

    def test_iter(self):
        """迭代器输入测试"""
        assert series_argument_proc( [SeriesIter, [1,2], [3,4], [5]] ) == [1,2,3,4,5]

    def test_mix_basic(self):
        """基本的混合测试"""
        assert series_argument_proc([
            SeriesMixElement, 1,2,3,
            SeriesMixIter, [4,5],[6,7],
            SeriesMixElement, 8, 9,
            SeriesIter, [10,11],[12]
        ]) == [1,2,3,4,5,6,7,8,9,10,11,12]

    def test_auto_basic(self):
        """自动推导测试"""
        assert series_argument_proc([
            SeriesAuto,
            1,2,3,
            [4,5,6],[7,8],
            9,10,
            [11],[12],
            13
        ]) == [1,2,3,4,5,6,7,8,9,10,11,12,13]

    def test_recur_basic(self):
        """迭代测试"""
        assert series_argument_proc([
            SeriesMixElement, 1,2,
            SeriesMixIter, [3,4], [SeriesMixElement,5,SeriesMixIter,[6,7],SeriesMixElement,8,9],
            SeriesMixElement,10,
            SeriesMixIter, [SeriesMixElement,11,SeriesMixIter,[SeriesMixIter,[12,13],SeriesMixElement,14],SeriesMixElement,15]
        ]) == [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

    def test_auto_recur(self):
        """基本的Auto测试"""
        assert series_argument_proc([
            SeriesAuto,
            1,2,
            [[3,4],5],[6,[7,[[8,9],10]]],11
        ]) == [1,2,3,4,5,6,7,8,9,10,11]


class TestFlatten:
    def test_default(self):
        assert list(flatten( [1,2,3,4,5] )) == [1,2,3,4,5]

    def test_element(self):
        assert list(flatten( [SeriesElement, 1,2,3,4,5] )) == [1,2,3,4,5]

    def test_iter(self):
        assert list(flatten( [SeriesIter, [1,2],[3],[4,5]] )) == [1,2,3,4,5]

    def test_iter_recur(self):
        assert list(flatten( [SeriesIter, [1, SeriesIter, [2,3]], [4,5]] )) == [1,2,3,4,5]

    def test_iter_element(self):
        assert list(flatten( [1, SeriesIter, [2,3], SeriesElement, 4, 5] )) == [1,2,3,4,5]

    def test_auto(self):
        assert list(flatten([
            SeriesAuto,
            1,2,3,
            [4,5,6],[7,8],
            9,10,
            [11],[12],
            13
        ])) == [1,2,3,4,5,6,7,8,9,10,11,12,13]