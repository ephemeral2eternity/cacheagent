from django.conf.urls import patterns, url
from qoe import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^init/', views.initQoE, name='init'),
	url(r'^query/', views.query, name='query'),
	url(r'^update', views.update, name='update'),
	url(r'^dump/', views.dump, name='dump'),
]
