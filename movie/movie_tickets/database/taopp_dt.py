# coding=utf-8
# author = zhouxin
# date = 2017.7.7
# description
# 淘票票数据库方法

import sqlite3

from movie.movie_tickets.database.gene_dt import GeneDt
from movie.movie_tickets.settings import DATABASE

class TaoppDt(GeneDt):

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE, timeout=10)
        self.build_or_conn('Taopp')
        self.dtname = 'Taopp'

if __name__ == '__main__':
    pass
    # tpp = TaoppDt()
    # tpp.insert()
    # res = tpp.search('苏州', '相城', '幸福蓝海')
    # res = tpp.search('苏州', '相城', '幸福蓝海')
    # print(res)
    # tpp.showall()
    # tpp.delete_all()
    # tpp.showall()
