from django.conf.urls import patterns, url
from monitor import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^load/', views.view_load, name='view_load'),
	url(r'^sys/', views.view_sys_stat, name='view_sys_stat'),
	url(r'^bw/', views.view_bw, name='view_bw'),
	url(r'^rtts/', views.view_rtts, name='view_rtts'),
	url(r'^dump/', views.dump, name='dump'),
]
