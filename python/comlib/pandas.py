
import numpy as np 
import pandas as pd 

def index(data, names=None, mode='auto'):
    """根据数据结构类型，调用对应的函数，生成一个Index"""
    if len(data):
        if mode == 'series':
            return pd.Index(data)
            
        if isinstance(data, list):
            if isinstance(data[0], list):
                return pd.MultiIndex.from_arrays(data, names=names)
            elif isinstance(data[0], tuple):
                return pd.MultiIndex.from_tuples(data, names=names)
            else:
                return pd.Index(data)
        elif isinstance(data, tuple):
            if isinstance(data[0], list):
                return pd.MultiIndex.from_product(data, names=names)
        elif isinstance(data, dict):
            ns = []
            ar = []
            for k,v in data:
                ns.append(k)
                ar.append(v)
            names = names if names else ns
            return pd.MultiIndex.from_arrays(ar, names=names)
        
    return None



class JoinIndex:
    pass


def join(left, right, left_on=None, right_on=None, how='inner', indicator=False):

    if left_on == JoinIndex:
        left_on = None
        left_index = True
    else:
        left_index = False

    if right_on == JoinIndex:
        right_on = None
        right_index = True
    else:
        right_index = False

    return pd.merge( left=left, right=right, left_on=left_on, right_on=right_on,
        left_index=left_index, right_index=right_index, how=how, indicator=indicator )
