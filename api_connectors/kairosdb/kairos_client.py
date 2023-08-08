import fnmatch
import logging

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

    def __init__(self, *args, port=8080, api_version=1, **kwargs):
        """Initialization method"""
        super().__init__(*args, **kwargs)
        self.request_headers.update({"User-Agent": "python-kairosdb"})
        self.api_endpoint = f"{self.api_endpoint}:{port}/api/v{api_version}"

        self._metricnames = None
        self._tagnames = None
        self._tagvalues = None

    @property
    def version(self):
        """KairosDB version"""
        response = self.get("version")
        logger.debug(f"[KAIROSDB version] {response}")
        return response.get("version")

    @property
    def health_status(self):
        """KairosDB health status"""
        response = self.get("health/status")
        logger.debug(f"[KAIROSDB health_status] {response}")
        return response

    @property
    def health_check(self):
        """KairosDB health check"""
        response = self.get("health/check")
        logger.debug(f"[KAIROSDB health_check] {response}")
        return response

    @property
    def metricnames(self):
        """Metric names"""
        if not self._metricnames:
            self._metricnames = self.get("metricnames").get("results")
        return self._metricnames

    @property
    def tagnames(self):
        """Tag names"""
        if not self._tagnames:
            self._tagnames = self.get("tagnames").get("results")
        return self._tagnames

    @property
    def tagvalues(self):
        """Tag values"""
        if not self._tagvalues:
            self._tagvalues = self.get("tagvalues").get("results")
        return self._tagvalues

    def search_metrics(self, matches, exclude_matches=None):
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

    def query_metrics(self, data):
        """Get metrics data points

        :param dict data: Data to post for query
        :return: Metric data points as :class:`dict`

        .. seealso:: \
            https://kairosdb.github.io/docs/restapi/QueryMetrics.html
        """
        return self.post("datapoints/query", data=data)

    def delete_metric(self, metric_name):
        """Delete a metric and all data points associated with the metric

        :param str metric_name: Name of the metric to delete

        .. seealso:: \
            https://kairosdb.github.io/docs/restapi/DeleteMetric.html
        """
        return self.delete("metric/%s" % metric_name)

    def delete_datapoints(self, data):
        """Delete metric data points

        :param dict data: Data to post for query

        .. seealso:: \
            https://kairosdb.github.io/docs/restapi/DeleteDataPoints.html
        """
        return self.post("datapoints/delete", data=data)
