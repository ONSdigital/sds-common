import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from sds_common.utilities.utils import generate_authentication_headers


class HttpService:

    def __init__(self, session: requests.Session, headers: dict[str, str] | None):
        self.session = session
        self.headers = headers

    @classmethod
    def create(cls, headers: dict[str, str] | None):
        session = cls._setup_session()
        headers = headers
        return cls(session, headers)

    @staticmethod
    def _setup_session() -> requests.Session:
        """
        Set up an http/s session.

        Returns:
            Session: an http/s session.
        """
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def make_post_request(self, url: str, data: dict) -> requests.Response:
        """
        Make a POST request to a specified URL.

        Parameters:
            url (str): the URL to send the POST request to.
            data (dict): the JSON data to send in the POST request.

        Returns:
            requests.Response: the response from the POST request.
        """

        response = self.session.post(url, json=data, headers=self.headers)
        return response

    def make_get_request(self, url: str, sds_headers=None) -> requests.Response:
        """
        Make a GET request to a specified URL.

        Parameters:
            url (str): the URL to send the GET request to.
            sds_headers (bool): whether to include the SDS headers in the request (for SDS API).

        Returns:
            requests.Response: the response from the GET request.
        """
        response = self.session.get(url, headers=self.headers)
        return response

HTTP_SERVICE = HttpService.create(None)
AUTHENTICATED_HTTP_SERVICE = HttpService.create(generate_authentication_headers())
