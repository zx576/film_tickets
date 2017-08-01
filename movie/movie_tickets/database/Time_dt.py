# coding=utf-8
# author = zhouxin
# date = 2017.7.20
# description
# 时光网数据

import sqlite3

from movie.movie_tickets.settings import DATABASE
from movie.movie_tickets.database.gene_dt import GeneDt


class TimeDt(GeneDt):

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE)
        self.build_or_conn('Time')
        self.dtname = 'Time'

    def _insert_dis(self, pk, district):

        sql = 'UPDATE {0} SET LOCATION = "{1}" WHERE ID = {2}'.format(
            self.dtname, district, pk
        )
        print(sql)
        self.conn.execute(sql)
        self.conn.commit()
        return True


if __name__ == '__main__':
    td = TimeDt()
    td.showall()