import unittest

from nl_interface import delete


class TestDeleteEntry(unittest.TestCase):
    def test_invalid_entry_type(self):
        self.assertRaises(ValueError, delete.delete_entry, ("username", "password"), "badentrytype", "")


if __name__ == '__main__':
    unittest.main()
