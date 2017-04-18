import unittest

from nl_interface import delete
from nl_interface.tests.constants_for_tests import credentials


class TestDeleteEntry(unittest.TestCase):
    def test_invalid_entry_type(self):
        self.assertRaises(ValueError, delete.delete_entry, credentials, "badentrytype", "")


if __name__ == '__main__':
    unittest.main()
