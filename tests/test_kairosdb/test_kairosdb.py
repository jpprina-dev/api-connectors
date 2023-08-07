"""Tests for APIClient base class."""
import json
import unittest
import pytest
from unittest.mock import patch
import requests
from api_connectors.kairosdb import KairosDBAPIClient

TEST_URL = "http://test-url"
TEST_ENDPOINT = "api/v1"
TEST_PORT = 8080
TEST_SSL = None
TEST_TIMEOUT = None
TEST_HEADERS = {"Content-Type": "application/json", "Accept": "application/json","User-Agent": "python-kairosdb"}


def build_url(path):
    return f"{TEST_URL}/{TEST_ENDPOINT}:{TEST_PORT}/{path}"

def create_api_client():
    return KairosDBAPIClient(TEST_URL)

@pytest.fixture
def example_response():
    with open('api_connector/resources/samples/sample_response.json', 'r+') as sample_file:
        sample_response = json.loads(sample_file)
    return sample_response


class TestKairosClient(unittest.TestCase):
    @patch("api_connectors.APIClient.requests.Session")
    def test_get_version(self, mock_request):
        client = create_api_client()
        mock_content = {"version": "KairosDB 0.9.4"}
        mock_request.return_value.request.return_value = requests.Response(**{
            "status_code": 200,
            "status": "success",
            "content": mock_content
            })
        response = client.version()
        self.assertEqual(mock_content["version"], response)
        mock_request.assert_called_once()
        mock_request.assert_called_with(
            "GET",
            build_url("version"),
            data={},
            headers=TEST_HEADERS,
            timeout=TEST_TIMEOUT,
            verify=TEST_SSL,
            )



if __name__ == "__main__":
    unittest.main()
