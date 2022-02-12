"""psono URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import re_path, include
from rest_framework import routers

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    #re_path(r'^', include(router.urls)),
    #re_path(r'^accounts/', include('allauth.urls')),
    #re_path(r'^rest-auth/', include('rest_auth.urls')),
    #re_path(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    re_path(r'^', include('restapi.urls')),
    re_path(r'^cron/', include('cron.urls')),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
