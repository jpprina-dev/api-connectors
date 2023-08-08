"""Tests for APIClient base class."""
import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from api_connectors.kairosdb import KairosDBAPIClient
from tests import ROOT_DIR

TEST_URL = "http://test-url"
TEST_ENDPOINT = "api/v1"
TEST_PORT = 8080
TEST_SSL = None
TEST_TIMEOUT = None
TEST_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "python-kairosdb",
}


def build_url(path):
    return f"{TEST_URL}:{TEST_PORT}/{TEST_ENDPOINT}/{path}"


def create_api_client():
    return KairosDBAPIClient(TEST_URL)


def sample_query():
    with open(
        Path.joinpath(ROOT_DIR, "api_connectors/resources/samples/sample_query.json"), "r+"
    ) as sample_file:
        query = json.load(sample_file)
    return query


# @pytest.fixture
# def sample_response():
#     with open("api_connector/resources/samples/sample_response.json", "r+") as sample_file:
#         response = json.loads(sample_file)
#     return response


class TestKairosClient(unittest.TestCase):
    @patch("api_connectors.APIClient.requests.Session")
    def test_get_version(self, mock_request):
        client = create_api_client()
        mock_content = {"version": "KairosDB 0.9.4"}
        mock_request.return_value.request.return_value = MagicMock(
            status_code=200, json=lambda: mock_content
        )
        response = client.version
        self.assertEqual(mock_content["version"], response)
        mock_request.return_value.request.assert_called_once()
        mock_request.return_value.request.assert_called_with(
            "GET",
            build_url("version"),
            data=json.dumps({}),
            headers=TEST_HEADERS,
            timeout=TEST_TIMEOUT,
            verify=TEST_SSL,
        )

    @patch("api_connectors.APIClient.requests.Session")
    def test_get_health_status(self, mock_request):
        client = create_api_client()
        mock_content = ["JVM-Thread-Deadlock: OK", "Datastore-Query: OK"]
        mock_request.return_value.request.return_value = MagicMock(
            status_code=200, json=lambda: mock_content, text=str(mock_content)
        )
        response = client.health_status
        self.assertEqual(str(mock_content), response["response"])
        mock_request.return_value.request.assert_called_once()
        mock_request.return_value.request.assert_called_with(
            "GET",
            build_url("health/status"),
            data=json.dumps({}),
            headers=TEST_HEADERS,
            timeout=TEST_TIMEOUT,
            verify=TEST_SSL,
        )

    @patch("api_connectors.APIClient.requests.Session")
    def test_get_health_check(self, mock_request):
        client = create_api_client()
        mock_request.return_value.request.return_value = MagicMock(status_code=204)
        response = client.health_check
        self.assertEqual(204, response["return_code"])
        mock_request.return_value.request.assert_called_once()
        mock_request.return_value.request.assert_called_with(
            "GET",
            build_url("health/check"),
            data=json.dumps({}),
            headers=TEST_HEADERS,
            timeout=TEST_TIMEOUT,
            verify=TEST_SSL,
        )

    @patch("api_connectors.APIClient.requests.Session")
    def test_get_metricnames(self, mock_request):
        client = create_api_client()
        mock_content = {"results": ["archive_file_search", "archive_file_tracked"]}
        mock_request.return_value.request.return_value = MagicMock(
            status_code=200, json=lambda: mock_content
        )
        response = client.metricnames
        self.assertEqual(mock_content["results"], response)
        mock_request.return_value.request.assert_called_once()
        mock_request.return_value.request.assert_called_with(
            "GET",
            build_url("metricnames"),
            data=json.dumps({}),
            headers=TEST_HEADERS,
            timeout=TEST_TIMEOUT,
            verify=TEST_SSL,
        )

    @patch("api_connectors.APIClient.requests.Session")
    def test_post_metrics(self, mock_request):
        client = create_api_client()
        mocked_query = sample_query()
        client.query_metrics(data=mocked_query)
        mock_request.return_value.request.assert_called_once()
        mock_request.return_value.request.assert_called_with(
            "POST",
            build_url("datapoints/query"),
            data=json.dumps(mocked_query),
            headers=TEST_HEADERS,
            timeout=TEST_TIMEOUT,
            verify=TEST_SSL,
        )


if __name__ == "__main__":
    unittest.main()
