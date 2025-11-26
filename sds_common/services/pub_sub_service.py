from sds_common.config.config import CONFIG
from google.cloud.pubsub_v1 import PublisherClient
from sds_common.models.schema_publish_errors import SchemaPublishError


class PubSubService:
    def __init__(self):
        self.publisher = PublisherClient()

    def send_message(self, error: SchemaPublishError, topic_id: str):
        """
        Sends a Pub/Sub message to the specified topic.

        :param error: The SchemaPublishError object containing message info to send.
        :param topic_id: The ID of the topic to send the message to.
        """
        topic_path = self.publisher.topic_path(CONFIG.PROJECT_ID, topic_id)
        message_json = error.generate_message_content()
        self.publisher.publish(topic_path, data=message_json.encode("utf-8"))


PUB_SUB_SERVICE = PubSubService()
