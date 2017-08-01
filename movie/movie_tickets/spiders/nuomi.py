# coding=utf-8
# author = zhouxin
# date=2017.7.20
# description
# 糯米网电影查询

import queue
import bs4
import re
import time
import threading
import json

from movie.movie_tickets.utils.req import Rep
from movie.movie_tickets.utils.decorators import make_print
from movie.movie_tickets.database.nuomi_dt import NuomiDt
from movie.movie_tickets.database.nuomi_citycode import nuomicode

class Nuomi:

    def __init__(self):

        self.citycodeurl = 'https://mdianying.baidu.com/city/choose'
        self.cityurl = 'https://mdianying.baidu.com/movie/cinema'
        self.rp = Rep()
        self.qe = queue.Queue()

    # ===================================================================================
    # 等号之内的内容为抓取电影院信息，与抓取排片信息区别开来
    # 获取城市代码
    def _get_city_code(self):

        page = self.rp.req_url(self.citycodeurl,formobile=True)
        if not page:
            return
        soup = bs4.BeautifulSoup(page, 'lxml')
        soup_a = soup.find_all('a', class_="city city-item")
        dct = {}

        for a in soup_a:
            dct[a.string] = a['data-citycode']

        return dct

    # 获取影院详细信息
    # 请求部分由 _get_cinema 处理
    # 解析网页并保存部分由 _parse_html 处理
    def _get_cinema(self, citycode, city):

        count = 0
        while True:

            url = self.cityurl + '?c={0}&cc={0}&pn={1}'.format(citycode,count)
            page = self.rp.req_url(url)
            if page is None:
                return
            page = json.loads(page)
            html = page['data']['html']
            is_end = self._parse_html(html, city)
            if is_end: break
            # soup = bs4.BeautifulSoup(html, 'lxml')
            # print(soup.prettify())
            # break
            count += 1

    # 解析网页，保存电影院信息
    def _parse_html(self, page, city):

        nuomi = NuomiDt()
        soup = bs4.BeautifulSoup(page, 'lxml')
        soup_a = soup.find_all('a', class_="portal-cinema-list-item-link")
        if len(soup_a) == 0: return True
        for a in soup_a:
            cinema_url = 'https://mdianying.baidu.com'+ a['href']
            cinema_name = a.find('div', class_="portal-cinema-name").get_text(strip=True)
            position = a.find('div', class_="portal-cinema-address-section").get_text(strip=True)
            if '区' in position:
                district = position.split('区')[0] + '区'
            elif '县' in position:
                district = position.split('县')[0] + '县'
            elif '市' in position:
                district = position.split('市')[0] + '市'
            else:
                district = position

            # print(city, cinema_name, cinema_url, position, district)
            nuomi.insert(city, district, cinema_name, cinema_url, position)
        return False

    # 将城市及其代码入队
    def _enqueue_citycode(self):

        # print(type(nuomicode))
        for city, code in nuomicode.items():
            self.qe.put((city, code))

    # 启动多线程开始爬取电影院信息
    # 默认最多 5 线程
    def crwaler(self):
        #　生产者
        #  添加待抓取元素到队列
        self._enqueue_citycode()
        while True:
            # 限制线程数
            if threading.active_count() > 5:
                time.sleep(3)
                continue
            # 退出条件
            # 队列为空
            if self.qe.empty():
                break
            # 提取待抓取元素
            item = self.qe.get()
            # 开启所线程
            threading.Thread(target=self._get_cinema, args=(item[1], item[0])).start()

    # =====================================================================================

    # =====================================================================================
    # 获取糯米某地区某电影院某影片价格
    # 1. 根据查询条件获取影院 id
    # 2. 根据影院 id 获取该影院正在上映电影
    # 3. 获取 查询电影的排片时间表链接
    # 4. 拿到价格
    def _get_tickets_info(self, *args):
        assert len(args) == 4, 'not enough parameters'
        nm = NuomiDt()
        cinema_url = nm.search(*args[:3])
        assert cinema_url, '未查询到该电影院'
        page = self.rp.req_url(cinema_url, formobile=True)
        assert page, '网络请求错误'
        return self._parse_tickets_html(page, args[3])

    def _parse_tickets_html(self, page, movie_name):

        pt = re.compile(movie_name)
        soup = bs4.BeautifulSoup(page, 'lxml')
        soup_div = soup.find('div', class_="mod m-movie-infos")
        soup_div_in = soup_div.find_all('div', attrs={'data-movie-id': True})
        movie_id = None
        for div in soup_div_in:

            is_matched = re.match(pt, str(div.div.get_text()))
            if is_matched:
                movie_id = div['data-movie-id']
                break

        # assert movie_id, '未找到此电影'
        if not movie_id: return
        # 查询电影信息
        soup_ul = soup.find_all('div', class_=True,
                            attrs={'data-movie-id': '{}'.format(movie_id),
                                   'data-log': True,
                                   'data-date': True,
                                   'data-choosetagmap': True})

        res = []
        daily_ = []
        cur_date = ''
        for i in soup_ul:
            i_date = i.get('data-date')
            # print(i_date, cur_date)
            if cur_date != i_date:
                if daily_: res.append(daily_)
                daily_ = []
                cur_date = i_date
            start_time = i.find('div', class_="start").string
            end_time = i.find('div', class_="end").string.replace('散场', '')
            lan = i.find('div', class_="lan").string
            theater = i.find('div', class_="theater").string
            price = i.find('div', class_="price").get_text(';').strip()
            price = price.split(';')[2]
            # member_price = i.find('div', class_="member-price")
            # if member_price:
            #     member_price = member_price.get_text(strip=True)
            #     member_price = member_price.replace('&yen', '-')

            # else:
            #     member_price = 'None'

            daily_.append((start_time, end_time, lan, theater, price))

        return res

    # 命令行查询方法
    def get_movie_from_nuomi(self, *args):

        res = self._get_tickets_info(*args)

        pre = 0
        new_res = []
        for i in range(1, len(res)):

            pre_time = res[pre][0].split(':')
            pre_time = int(''.join(pre_time))

            cur_time = res[i][0].split(':')
            cur_time = int(''.join(cur_time))

            if pre_time > cur_time:
                break
            new_res.append(res[i])
            pre += 1

        return new_res

    # 提供给 django 查询的接口
    def get_timetable_from_nuomi(self, url, movie_name, date_mark=0):

        page = self.rp.req_url(url)
        if not page: return
        try:
            res = self._parse_tickets_html(page, movie_name)
            if not res: return
            return res[date_mark]
        except:
            return

if __name__ == '__main__':
    nm = Nuomi()
    res = nm.get_timetable_from_nuomi('https://mdianying.baidu.com/cinema/detail?cinemaId=409#showing', '建军大业',1)
    # for i in res:
    #     print(i)
    # nm._get_city_code()
    # nm._get_cinema(289, '上海')
    # nm.crwaler()
    # res = nm._get_tickets_info('上海', '闵行', '保利', '悟空')
    # pre = 0
    # for i in range(1,len(res)):
    #
    #     pre_time = res[pre][0].split(':')
    #     pre_time = int(''.join(pre_time))
    #
    #     cur_time = res[i][0].split(':')
    #     cur_time = int(''.join(cur_time))
    #
    #     if pre_time > cur_time:
    #         break
    #
    #     pre += 1


