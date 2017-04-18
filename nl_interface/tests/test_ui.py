import unittest

from nl_interface import ui


class TestThreadedAction(unittest.TestCase):
    def test_return_values(self):
        def trivial(val):
            """Return the input value"""
            return val

        vals = [0, -1, "text", "None", None, [], {}, 1.5, 123]

        for val in vals:
            self.assertEqual(ui.threaded_action(trivial, val=val), trivial(val), "Error on {}".format(val))



if __name__ == '__main__':
    unittest.main()
