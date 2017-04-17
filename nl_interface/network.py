from enum import Enum

import requests.exceptions


class StatusCode(Enum):
    """An Enum represented the status codes of the result of network connection attempts"""
    SUCCESS = 0
    CONNECTION_ERROR = 1
    UNAUTHORISED = 2
    OTHER_ERROR = 3


def make_request(request, *args, **kwargs):
    """Wrapper for requests functions to order to handle errors
    
    :param request: A function from the requests library, e.g. requests.get, requests.delete, etc.
    :param args: Args to pass to request
    :param kwargs: Keyword args to pass to request
    :return The result of the request or StatusCode.CONNECTION_ERROR if the request failed 
    """
    try:
        return request(*args, **kwargs)
    except requests.exceptions.ConnectionError:
        return StatusCode.CONNECTION_ERROR


