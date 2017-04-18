import unittest
from unittest import mock

from nl_interface import update
from nl_interface.tests.constants_for_tests import credentials


class TestUpdateAnimeListEntry(unittest.TestCase):
    def test_invalid_search_type(self):
        self.assertRaises(ValueError, update.update_anime_list_entry, credentials, "badsearchtype", "")


class TestUpdateMangaListEntry(unittest.TestCase):
    def test_invalid_search_type(self):
        self.assertRaises(ValueError, update.update_manga_list_entry, credentials, "badsearchtype", "")


class testSearchList(unittest.TestCase):
    def test_invalid_search_type(self):
        self.assertRaises(ValueError, update.search_list, credentials[0], "badsearchtype", "")

    def test_no_results(self):
        self.assertEqual(update.search_list(credentials[0], "anime", "longstringthatshouldnotreturnaresult"),
                         update.ListSearchStatusCode.NO_RESULTS)
        self.assertEqual(update.search_list(credentials[0], "manga", "longstringthatshouldnotreturnaresult"),
                         update.ListSearchStatusCode.NO_RESULTS)

    def test_one_result(self):
        search_term = "naruto"  # change this for something for that is unique on each the lists if needed

        anime_search = update.search_list(credentials[0], "anime", search_term)
        self.assertEqual(anime_search.name, "anime")
        self.assertEqual(anime_search.parent.name, "myanimelist")

        manga_search = update.search_list(credentials[0], "manga", search_term)
        self.assertEqual(manga_search.name, "manga")
        self.assertEqual(manga_search.parent.name, "myanimelist")

    def test_good_result(self):
        with mock.patch("click.prompt", side_effect=[1, 1]):
            search_term = "no"  # change this for something for that should return multiple results

            anime_search = update.search_list(credentials[0], "anime", search_term)
            self.assertEqual(anime_search.name, "anime")
            self.assertEqual(anime_search.parent.name, "myanimelist")

            manga_search = update.search_list(credentials[0], "manga", search_term)
            self.assertEqual(manga_search.name, "manga")
            self.assertEqual(manga_search.parent.name, "myanimelist")


class TestViewList(unittest.TestCase):
    def test_invalid_search_type(self):
        self.assertRaises(ValueError, update.view_list, credentials[0], "badsearchtype")


if __name__ == '__main__':
    unittest.main()
