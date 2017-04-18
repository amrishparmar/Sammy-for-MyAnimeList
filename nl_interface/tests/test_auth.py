import unittest
from unittest import mock

from nl_interface import auth
from nl_interface import network
from .constants_for_tests import credentials


class TestGetUserCredentials(unittest.TestCase):
    def test_normal_input(self):
        cases = [
            ("username", "password"),
            ("name", "pass"),
            ("n", "p")
        ]
        for case in cases:
            with mock.patch("click.prompt", side_effect=[case[0], case[1]]):
                self.assertEqual(auth.get_user_credentials("get usr msg", "get pwd msg"), (case[0], case[1]))


class TestValidateCredentials(unittest.TestCase):
    def test_empty_username(self):
        self.assertEqual(auth.validate_credentials(("", "password")).name, network.StatusCode.UNAUTHORISED.name)

    def test_empty_password(self):
        self.assertEqual(auth.validate_credentials(("username", "")).name, network.StatusCode.UNAUTHORISED.name)

    def test_valid_password(self):
        self.assertEqual(auth.validate_credentials(credentials).name, network.StatusCode.SUCCESS.name)


if __name__ == '__main__':
    unittest.main()
