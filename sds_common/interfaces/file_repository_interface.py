from abc import ABC

class FileRepositoryInterface(ABC):
    def get_file_as_json(self, filename: str) -> dict:
        """
        Gets a file with a specific filename and loads it as json.

        :param filename: name of file being loaded.
        :return: dict: the file loaded as json.
        """
        ...

    def upload_file_from_path(self, filepath: str):
        """
        Uploads a file from a local file path.

        :param filepath: path to the local file to be uploaded.
        """
        ...

    def delete_file(self, filename: str):
        """
        Deletes a file with the specified filename.

        :param filename: name of the file to be deleted.
        """
        ...

    def check_file_exists(self, filename: str) -> bool:
        """
        Checks if a file exists with the specified filename.

        :param filename: name of the file to be checked.
        :return: True if file exists, False otherwise.
        """
        ...
