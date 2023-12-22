from django.urls import path

from . import api
from .waffle import (
    waffle_switches,
    API_USERS
)

urlpatterns = []

if waffle_switches[API_USERS]:
    urlpatterns += [
        path("users/", api.UsersAPIView.as_view(), name="openedx_plugin_api_users"),
        path("users/update/", api.UsersProfileUpdateView.as_view(), name="openedx_plugin_api_users_update"),
        path("users/image/<str:username>/", api.UserProfileImageUpdateView.as_view(), name="openedx_plugin_api_users_image"),
        path('users/test/', api.TestApiView.as_view(), name='openedx_plugin_api_users_test'),
    ]