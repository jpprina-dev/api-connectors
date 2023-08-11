from typing import List, Union

import fnmatch
import logging
from datetime import datetime

from api_connectors.APIClient import APIClient

logger = logging.getLogger(__name__)


class KairosDBAPIClient(APIClient):
    """KairosDB API interface

    .. attribute:: version

        KairosDB version from API.

        .. seealso:: \
            https://kairosdb.github.io/docs/restapi/Version.html

    .. attribute:: health_status

        KairosDB health status from API.

        .. seealso:: \
            https://kairosdb.github.io/docs/restapi/Health.html#status

    .. attribute:: health_check

        KairosDB health check from API.

        .. seealso:: \
            https://kairosdb.github.io/docs/restapi/Health.html#check

    .. attribute:: metricnames

        KairosDB metric names from API.

        .. seealso:: \
            https://kairosdb.github.io/docs/restapi/ListMetricNames.html

    .. attribute:: tagnames

        KairosDB tag names from API.

        .. seealso:: \
            https://kairosdb.github.io/docs/restapi/ListTagNames.html

    .. attribute:: tagvalues

        KairosDB tag values from API.

        .. seealso:: \
            https://kairosdb.github.io/docs/restapi/ListTagValues.html
    """

    def __init__(self, *args, **kwargs):
        """Initialization method"""
        super().__init__(*args, **kwargs)
        self.request_headers.update({"User-Agent": "python-kairosdb"})
        self.api_endpoint = f"{self.api_endpoint}/api/v1"

        self._metricnames = None
        self._log_header = "[KAIROSDB API]"

    @property
    def version(self):
        """KairosDB version"""
        response = self.get("version")
        logger.debug(f"{self._log_header} version: {response}")
        return response.get("version")

    @property
    def health_status(self):
        """KairosDB health status"""
        response = self.get("health/status")
        logger.debug(f"{self._log_header} health_status: {response}")
        return response

    @property
    def health_check(self):
        """KairosDB health check"""
        response = self.get("health/check")
        logger.debug(f"{self._log_header} health_check: {response}")
        return response

    @property
    def metricnames(self):
        """Metric names"""
        if not self._metricnames:
            response = self.get("metricnames")
            logger.debug(f"{self._log_header} metricnames: {response}")
            self._metricnames = response.get("results")
        return self._metricnames

    def search_metrics(self, matches, exclude_matches=[]):
        """Search KairosDB metrics using glob matches

        :param list matches: List of glob matches
        :param list exclude_matches: List of glob matches for exclusions
        :return: Matched metric names as :func:`list`
        """
        x_metrics = []

        for match in exclude_matches:
            x_metrics.extend(fnmatch.filter(self.metricnames, match))

        matched_metrics = []
        for match in matches:
            for metric in fnmatch.filter(self.metricnames, match):
                if metric not in set(x_metrics):
                    matched_metrics.append(metric)

        return matched_metrics

    def query_metrics_by_json(self, data):
        """Get metrics data points by KairosDB json

        :param dict data: Data to post for query
        :return: Metric data points as :class:`dict`

        .. seealso:: \
            https://kairosdb.github.io/docs/restapi/QueryMetrics.html
        """
        response = self.post("datapoints/query", data=data)
        logger.debug(f"{self._log_header} query_metrics: {response}")
        return response

    def query_metrics(
        self, metrics: Union[str, list[str]], start_datetime: str, end_datetime: str
    ) -> dict:
        """Get metrics data points. Both the start and end datetimes are inclusive,
        meaning that data points falling on either the start or end timestamp will be
        included in the query response.

        :param metrics: metric or metrics to query
        :type metrics: Union[str, List[str]]
        :param start_datetime: start date and time to query in '%Y-%m-%d %H:%M:%S' format
        :type start_datetime: str
        :param end_datetime: end date and time to query in '%Y-%m-%d %H:%M:%S' format
        :type end_datetime: str
        :return: Metric data points as :class:`dict`
        :rtype: dict
        """
        _metrics = []
        if not isinstance(metrics, str) and not isinstance(metrics, list):
            raise ValueError("Must be a str or List[str] with metric(s) to query")
        elif isinstance(metrics, list):
            _metrics.extend(metrics)
        else:
            _metrics.append(metrics)

        if not all(isinstance(elem, str) for elem in _metrics):
            raise ValueError("Must be a List[str] with metrics to query")

        # TODO: Update the whole function in a Pydantic manner
        start_ms: int = int(
            datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S").timestamp() * 1000
        )
        end_ms: int = int(datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
        data = {
            "metrics": [{"tags": {}, "name": name} for name in _metrics],
            "plugins": [],
            "cache_time": 0,
            "start_absolute": start_ms,
            "end_absolute": end_ms,
        }

        response = self.post("datapoints/query", data=data)
        logger.debug(f"{self._log_header} query_metrics: {response}")
        # TODO: return_code not handled
        return response

    def delete_metric(self, metric_name):
        """Delete a metric and all data points associated with the metric

        :param str metric_name: Name of the metric to delete

        .. seealso:: \
            https://kairosdb.github.io/docs/restapi/DeleteMetric.html
        """
        return self.delete(f"metric/{metric_name}")

    def delete_datapoints(self, data):
        """Delete metric data points

        :param dict data: Data to post for query

        .. seealso:: \
            https://kairosdb.github.io/docs/restapi/DeleteDataPoints.html
        """
        return self.post("datapoints/delete", data=data)
