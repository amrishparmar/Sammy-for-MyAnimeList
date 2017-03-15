import requests
import click
from enum import Enum


class StatusCode(Enum):
    SUCCESS = 0
    CONNECTION_ERROR = 1
    UNAUTHORISED = 2
    OTHER = 3


def get_user_credentials(username_msg, password_msg):
    # get the username
    username = click.prompt(username_msg)
    # get the password (the characters should be hidden in the terminal as they are entered)
    password = click.prompt(password_msg, hide_input=True)

    return username, password


def authenticate_user(credentials):
    """Verify the validity of a pair of credentials

    :param credentials:
    :return: If successful a tuple containing strings in format (username, password) error code otherwise
    """

    try:
        r = requests.get("https://myanimelist.net/api/account/verify_credentials.xml", auth=credentials)
    except requests.exceptions.ConnectionError:
        return StatusCode.CONNECTION_ERROR

    if r.status_code == 200:
        return credentials
    elif r.status_code == 401:
        return StatusCode.UNAUTHORISED
    else:
        return StatusCode.OTHER

