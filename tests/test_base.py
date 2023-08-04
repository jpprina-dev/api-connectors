"""Tests for APIClient base class."""
import json
import unittest
from unittest.mock import patch

from requests.exceptions import Timeout

from api_connectors.base import APIClient

TEST_URL = "http://test-url"
TEST_ENDPOINT = "api"
TEST_SSL = False
TEST_TIMEOUT = 1
TEST_DATA = {"test": "test_data"}
TEST_PATH = "test/path"
TEST_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def create_api_client():
    return APIClient(TEST_URL, TEST_ENDPOINT, TEST_SSL, TEST_TIMEOUT)


class TestBase(unittest.TestCase):
    @patch("APIClient.requests.request")
    def test_request(self, mock_request):
        client = create_api_client()
        method = "GET"
        mock_request.side_effect = Timeout
        with self.assertRaises(Timeout):
            client.request(TEST_PATH, method, TEST_DATA)
            mock_request.assert_called_once()
            mock_request.assert_called_with(
                method,
                f"{TEST_URL}/{TEST_ENDPOINT}/{TEST_PATH}",
                json.dumps(TEST_DATA),
                TEST_HEADERS,
                TEST_TIMEOUT,
                TEST_SSL,
            )


if __name__ == "__main__":
    unittest.main()
