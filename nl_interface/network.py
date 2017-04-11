from enum import Enum

import requests.exceptions


class StatusCode(Enum):
    """An Enum represented the status codes of the result of auth attempts"""
    SUCCESS = 0
    CONNECTION_ERROR = 1
    UNAUTHORISED = 2
    OTHER_ERROR = 3


def make_request(request, *args, **kwargs):
    """Wrapper for requests functions to order to handle errors"""
    try:
        return request(*args, **kwargs)
    except requests.exceptions.ConnectionError:
        return StatusCode.CONNECTION_ERROR


