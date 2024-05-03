# coding=utf-8
"""
Lawrence McDaniel - https://lawrencemcdaniel.com
Oct-2021

Course Management Studio App Models
"""
from django.db import models
from model_utils.models import TimeStampedModel
from django.contrib.auth import get_user_model

from opaque_keys.edx.django.models import CourseKeyField, UsageKeyField

User = get_user_model()

pass
