import requests
import click
from enum import Enum


class StatusCode(Enum):
    """An Enum represented the status codes of the result of auth attempts"""
    SUCCESS = 0
    CONNECTION_ERROR = 1
    UNAUTHORISED = 2
    OTHER_ERROR = 3


def get_user_credentials(username_msg, password_msg):
    """Get a username and password from the user

    :param username_msg: The message to display when getting the username
    :param password_msg: The message to display when getting the username
    :return: A tuple of strings in the form (username, password)
    """
    # get the username
    username = click.prompt(username_msg)
    # get the password (the characters should be hidden in the terminal as they are entered)
    password = click.prompt(password_msg, hide_input=True)

    return username, password


def validate_credentials(credentials):
    """Verify the validity of a pair of credentials

    :param credentials: A tuple of strings in the form (username, password)
    :return: If successful a tuple containing strings in format (username, password) error code otherwise
    """

    try:
        r = requests.get("https://myanimelist.net/api/account/verify_credentials.xml", auth=credentials)
    except requests.exceptions.ConnectionError:
        return StatusCode.CONNECTION_ERROR

    if r.status_code == 200:
        return StatusCode.SUCCESS
    elif r.status_code == 401:
        return StatusCode.UNAUTHORISED
    else:
        return StatusCode.OTHER_ERROR

