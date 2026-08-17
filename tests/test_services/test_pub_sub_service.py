"""Tests for PubSubService."""
from __future__ import annotations

from unittest.mock import MagicMock


from sds_common.services.pub_sub_service import PubSubService


class TestPubSubService:
    def _make_service(self) -> tuple[PubSubService, MagicMock]:
        publisher = MagicMock()
        publisher.topic_path.return_value = "projects/proj/topics/my-topic"
        svc = PubSubService(publisher_client=publisher, project_id="proj")
        return svc, publisher

    def test_send_message_publishes_to_correct_topic(self):
        svc, publisher = self._make_service()
        svc.publish('{"error_type": "E", "message": "M", "filepath": "/f"}', "my-topic")
        publisher.topic_path.assert_called_once_with("proj", "my-topic")
        publisher.publish.assert_called_once()

    def test_send_message_encodes_as_utf8_bytes(self):
        svc, publisher = self._make_service()
        svc.publish('{"key": "value"}', "my-topic")
        call_args = publisher.publish.call_args
        published_data = call_args[1].get("data") or call_args[0][1]
        assert isinstance(published_data, bytes)
        assert b'"key"' in published_data

    def test_send_message_uses_project_id(self):
        svc, publisher = self._make_service()
        svc.publish("msg", "topic-id")
        publisher.topic_path.assert_called_with("proj", "topic-id")

    def test_send_message_accepts_plain_string(self):
        """PubSubService is decoupled from SchemaPublishError — accepts any str."""
        svc, publisher = self._make_service()
        svc.publish("plain string message", "topic-id")
        publisher.publish.assert_called_once()

    def test_schema_publish_error_can_be_serialised_for_send_message(self):
        """Callers serialise errors themselves before passing to send_message."""
        from sds_common.models.schema_publish_errors import SchemaPublishError
        error = SchemaPublishError("EType", "A message", "/path.json")
        svc, publisher = self._make_service()
        svc.publish(error.generate_message_content(), "my-topic")
        publisher.publish.assert_called_once()
