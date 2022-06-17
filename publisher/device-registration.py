from google.cloud import pubsub_v1
import json


publisher = pubsub_v1.PublisherClient.from_service_account_json(".key/service-account-key.json")

project_id = "niyoproject-306620"
topic_id = "device-registration"

# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
topic_path = publisher.topic_path(project_id, topic_id)

data = {
    "reader_id": "anu2"
}

# When you publish a message, the client returns a future.
future = publisher.publish(topic_path, bytes(json.dumps(data), "utf-8"))

print(future.result())
