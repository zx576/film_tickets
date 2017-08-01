# coding=utf-8
# author = zhouxin
# date = 2017.7.5
# description
# 目前为一些调试用的装饰器

from functools import wraps


# 完成函数， 打印参数
def make_print(func):
    @wraps(func)
    def func_ins(*args):

        func(*args)
        print('完成 {0} 函数，参数为{1}'.format(func.__name__, args))
        return True

    return func_ins

