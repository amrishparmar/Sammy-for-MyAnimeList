import unittest

import requests

from nl_interface import network


class TestMakeRequest(unittest.TestCase):
    def test_get(self):
        test_url = "http://info.cern.ch/hypertext/WWW/TheProject.html"

        mk_request_result = network.make_request(requests.get, url=test_url)
        request_result = requests.get(test_url)

        self.assertEqual(mk_request_result.text, request_result.text)


if __name__ == '__main__':
    unittest.main()
