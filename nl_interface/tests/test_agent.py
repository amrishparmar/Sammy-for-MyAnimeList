import sys
import unittest
from unittest import mock
from io import StringIO

from nl_interface import agent
from nl_interface import synonyms
from nl_interface import query_processing


class TestPrintMsg(unittest.TestCase):
    def test_normal_string(self):
        out = StringIO()
        sys.stdout = out
        agent.print_msg("This is a test string.")
        output = out.getvalue().strip()
        expected = "Sammy> This is a test string."
        self.assertEqual(output[-len(expected):], expected)

    def test_empty_string(self):
        out = StringIO()
        sys.stdout = out
        agent.print_msg("")
        output = out.getvalue().strip("\n")
        expected = "Sammy> "
        self.assertEqual(output[-len(expected):], expected)


class TestGetQuery(unittest.TestCase):
    def test_exit_query(self):
        for syn in synonyms.terms["exit"]:
            with mock.patch("click.prompt", side_effect=[syn]):
                self.assertIsNone(agent.get_query())


class TestProcessQuery(unittest.TestCase):
    def test_exit_query(self):
        for syn in synonyms.terms["exit"]:
            self.assertEqual(agent.process_query(syn).name, query_processing.Extras.EXIT.name)


if __name__ == '__main__':
    unittest.main()
