import time

from google.cloud import storage
from sds_common.test_helpers.pub_sub_helper import PubSubHelper

storage_client = storage.Client()


def pubsub_setup(pubsub_helper: PubSubHelper, subscriber_id: str):
    """Creates any subscribers that may be used in tests"""
    pubsub_helper.try_create_subscriber(subscriber_id)


def pubsub_teardown(pubsub_helper: PubSubHelper, subscriber_id: str):
    """Deletes subscribers that may have been used in tests"""
    pubsub_helper.try_delete_subscriber(subscriber_id)


def pubsub_purge_messages(pubsub_helper: PubSubHelper, subscriber_id: str):
    """Purge any messages that may have been sent to a subscriber"""
    pubsub_helper.purge_messages(subscriber_id)


def inject_wait_time(seconds: int):
    """
    Method to inject a wait time into the test to allow resources properly spin up and tear down.

    :param seconds: the number of seconds to wait
    """
    time.sleep(seconds)


def poll_subscription(pubsub_helper, subscriber_id, timeout=45) -> list[dict] | None:
    """
    Polls a subscription for messages until the timeout is reached.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = pubsub_helper.pull_and_acknowledge_messages(subscriber_id)
        if response:
            return response
        time.sleep(3)
    return None
