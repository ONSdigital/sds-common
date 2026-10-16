from __future__ import annotations

from unittest.mock import MagicMock, patch

import sds_common

from sds_common.test_helpers.integration_helpers import (
    cleanup,
    clear_integration_helper_cache,
    poll_subscription,
    pubsub_purge_messages,
    pubsub_setup,
    pubsub_teardown,
)


class TestCleanup:
    def test_cleanup_is_exported_from_top_level_package(self):
        assert sds_common.cleanup is cleanup

    def test_cleanup_uses_supplied_firebase_loader(self):
        firebase_loader = MagicMock()
        firebase_loader.get_client.return_value = "firestore-client"
        firebase_loader.get_schemas_collection.return_value = "schemas-collection"

        with patch(
            "sds_common.test_helpers.integration_helpers.perform_delete_on_collection_with_test_survey_id"
        ) as mock_delete:
            cleanup(firebase_loader)

        mock_delete.assert_called_once_with("firestore-client", "schemas-collection", "test_survey_id")

    def test_cleanup_reuses_cached_loader(self):
        clear_integration_helper_cache()
        firestore_client = MagicMock()
        firestore_client.collection.return_value = "schemas-collection"

        with patch("sds_common.test_helpers.integration_helpers.get_config") as mock_get_config:
            mock_get_config.return_value.PROJECT_ID = "test-project"
            mock_get_config.return_value.FIRESTORE_DB_NAME = "test-db"
            with patch(
                "sds_common.test_helpers.integration_helpers.firestore.Client",
                return_value=firestore_client,
            ) as mock_firestore_client:
                with patch(
                    "sds_common.test_helpers.integration_helpers.perform_delete_on_collection_with_test_survey_id"
                ) as mock_delete:
                    cleanup()
                    cleanup()

        mock_firestore_client.assert_called_once_with(project="test-project", database="test-db")
        assert mock_delete.call_count == 2


class TestPubSubHelpers:
    def test_pubsub_helpers_are_exported_from_top_level_package(self):
        assert sds_common.pubsub_setup is pubsub_setup
        assert sds_common.pubsub_teardown is pubsub_teardown
        assert sds_common.pubsub_purge_messages is pubsub_purge_messages
        assert sds_common.poll_subscription is poll_subscription

    def test_pubsub_setup_supports_injected_helper(self):
        helper = MagicMock()

        pubsub_setup("subscriber-1", "topic-1", pubsub_helper=helper)

        helper.try_create_subscriber.assert_called_once_with("subscriber-1")

    def test_pubsub_setup_can_build_helper_without_facade(self):
        helper = MagicMock()
        clear_integration_helper_cache()

        with patch("sds_common.test_helpers.integration_helpers.get_config") as mock_get_config:
            mock_get_config.return_value.PROJECT_ID = "test-project"
            with patch(
                "sds_common.test_helpers.integration_helpers.SubscriberClient",
                return_value=MagicMock(),
            ) as mock_subscriber_client:
                with patch(
                    "sds_common.test_helpers.integration_helpers.PublisherClient",
                    return_value=MagicMock(),
                ) as mock_publisher_client:
                    with patch(
                        "sds_common.test_helpers.integration_helpers.PubSubHelper",
                        return_value=helper,
                    ) as mock_helper_cls:
                        pubsub_setup("subscriber-1", "topic-1")
                        pubsub_setup("subscriber-2", "topic-1")

        mock_helper_cls.assert_called_once_with(
            topic_id="topic-1",
            subscriber_client=mock_subscriber_client.return_value,
            publisher_client=mock_publisher_client.return_value,
            project_id="test-project",
        )
        assert helper.try_create_subscriber.call_args_list == [
            (("subscriber-1",), {}),
            (("subscriber-2",), {}),
        ]

    def test_pubsub_teardown_uses_injected_helper(self):
        helper = MagicMock()

        pubsub_teardown("subscriber-1", "topic-1", pubsub_helper=helper)

        helper.try_delete_subscriber.assert_called_once_with("subscriber-1")

    def test_pubsub_purge_messages_uses_injected_helper(self):
        helper = MagicMock()

        pubsub_purge_messages("subscriber-1", "topic-1", pubsub_helper=helper)

        helper.purge_messages.assert_called_once_with("subscriber-1")

    def test_poll_subscription_uses_injected_helper(self):
        helper = MagicMock()
        helper.pull_and_acknowledge_messages.return_value = [{"message": "ok"}]

        response = poll_subscription("subscriber-1", "topic-1", pubsub_helper=helper)

        assert response == [{"message": "ok"}]
        helper.pull_and_acknowledge_messages.assert_called_once_with("subscriber-1")

    def test_poll_subscription_returns_none_after_timeout(self):
        helper = MagicMock()
        helper.pull_and_acknowledge_messages.return_value = None

        with patch("sds_common.test_helpers.integration_helpers.time.time", side_effect=[0, 1, 4]):
            with patch("sds_common.test_helpers.integration_helpers.time.sleep") as mock_sleep:
                response = poll_subscription("subscriber-1", "topic-1", timeout=3, pubsub_helper=helper)

        assert response is None
        assert helper.pull_and_acknowledge_messages.call_count == 1
        mock_sleep.assert_called_once_with(3)

    def test_pubsub_helpers_reuse_cached_helper(self):
        clear_integration_helper_cache()
        helper = MagicMock()

        with patch("sds_common.test_helpers.integration_helpers.get_config") as mock_get_config:
            mock_get_config.return_value.PROJECT_ID = "test-project"
            with patch(
                "sds_common.test_helpers.integration_helpers.SubscriberClient",
                return_value=MagicMock(),
            ) as mock_subscriber_client:
                with patch(
                    "sds_common.test_helpers.integration_helpers.PublisherClient",
                    return_value=MagicMock(),
                ) as mock_publisher_client:
                    with patch(
                        "sds_common.test_helpers.integration_helpers.PubSubHelper",
                        return_value=helper,
                    ) as mock_helper_cls:
                        pubsub_teardown("subscriber-1", "topic-1")
                        pubsub_purge_messages("subscriber-2", "topic-1")
                        poll_subscription("subscriber-3", "topic-1")

        mock_helper_cls.assert_called_once_with(
            topic_id="topic-1",
            subscriber_client=mock_subscriber_client.return_value,
            publisher_client=mock_publisher_client.return_value,
            project_id="test-project",
        )


