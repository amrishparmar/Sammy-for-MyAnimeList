import unittest

from nl_interface import search
from .constants_for_tests import credentials


class TestSearch(unittest.TestCase):
    def test_invalid_search_type(self):
        self.assertRaises(ValueError, search.search, ("username", "password"), "badsearchtype", "")

    def test_no_results(self):
        self.assertEqual(search.search(credentials, "anime", "longstringthatshouldnotreturnaresult", False),
                         search.StatusCode.NO_RESULTS)


if __name__ == '__main__':
    unittest.main()
