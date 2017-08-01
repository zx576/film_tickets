# coding=utf-8
# author = zhouxin
# date = 2017.7.26
# description
# 获取 tpp 城市代码


from movie.movie_tickets.database.taopiaopiao_citycode import city


def rebuild_city():

    dct = {}

    city_dct = city.get('returnValue')
    for k, v in city_dct.items():
        dct[k] = []
        for i in v:
            dct[k].append(i.get('regionName'))


    print(dct)

rebuild_city()