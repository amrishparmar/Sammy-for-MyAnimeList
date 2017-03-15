import unittest
from unittest import mock

from .. import auth


class TestGetUserCredentials(unittest.TestCase):
    def test_normal_input(self):
        cases = {
            "username": "password",
            "name": "pass",
            "n": "p"
        }
        for key in cases.keys():
            with mock.patch("click.prompt", side_effect=[key, cases[key]]):
                self.assertEqual(auth._get_user_credentials(), (key, cases[key]))


# class TestAuthenticateUser(unittest.TestCase):
#     def test_invalid_credentials(self):
#         with mock.patch("auth._get_user_credentials", return_value=("username", "password")):
#             with mock.patch("click.echo"):
#                 with mock.patch("click.confirm", return_value='n'):
#                     self.assertEqual(auth.authenticate_user(), False)
#

if __name__ == '__main__':
    unittest.main()
