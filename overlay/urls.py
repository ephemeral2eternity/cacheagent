from django.conf.urls import patterns, url
from overlay import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^remove', views.delete_obj, name='delete_obj'),
	url(r'^init/', views.initServer, name='init'),
	url(r'^query/', views.query, name='query'),
	url(r'^update', views.update, name='update'),
	url(r'^peer/', views.peer, name='peer'),
	url(r'^delete/', views.delete, name='delete'),
	url(r'^add', views.add, name='add'),
]
