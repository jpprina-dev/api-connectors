"""Tests for APIClient base class."""
import json
import unittest
from unittest.mock import patch

from api_connectors.APIClient import APIClient

TEST_URL = "http://test-url"
TEST_ENDPOINT = "api"
TEST_SSL = False
TEST_TIMEOUT = 1
TEST_DATA = {"test": "test_data"}
TEST_PATH = "test/path"
TEST_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def create_api_client():
    return APIClient(TEST_URL, TEST_ENDPOINT, TEST_SSL, TEST_TIMEOUT)


class TestAPIClient(unittest.TestCase):
    @patch("api_connectors.APIClient.APIClient.request")
    def test_request(self, mock_request):
        client = create_api_client()
        mock_request.side_effect = {"return_code": 200, "status": "success"}
        client.get(path=TEST_PATH, data=TEST_DATA)
        mock_request.assert_called_once()
        mock_request.assert_called_with(path=TEST_PATH, data=TEST_DATA, method="GET")

    @patch("api_connectors.APIClient.requests.Session")
    def test_get(self, session_mock):
        client = create_api_client()
        client.post(path=TEST_PATH, data=TEST_DATA)
        session_mock.return_value.request.assert_called_once()
        session_mock.return_value.request.assert_called_with(
            "POST",
            f"{TEST_URL}/{TEST_ENDPOINT}/{TEST_PATH}",
            data=json.dumps(TEST_DATA),
            headers=TEST_HEADERS,
            timeout=TEST_TIMEOUT,
            verify=TEST_SSL,
        )


if __name__ == "__main__":
    unittest.main()
