from abc import ABC, abstractmethod

import requests


class HttpServiceInterface(ABC):
    @abstractmethod
    def make_get_request(self, url: str, params: dict = None) -> requests.Response:
        ...

    @abstractmethod
    def make_post_request(self, url: str, data: dict, params: dict = None) -> requests.Response:
        ...

