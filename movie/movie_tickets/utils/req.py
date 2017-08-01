# coding=utf-8
# author = zhouxin
# date = 2017.7.4
'''
description:
封装请求网页的方法，包含普通的 request，也包含 selenium 等

'''

import requests
from movie.movie_tickets.utils.headers import get_header, get_header_mobile
from movie.movie_tickets.utils.proxy import ProxyList
from movie.movie_tickets.utils.decorators import make_print
import re

pr = ProxyList()


class Rep:

    def __init__(self):
        self.response_header = None
        self.citycode = None

    def get_header(self, formobile=False,):
        headers = get_header_mobile() if formobile else get_header()
        return headers

    def get_proxy(self):
        return pr.get_proxy()

    # 请求网页，成功返回页面信息，失败返回 None
    # @make_print
    def _req_url(self, url, headers, proxies):
        # print(headers)
        try:
            req = requests.get(url, headers=headers, proxies=proxies, timeout=2)
            self.response_header = req.headers
            req.raise_for_status()
            return req.text

        except:
            return None

    # 请求网页，成功返回页面信息，失败则更换 headers 与 proxies 重新请求，最多重复 3 次
    def req_url(self, url, formobile=False, error=0, use_re_header=False):

        if error == 5:
            print('请求网页 {0} 失败'.format(url))
            return None

        headers = self.get_header(formobile)
        if use_re_header and self.response_header:
            headers['cookie'] = self.citycode or self.extract_header()

        proxies = pr.get_proxy()

        res = self._req_url(url, headers=headers, proxies=proxies)
        if res:
            return res
        else:
            return self.req_url(url, error=error+1, use_re_header=use_re_header, formobile=formobile)

    def extract_header(self):

        set_cookie = self.response_header['Set-Cookie']
        pt1 = re.compile('tb_city=\d+;')
        cookie = re.findall(pt1, set_cookie)[0]
        self.citycode = cookie

        return cookie


# print(get_header())
# rq = Rep()
# ini_url = 'https://dianying.taobao.com/cinemaList.htm?city=440300'
# url = 'https://dianying.taobao.com/ajaxCinemaList.htm?page=1&pageSize=10&pageLength=22&n_s=new'
# s = rq.req_url(ini_url, use_re_header=True)
# s2 = rq.req_url(url, use_re_header=True)
# print(rq.response_header)
# print(s2)
