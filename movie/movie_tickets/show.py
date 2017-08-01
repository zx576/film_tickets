# coding=utf-8
# author = zhouxin

import threading

from spiders.time import Time
from spiders.nuomi import Nuomi
from spiders.taopiaopiao import TaoPiaoPiao
from spiders.meituan import MeiTuan

def show_shce(res, supplier):

    print('=============================')
    print('数据提供商: {}'.format(supplier))

    for i in res:
        print(i)

def time_(*args):
    print('show',*args)
    ti = Time()
    res = ti.get_movie_from_time(*args)
    show_shce(res, '时光网')

def nuomi_(*args):
    nm = Nuomi()
    res = nm.get_movie_from_nuomi(*args)
    show_shce(res, '糯米')

def taopp_(*args):
    tpp = TaoPiaoPiao()
    res = tpp.get_movie_from_taopp(*args)
    show_shce(res, '淘票票')

def meituan_(*args):
    mt = MeiTuan()
    res = mt.get_movie_from_meituan(*args)
    show_shce(res, '美团')


sup = [time_, nuomi_, taopp_, meituan_]

def _search(*a):

    Threads = []
    for i in sup:
        Threads.append(threading.Thread(target=i, args=(*a,)))

    for j in Threads:
        j.start()

    for k in Threads:
        k.join()

_search('上海', '闵行', '保利', '悟空')

# time_('上海', '闵行', '保利', '悟空')
# nuomi_('上海', '闵行', '保利', '悟空')
# taopp_('上海', '闵行', '保利', '悟空')
# meituan_('上海', '闵行', '保利', '悟空')
