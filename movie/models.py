from django.db import models

class CinemaUrl(models.Model):

    # 城市名
    city = models.CharField('城市', max_length=50)
    # 区、县、等二级地址
    district = models.CharField('区/县', max_length=255)
    # 详细地址
    location = models.CharField('详细地址', max_length=255, default='')
    # 电影院名
    cinema_name = models.CharField('电影院名', max_length=255, default='')
    # meituan 电影院地址
    meituan_url = models.URLField('美团地址', default='')
    # 时光网地址
    time_url = models.URLField('时光地址', default='')
    #　淘票票地址
    taopp_url = models.URLField('淘票票地址', default='')
    # nuomi 地址
    nuomi_url = models.URLField('糯米地址', default='')
    # 创建时间
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    # 是否有效
    is_active = models.BooleanField('是否有效', default=True)
    # 访问次数
    view_count = models.IntegerField('访问次数', default=0)
    # 索引码
    code = models.IntegerField('索引码')


class Movie(models.Model):

    name = models.CharField('电影名', max_length=255)
    rating = models.FloatField('评分', default=0)
    # poster = models.ImageField('电影封面', upload_to='poster/')
    poster_url_big = models.URLField('电影封面-大', default='')
    poster_url_me = models.URLField('电影封面-中', default='')
    # 由于可能有多名导演和演员，单个之间以 "-" 连接，以备后用
    # 比如 张译/张震/雷佳音  |  宁浩/杨庆 这种形式
    directors = models.CharField('导演', max_length=255)
    casts = models.CharField('演员', max_length=255)
    genes = models.CharField('类型', max_length=255)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    is_top = models.BooleanField('是否评分最高', default=False)
    is_in_theater = models.BooleanField('正在上映', default=True)

    def __str__(self):
        return self.name

class Cover(models.Model):

    name = models.CharField('封面名', max_length=100, default='cover')
    cover_img = models.ImageField('封面图片', upload_to='cover/', default='cover/default.jpg')
    # cover_url = models.URLField('封面地址', default='')
    is_alive = models.BooleanField('正在使用', default=False)












