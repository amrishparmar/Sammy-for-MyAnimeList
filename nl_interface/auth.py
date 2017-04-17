import requests
import click
from enum import Enum

import network
import ui


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
    :return: A network.StatusCode enum value
    """
    # prepare the url
    url = "https://myanimelist.net/api/account/verify_credentials.xml"

    # send the async add request to the server
    r = ui.threaded_action(network.make_request, msg="Authenticating", request=requests.get, url=url, auth=credentials)

    if r == network.StatusCode.CONNECTION_ERROR:
        return r
    elif r.status_code == 200:
        return network.StatusCode.SUCCESS
    elif r.status_code == 401:
        return network.StatusCode.UNAUTHORISED
    else:
        return network.StatusCode.OTHER_ERROR
