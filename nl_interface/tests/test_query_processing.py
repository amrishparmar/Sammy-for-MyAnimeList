import unittest

from nl_interface import query_processing as qp


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


class TestStripType(unittest.TestCase):
    pass


class TestDetermineAction(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
