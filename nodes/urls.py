from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<node_id>[0-9]+)/$',
        views.node, name='node'),
    url(r'^(?P<node_id>[0-9]+)/start$',
        views.start, name='start'),
    url(r'^(?P<node_id>[0-9]+)/stop$',
        views.stop, name='stop'),
    url(r'^(?P<from_node_id>[0-9]+)/connect/(?P<to_node_id>[0-9]+)$',
        views.connect, name='connect'),
    url(r'^(?P<from_node_id>[0-9]+)/disconnect/(?P<to_node_id>[0-9]+)$',
        views.disconnect, name='disconnect'),
    url(r'^all/start$',
        views.start_all, name='start_all'),
    url(r'^all/stop$',
        views.stop_all, name='stop_all'),
    url(r'^broadcast/(?P<content>.+)$',
        views.broadcast, name='broadcast'),
    url(r'^new/(?P<node_name>.+)$',
        views.new, name='new'),
    url(r'^(?P<node_id>[0-9]+)/yell/(?P<content>.+)$',
        views.yell, name='yell'),
    url(r'^(?P<from_node_id>[0-9]+)/whisper/'
        '(?P<to_node_id>[0-9]+)/'
        '(?P<content>.+)$',
        views.whisper, name='whisper'),
    url(r'^(?P<node_id>[0-9]+)/tell/class/(?P<class_name>.+)/(?P<content>.+)$',
        views.tell_class, name='tell_class'),
    url(r'^(?P<node_id>[0-9]+)/tell/network/(?P<content>.+)$',
        views.tell_network, name='tell_network'),
]
