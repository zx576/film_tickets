# coding=utf-8
# author = zhouxin
# date = 2017.7.20
# description
# 糯米网数据相关

import sqlite3

from movie.movie_tickets.database.gene_dt import GeneDt
from movie.movie_tickets.settings import DATABASE


class NuomiDt(GeneDt):

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE, timeout=10)
        self.build_or_conn('Nuomi')
        self.dtname = 'Nuomi'


if __name__ == '__main__':
    nm = NuomiDt()
    nm.showall()