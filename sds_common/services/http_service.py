from typing import Self

import google.auth.transport.requests
import google.oauth2.id_token
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from google.cloud import iam_credentials_v1

from sds_common.config.config import CONFIG
from sds_common.services.gcp_secret_service import GcpSecretService
from sds_common.interfaces.secret_service_interface import SecretServiceInterface
from sds_common.interfaces.http_service_interface import HttpServiceInterface


class HttpService(HttpServiceInterface):
    def __init__(self, secret_service: SecretServiceInterface, session: requests.Session, headers: dict[str, str] | None):
        self.secret_service = secret_service
        self.session = session
        self.headers = headers

    @classmethod
    def create(cls, authentication_headers: bool, secret_service: SecretServiceInterface | None = None) -> Self:
        """
        Factory method to create an instance of HttpService.

        :param authentication_headers: whether to include authentication headers.
        :param secret_service: an instance of SecretServiceInterface to retrieve secrets for authentication.
                               Only required when authentication_headers=True.
        :return: an instance of HttpService.
        """
        session = cls._setup_session()
        headers = cls.generate_authentication_headers() if authentication_headers else None
        return cls(secret_service, session, headers)

    @staticmethod
    def _setup_session() -> requests.Session:
        """
        Set up an http/s session.

        :return: an http/s session.
        """
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def make_post_request(self, url: str, data: dict, params: dict = None) -> requests.Response:
        """
        Make a POST request to a specified URL.

        :param url: the URL to send the POST request to.
        :param data: the JSON data to send in the POST request.
        :param params: the query parameters to include in the POST request.
        :return: the response from the POST request.
        """

        response = self.session.post(url, json=data, headers=self.headers, params=params)
        return response

    def make_get_request(self, url: str, params: dict = None) -> requests.Response:
        """
        Make a GET request to a specified URL.

        :param url: the URL to send the GET request to.
        :param params: the query parameters to include in the GET request.
        :return: the response from the GET request.
        """
        response = self.session.get(url, headers=self.headers, params=params)
        return response

    @staticmethod
    def generate_authentication_headers() -> dict[str, str]:
        """
        Create headers for authentication through SDS load balancer.
        This method is only used when the application is run on GCP and the metadata server can be used in fetch_id_token

        :return dict[str, str]: the headers required for remote authentication.
        """
        secret_service = GcpSecretService()
        oauth_client_id = secret_service.get_oauth_client_id()
        auth_req = google.auth.transport.requests.Request()
        auth_token = google.oauth2.id_token.fetch_id_token(
            auth_req, audience=oauth_client_id
        )

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }

        return headers

    @staticmethod
    def generate_authentication_headers_by_impersonation() -> dict[str, str]:
        """
        Create headers for authentication through SDS load balancer.
        This method is only used when the application is run locally. It uses the user account that is logged in
        as default-application to impersonate the default App Engine account to generate the Open ID token.
        User account requires the role "Service Account Token Creator"

        :return dict[str, str]: the headers required for remote authentication.
        """
        secret_service = GcpSecretService()
        oauth_client_id = secret_service.get_oauth_client_id()
        impersonated_sa_email = f"{CONFIG.PROJECT_ID}@appspot.gserviceaccount.com"
        iam_credentials_client = iam_credentials_v1.IAMCredentialsClient()
        resource_name = f"projects/-/serviceAccounts/{impersonated_sa_email}"

        response = iam_credentials_client.generate_id_token(
            name=resource_name,
            audience=oauth_client_id,
            include_email=True
        )

        auth_token = response.token

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }

        return headers
