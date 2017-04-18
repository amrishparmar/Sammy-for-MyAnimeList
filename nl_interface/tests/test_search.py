import unittest
from unittest import mock

from nl_interface import search
from nl_interface.tests.constants_for_tests import credentials


class TestSearch(unittest.TestCase):
    def test_invalid_search_type(self):
        self.assertRaises(ValueError, search.search, ("username", "password"), "badsearchtype", "")

    def test_no_results(self):
        self.assertEqual(search.search(credentials, "anime", "longstringthatshouldnotreturnaresult", False),
                         search.StatusCode.NO_RESULTS)
        self.assertEqual(search.search(credentials, "manga", "longstringthatshouldnotreturnaresult", False),
                         search.StatusCode.NO_RESULTS)

    def test_good_result(self):
        with mock.patch("click.prompt", side_effect=[1, 1]):
            anime_search = search.search(credentials, "anime", "test", False)
            self.assertEqual(anime_search.name, "entry")
            self.assertEqual(anime_search.parent.name, "anime")

            manga_search = search.search(credentials, "manga", "test", False)
            self.assertEqual(manga_search.name, "entry")
            self.assertEqual(manga_search.parent.name, "manga")


if __name__ == '__main__':
    unittest.main()
