import unittest

from nl_interface import query_processing as qp
from nl_interface import synonyms


class TestNormalise(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(qp.normalise(""), "")

    def test_lowercase(self):
        self.assertEqual(qp.normalise("lowercase"), "lowercase")

    def test_uppercase(self):
        self.assertEqual(qp.normalise("UPPERCASE"), "uppercase")

    def test_title_case(self):
        self.assertEqual(qp.normalise("Title Case"), "title case")

    def test_mixed_case(self):
        self.assertEqual(qp.normalise("mIxEd cASe"), "mixed case")

    def test_string_with_punctation(self):
        self.assertEqual(qp.normalise("String with punct!"), "string with punct")
        self.assertEqual(qp.normalise("String with punct!!!"), "string with punct")
        self.assertEqual(qp.normalise("String with __punct__?"), "string with __punct")


class TestStripInfo(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(qp.strip_info(""), "")

    def test_info_only(self):
        for syn in synonyms.terms["information"]:
            self.assertEqual(qp.strip_info(syn), "")
            self.assertEqual(qp.strip_info(" {} ".format(syn)), "")

    def test_no_info_syn(self):
        self.assertEqual(qp.strip_info("teststring"), "teststring")
        self.assertEqual(qp.strip_info(" teststring "), " teststring ")
        self.assertEqual(qp.strip_info("test string"), "test string")

    def test_info_syn_at_end(self):
        for syn in synonyms.terms["information"]:
            self.assertEqual(qp.strip_info("a string {}".format(syn)), "a string")
            self.assertEqual(qp.strip_info("blah blah {}".format(syn)), "blah blah")

    def test_info_syn_at_end_no_space(self):
        for syn in synonyms.terms["information"]:
            self.assertEqual(qp.strip_info("sometext{}".format(syn)), "sometext{}".format(syn))


class TestStripType(unittest.TestCase):
    def test_empty_string(self):
        self.assertTupleEqual(qp.strip_type(""), ("", None))

    def test_type_only(self):
        self.assertTupleEqual(qp.strip_type("anime"), ("", qp.MediaType.ANIME))
        self.assertTupleEqual(qp.strip_type(" anime "), ("", qp.MediaType.ANIME))

        self.assertTupleEqual(qp.strip_type("manga"), ("", qp.MediaType.MANGA))
        self.assertTupleEqual(qp.strip_type(" manga "), ("", qp.MediaType.MANGA))

    def test_no_type(self):
        self.assertTupleEqual(qp.strip_type("teststring"), ("teststring", None))
        self.assertTupleEqual(qp.strip_type(" teststring "), (" teststring ", None))
        self.assertTupleEqual(qp.strip_type("test string"), ("test string", None))

    def test_type_at_end(self):
        self.assertTupleEqual(qp.strip_type("test string anime"), ("test string", qp.MediaType.ANIME))
        self.assertTupleEqual(qp.strip_type("test string manga"), ("test string", qp.MediaType.MANGA))

    def test_type_at_end_no_space(self):
        self.assertTupleEqual(qp.strip_type("sometext_anime"), ("sometext_anime", None))
        self.assertTupleEqual(qp.strip_type("sometext_manga"), ("sometext_manga", None))


class TestDetermineAction(unittest.TestCase):
    def test_empty_string(self):
        self.assertIsNone(qp.determine_action(""))

    def test_search_no_ambiguity(self):
        for syn in synonyms.actions["search"]:

            strings = [
                "{}".format(syn),
                "{} for".format(syn),
                "{} for test".format(syn),
                "i want to {} for test test".format(syn)
            ]

            for s in strings:
                self.assertEqual(qp.determine_action(s), qp.OperationType.SEARCH)

    def test_search_with_ambiguity(self):
        for ssyn in synonyms.actions["search"]:
            for osyn in synonyms.actions["update"] + synonyms.actions["increment"] + synonyms.actions["add"] \
                    + synonyms.actions["delete"] + synonyms.actions["view_list"]:

                strings = [
                    "{} {}".format(ssyn, osyn),
                    "{} for {}".format(ssyn, osyn),
                    "i want to {} for {}".format(ssyn, osyn)
                ]

                for s in strings:
                    self.assertEqual(qp.determine_action(s), qp.OperationType.SEARCH,
                                     "ssyn: {}, osyn: {}, s: {}".format(ssyn, osyn, s))

    def test_update_no_ambiguity(self):
        for syn in synonyms.actions["update"]:

            strings = [
                "{}".format(syn),
                "{} test".format(syn),
                "{} the test anime".format(syn),
                "i want to {} the test manga".format(syn)
            ]

            for s in strings:
                if syn != "give":
                    self.assertEqual(qp.determine_action(s), qp.OperationType.UPDATE, "syn: {}, s: {}".format(syn, s))
                else:
                    self.assertEqual(qp.determine_action(s), qp.OperationType.SEARCH, "syn: {}, s: {}".format(syn, s))

    def test_update_with_ambiguity(self):
        for ssyn in synonyms.actions["update"]:
            for osyn in synonyms.actions["search"] + synonyms.actions["increment"] + synonyms.actions["add"] \
                    + synonyms.actions["delete"] + synonyms.actions["view_list"]:

                strings = [
                    "{} {}".format(ssyn, osyn),
                    "{} the {} anime".format(ssyn, osyn),
                    "i want to {} the {} manga".format(ssyn, osyn)
                ]

                for s in strings:
                    if ssyn != "give":
                        self.assertEqual(qp.determine_action(s), qp.OperationType.UPDATE,
                                         "ssyn: {}, osyn: {}, s: {}".format(ssyn, osyn, s))
                    else:
                        self.assertEqual(qp.determine_action(s), qp.OperationType.SEARCH,
                                         "ssyn: {}, osyn: {}, s: {}".format(ssyn, osyn, s))

    def test_increment_no_ambiguity(self):
        for syn in synonyms.actions["increment"]:

            strings = [
                "{}".format(syn),
                "{} test".format(syn),
                "{} the test anime".format(syn),
                "i want to {} the test manga".format(syn)
            ]

            for s in strings:
                self.assertEqual(qp.determine_action(s), qp.OperationType.UPDATE, "syn: {}, s: {}".format(syn, s))

    def test_increment_with_ambiguity(self):
        for ssyn in synonyms.actions["increment"]:
            for osyn in synonyms.actions["search"] + synonyms.actions["update"] + synonyms.actions["add"] \
                    + synonyms.actions["delete"] + synonyms.actions["view_list"]:

                strings = [
                    "{} {}".format(ssyn, osyn),
                    "{} the {} anime".format(ssyn, osyn),
                    "i want to {} the {} manga".format(ssyn, osyn)
                ]

                for s in strings:
                    self.assertEqual(qp.determine_action(s), qp.OperationType.UPDATE,
                                     "ssyn: {}, osyn: {}, s: {}".format(ssyn, osyn, s))

    def test_add_no_ambiguity(self):
        for syn in synonyms.actions["add"]:

            strings = [
                "{}".format(syn),
                "{} test".format(syn),
                "{} the test anime".format(syn),
                "i want to {} the test manga onto my list".format(syn)
            ]

            for s in strings:
                self.assertEqual(qp.determine_action(s), qp.OperationType.ADD, "syn: {}, s: {}".format(syn, s))

    def test_add_with_ambiguity(self):
        for ssyn in synonyms.actions["add"]:
            for osyn in synonyms.actions["search"] + synonyms.actions["update"] + synonyms.actions["increment"] \
                    + synonyms.actions["delete"] + synonyms.actions["view_list"]:

                strings = [
                    "{} {}".format(ssyn, osyn),
                    "{} the {} anime".format(ssyn, osyn),
                    "i want to {} the {} manga".format(ssyn, osyn)
                ]

                for s in strings:
                    self.assertEqual(qp.determine_action(s), qp.OperationType.ADD,
                                     "ssyn: {}, osyn: {}, s: {}".format(ssyn, osyn, s))

    def test_delete_no_ambiguity(self):
        for syn in synonyms.actions["delete"]:

            strings = [
                "{}".format(syn),
                "{} test".format(syn),
                "{} the test anime".format(syn),
                "i want to {} test from my manga list".format(syn)
            ]

            for s in strings:
                self.assertEqual(qp.determine_action(s), qp.OperationType.DELETE, "syn: {}, s: {}".format(syn, s))

    def test_delete_with_ambiguity(self):
        for ssyn in synonyms.actions["delete"]:
            for osyn in synonyms.actions["search"] + synonyms.actions["update"] + synonyms.actions["increment"] \
                    + synonyms.actions["add"] + synonyms.actions["view_list"]:

                strings = [
                    "{} {}".format(ssyn, osyn),
                    "{} the {} anime".format(ssyn, osyn),
                    "i want to {} the {} manga".format(ssyn, osyn)
                ]

                for s in strings:
                    self.assertEqual(qp.determine_action(s), qp.OperationType.DELETE,
                                     "ssyn: {}, osyn: {}, s: {}".format(ssyn, osyn, s))

    def test_view_list(self):
        for syn in synonyms.actions["view_list"]:

            strings = [
                "{} my anime list".format(syn),
                "i want to {} my manga list".format(syn)
            ]

            for s in strings:
                self.assertEqual(qp.determine_action(s), qp.OperationType.VIEW_LIST, "syn: {}, s: {}".format(syn, s))


if __name__ == '__main__':
    unittest.main()
