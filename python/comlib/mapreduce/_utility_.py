
            
def function_argument_fill(func, *keys):


if 'stack' in pred.__code__.co_varnames:    # pred函数包含stack参数
                arg_num = pred.__code__.co_argcount-1
                if arg_num == -1:
                    def match_i(self, *datum, stack=[]): 
                        return pred(*datum, stack=stack)
                else:
                    def match_i(self, *datum, stack=[]): 
                        return pred(*(datum[:arg_num]), stack=stack)
            else:
                arg_num = pred.__code__.co_argcount
                if arg_num == 0:
                    def match_i(self, *datum, stack=[]):
                        return pred(*datum)
                else:
                    def match_i(self, *datum, stack=[]):
                        return pred(*(datum[:arg_num]))
