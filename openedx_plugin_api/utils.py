# coding=utf-8
"""
written by:     Lawrence McDaniel
                https://lawrencemcdaniel.com

date:           sep-2021

usage:          utility and convenience functions for
                openedx_plugin_api plugin
"""
# python stuff
import re

def get_name_validation_error(name):
    """Get the built-in validation error message for when
    the user's real name is invalid in some way (we wonder how).

    :param name: The proposed user's real name.
    :return: Validation error message.
    """

    def contains_html(value):
        """
        Validator method to check whether name contains html tags
        """
        regex = re.compile('(<|>)', re.UNICODE)
        return bool(regex.search(value))

    def contains_url(value):
        """
        Validator method to check whether full name contains url
        """
        regex = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))*', value)
        return bool(regex)

    if name:
        # Validation for the name length
        if len(name) > 255:
            return "Full name can't be longer than 255 symbols"

        return 'Enter a valid name' if (contains_html(name) or contains_url(name)) else ''