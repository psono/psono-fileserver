"""psono URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from django.conf import settings
from os.path import join, dirname, abspath
import django
from . import views

urlpatterns = [

    # url(r'^$', views.api_root),

    url(r'^healthcheck/$', views.HealthCheckView.as_view(), name='healthcheck'),
    url(r'^upload/$', views.UploadView.as_view(), name='upload'),
    url(r'^download/$', views.DownloadView.as_view(), name='download'),
    url(r'^info/$', views.InfoView.as_view(), name='info'),

]

if settings.DEBUG:
    # URLs for development purposes only
    urlpatterns += [
        url(r'^coverage/(?P<path>.*)$', django.views.static.serve,
            {'document_root':join(dirname(abspath(__file__)), '..', '..', 'htmlcov')}),
    ]