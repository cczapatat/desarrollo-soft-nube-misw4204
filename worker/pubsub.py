import os
import json
from google.cloud import pubsub_v1

project_id = os.environ.get('GCLOUD_PROJECT')
subscription_id = os.environ.get('NAME_SUB', 'videos-sub')

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)


def callback(message: pubsub_v1.subscriber.message.Message, process) -> None:
    print(f"Received on pubSub: {message}")

    try:
        msn = (str(message.data)
               .replace('b"', '')
               .replace('"', '')
               .replace("'", '"'))
        body_parsed = json.loads(msn)
        process(body_parsed)
    except Exception as ex:
        print(f"Error Generate during PubSub, ${str(ex)}")

    message.ack()


def run_pubsub(process):
    subscriber.subscribe(subscription_path, callback=lambda message: callback(message, process))
    print(f"Listening for messages on {subscription_path}..\n")

    try:
        while True:
            pass
    except:
        print("Fail Pub Sub")
