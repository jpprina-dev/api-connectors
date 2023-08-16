"""Tests for APIClient base class."""
import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from api_connectors.kairosdb import KairosDBAPIClient
from tests import ROOT_DIR

TEST_URL = "http://test-url:8080"
TEST_ENDPOINT = "api/v1"
TEST_SSL = None
TEST_TIMEOUT = None
TEST_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "python-kairosdb",
}
TEST_METRIC_NAMES = ["abc.123", "xyz.456"]
TEST_START_DATETIME = "2023-08-03 12:13:14"
TEST_END_DATETIME = "2023-08-10 12:13:14"


def build_url(path):
    return f"{TEST_URL}/{TEST_ENDPOINT}/{path}"


def create_api_client():
    return KairosDBAPIClient(TEST_URL)


def sample_json(file_name):
    with open(
        Path.joinpath(ROOT_DIR, f"api_connectors/resources/samples/{file_name}"), "r+"
    ) as sample_file:
        query = json.load(sample_file)
    return query


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
    def test_post_metrics_by_json(self, mock_request):
        client = create_api_client()
        mocked_query = sample_json("sample_query.json")
        client.query_metrics_by_json(data=mocked_query)
        mock_request.return_value.request.assert_called_once()
        mock_request.return_value.request.assert_called_with(
            "POST",
            build_url("datapoints/query"),
            data=json.dumps(mocked_query),
            headers=TEST_HEADERS,
            timeout=TEST_TIMEOUT,
            verify=TEST_SSL,
        )

    @patch("api_connectors.APIClient.requests.Session")
    def test_post_metrics_one_metric(self, mock_request):
        client = create_api_client()
        mocked_query = sample_json("sample_query_1.json")
        mocked_respose = sample_json("sample_response_1.json")
        status_code = 200
        mock_request.return_value.request.return_value = MagicMock(
            status_code=status_code, json=lambda: mocked_respose
        )
        response = client.query_metrics(
            TEST_METRIC_NAMES[0], TEST_START_DATETIME, TEST_END_DATETIME
        )
        mock_request.return_value.request.assert_called_once()
        mock_request.return_value.request.assert_called_with(
            "POST",
            build_url("datapoints/query"),
            data=json.dumps(mocked_query),
            headers=TEST_HEADERS,
            timeout=TEST_TIMEOUT,
            verify=TEST_SSL,
        )
        mocked_respose.update({"return_code": status_code})
        self.assertEqual(response, mocked_respose)

    @patch("api_connectors.APIClient.requests.Session")
    def test_post_metrics_two_mnetrics(self, mock_request):
        client = create_api_client()
        mocked_query = sample_json("sample_query_2.json")
        mocked_respose = sample_json("sample_response_2.json")
        status_code = 200
        mock_request.return_value.request.return_value = MagicMock(
            status_code=status_code, json=lambda: mocked_respose
        )
        response = client.query_metrics(TEST_METRIC_NAMES, TEST_START_DATETIME, TEST_END_DATETIME)
        mock_request.return_value.request.assert_called_once()
        mock_request.return_value.request.assert_called_with(
            "POST",
            build_url("datapoints/query"),
            data=json.dumps(mocked_query),
            headers=TEST_HEADERS,
            timeout=TEST_TIMEOUT,
            verify=TEST_SSL,
        )
        mocked_respose.update({"return_code": status_code})
        self.assertEqual(response, mocked_respose)

    def test_post_metrics_wrong_arg_type_value_error_1(self):
        client = create_api_client()
        with pytest.raises(ValueError):
            client.query_metrics(123, TEST_START_DATETIME, TEST_END_DATETIME)

    def test_post_metrics_wrong_arg_type_value_error_2(self):
        client = create_api_client()
        with pytest.raises(ValueError):
            client.query_metrics([123, 234], TEST_START_DATETIME, TEST_END_DATETIME)


if __name__ == "__main__":
    unittest.main()
