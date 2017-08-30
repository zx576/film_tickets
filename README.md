## 电影票查询

#### 运行环境

- python 3+
- django 1.10
- linux/windows


#### 运行依赖包

- requests
- bs4
- lxml
- python-Levenshtein
- django-import-export


#### 如何使用

`git clone https://github.com/zx576/film_tickets`

进入项目文件夹

创建超级用户

`python manage.py createsuperuser`

依次输入用户名和密码即可

`python manage.py runserver`

django 自检无误后，在浏览器输入

`127.0.0.1:8000/movie`

#### 文件说明

文件结构分为三大块

1. 文件夹 douban_movie 该部分使用豆瓣 api 每日更新上映电影
2. 文件夹 movie_tickets 该部分包含了几个电影票网站的电影院信息爬虫以及某电影院某电影排片信息爬虫
3. django 项目

##### douban_movie

get_douban_in_thrater.py 

包含了以下作用：

- 爬取当日上映的前 10 部电影
- 比对目前数据库的上映影片，更新数据库
- 找到评分最高的影片，设置置顶


##### movie_tickets

database/  包含了该爬虫项目的数据库处理方法，数据库为 sqlite3

    gene_dt.py 通用的数据库数据库处理方法，包含了建表、查询、写入、删除等
    其他以 dt 结尾的文件  继承了 gene_dt.py 中的通用类，不同的网站对应了不同的数据库 table
    其他以 citycode 结尾的文件  在对应电影票网上可下载到的城市代码数据
  
spiders/
  
    下面 4 个文件表示不同网站的爬虫
  
utils/
    
    decorators.py 一个装饰器辅助开发文件
    headers.py  包含了收集的 headers 
    proxy.py    获取代理
    rep.py      使用代理重新对 requests 请求做了一层包装
    
settings.py 一些基本的设置
show.py 命令行获取电影排片信息


#### 项目思路

1. 使用爬虫爬取各电影票网站所有的电影院链接
2. 使用豆瓣 API 获取当日上映的电影信息
3. django 显示电影信息，提供给用户选择电影院的接口
4. 将电影院信息发送到 django 后台进行查询，爬取对应的排片信息显示给用户


#### 一些技术细节

1、 ajax 加载

本项目使用到了比较多的 ajax 加载技术，给出前后端的一份代码

示例：
实现功能：选择区/县，发送到后台，提取出电影院

html 代码

```html
<!--...-->
<li><a href="javascript:void(0);" class="city_">闵行区</a></li>
<!--...-->
```

js 代码

```javascript

// 选择区/县，发送到后台，提取出电影院
$(document).ready(function () {
    $(document).on('click', '.city_', function(){
        // 获取发送到后端的信息
        // 城市名 区名
        var dis = this.text;
        var city = $('#choose-city a').text();
        // ajax post 请求
        $.post('/movie/cinema', {
            // 发送信息
            'city':city,
            'district': dis,
            csrfmiddlewaretoken: '{{ csrf_token }}'
        },function (data) {
            // 回调函数， 处理后端信息
            $('#movie-choose-x').html(data);
        })
    })
});
```
views.py

```python
from django.shortcuts import render_to_response
from .models import CinemaUrl

# 根据页面返回的地区，获取该地区所有的电影院
# ajax 请求
def cinema(request):

    if request.is_ajax():
        # 获取前端信息
        city = request.POST.get('city', None)
        district = request.POST.get('district')
        # 查询数据库
        query = CinemaUrl.objects.filter(city__contains=city).filter(district__startswith=district)
        # 包装数据
        content = {
            'cinemas': query
        }
        # 使用 render_to_response 函数处理模板数据并发送到前端
        return render_to_response('movie/cinema.html', content)

```

template/cinema.html

```djangotemplate

    <ul class="nav nav-pills">
        {% for cine in cinemas %}
        <li>
            <a href="javascript:void(0);" id="{{ cine.id }}" class="cinema">
                {{ cine.cinema_name }}  
            </a>
        </li>
        {% endfor %}

    </ul>

```

如此，就是一份完整的 django-js-html 协同完成 ajax 加载的代码。在页面触发点击事件，将必要的信息发送到后端查找，最后在页面显示查找结果。


2、使用 django 环境运行代码

在使用豆瓣 API 部分，获取数据后需通过 django models 对数据库进行更新。所以需要一个运行在一个独立的 django 环境中。
添加以下代码可以完成此功能：

```python

import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "film_tickets.settings")
django.setup()

# 这样可以正常的导入 .models 中的类的
from movie.models import Movie

# your code here
```

3、python-Levenshtein


在初期的电影院信息的爬取过程中，各家的信息分别在数据库中不同的表内，接入到 django 后，产生了合并 表 的需求，但各家网站可能对于同一电影院显示的名称有细微差别。
所以使用了 python-Levenshtein 自然语言处理库对电影院名甚至电影院地点进行比对，根据结果判断是否为同一家影院。

```linux

>>> import Levenshtein
>>> Levenshtein.ratio('时代影城', '上海时代影城')
0.8
>>> Levenshtein.ratio('时代影城', '保利江川影院')
0.2

```
