import base64
from operator import sub
from google.cloud import firestore
from google.cloud import pubsub_v1
import json
from concurrent.futures import TimeoutError


# Declare the project ID
project_id = "niyoproject-306620"

# Connect to Firestore DB (Native Mode)
db = firestore.Client(project=project_id)

# Set active collection to readers
readers = db.collection(u'readers')
cards = db.collection(u'cards')

# Initiate Publisher and Subscriber for PubSub
publisher = pubsub_v1.PublisherClient()
subscriber_web = pubsub_v1.SubscriberClient()

action = None
amount = None
topic_id = None
topic_path = None
subscription_path_web = None
subscription_web = None
streaming_pull_future = None

timeout = 1800.0

def update_firestore(action, amount, card_id, reader_id):
     print("called update firestore")
     reader_data = {}
     reader_data["action"] = "success"
     reader_data["card"] = str(card_id)
     reader_data["amount"] = amount
     card_ref = cards.document(str(card_id))
     card = card_ref.get()
     if card.exists:
          print("Card exists")
          print(card)
          if action == "balance":
               reader_data["amount"] = card.get("balance")
          elif action == "credit":
               reader_data["amount"] = amount
               card_ref.set({
                    u'balance': card.get("balance") + amount
               }, merge=True)
          elif action == "debit":
               reader_data["amount"] = amount
               card_ref.set({
                    u'balance': card.get("balance") - amount
               }, merge=True)
     else:
          print("Card does not exist performing action according to", action)
          if action == "balance":
               print("Creating 0 balance for new card", card_id)
               reader_data["amount"] = 0
               cards.document(card_id).set({
                    u'balance': 0
               })
          elif action == "credit":
               print("Creating new balance for new card", card_id, amount)
               reader_data["amount"] = amount
               cards.document(card_id).set({
                    u'balance': amount
               })
          elif action == "debit":
               print("Debiting 0 balance for new card", card_id, amount)
               reader_data["amount"] = 0
               cards.document(card_id).set({
                    u'balance': 0
               })
               reader_data["action"] = "failed"
          else:
               print("What the action is this?", action)
     print("Final updates to reader")
     reader_ref = readers.document(reader_id)
     reader_ref.set(reader_data)
     print("Done updating")


def callback(message: pubsub_v1.subscriber.message.Message) -> None:
     print(f"Received {message}.")
     message.ack()
     data = json.loads(message.data)
     print(data)
     if "card_id" in data.keys() and "reader_id" in data.keys() and "action" in data.keys() and "amount" in data.keys():
          print("calling this")
          update_firestore(data["action"], data["amount"], data["card_id"], data["reader_id"])
     else:
          print("Not calling it")
          print("card_id" in data.keys())
          print("reader_id" in data.keys())

def main(event, context):
     """Triggered by a change to a Firestore document.
     Args:
          event (dict): Event payload.
          context (google.cloud.functions.Context): Metadata for the event.
     """
     resource_string = context.resource
     # print out the resource string that triggered the function
     print(f"Function triggered by change to: {resource_string}.")
     # now print out the entire event object
     print(str(event))

     path_parts = context.resource.split('/documents/')[1].split('/')
     collection_path = path_parts[0]
     reader_id = '/'.join(path_parts[1:])

     reader_doc = db.collection(collection_path).document(reader_id)

     action = event["value"]["fields"]["action"]["stringValue"]

     if action in ["none", "success", "failed"]:
          pass
     else:
          amount = int(event["value"]["fields"]["amount"]["integerValue"])
          # Connect to PubSub topic as subscriber
          topic_id = reader_id
          topic_path = publisher.topic_path(project_id, topic_id)

          subscription_path_web = subscriber_web.subscription_path(project_id, topic_id + "_web")

          if subscription_path_web not in [subs for subs in publisher.list_topic_subscriptions(request = {'topic': topic_path})]:
            with subscriber_web:
                subscription_web = subscriber_web.create_subscription(
                    request = {'name': subscription_path_web, 'topic': topic_path, 'enable_exactly_once_delivery': True}
                )
                print(f'Subscription {subscription_path_web} created successfully!')
          
          # Publish read action to device

          data = {
               "read": True,
               "action": action,
               "amount": amount
          }

          future = publisher.publish(topic_path, bytes(json.dumps(data), "utf-8"))
          print(future.result())

          # Listen for device messages

          streaming_pull_future = subscriber_web.subscribe(subscription_path_web, callback=callback)
          print(f"Listening for messages on {subscription_path_web}..\n")

          # Wrap subscriber in a 'with' block to automatically call close() when done.
          with subscriber_web:
               try:
                    # When `timeout` is not set, result() will block indefinitely,
                    # unless an exception is encountered first.
                    streaming_pull_future.result(timeout=timeout)
               except TimeoutError:
                    streaming_pull_future.cancel()  # Trigger the shutdown.
                    streaming_pull_future.result()  # Block until the shutdown is complete.

          # Perform action

          # Update firestore
