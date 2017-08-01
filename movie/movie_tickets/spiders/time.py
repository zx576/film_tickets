# coding=utf-8
# author = zhouxin
# date = 2017.7.20
# description
# 时光网电影票信息

import bs4
import re
import json
import threading
import time
import queue
import datetime

from movie.movie_tickets.utils.req import Rep
from movie.movie_tickets.database.timecitycode import timeData
from movie.movie_tickets.database.Time_dt import TimeDt

class Time:

    def __init__(self):

        self.rp = Rep()
        self.rooturl = 'http://theater.mtime.com/'
        self.td = TimeDt()
        self.qe = queue.Queue()

    # ===================================================================================
    # 等号之内的内容为抓取电影院信息，与抓取排片信息区别开来
    # 解析下载的时光网影院文件
    # 按规定格式将数据存入数据库
    def _parse_time_dt(self):
        data = timeData['locations']['List']
        count = 0
        for area in data:
            # if count == 10: break
            self._prase_area(area)
            # count += 1

    # 解析一级地名
    def _prase_area(self, area):
        # 一级地名下的二级地名电影院信息
        dis = area['Districts']['List']
        city = area['NameCn']
        _city = area['NameEn']
        sid = _city
        for district in dis:
            sid = self._parse_area_scale_2(district,city)

        # 一级地名下的电影院信息
        if sid != _city:
            sid = '_'.join(sid.split('_')[:-1])
        else:
            sid = _city
        _cinema_url = self.rooturl + sid
        for cine in area['Cinemas']['List']:

            cinema_url = _cinema_url + '/' + str(cine['Id'])
            cinema_name = cine['NameCn']
            # print(city, city, cinema_name, cinema_url, cinema_name)
            self.td.insert(city, city, cinema_name, cinema_url, cinema_name)

    # 解析二级地名
    def _parse_area_scale_2(self, dist, city):

        _cinema_url = self.rooturl + dist['StringId']
        area = dist['NameCn']
        for cine in dist['Cinemas']['List']:

            cinema_url = _cinema_url + '/' + str(cine['Id'])
            cinema_name = cine['NameCn']
            # print(city, area, cinema_name, cinema_url, cinema_name)
            self.td.insert(city, area, cinema_name, cinema_url, cinema_name)

        return dist['StringId']


    def _optimize_district(self, i):
        try:
            url, pk = i[4], i[0]
            self._get_district(url, pk)
        except:
            return

    def s(self):
        count = 0
        for i in self.td.extract():
            count += 1
            if count <= 4119: continue
            self.qe.put(i)
        while True:
            if threading.active_count() > 5:
                time.sleep(5)
                continue
            item = self.qe.get()
            threading.Thread(target=self._optimize_district, args=(item,)).start()

    def _get_district(self, url, pk):

        pattern = re.compile(r'"address":"(.+?)","')
        text = self.rp.req_url(url)
        res = re.findall(pattern, text)
        if not res:
            return
        # print(pk)
        self.td._insert_dis(pk, res[0])
    # =====================================================================================

    # =====================================================================================
    # 获取时光某地区某电影院某影片价格
    # 1. 根据查询条件获取影院 id
    # 2. 根据影院 id 获取该影院正在上映电影
    # 3. 获取 查询电影的排片时间表链接
    # 4. 拿到价格
    def _get_tickets_info(self, *args):
        print('_get',args)
        assert len(args) == 4, 'not enough parameters'
        nm = TimeDt()
        cinema_url = nm.search(*args[:3])
        # print(cinema_url)
        assert cinema_url, '未查询到该电影院'
        # page = requests.get(cinema_url).text
        page = self.rp.req_url(cinema_url)
        assert page, '网络请求错误'
        # print(args[3])
        return self._parse_tickets_html(page, args[3], str_date=0)

    def _parse_tickets_html(self, page, movie, str_date):

        soup = bs4.BeautifulSoup(page, 'lxml')
        soup_s = soup.find('script', text=re.compile('cinemaShowtimesScriptVariables'))
        text = soup_s.get_text(strip=True)
        # print(text)
        # 处理 js 字典
        # 将 js 字典转为 python 可用的字典
        start_ = text.index('{')
        res = str(text[start_:])
        # print(res)
        res = res.replace('true', '1')
        res = res.replace('false', '0')
        res = re.sub(r'new Date\(', '', res)
        res = re.sub('\)', '', res)
        dct = json.loads(res)

        movieid = self._get_movie_id(dct['movies'], movie)
        # assert movieid, '未查询到该电影'
        # print(movieid)
        if not movieid: return
        # print('')
        # 获取　非当日　排片
        date_ = self._check_date(str_date)
        if date_:
            return movieid
        else:
            time_sche = self._get_movie_sche(dct['showtimes'], movieid)
            return time_sche

    # 检查请求日期
    def _check_date(self, str_date):
        today = datetime.date.today()
        date_ = datetime.datetime.strptime(str_date, "%Y-%m-%d").date()
        delta = (date_ - today).days
        if delta > 0:
            return str_date
        else:
            return False

    def _get_movie_sche_m(self, cinema_id, movie_id, str_date):
        url = 'http://m.mtime.cn/Service/callback.mi/showtime/' \
              'ShowTimesByCinemaMovieDate.api?cinemaId={0}&movieId={1}&date={2}'.format(cinema_id, movie_id, str_date)

        # print(url)
        page = self.rp.req_url(url)
        if not page : return
        dct = json.loads(page)
        # print(dct)
        res = []
        for item in dct['s']:
            # print(item)
            start = self._stamp2time(item['showDay'])
            end = self._stamp2time(item['showDay'] + (item['length']*60))
            lang = item['language'] + item['versionDesc']
            hall = item['hall']
            price = item['price']
            res.append((start, end, lang, hall, price))

        return res

    def _stamp2time(self, stamp):

        beijing_stamp = stamp
        time_local = time.localtime(beijing_stamp)
        return time.strftime("%H:%M", time_local)

    # 获取电影　ID
    def _get_movie_id(self, films, movie):
        pt = re.compile(movie)
        for film in films:
            name = film['movieTitleCn']
            is_matched = re.match(pt, name)
            if is_matched:
                return film['movieId']

        return None

    # 获取 PC 端排片
    def _get_movie_sche(self, showtimes, id):

        res = []
        for s in showtimes:
            if s['movieId'] != id:
                continue
            s_time = s['realtime'].split(':')
            hour = s_time[0][-2:]
            start_time = hour + ':' + s_time[1]
            end_time = s['movieEndTime'].replace('预计', '').replace('散场', '')
            lang = s['language']
            hall = s['hallName']
            vision = s['version']
            price = s['mtimePrice']
            if price == 0:
                continue
            res.append((start_time, end_time, lang+vision, hall, price))
        return res

    def get_movie_from_time(self, *args):
        # city, dis, c_name, m_name = args
        return self._get_tickets_info(*args)


    def get_timetable_from_time(self, url, film_name, str_date):

        # cinema_url = url + '/?d={}'.format(str_date)
        # print(cinema_url)
        cinema_id = url.split('/')[-1]

        page = self.rp.req_url(url)
        # print(page)
        if not page: return
        # assert page, '网络请求错误'
        # print(args[3])
        try:
            res_or_id = self._parse_tickets_html(page, film_name, str_date)
            if isinstance(res_or_id, list):
                return res_or_id
            elif isinstance(res_or_id, int):
                return self._get_movie_sche_m(cinema_id, res_or_id, str_date)
        except Exception as e:
            print(e)
            return

if __name__ ==  '__main__':
    ti = Time()
    res = ti.get_timetable_from_time('http://theater.mtime.com/China_Shanghai_Xuhuiqu/1045', '建军大业', '2017-08-01')
    # print(res)
    # for i in res:
    #     print(i)
    # ti.s()
    # ti._parse_time_dt()
    # res = ti._get_tickets_info('上海', '杨浦', '中影', '悟空')
    # for i in res:
    #     print(i)
    # res = ti._stamp2time(1501449973)
    # print(res)