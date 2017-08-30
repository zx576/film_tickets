# coding=utf-8
# author = zhouxin
# date = 2017.7.24
# description
# 从 豆瓣 api 获取当前上映的电影

import os, django
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "film_tickets.settings")
django.setup()

from movie.models import Movie

import requests

class DoubanMovie:

    def __init__(self):

        self.url = 'https://api.douban.com/v2/movie/in_theaters'

    # 请求豆瓣 API 返回 json 信息
    def _get_movie(self, url):
        req = requests.get(url)
        req.raise_for_status()
        return req.json()

    # 解析 api 返回的 json 信息
    # 返回一个列表， 包含所有 电影(Movie) 实例
    # 浏览不同的电影票购买网站，发现当前天在映的电影不会超过 10 部
    # 所以取豆瓣结果中 评分不为 0 的电影前 10 部即可
    def _parse_movie(self, dct):

        movie_lst = dct.get('subjects', None)
        # print(movie_lst)
        assert movie_lst
        cur_movies = []
        count = 0
        for m in movie_lst:
            # 只取前十部
            if count >= 10:
                break
            count += 1
            title = m.get('title')
            # 查看该电影是否已经收录
            # 已经收录则继续循环
            added = self._is_included(title)
            if added:
                cur_movies.append(added)
                continue
            # 查看该电影的评分
            # 如果为 0 则说明还未上映，直接跳过
            # MMP,也有可能是评分被关闭了，比如 建军大业
            rate = m.get('rating').get('average')
            # if rate == 0:
            #     continue
            b_url = m.get('images').get('large')
            m_url = m.get('images').get('medium')
            casts = []
            for c in m.get('casts'):
                casts.append(c.get('name'))
            casts = '/'.join(casts)
            directors = []
            for d in m.get('directors'):
                directors.append(d.get('name'))
            directors = '/'.join(directors)
            genes = '/'.join(m.get('genres'))

            # print(title,rate,b_url,m_url,casts,directors,genes)
            new = self._add_movie(title,rate,b_url,m_url,casts,directors,genes)
            cur_movies.append(new)


        # print(cur_movies)
        # print(len(cur_movies))
        return cur_movies

    # 依据电影名查询数据是已经添加进数据库
    #　放回该电影实例如果已存在，否则返回 false
    def _is_included(self, title):

        try:
            m = Movie.objects.get(name=title)
            return m
        except:
            return False

    # 新增电影实例
    def _add_movie(self,title, rate, b_url, m_url, casts, directors, genes):

        new = Movie.objects.create(
            name=title,
            rating=rate,
            poster_url_big=b_url,
            poster_url_me=m_url,
            directors=directors,
            casts=casts,
            genes=genes,
            is_in_theater=True

        )

        return new

    # 检查数据内的电影是否有已经下映的
    # 如果已经下映 修改 is_in_theater 为 False
    def _invalid_old(self, m_lst):
        # print(m_lst)
        m_id = self._set_top(m_lst)
        for movie in m_lst:
            m_id.append(movie.id)

        # print(m_id)
        query = Movie.objects.filter(is_in_theater=True)
        for m in query:
            # print(m.id)
            if m.id not in m_id:
                m.is_in_theater = False
                m.save()

    # 设置评分最高的电影
    def _set_top(self,m_lst):
        top = Movie.objects.filter(is_top=True)
        # print(top)
        max_rate = 0
        if top:
            top_m = top[0]
            max_rate = top_m.rating
            top_m.is_top = False
            top_m.save()
        top_id = 0
        id = []
        for i in range(len(m_lst)):
            id.append(m_lst[i].id)
            if m_lst[i].rating >= max_rate:
                max_rate = m_lst[i].rating
                top_id = i

        top_movie = m_lst[top_id]
        # print(top_movie.name)
        top_movie.is_top = True
        top_movie.save()

        return id

    # 执行
    def run_douban(self):

        movie_json = self._get_movie(self.url)
        movie_lst = self._parse_movie(movie_json)
        self._invalid_old(movie_lst)


    # ===============
    def _test(self):
        query = Movie.objects.all()
        for i in query:
            # print(i.is_in_theater)

            i.is_in_theater = True
            i.save()

if __name__ == '__main__':

    db = DoubanMovie()
    db.run_douban()
# db._test()
