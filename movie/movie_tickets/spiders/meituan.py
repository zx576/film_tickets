# coding=utf-8
# author = zhouxin
# date = 2017.7.5

# description:
# 收集主要城市电影院信息
# 在 django 项目中放弃了此接口
#　原因是在 pc端 太难拿到实际价格了

import bs4
import queue
import threading
import time
import re
import requests

from movie.movie_tickets.utils.req import Rep
from movie.movie_tickets.database.meituan_dt import MeiTuan_Dt


class MeiTuan:

    def __init__(self):

        self.next_cinemapage_url = '/dianying/cinemalist/all/all'
        self.area_queue = queue.Queue()
        self.mt = MeiTuan_Dt()
        self.rq = Rep()

    # ===================================================================================
    # 等号之内的内容为抓取电影院信息，与抓取排片信息区别开来
    # 获取所有地区 子 根 域名
    # 将其加入到队列中
    def get_district(self,url):

        content = self.rq.req_url(url)
        if not content:
            print('{} 请求错误'.format(url))
        soup = bs4.BeautifulSoup(content, 'lxml')
        soup_a = soup.find_all('a', class_='isonline')
        # print(len(soup_a))
        for a in soup_a:
            dct = {}
            district = a.string
            district_url = a['href']
            dct['area'] = district
            dct['url'] = district_url
            print(dct)
            self.area_queue.put(dct)

    # 递归抓取 某 地区所有影院信息
    def get_cinema_list(self, url, city, next_page='/dianying/cinemalist/all/all'):
        # 递归抓取退出条件
        if next_page is None:
            return None

        mt = MeiTuan_Dt()
        url = url + next_page
        content = self.rq.req_url(url)
        if not content:
            print('{} 请求错误'.format(url))
            return

        # 获取详细信息
        soup = bs4.BeautifulSoup(content, 'lxml')
        soup_div = soup.find_all('div', class_='cinema-item__block cinema-item__block--detail')
        for div in soup_div:

            cinema_name = div.a.string
            cinema_url = 'http:' + div.a['href']
            position_info = div.dl.get_text('|', strip=True)
            position = position_info.split('|')[1]
            if '区' in position:
                district = position.split('区')[0] + '区'
            elif '县' in position:
                district = position.split('县')[0] + '县'
            elif '市' in position:
                district = position.split('市')[0] + '市'
            else:
                district = position

            mt.insert(city, district, cinema_name, cinema_url, position)

        # 获取下一页的链接
        # 迭代抓取
        soup_next = soup.find('a', attrs={'gaevent': 'content/page/next'})
        next_page = soup_next['href'] if soup_next else None
        return self.get_cinema_list(url, city, next_page)

    def crawler(self):
        # threads = []
        print('jobs begin')
        index_url = 'http://www.meituan.com/index/changecity/initiative'
        self.get_district(index_url)
        print(self.area_queue.qsize())
        while True:
            if self.area_queue.empty():
                break
            if threading.active_count() >= 5:
                time.sleep(5)
                continue

            loc = self.area_queue.get()
            city = loc['area']
            loc_url = loc['url']
            threading.Thread(target=self.get_cinema_list, args=(loc_url, city)).start()
            # threading.Thread(target=self.get_cinema_list, args=()).join()

        print('jobs done')

    # =====================================================================================

    # =====================================================================================
    # 获取某家电影院某部电影票价
    # 美团电影真实票价难以获取，或者说获取成本偏高
    #　其采用的技术为，加载一张布满数字的图片，使用定位的方式定位图片上某个数字，达到显示价格的目的
    # 对于爬虫来说，显得很难抓取分析
    # 所以这里给出的都是门店价，几乎毫无参考价值
    def get_movie_tickets(self, *args):
        assert len(args) == 4, 'not enough parameters \n type in -h for help'
        movie_name = args[3]
        mt = MeiTuan_Dt()
        cinema_url = mt.search(*args[:3])
        assert cinema_url, '未查询到该电影院'
        content = self.rq.req_url(cinema_url)
        # content = requests.get(cinema_url).text
        # print(content)
        assert content, '请求失败，请检查 /utils/req.py 中 req_url 函数是否工作正常'
        soup = bs4.BeautifulSoup(content, 'lxml')
        soup_film = soup.find('a', class_='movie-info__name', title=re.compile(movie_name))
        assert soup_film, '暂无此电影'
        soup_div = soup_film.find_parent('div', class_='movie-info')
        soup_table = soup_div.find('table', class_='time-table time-table--current')
        soup_tr = soup_table.find_all('tr')[1:]
        price_table = []
        for tr in soup_tr:
            td = tr.find_all('td')

            time_range = td[0].get_text(strip=True).replace('&nbsp;&minus;&nbsp;', '-')
            lang = td[1].string
            loc = td[2].string
            price_td = td[3].find('del')
            price = price_td.string if price_td else '不能获取价格'

            price_ = [time_range, lang, loc, price]
            price_table.append(price_)

        return price_table

    def get_movie_from_meituan(self, *args):

        return self.get_movie_tickets(*args)


# m = MeiTuan()
# m.get_district('http://www.meituan.com/index/changecity/initiative')
# index = 'http://zk.meituan.com'
# m.get_cinema_list(index, '周口')
# m.mt.works_done()
# m.crawler()
# res = m.get_movie_tickets('上海', '闵行', '17.5', '悟空传')
# for i in res:
#     print(i)

