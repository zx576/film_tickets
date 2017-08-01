# coding=utf-8
# author = zhouxin
# date = 2017.7.4

'''
description:
获取代理

'''

import requests


class ProxyList:



    def __init__(self):
        self._proxies = []
        self.mark = 0
        self.offset = 20
        self.URL = 'http://lab.crossincode.com/proxy/get/?num=20'
        self._get_proxies(self.URL)

    def _get_proxies(self, url):
        try:
            req = requests.get(url)
            proxy_lst = req.json()['proxies']
            for proxy in proxy_lst:
                dct = {}
                dct['http'] = proxy['http']
                self._proxies.append(dct)
        except:
            return None

    def get_proxy(self):
        self._check()
        proxy = self._proxies[self.mark%len(self._proxies)]
        self.mark += 1
        return proxy

    def _check(self):
        if len(self._proxies) > 5:
            return

        else:
            url = self.URL + '&offset={}'.format(self.offset)
            self._get_proxies(url)
            self.offset += 20

        return

    def remove(self, item):
        if item in self._proxies:
            self._proxies.remove(item)
        else:
            print('无此IP')

    def __str__(self):
        return str(self._proxies)

