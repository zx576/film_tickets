from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<movie_id>[0-9]+)$', views.movie, name='movie'),
    url(r'^cinema$', views.cinema, name='cinema'),
    url(r'^tickets$', views.tickets, name='tickets')

]
