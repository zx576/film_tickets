# coding=utf-8
# author = zhouxin
# date = 2017.7.6

# description
# 淘票票电影票价查询

import queue
import bs4
import re
import time
import threading

from movie.movie_tickets.utils.req import Rep
from movie.movie_tickets.database.taopiaopiao_citycode import city
from movie.movie_tickets.database.taopp_dt import TaoppDt
from movie.movie_tickets.utils.decorators import make_print


class TaoPiaoPiao:

    def __init__(self):

        self.loc_queue = queue.Queue()
        self.cinemalist_url = 'https://dianying.taobao.com/cinemaList.htm'
        self.rq = Rep()

    # ===================================================================================
    # 等号之内的内容为抓取电影院信息，与抓取排片信息区别开来
    # 从 导入的city文件中 获取城市代码，插入队列
    def get_city_code(self):
        city_and_code = city['returnValue']
        for key, value in city_and_code.items():
            for region in value:
                self.loc_queue.put(region)

        return True

    # 通过城市代码 获取 影院信息
    # 有些地方的影院较多，继续以 ajax 形式加载，这部分内容由 get_cinema_id_more 处理
    # 网页解析保存统一交给 _save_cinema_id 处理
    # @make_print
    def get_cinema_id(self, citycode, city):
        req_res = Rep()
        url = self.cinemalist_url + '?city=' + str(citycode)
        content = req_res.req_url(url, use_re_header=True)
        if content is None:
            return
        soup = bs4.BeautifulSoup(content, 'lxml')
        soup_ul = soup.find('ul', class_="sortbar-detail J_cinemaList")
        self._save_cinema_id(soup_ul, city)
        soup_more = soup.find('div', class_='sortbar-more J_cinemaMore')
        if soup_more:
            data_ajax = soup_more['data-ajax']
            data_pram = soup_more['data-param']
            pattern = re.compile('pageLength=(\d+)')
            page_length = int(re.findall(pattern, data_pram)[0])
            ini_url = data_ajax + '?page={0}&pageSize=10&pageLength={1}&n_s=new'
            return self.get_cinema_id_more(ini_url, page_length, city, req_res)

    # 处理额外加载的影院信息
    def get_cinema_id_more(self, url, pagelength, city, req_res, curpage=1):
        if curpage > pagelength:
            return
        r_url = url.format(curpage, pagelength)
        r_url = r_url.replace('http', 'https')
        content = req_res.req_url(r_url, use_re_header=True)
        if content is None:
            return
        soup = bs4.BeautifulSoup(content, 'lxml')
        self._save_cinema_id(soup, city)

        return self.get_cinema_id_more(url, pagelength,city, req_res,curpage=curpage+1)

    # 解析网页并保存数据
    def _save_cinema_id(self, content, city):

        tpp = TaoppDt()
        soup_li = content.find_all('li')
        for li in soup_li:
            cinema_a = li.find('a', class_='detail-left pictures')
            cinema_url = cinema_a['href']
            # cinema_name = cinema_a.span.img['alt']
            cinema_name = li.find('h4').a.string
            position = li.find('span', class_='limit-address').string
            if '区' in position:
                district = position.split('区')[0] + '区'
            elif '县' in position:
                district = position.split('县')[0] + '县'
            elif '市' in position:
                district = position.split('市')[0] + '市'
            else:
                district = position
            # print(cinema_url, cinema_name, position)
            # mt.insert('秦皇岛', '北戴河区', '北戴河影谷影院', 'http://qhd.meituan.com/shop/5441476', '北戴河区联峰北路80号（北戴河舌尖美食城）')
            tpp.insert(city, district, cinema_name, cinema_url, position)

    # 爬取 电影院信息主程序
    def crawler(self):
        self.get_city_code()
        # print(self.loc_queue.qsize())
        while True:
            if self.loc_queue.empty():
                break
            if threading.active_count() > 5:
                time.sleep(5)
                continue
            item = self.loc_queue.get()
            city = item['regionName']
            citycode = item['cityCode']
            threading.Thread(target=self.get_cinema_id, args=(citycode, city)).start()

    # =====================================================================================

    # =====================================================================================
    # 获取淘票票某地区某电影院某影片价格
    # 1. 根据查询条件获取影院 id
    # 2. 根据影院 id 获取该影院正在上映电影
    # 3. 获取 查询电影的排片时间表链接
    # 4. 拿到价格
    def get_movie_tickets(self, *args):
        assert len(args) == 4, 'not enough parameters \n type in -h for help'
        movie_name = args[3]
        mt = TaoppDt()
        cinema_url = mt.search(*args[:3])
        # print(cinema_url)
        assert cinema_url, '未查询到该电影院'
        pattern = re.compile(r'cinemaId=(\d+)')
        cinemaid = re.findall(pattern, cinema_url)[0]
        film_url = 'https://dianying.taobao.com/cinemaDetailSchedule.htm?cinemaId=' + str(cinemaid)
        content = self.rq.req_url(film_url)
        assert content, '请求失败，请检查 /utils/req.py 中 req_url 函数是否工作正常'
        soup = bs4.BeautifulSoup(content, 'lxml')
        soup_film = soup.find('a', text=re.compile(movie_name))
        assert soup_film, '未查询到该电影'
        film_param = soup_film['data-param']

        return self._get_ticket_info(film_param)

    def _get_ticket_info(self, param):
        ticket_url = 'https://dianying.taobao.com/cinemaDetailSchedule.htm?' + param
        content = self.rq.req_url(ticket_url)
        if content is None:
            return

        soup = bs4.BeautifulSoup(content, 'lxml')
        soup_tb = soup.find('tbody')
        soup_tr = soup_tb.find_all('tr')

        res = []
        for tr in soup_tr:
            td = tr.find_all('td')

            time_pt = re.compile('\d+:\d+')
            _time_range = td[0].get_text(strip=True)
            time_range = re.findall(time_pt, _time_range)
            # time_range = '-'.join(re.findall(time_pt, _time_range))
            long = td[1].get_text(strip=True)
            pos = td[2].get_text(strip=True)
            price = tr.find('em', class_='now').string
            time_table = time_range + [long, pos, price]
            res.append(time_table)

        return res

    def get_movie_from_taopp(self, *args):

        return self.get_movie_tickets(*args)

    def get_timetable_from_taopp(self, url, film_name, date_):

        cinema_url = url
        pattern = re.compile(r'cinemaId=(\d+)')
        cinemaid = re.findall(pattern, cinema_url)[0]
        film_url = 'https://dianying.taobao.com/cinemaDetailSchedule.htm?cinemaId=' + str(cinemaid)
        content = self.rq.req_url(film_url)
        # assert content, '请求失败，请检查 /utils/req.py 中 req_url 函数是否工作正常'
        if not content: return
        soup = bs4.BeautifulSoup(content, 'lxml')
        soup_film = soup.find('a', text=re.compile(film_name))
        # assert soup_film, '未查询到该电影'
        if not soup_film: return
        film_param = soup_film['data-param']
        param = re.sub(r'\d+-\d+-\d+', date_, film_param)
        # print(film_param)
        try:
            return self._get_ticket_info(param)
        except:
            return


if __name__ == '__main__':
    url = 'http://dianying.taobao.com/cinemaDetail.htm?cinemaId=5766&n_s=new'
    film_name = '战狼'
    tpp = TaoPiaoPiao()
    res = tpp.get_timetable_from_taopp(url, film_name, '2017-08-01')

    # for i in res:
    #     print(i)
# tpp.get_city_code()
# print(tpp.loc_queue.qsize())
# tpp.crawler()
# res = tpp.get_movie_tickets('苏州', '相城', '幸福蓝海', '京城81号2')
# for i in res:
#     print(i)

# tpp.get_cinema_id(320500, '苏州')

