from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<node_id>[0-9]+)/$', views.node, name='node'),
    url(r'^(?P<node_id>[0-9]+)/start$', views.start, name='start'),
    url(r'^(?P<node_id>[0-9]+)/stop$', views.stop, name='stop'),
    url(r'^all/stop$', views.stop_all, name='stop_all'),
    url(r'^broadcast/(?P<content>.+)$', views.broadcast, name='broadcast'),
    url(r'^new/(?P<node_name>.+)$', views.new, name='new'),
    url(r'^(?P<node_id>[0-9]+)/yell/(?P<content>.+)$', views.yell, name='yell'),
]
