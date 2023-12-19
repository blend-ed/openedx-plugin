# coding=utf-8
"""
written by:     Lawrence McDaniel
                https://lawrencemcdaniel.com

date:           sep-2021

usage:          Example custom REST API leveraging misc functionality from
                Open edX repos.
"""
# python stuff
import os
import json

# django stuff
from django.contrib.auth import get_user_model
from openedx.core.lib.api.view_utils import view_auth_classes

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# open edx stuff
from common.djangoapps.student.models import email_exists_or_retired

# our stuff
from .utils import get_name_validation_error
from .__about__ import __version__

User = get_user_model()


class ResponseSuccess(Response):
    def __init__(self, data=None, http_status=None, content_type=None):
        _status = http_status or status.HTTP_200_OK
        data = data or {}
        reply = {"response": {"success": True}}
        reply["response"].update(data)
        super().__init__(data=reply, status=_status, content_type=content_type)


@view_auth_classes(is_authenticated=True)
class UsersAPIView(APIView):
    def get(self, request):
        users = User.objects.all()
        results = [{"id": user.id, "name": user.username} for user in users]
        return Response(results, content_type="application/json")

class APIInfoView(APIView):
    def get(self, request):
        return ResponseSuccess({"version": __version__})

@view_auth_classes(is_authenticated=True)
class UsersProfileUpdateView(APIView):
    """
    Update all the details of the user's profile.
    """
    def get(self, request):
        # tell the users what all parameters to be passed
        print(request)
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"message": f"Username must be passed to update the profile and use method as POST."},
        )
    def post(self, request):
       print(request)
       data = request.data
       username = data.get("username")
       if not username:
           return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": f"Username must be passed to update the profile."},
            )
       try:
            user = User.objects.get(username=username)
            email = data.get("email", user.email)
            if not email == user.email:
                if email_exists_or_retired(email):
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={"message": f"An account with the email ID: '{email}' already exists."},
                    )
            user.email = email
            name_validation_error = get_name_validation_error(data.get("name", user.profile.name))
            if len(name_validation_error) > 0:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"message": name_validation_error},
                )
            user.profile.name = data.get("name", user.profile.name)
            user.profile.gender = data.get("gender", user.profile.gender)
            user.profile.year_of_birth = data.get("year_of_birth", user.profile.year_of_birth)
            user.profile.level_of_education = data.get("level_of_education", user.profile.level_of_education)
            user.profile.country = data.get("country", user.profile.country)
            user.save()
            user.profile.save()
            return ResponseSuccess(
                data={"message": f"Profile updated successfully for user '{username}'."},
                content_type="application/json"
            )
            
       except User.DoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": f"No user '{username}' found with given username."},
            )
