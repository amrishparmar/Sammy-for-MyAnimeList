import unittest

from nl_interface import add


class TestAddEntry(unittest.TestCase):
    def test_invalid_entry_type(self):
        self.assertRaises(ValueError, add.add_entry, ("username", "password"), "badentrytype", "", "")

    def test_none_for_both_optional_args(self):
        self.assertRaises(ValueError, add.add_entry, ("username", "password"), "anime")
        self.assertRaises(ValueError, add.add_entry, ("username", "password"), "manga")
        self.assertRaises(ValueError, add.add_entry, ("username", "password"), "anime", None, None)
        self.assertRaises(ValueError, add.add_entry, ("username", "password"), "manga", None, None)


if __name__ == '__main__':
    unittest.main()
