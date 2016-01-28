from django.conf.urls import patterns, url
from client import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^query/', views.query, name='query'),
	url(r'^add', views.add, name='add'),
	url(r'^pclient/', views.pclient, name='pclient'),
	url(r'^vclient/', views.vclient, name='vclient'),
]
