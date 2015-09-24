from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/add-items/$', 'liszt.apis.add_items', name='add_items'),
    url(r'^api/search/$', 'liszt.apis.search', name='search'),

    url(r'^$', 'liszt.views.home', name='home'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^tag/(?P<tag>[^\/]+)/$', 'liszt.views.tag', name='tag'),
    url(r'^(?P<context_slug>[^\/]+)/(?P<list_slug>[^\/]+)/$', 'liszt.views.list_detail', name='list_detail'),
    url(r'^(?P<context_slug>[^\/]+)/$', 'liszt.views.context_detail', name='context_detail'),
]
