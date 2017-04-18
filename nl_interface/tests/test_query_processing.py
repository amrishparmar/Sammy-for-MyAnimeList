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
    pass


if __name__ == '__main__':
    unittest.main()
