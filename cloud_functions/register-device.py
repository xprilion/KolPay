import base64
from operator import sub
from google.cloud import firestore
from google.cloud import pubsub_v1
import json

# Declare the project ID
project_id = "niyoproject-306620"

# Connect to Firestore DB (Native Mode)
db = firestore.Client(project=project_id)
# Set active collection to user
readers = db.collection(u'readers')

# Initiate Publisher and Subscriber for PubSub
publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()
subscriber_web = pubsub_v1.SubscriberClient()

def register_device(reader_id):
    # First, create an entry on Firestore
    data = {
        u'action': u'none',
        u'amount': 0
    }
    readers.document(reader_id).set(data)

    # Then, create a topic in PubSub with the reader_id
    topic_id = reader_id
    topic_path = publisher.topic_path(project_id, topic_id)
    if topic_path not in [topic.name for topic in publisher.list_topics(request = {'project': f'projects/{project_id}'})]:
        topic = publisher.create_topic(request={"name": topic_path})
        print(f'Topic {topic_path} created successfully!')
        subscription_path = subscriber.subscription_path(project_id, topic_id)
        subscription_path_web = subscriber_web.subscription_path(project_id, topic_id + "_web")
        if subscription_path not in [subs for subs in publisher.list_topic_subscriptions(request = {'topic': topic_path})]:
            with subscriber:
                subscription = subscriber.create_subscription(
                    request = {'name': subscription_path, 'topic': topic_path, 'enable_exactly_once_delivery': True}
                )
                print(f'Subscription {subscription_path} created successfully!')
            with subscriber_web:
                subscription_web = subscriber_web.create_subscription(
                    request = {'name': subscription_path_web, 'topic': topic_path, 'enable_exactly_once_delivery': True}
                )
                print(f'Subscription {subscription_path_web} created successfully!')
        else:
            print(f'Subscription {subscription_path} or {subscription_path_web} already exists, skipping!')
    else:
        print(f'Topic {topic_path} already exists, skipping!')
        



def main(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    data = json.loads(pubsub_message)

    print("Reader ID:" + str(data["reader_id"]))

    register_device(data["reader_id"])
