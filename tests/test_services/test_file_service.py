"""Tests for FileService."""
from __future__ import annotations

from unittest.mock import MagicMock

from sds_common.services.file_service import FileService


def _make_repo():
    return MagicMock()


class TestFileService:
    def test_upload_file_delegates_to_repository(self):
        svc = FileService(bucket_repository=_make_repo())
        svc.bucket_repository.upload_file_from_path = MagicMock()
        svc.upload_file("/tmp/myfile.json")
        svc.bucket_repository.upload_file_from_path.assert_called_once_with("/tmp/myfile.json")

    def test_retrieve_json_file_delegates_to_repository(self):
        repo = _make_repo()
        repo.get_file_as_json.return_value = {"key": "value"}
        svc = FileService(bucket_repository=repo)
        result = svc.retrieve_json_file("myfile.json")
        repo.get_file_as_json.assert_called_once_with("myfile.json")
        assert result == {"key": "value"}

    def test_delete_file_delegates_to_repository(self):
        repo = _make_repo()
        svc = FileService(bucket_repository=repo)
        svc.delete_file("oldfile.json")
        repo.delete_file.assert_called_once_with("oldfile.json")

    def test_check_file_exists_delegates_to_repository(self):
        repo = _make_repo()
        repo.check_file_exists.return_value = True
        svc = FileService(bucket_repository=repo)
        assert svc.check_file_exists("exists.json") is True

    def test_check_file_not_exists(self):
        repo = _make_repo()
        repo.check_file_exists.return_value = False
        svc = FileService(bucket_repository=repo)
        assert svc.check_file_exists("missing.json") is False

    def test_file_service_has_no_bucket_attribute(self):
        """FileService no longer exposes .bucket — callers must use .bucket_repository."""
        repo = _make_repo()
        svc = FileService(bucket_repository=repo)
        assert not hasattr(svc, 'bucket')
