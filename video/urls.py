from django.conf.urls import patterns, url
from video import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^init/', views.initVideo, name='init'),
	url(r'^query/', views.query, name='query'),
	url(r'^add/', views.add, name='add'),
	url(r'^discover/', views.discover, name='discover'),
	url(r'^getSrv', views.getSrv, name='getSrv'),
]
