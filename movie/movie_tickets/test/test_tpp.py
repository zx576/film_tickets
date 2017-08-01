# coding=utf-8

import requests

url = 'https://dianying.taobao.com/ajaxCinemaList.htm?page=12&pageSize=10&pageLength=25&sortType=0&n_s=new'

headers = {
    'cookie': 'tb_city=440300;'
              # ' UM_distinctid=15d01a188dc5ac-02597d112272b2-1d2a1f03-1fa400-15d01a188ddac1; '
              # 'uc3=sg2=AQI8o%2Fv3ask5xE4LnMxxN2G4EbA%2FhJ%2FFjc3ciaaypX8%3D&nk2=F55h%2FT4WpjTcEw%3D%3D&id2=VAcOG9yMcJ3t&vt3=F8dBzWEX8iLFOxqA7PM%3D&lg2=UtASsssmOIJ0bQ%3D%3D;'
              # ' uss=VqoC7N75Ke3QxKWeSnzmB9PxPByFkkYcAOqhb17Ts3kUoqmazqj2ADOlIlM%3D; '
              # 'lgc=thkingzhou; tracknick=thkingzhou; '
              # '_cc_=WqG3DMC9EA%3D%3D; '
              # 'tg=0; '
              # 'l=As3NHBj0wblToADHxfGgzrt2XeNHqgF8; '
              # 'mt=ci=0_1; v=0; _tb_token_=vH8BAP16nq; '
              # 'swfstore=181599; '
              # 'uc1=cookie14=UoW%2BsW9rDGexzQ%3D%3D; '
              # 'cookie2=1cb37cc8c608d43d89ca5b503ef6f97a; '
              # 't=577072644a0fe2603bb4e61450519683; '

              # 'tb_cityName="1tjH7A=="; '
              # 'cna=zx6TEZIwc30CAYviL5jn3Y1m; '
              # 'x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; '
              # 'isg=Al1daCyq2KMkKLyVYcFho8RAbDCX0pRUzulPUx8ikbTj1n0I58qhnCtGZv2q',

}

headers_ = {
    'cookie': 'thw=cn;'
              ' UM_distinctid=15d01a188dc5ac-02597d112272b2-1d2a1f03-1fa400-15d01a188ddac1; '
              'uc3=sg2=AQI8o%2Fv3ask5xE4LnMxxN2G4EbA%2FhJ%2FFjc3ciaaypX8%3D&nk2=F55h%2FT4WpjTcEw%3D%3D&id2=VAcOG9yMcJ3t&vt3=F8dBzWEX8iLFOxqA7PM%3D&lg2=UtASsssmOIJ0bQ%3D%3D;'
              ' uss=VqoC7N75Ke3QxKWeSnzmB9PxPByFkkYcAOqhb17Ts3kUoqmazqj2ADOlIlM%3D; '
              'lgc=thkingzhou; tracknick=thkingzhou; '
              '_cc_=WqG3DMC9EA%3D%3D; '
              'tg=0; '
              'l=As3NHBj0wblToADHxfGgzrt2XeNHqgF8; '
              'mt=ci=0_1; v=0; _tb_token_=vH8BAP16nq; '
              'swfstore=181599; '
              'uc1=cookie14=UoW%2BsW9rDGexzQ%3D%3D; '
              'cookie2=1cb37cc8c608d43d89ca5b503ef6f97a; '
              't=577072644a0fe2603bb4e61450519683; '
              'tb_city=500100; '
              'tb_cityName="1tjH7A=="; '
              'cna=zx6TEZIwc30CAYviL5jn3Y1m; '
              'x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; '
              'isg=Al1daCyq2KMkKLyVYcFho8RAbDCX0pRUzulPUx8ikbTj1n0I58qhnCtGZv2q',

}

hd = {'cookie': 'tb_city=440300;', 'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)'}

def req_tpp(url):
    req = requests.get(url, headers=hd)
    print(req.text)

req_tpp(url)

