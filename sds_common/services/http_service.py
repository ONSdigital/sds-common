import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
import google.oauth2.id_token

from sds_common.services.secret_service import SECRET_SERVICE


class HttpService:

    def __init__(self, session: requests.Session, headers: dict[str, str] | None):
        self.session = session
        self.headers = headers

    @classmethod
    def create(cls, authentication_headers: bool):
        session = cls._setup_session()
        headers = cls.generate_authentication_headers() if authentication_headers else None
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

    def make_get_request(self, url: str) -> requests.Response:
        """
        Make a GET request to a specified URL.

        Parameters:
            url (str): the URL to send the GET request to.

        Returns:
            requests.Response: the response from the GET request.
        """
        response = self.session.get(url, headers=self.headers)
        return response

    @staticmethod
    def generate_authentication_headers() -> dict[str, str]:
        """
        Create headers for authentication through SDS load balancer.

        Returns:
            dict[str, str]: the headers required for remote authentication.
        """
        oauth_client_id = SECRET_SERVICE.get_oauth_client_id()
        auth_req = google.auth.transport.requests.Request()
        auth_token = google.oauth2.id_token.fetch_id_token(
            auth_req, audience=oauth_client_id
        )

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }

        return headers

HTTP_SERVICE = HttpService.create(False)
AUTHENTICATED_HTTP_SERVICE = HttpService.create(True)
