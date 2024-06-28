"""psono URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  re_path(r'^blog/', include(blog_urls))
"""
from django.urls import re_path
from . import views

urlpatterns = [

    # re_path(r'^$', views.api_root),

    re_path(r'^healthcheck/$', views.HealthCheckView.as_view(), name='healthcheck'),
    re_path(r'^upload/$', views.UploadView.as_view(), name='upload'),
    re_path(r'^download/$', views.DownloadView.as_view(), name='download'),
    re_path(r'^info/$', views.InfoView.as_view(), name='info'),

]
