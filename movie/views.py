import datetime

from django.shortcuts import render, render_to_response
from django.http import Http404
# Create your views here.

from .models import Cover, CinemaUrl, Movie
from movie.movie_tickets.spiders.nuomi import Nuomi
from movie.movie_tickets.spiders.taopiaopiao import TaoPiaoPiao
from movie.movie_tickets.spiders.time import Time


# 首页
def index(request):
    cover = Cover.objects.filter(is_alive=True)
    if cover:
        cover = cover[0]
        print('cover ok')
    movies = Movie.objects.filter(is_in_theater=True).filter(is_top=False)
    top_movie = Movie.objects.get(is_top=True)
    content = {
        'cover': cover,
        'movies': movies,
        'top': top_movie
    }

    return render(request, 'movie/index.html', content)


# 某一电影详情页面
def movie(request, movie_id):

    m = Movie.objects.get(pk=movie_id)
    # 查询 ID 返回地址
    content = {
        'item': m
    }
    return render(request, 'movie/display.html', content)


# 根据页面返回的地区，获取该地区所有的电影院
# ajax 请求
def cinema(request):

    if request.is_ajax():

        city = request.POST.get('city', None)
        district = request.POST.get('district', None)
        if not city and not district:
            return Http404('not enough parameters')
        query = CinemaUrl.objects.filter(city__contains=city).filter(district__startswith=district)
        # print(query)
        # for i in query:
        #     print(i.district, i.cinema_name)

        content = {
            'cinemas': query
        }

        return render_to_response('movie/cinema.html', content)


# 根据页面返回的电影院索引值，获取票价
# ajax　请求
def tickets(reqeust):

    if reqeust.is_ajax():
        # print(reqeust.POST)
        str_date = reqeust.POST.get('date')
        if not str_date:
            return Http404('need parameter "date"')
        # 给时光网的时间参数
        date_ = datetime.datetime.strptime(str_date, "%Y-%m-%d").date()
        # 给糯米的时间参数
        delta = (date_ - datetime.date.today()).days
        # 给淘票票的时间参数直接为 str_date

        time_date = ''.join(str_date.split('-'))
        pk = reqeust.POST.get('pk')
        film = reqeust.POST.get('film')

        if not pk and not film:
            return Http404('lack of parameters "pk" or "film" or both')
        res_data = []
        cine = CinemaUrl.objects.get(pk=pk)

        # 糯米网 url
        nuo = cine.nuomi_url
        if nuo:
            dct = {}
            nm = Nuomi()
            res = nm.get_timetable_from_nuomi(nuo, film,delta)
            dct['website'] = '糯米'
            if res:
                dct['timetable'] = res
                res_data.append(dct)

        # 淘票票
        tpp = cine.taopp_url
        if tpp:
            dct = {}
            taopp = TaoPiaoPiao()
            res = taopp.get_timetable_from_taopp(tpp, film,str_date)
            dct['website'] = '淘票票'
            if res:
                dct['timetable'] = res
                res_data.append(dct)

        # 时光网
        time = cine.time_url
        if time:
            dct = {}
            ti = Time()
            res = ti.get_timetable_from_time(time, film, str_date)
            dct['website'] = '时光'
            if res:
                dct['timetable'] = res
                res_data.append(dct)

        content = {
            'data': res_data
        }

        return render_to_response('movie/timetable.html', content)