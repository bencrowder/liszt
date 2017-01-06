from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.contrib import admin

from liszt import apis as liszt_apis
from liszt import views as liszt_views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/add-items/$', liszt_apis.add_items, name='add_items'),
    url(r'^api/search/$', liszt_apis.search, name='search'),
    url(r'^api/toggle-item/(?P<item_id>[^\/]+)/$', liszt_apis.toggle_item, name='toggle_item'),
    url(r'^api/toggle-starred-item/(?P<item_id>[^\/]+)/$', liszt_apis.toggle_starred_item, name='toggle_starred_item'),
    url(r'^api/toggle-starred-list/(?P<list_id>[^\/]+)/$', liszt_apis.toggle_starred_list, name='toggle_starred_list'),
    url(r'^api/update-item/(?P<item_id>[^\/]+)/$', liszt_apis.update_item, name='update_item'),
    url(r'^api/update-list/(?P<list_id>[^\/]+)/$', liszt_apis.update_list, name='update_list'),
    url(r'^api/sort-things/(?P<type>[^\/]+)/$', liszt_apis.sort_things, name='sort_things'),
    url(r'^api/get-review-items/$', liszt_apis.get_review_items, name='get_review_items'),

    url(r'^$', liszt_views.home, name='home'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^starred/$', liszt_views.starred, name='starred'),
    url(r'^overview/$', liszt_views.overview, name='overview'),
    url(r'^review/$', liszt_views.review, name='review'),
    url(r'^dateview/$', liszt_views.dateview, name='dateview'),
    url(r'^(?P<context_slug>[^\/]+)/contextview/$', liszt_views.context_view, name='context_view'),
    url(r'^(?P<context_slug>[^\/]+)/(?P<list_slugs>.+)/$', liszt_views.list_detail, name='list_detail'),
    url(r'^(?P<context_slug>[^\/]+)/$', liszt_views.context_detail, name='context_detail'),
]
