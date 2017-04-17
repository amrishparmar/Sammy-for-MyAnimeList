import sys
import unittest
from io import StringIO

from nl_interface import agent


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


if __name__ == '__main__':
    unittest.main()
