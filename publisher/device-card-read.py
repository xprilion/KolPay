import base64
from operator import sub
from google.cloud import pubsub_v1
import json
from concurrent.futures import TimeoutError
import uuid

# Declare the project ID
project_id = "niyoproject-306620"

# Initiate Publisher and Subscriber for PubSub
publisher = pubsub_v1.PublisherClient.from_service_account_json(".key/service-account-key.json")
subscriber = pubsub_v1.SubscriberClient.from_service_account_json(".key/service-account-key.json")

reader_id = "anu2"
card_id = "f50ec0b7-f960-400d-91f0-c42a6d44e3d0"
action = None
amount = None
topic_id = None
topic_path = None
subscription_path = None
subscription = None
streaming_pull_future = None

timeout = 300.0

def read_card():
    topic_path = publisher.topic_path(project_id, reader_id)
    payload = {
        'reader_id': reader_id,
        'card_id': card_id,
        'action': action,
        'amount': amount
    }
    future = publisher.publish(topic_path, bytes(json.dumps(payload), "utf-8"))
    print(f'Card details published successfully with message: {future.result()}')

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    global action, amount
    print(f"Received {message}.")
    message.ack()
    data = json.loads(message.data)
    if "action" in data.keys():
        action = data["action"]
    if "amount" in data.keys():
        amount = data["amount"]
    if "read" in data.keys() and data["read"] == True:
        read_card()

def main():
    # Connect to PubSub topic as subscriber
    topic_id = reader_id
    topic_path = publisher.topic_path(project_id, topic_id)
    subscription_path = subscriber.subscription_path(project_id, topic_id)

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.


main()