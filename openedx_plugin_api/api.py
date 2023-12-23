# coding=utf-8
"""
written by:     Lawrence McDaniel
                https://lawrencemcdaniel.com

date:           sep-2021

usage:          Example custom REST API leveraging misc functionality from
                Open edX repos.
"""
# python stuff
import itertools
from contextlib import closing
import logging


# django stuff
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser

# open edx stuff
from common.djangoapps.student.models import email_exists_or_retired
from openedx.core.lib.api.view_utils import view_auth_classes
from openedx.core.djangoapps.profile_images.images import IMAGE_TYPES, create_profile_images, remove_profile_images, validate_uploaded_image
from openedx.core.djangoapps.profile_images.exceptions import ImageValidationError
from openedx.core.lib.api.parsers import TypedFileUploadParser
from openedx.core.djangoapps.user_api.accounts.image_helpers import get_profile_image_names, set_has_profile_image
from openedx.core.djangoapps.user_api.errors import UserNotFound

# our stuff
from .utils import get_name_validation_error, _make_upload_dt
from .__about__ import __version__

User = get_user_model()
log = logging.getLogger(__name__)


LOG_MESSAGE_CREATE = 'Generated and uploaded images %(image_names)s for user %(user)s'
LOG_MESSAGE_DELETE = 'Deleted images %(image_names)s for user %(user)s'

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
            user.is_staff = data.get("is_staff", user.is_staff)
            user.profile.name = data.get("name", user.profile.name)
            user.profile.gender = data.get("gender", user.profile.gender)
            user.profile.year_of_birth = data.get("year_of_birth", user.profile.year_of_birth)
            user.profile.level_of_education = data.get("level_of_education", user.profile.level_of_education)
            user.profile.country = data.get("country", user.profile.country)
            user.profile.phone_number = data.get("phone_number", user.phone_number)
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

@view_auth_classes(is_authenticated=True)
class UserProfileImageUpdateView(APIView):
    
    upload_media_types = set(itertools.chain(*(image_type.mimetypes for image_type in IMAGE_TYPES.values())))
    parser_classes = (MultiPartParser, FormParser, TypedFileUploadParser)

    def get(self, request, username):
        print(request, username)
        log.info('request', {'request': request, 'username': username})
        users = User.objects.all()
        results = [{"id": user.id, "name": user.username} for user in users]
        return Response(results, content_type="application/json")

    def post(self, request, username):
        """
        POST /openedx_plugin/api/users/image/{username}
        """

        print('request', request)
        log.info('request', {'request': request, 'username': username})

        # validate request:
        # verify that the user's
        # ensure any file was sent
        if 'file' not in request.FILES:
            return Response(
                {
                    "developer_message": "No file provided for profile image",
                    "user_message": _("No file provided for profile image"),

                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # process the upload.
        uploaded_file = request.FILES['file']

        # no matter what happens, delete the temporary file when we're done
        with closing(uploaded_file):

            # image file validation.
            try:
                validate_uploaded_image(uploaded_file)
            except ImageValidationError as error:
                return Response(
                    {"developer_message": str(error), "user_message": error.user_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # generate profile pic and thumbnails and store them
            profile_image_names = get_profile_image_names(username)
            create_profile_images(uploaded_file, profile_image_names)

            # update the user account to reflect that a profile image is available.
            set_has_profile_image(username, True, _make_upload_dt())

            log.info(
                LOG_MESSAGE_CREATE,
                {'image_names': list(profile_image_names.values()), 'user': username}
            )

        # send client response.
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, username):
        """
        DELETE /openedx_plugin/api/users/image/{username}
        """

        try:
            # update the user account to reflect that the images were removed.
            set_has_profile_image(username, False)

            # remove physical files from storage.
            profile_image_names = get_profile_image_names(username)
            remove_profile_images(profile_image_names)

            log.info(
                LOG_MESSAGE_DELETE,
                {'image_names': list(profile_image_names.values()), 'user': username}
            )
        except UserNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # send client response.
        return Response(status=status.HTTP_204_NO_CONTENT)

class TestApiView(APIView):
    def get(self, request):
        print('request', request)
        log.info(f'request: {request}')
        return ResponseSuccess({"message": "Hello asdfas World!"})