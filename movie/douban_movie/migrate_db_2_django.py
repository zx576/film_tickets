# coding=utf-8
# author = zhouxin
# date = 2017.7.25
# description
# 将之前在 movie_ticket 项目中产生的数据迁移到 django 数据库中

import os, django
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

import Levenshtein

from movie.models import CinemaUrl
from movie.movie_tickets.database.taopp_dt import TaoppDt
from movie.movie_tickets.database.nuomi_dt import NuomiDt
from movie.movie_tickets.database.Time_dt import TimeDt


class Migration:

    def __init__(self):
        self.tpp = TaoppDt()
        self.nm = NuomiDt()
        self.ti = TimeDt()

    # 以淘票票数据作为比对基础
    # 不做处理，直接存入
    def ini_tpp(self):


        count = 0
        for item in self.tpp.extract():

            # if count == 10:
            #     break
            # count += 1
            # city,district,location,cinema_name,taopp_url = item[1], item[2], item[5], item[3], item[4]
            # print(city,district,location,cinema_name,taopp_url)
            CinemaUrl.objects.create(
                city=item[1],
                district=item[2],
                location=item[5],
                cinema_name=item[3],
                taopp_url=item[4],
                code=item[0]

            )
            # break

    # 优化 district 字段
    def _optimize_district(self):
        query = CinemaUrl.objects.all()
        for i in query:
            position = i.district
            if '市' in position:
                district = position.split('市')[0] + '市'
            elif '县' in position:
                district = position.split('县')[0] + '县'
            elif '区' in position:
                district = position.split('区')[0] + '区'
            elif '镇' in position:
                district = position.split('区')[0] + '镇'
            else:
                district = position

            if len(district) == 1:
                district = i.city + district

            i.district = district
            i.save()

    # 合并 糯米 table 到 django
    def _add_nuomi(self):

        count_1 = 0
        count_2 = 0
        for item in self.nm.extract():
            # count += 1
            # if count < 100:continue
            # if count == 200: break
            city, district, location, cinema_name, nuomi_url = item[1], item[2], item[5], item[3], item[4]
            # print('--------------------')
            # print(location, cinema_name)
            q_res = self._query_url(city, district, location, cinema_name)
            if q_res:
                # print(q_res)
                q_res.nuomi_url = nuomi_url
                q_res.save()
                count_1 += 1
            else:
                CinemaUrl.objects.create(
                    city=city,
                    district=district,
                    location=location,
                    cinema_name=cinema_name,
                    nuomi_url=nuomi_url,
                    code=0
                )
                count_2 += 1

            print(count_1, count_2)
            # break


    # 查询电影 url
    def _query_url(self, city, district, location, cinema_name):
        # 梯次比对
        query = CinemaUrl.objects.filter(city__contains=city)
        if not query:
            return

        # 梯次一： 直接比较电影院名
        query_c_name = query.filter(cinema_name__contains=cinema_name)
        if len(query_c_name) == 1:
            # print('梯次一比较')
            return query_c_name[0]

        # 梯次二：模糊比较电影院名
        rates = []
        for idx in range(len(query)):
            rate1 = Levenshtein.ratio(query[idx].cinema_name, cinema_name)
            if rate1 > 0.7:
                return query[idx]
            rate2 = Levenshtein.ratio(query[idx].location, location)
            if rate2 > 0.7:
                return query[idx]
            rates.append(rate1*rate2)

        if max(rates) < 0.2:
            return None
        i = rates.index(max(rates))
        return query[i]

    # 合并 时光网 数据
    def _time(self):
        count_1 = 1
        count_2 = 2
        for item in self.ti.extract():
            city, district, location, cinema_name, time_url = item[1], item[2], item[5], item[3], item[4]
            # print(city, district, location, cinema_name, time_url)
            q_res = self._query_url(city, district, location, cinema_name)
            if q_res:
                # print(q_res)
                q_res.time_url = time_url
                q_res.save()
                count_1 += 1
            else:
                CinemaUrl.objects.create(
                    city=city,
                    district=district,
                    location=location,
                    cinema_name=cinema_name,
                    time_url=time_url,
                    code=0
                )
                count_2 += 1
            print(count_1, count_2)
            # break

    # 如果在正式环境中执行
    # 就赶紧辞职跑路吧
    def _delete(self):
        m = CinemaUrl.objects.all()
        m.delete()

    def _test(self):

        query = CinemaUrl.objects.filter(city__contains='随州')
        print(len(query))

    def _show_all(self):

        query = CinemaUrl.objects.all()
            # .filter(time_url__startswith='http').filter(nuomi_url__startswith='http').filter(taopp_url__startswith='http')
            # filter(city__contains='上海')
            # .filter(time_url__startswith='http').filter(nuomi_url__startswith='http').filter(taopp_url__startswith='http')
        print(len(query))

        city_lst = []
        # ============================
        # for item in query:
        #     if item.city in city_lst:
        #         continue
        #     city_lst.append(item.city)
        # print(city_lst)
        # print(len(city_lst))
        # ============================
        # for i in query:
            # print(i.city, i.district, i.cinema_name, i.location)

        # =============================
        # dct = {'subjects': []}
        # for item in query:
        #     if item.city in dct:
        #         city_lst = dct[item.city]
        #         if item.district in city_lst:
        #             continue
        #         else:
        #             dct[item.city].append(item.district)
        #
        #     else:
        #         dct[item.city] = [item.district,]
        #
        # print(dct)
        # ==============================
        # def find_city(c):
        #     item_lst = dct.get('subjects')
        #     for i in range(len(item_lst)):
        #         city_name = item_lst[i]['city'].replace(' ', '')
        #         c = c.replace(' ', '')
        #         if city_name == c:
        #             return i
        #
        # def find_dis(lst, dis):
        #     for i in range(len(lst)):
        #         if lst[i]['name'] == dis:
        #             return i
        #
        # def find_cine(lst, name):
        #     for i in range(len(lst)):
        #         if lst[i]['name'] == name:
        #             return i
        #
        #
        # for item in query:
        #
        #     idx = find_city(item.city)
        #     if idx:
        #         dis_lst = dct.get('subjects')[idx].get('dis')
        #         dis_idx = find_dis(dis_lst, item.district)
        #         if dis_idx:
        #             cine_lst = dis_lst[dis_idx].get('cinemas')
        #             cine_idx = find_cine(cine_lst, item.cinema_name)
        #             if not cine_idx:
        #                 new_cine = {
        #                     'name': item.cinema_name,
        #                     'location': item.location,
        #                     'code': item.id
        #                 }
        #                 dct.get('subjects')[idx].get('dis')[dis_idx].get('cinemas').append(new_cine)
        #         else:
        #             new_dis = {
        #                 'name': item.district,
        #                 'cinemas':[
        #                     {
        #                         'name': item.cinema_name,
        #                         'location': item.location,
        #                         'code': item.id
        #                     }
        #                 ]
        #             }
        #             dct.get('subjects')[idx].get('dis').append(new_dis)
        #     else:
        #         new_c = {
        #             'city': item.city,
        #             'dis':[
        #                 {
        #                     'name': item.district,
        #                     'cinemas': [
        #                         {
        #                             'name': item.cinema_name,
        #                             'location': item.location,
        #                             'code': item.id
        #                         }
        #                     ]
        #                 }
        #             ]
        #         }
        #         dct['subjects'].append(new_c)
        #
        #
        # print(dct)

    # def _show_all_cine(self):


if __name__ == '__main__':
    m = Migration()

    m._show_all()
