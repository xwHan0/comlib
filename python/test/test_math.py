import sys
from pathlib import Path
p = Path(__file__)
q = p.parents[1]

sys.path.append(str(q))

# print(sys.path)


from comlib.ex.math import xgcd, xlcm, xsumproduct

class TestMath(object):
    def test_gcd_null(self): assert xgcd() == 0
    def test_gcd_one(self): assert xgcd(150) == 150
    def test_gcd_two(self): assert xgcd(2,3) == 1
    def test_gcd_three(self): assert xgcd(2,4,6) == 2
    def test_gcd_common(self): assert xgcd( 30, 15, 10 ) == 5
    def test_gcd_seq(self): assert xgcd(200, [300, 50], 150) == 50

    def test_lcm_null(self): assert xlcm() == 0
    def test_lcm_one(self): assert xlcm(150) == 150
    def test_lcm_two(self): assert xlcm(2,3) == 6
    def test_lcm_three(self): assert xlcm(2,3,5) == 30
    def test_lcm_common(self): assert xlcm( 2, 4, 8, 16 ) == 16
    def test_lcm_seq(self): assert xlcm(2, [3, 4], 5) == 60

    def test_sumproduct(self): assert xsumproduct( [1,2,3], [4,5,6] ) == 32








