from __future__ import annotations
import time
from functools import lru_cache

from google.cloud.pubsub_v1 import PublisherClient, SubscriberClient
from google.cloud import firestore

from sds_common.config.config import get_config
from sds_common.test_helpers.common_test_data import test_survey_id
from sds_common.test_helpers.firebase_loader import FirebaseLoader
from sds_common.test_helpers.firestore_helpers import perform_delete_on_collection_with_test_survey_id
from sds_common.test_helpers.pub_sub_helper import PubSubHelper

config = get_config()


@lru_cache(maxsize=None)
def _get_firebase_loader(project_id: str, firestore_db_name: str) -> FirebaseLoader:
    return FirebaseLoader(
        firestore.Client(
            project=project_id,
            database=firestore_db_name,
        )
    )


@lru_cache(maxsize=None)
def _get_pubsub_helper(topic_id: str, project_id: str) -> PubSubHelper:
    return PubSubHelper(
        topic_id=topic_id,
        subscriber_client=SubscriberClient(),
        publisher_client=PublisherClient(),
        project_id=project_id,
    )


def clear_integration_helper_cache() -> None:
    """Clear cached helper instances; useful when test config changes within a process."""
    _get_firebase_loader.cache_clear()
    _get_pubsub_helper.cache_clear()


def cleanup(firebase_loader: FirebaseLoader | None = None):
    """
    Cleans up all schema test data created in FireStore.
    Should be run before and after test to account for test failures.
    """
    if firebase_loader is None:
        firebase_loader = _get_firebase_loader(config.PROJECT_ID, config.FIRESTORE_DB_NAME)

    client = firebase_loader.get_client()
    perform_delete_on_collection_with_test_survey_id(
        client,
        firebase_loader.get_schemas_collection(),
        test_survey_id,
    )


def pubsub_setup(
    subscriber_id: str,
    topic_id: str,
    pubsub_helper: PubSubHelper | None = None,
):
    """Creates any subscribers that may be used in tests"""
    if pubsub_helper is None:
        pubsub_helper = _get_pubsub_helper(topic_id, config.PROJECT_ID)
    pubsub_helper.try_create_subscriber(subscriber_id)


def pubsub_teardown(
    subscriber_id: str,
    topic_id: str,
    pubsub_helper: PubSubHelper | None = None,
):
    """Deletes subscribers that may have been used in tests"""
    if pubsub_helper is None:
        pubsub_helper = _get_pubsub_helper(topic_id, config.PROJECT_ID)
    pubsub_helper.try_delete_subscriber(subscriber_id)


def pubsub_purge_messages(
    subscriber_id: str,
    topic_id: str,
    pubsub_helper: PubSubHelper | None = None,
):
    """Purge any messages that may have been sent to a subscriber"""
    if pubsub_helper is None:
        pubsub_helper = _get_pubsub_helper(topic_id, config.PROJECT_ID)
    pubsub_helper.purge_messages(subscriber_id)


def inject_wait_time(seconds: int):
    """
    Injects a wait time to allow GCP resources to spin up and tear down.

    :param seconds: the number of seconds to wait
    """
    time.sleep(seconds)


def poll_subscription(
    subscriber_id: str,
    topic_id: str,
    timeout: int = 45,
    pubsub_helper: PubSubHelper | None = None,
) -> list[dict] | None:
    """
    Polls a subscription for messages until the timeout is reached.
    """
    if pubsub_helper is None:
        pubsub_helper = _get_pubsub_helper(topic_id, config.PROJECT_ID)
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = pubsub_helper.pull_and_acknowledge_messages(subscriber_id)
        if response:
            return response
        time.sleep(3)
    return None
