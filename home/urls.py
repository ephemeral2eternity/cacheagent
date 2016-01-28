from django.conf.urls import patterns, url
from home import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
]
