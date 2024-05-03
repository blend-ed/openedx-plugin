# coding=utf-8
from django.conf import settings
from django.conf.urls import url

from .waffle import waffle_switches, ANALYTICS_REPORT

urlpatterns = []

if waffle_switches[ANALYTICS_REPORT]:
    urlpatterns += []