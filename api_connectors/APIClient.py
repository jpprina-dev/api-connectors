import json
from functools import partial

import logging
import requests


logger = logging.getLogger(__name__)


class APIClient:
    """API client

    It implements common HTTP methods GET, POST, PUT and DELETE
    This client is using :mod:`requests` package. Please see
    http://docs.python-requests.org/ for more information.

    :param str api_endpoint: API endpoint
    :param bool verify: Control SSL certificate validation
    :param int timeout: Request timeout in seconds

    .. method:: get(self, path, data=None, **kwargs)

        Partial method invoking :meth:`~APIClient.request` with
        http method *GET*.

    .. method:: post(self, path, data=None, **kwargs)

        Partial method invoking :meth:`~APIClient.request` with
        http method *POST*.

    .. method:: put(self, path, data=None, **kwargs)

        Partial method invoking :meth:`~APIClient.request` with
        http method *PUT*.

    .. method:: delete(self, path, data=None, **kwargs)

        Partial method invoking :meth:`~APIClient.request` with
        http method *DELETE*.
    """

    def __init__(self, api_endpoint, verify=None, timeout=None):
        """Initialization method"""
        self.verify = verify
        self.timeout = timeout

        self.api_endpoint = api_endpoint

        self.request_headers = {"Content-Type": "application/json", "Accept": "application/json"}

        self.r_session = requests.Session()

        # Directly expose common HTTP methods
        self.get = partial(self.request, method="GET")
        self.post = partial(self.request, method="POST")
        self.put = partial(self.request, method="PUT")
        self.delete = partial(self.request, method="DELETE")

    def request(self, path, method, data=None, **kwargs):
        """Handle requests to API

        :param str path: API endpoint's path to request
        :param str method: HTTP method to use
        :param dict data: Data to send (optional)
        :return: Parsed json response as :class:`dict`

        Additional named argument may be passed and are directly transmitted
        to :meth:`request` method of :class:`requests.Session` object.
        """
        if not path.startswith("http://") and not path.startswith("https://"):
            url = f"{self.api_endpoint}/{path}"
        else:
            url = path

        if data is None:
            data = {}

        response = self.r_session.request(
            method,
            url,
            data=json.dumps(data),
            headers=self.request_headers,
            timeout=self.timeout,
            verify=self.verify,
            **kwargs,
        )
        logger.debug(f"API response {response}")

        if response.status_code == 204:
            return {"return_code": response.status_code, "status": "success"}

        try:
            response_data = {"return_code": response.status_code}
            response_data.update(response.json())
            return response_data
        except ValueError:
            return {"return_code": response.status_code, "response": response.text}
