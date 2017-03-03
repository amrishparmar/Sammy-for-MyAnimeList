import unittest
from unittest import mock
import sys
from io import StringIO
import helpers


class TestGetStatusChoice(unittest.TestCase):

    def test_valid_cases(self):
        for i in range(1, 7):
            with mock.patch('click.prompt', return_value=i):
                with mock.patch('click.echo'):
                    self.assertEqual(helpers.get_status_choice_from_user("anime"), None if i == 6 else i)
                    self.assertEqual(helpers.get_status_choice_from_user("manga"), None if i == 6 else i)

    def test_invalid_cases(self):
        for i in [-12123, -1, 0, 7, 2102]:
            with mock.patch('click.prompt', side_effect=[i, 1]):
                out = StringIO()
                sys.stdout = out
                helpers.get_status_choice_from_user("anime")
                output = out.getvalue().strip()
                expected = "You must enter a value between 1 and 6."
                self.assertEqual(output[-len(expected):], expected, "\n\nFailure on input value " + str(i))

        for i in [-12123, -1, 0, 7, 2102]:
            with mock.patch('click.prompt', side_effect=[i, 1]):
                out = StringIO()
                sys.stdout = out
                helpers.get_status_choice_from_user("manga")
                output = out.getvalue().strip()
                expected = "You must enter a value between 1 and 6."
                self.assertEqual(output[-len(expected):], expected, "\n\nFailure on input value " + str(i))


class TestGetScoreChoice(unittest.TestCase):
    def test_valid_cases(self):
        for i in range(0, 11):
            with mock.patch("click.prompt", return_value=i):
                with mock.patch("click.echo"):
                    self.assertEqual(helpers.get_score_choice_from_user(), None if i == 0 else i)

    def test_invalid_cases(self):
        for i in [-12123, -1, 11, 2102]:
            with mock.patch('click.prompt', side_effect=[i, 1]):
                out = StringIO()
                sys.stdout = out
                helpers.get_score_choice_from_user()
                output = out.getvalue().strip()
                expected = "You must enter a value between 1 and 10."
                self.assertEqual(output[-len(expected):], expected, "\n\nFailure on input value {}".format(i))


class TestGetNewCount(unittest.TestCase):
    def test_valid_cases(self):
        for i in range(0, 10):
            with mock.patch("click.prompt", return_value=i):
                with mock.patch("click.echo"):
                    self.assertEqual(helpers.get_new_count_from_user("test"), i)

    def test_invalid_cases(self):
        for i in [-12123, -2323, -2, -1]:
            with mock.patch('click.prompt', side_effect=[i, 1]):
                out = StringIO()
                sys.stdout = out
                helpers.get_new_count_from_user("test")
                output = out.getvalue().strip()
                expected = "You must enter a value greater than or equal to zero."
                self.assertEqual(output[-len(expected):], expected, "\n\nFailure on input value {}".format(i))

if __name__ == '__main__':
    unittest.main()
