# coding=utf-8
# author = zhouxin
# date = 2017.7.5

# description
# 包装一些爬取 美团 网站的数据库方法
import sqlite3

from movie.movie_tickets.settings import DATABASE
from movie.movie_tickets.database.gene_dt import GeneDt


# 继承一些通用的数据库操作方法
class MeiTuan_Dt(GeneDt):

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE)
        self.build_or_conn('Meituan')
        self.dtname = 'Meituan'


# mt = MeiTuan_Dt()
# mt.insert('秦皇岛', '北戴河区', '北戴河影谷影院', 'http://qhd.meituan.com/shop/5441476', '北戴河区联峰北路80号（北戴河舌尖美食城）')
# mt.showall()
# res = mt.search('秦皇岛', '北戴河', '影谷')
# print(res)