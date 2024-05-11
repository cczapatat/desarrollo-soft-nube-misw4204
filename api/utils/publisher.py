import os
from google.cloud import pubsub_v1

project_id = os.environ.get('GCLOUD_PROJECT')
name_queue = os.environ.get('NAME_QUEUE', 'videos')
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, name_queue)


def publish_messages_data(message: str) -> None:
    future = publisher.publish(topic_path, message.encode("utf-8"))
    print(future.result())

    print(f"Published messages to {topic_path}.")
