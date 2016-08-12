from django.conf.urls import url
from lab1 import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	url(r'^$', views.url_list, name='url_list'),
	url(r'^url/(?P<pk>\d+)/$', views.url_detail, name='url_detail'),
	url(r'^delete/(?P<pk>\d+)$', views.url_delete, name='url_delete'),
	url(r'^accounts/login/$', auth_views.login, name='login'),
	url(r'^accounts/logout/$', views.logout_view, name='logout'),
]
