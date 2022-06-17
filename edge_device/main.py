import re
from google.cloud import pubsub_v1
import json
import time
import signal
import ndef
import RPi.GPIO as GPIO
from mfrc522 import MFRC522
from alive_progress import alive_bar

# Create instance of MIFARE rfid reader
MIFAREReader = MFRC522(debugLevel='INFO')

# Create instances of gcp pubsub publishers and subcribers
publisher = pubsub_v1.PublisherClient.from_service_account_json(".key/service-account-key.json")
subscriber = pubsub_v1.SubscriberClient.from_service_account_json(".key/service-account-key.json")

# Declare globals
READER_ID = "kolpay_pos1"
project_id = "niyoproject-306620"
device_reg_topic_id = "device-registration"

def register_device():
    # The `topic_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/topics/{topic_id}`
    device_reg_topic_path = publisher.topic_path(project_id, device_reg_topic_id)

    # Sending the reader_id payload to 'device-registration' topic triggers a cloud function 
    # and creates all the required pubsub topic, subscriptions and firestore entries
    device_reg_payload = {
        "reader_id": READER_ID
    }
    print(f'Registering pos device with id: {device_reg_payload["reader_id"]} with cloud...')

    # When you publish a message, the client returns a future.
    future = publisher.publish(device_reg_topic_path, bytes(json.dumps(device_reg_payload), "utf-8"))

    print(f'Device registration successful with message: {future.result()}')

    # Waiting for 30 seconds to allow all the necessary cloud functions to complete
    print('Please wait! setting up.')
    with alive_bar() as bar:
        for i in range(30):
            time.sleep(1)
            bar()

def listen_for_read_event():
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{topic_id}`
    subscription_path = subscriber.subscription_path(project_id, READER_ID)
    print(f"Listening for messages on {subscription_path}..\n")

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=read_card_and_push_to_pubsub)

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # Blocks program execution indefinitely unless an Exception occurs
            streaming_pull_future.result()
        except Exception:
            # Shutdown the streaming pull
            streaming_pull_future.cancel()

def read_card_and_push_to_pubsub(message):
    try:
        data = json.loads(message.data) # Read json data from subscription
        message.ack() # Acknowledge and remove the message from pubsub queue
        if data['read']:
            print(f'Recieved data {data} from server!')
            # Initialize rfid reader and scan for card, when card reading is complete, return card uuid
            uuid = read_rfid()
            device_topic_path = publisher.topic_path(project_id, READER_ID)
            # Send payload to pubsub
            payload = {
                'reader_id': READER_ID,
                'card_id': uuid,
                'action': data['action'],
                'amount': data['amount']
            }
            future = publisher.publish(device_topic_path, bytes(json.dumps(payload), "utf-8"))
            print(f'Card details published successfully for action: {data["action"]} with message: {future.result()}')
    except Exception as e:
        pass
        # print(f'Error occurred while decoding message data')

def read_rfid():
    read_complete_flag = False
    print('Scanning for cards, please wait...')
    while not read_complete_flag:
    
        # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            print("Card detected")
        
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:

            # Print UID
            print("Card read with UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
        
            # This is the default key for authentication
            FACTORY_KEY = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
            KEY_MIFARE_AD = [0xA0,0xA1,0xA2,0xA3,0xA4,0xA5]
            KEY_NDEF = [0xD3,0xF7,0xD3,0xF7,0xD3,0xF7]
            
            # Select the scanned tag
            MIFAREReader.MFRC522_SelectTag(uid)
            buf = []
            # Loop from sector 1 to sector 15
            for i in range(4, 64):
                # Read only the 3 data blocks of each sector and append to buf, thus ignoring the sector trailer blocks
                if i not in [3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63]:
                    status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, i, KEY_NDEF, uid)

                    # Check if authenticated
                    if status == MIFAREReader.MI_OK:
                        buf.extend(MIFAREReader.MFRC522_Read(i))
                    else:
                        print("Authentication error")
            
            # Stop authentication
            MIFAREReader.MFRC522_StopCrypto1()
            # print(bytearray(buf[2:]))

            # NDEF tag is stored as TLV, 0x03 (Tag) denotes NDEF data, next byte denotes length of the data and is followed by n bytes of data mentioned length field
            # ndeflib can decode ndef fields from only the TLV data field, thus slicing first 2 bytes 
            uuid = list(ndef.message_decoder(bytearray(buf[2:])))[0]._text
            
            # Cleanly exit all ports
            GPIO.cleanup()
            read_complete_flag = True

        if read_complete_flag:
            return uuid

if __name__ == '__main__':
    # Register the reader with cloud
    register_device()

    # Listen to the created subscription for read request
    listen_for_read_event()
