# coding = utf-8
# author = zhouxin
# date = 2017.7.7

# description
# 通用的一些数据库操作方法

from movie.movie_tickets.utils import decorators
import sqlite3
from movie.movie_tickets.settings import DATABASE

class GeneDt:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE)
        self.dtname = ''

    def build_or_conn(self, table):

        check_table_sql = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name= '{}';".format(table)
        build_table_sql = '''
            CREATE TABLE '{}'
            (
              ID INTEGER PRIMARY KEY NOT NULL,
              CITY TEXT,
              DISTRICT TEXT,
              CINEMA_NAME TEXT,
              CINEMA_URL TEXT,
              LOCATION TEXT
            );
        '''.format(table)

        query = self.conn.execute(check_table_sql).fetchone()[0]
        if query == 0:
            self.conn.execute(build_table_sql)

    # 插入内容
    # @decorators.make_print  # 打印输出查看函数运行
    def insert(self, *args):
        assert len(args) == 5, 'not enough parameter'

        sql = r'''
                INSERT INTO {0}(
                ID, CITY, DISTRICT, CINEMA_NAME, CINEMA_URL, LOCATION
                )
                VALUES (NULL, "{1}", "{2}", "{3}", "{4}", "{5}")
            '''.format(self.dtname, *args)

        self.conn.execute(sql)
        self.conn.commit()
        return True

    # 查找影院信息，返回影院 url
    def search(self, *args):
        # print(args)
        assert len(args) == 3, 'not enough parameter'

        sql = r'''
                SELECT CINEMA_URL FROM {3} WHERE CITY == '{0}' AND DISTRICT LIKE '%{1}%' AND CINEMA_NAME LIKE '%{2}%';
            '''.format(*args, self.dtname)

        # print(sql)
        query = self.conn.execute(sql)
        cinema = query.fetchone()

        # print(cinema)
        return cinema[0] if cinema else None

    def delete_all(self):

        sql = 'DELETE from {} where CITY != "";'.format(self.dtname)
        self.conn.execute(sql)
        self.conn.commit()
        # self.conn.close()

    def extract(self):
        sql = r'''
                        SELECT * FROM {};
                    '''.format(self.dtname)

        query = self.conn.execute(sql)
        all_cinema = query.fetchall()
        for i in all_cinema:
            yield i

    # 显示所有内容
    def showall(self):
        sql = r'''
                SELECT * FROM {};
            '''.format(self.dtname)

        query = self.conn.execute(sql)
        all_cinema = query.fetchall()
        print(all_cinema[0])
        # print(len(all_cinema))
        # count = 0
        # for i in all_cinema:
        #     # if count < 2800: continue
        #     if count == 3000: break
        #     print(i)
        #     count += 1




# ss = GeneDt()