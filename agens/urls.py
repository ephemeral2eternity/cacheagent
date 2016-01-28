from django.conf.urls import patterns, include, url
from django.contrib import admin
import django_cron
# django_cron.autodiscover()

urlpatterns = [
    # Examples:
    url(r'^', include('home.urls'), name='home'),
    url(r'^monitor/', include('monitor.urls')),
    url(r'^overlay/', include('overlay.urls')),
    url(r'^video/', include('video.urls')),
    url(r'^qoe/', include('qoe.urls')),
    url(r'^client/', include('client.urls')),

    url(r'^admin/', include(admin.site.urls)),
]
