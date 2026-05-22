from abc import ABC, abstractmethod


class SecretServiceInterface(ABC):
    @abstractmethod
    def get_oauth_client_id(self) -> str:
        ...

