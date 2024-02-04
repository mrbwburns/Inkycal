import json

import paho.mqtt.client as mqtt


class mqtt_client:
    def __init__(self, host:str, port:int, user:str, password:str, topic:str):
        """
        Implementation of a MQTT message broker client connection,
        including subscribing a certain topic and the necessary callbacks.
        :param
            host: the MQTT server IP
            port: the MQTT server port
            user: the MQTT server username
            password: the MQTT server password
            topic: the topic to subscribe to
        """
        self.topic = topic
        self.state = 0
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(user, password)
        self.client.connect(host=host, port=port, keepalive=60)
        self.client.loop_start()

    def __exit__(self):
        self.client.loop_stop()

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.client.subscribe(self.topic, 0)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        # Decode the payload from bytes to a string
        payload_string = str(msg.payload.decode("utf-8"))

        # Parse the JSON string into a Python dictionary
        self.state = json.loads(payload_string)

    # The get function to retrieve the desired reading
    def get_key(self, key: str):
        return_value = None
        if self.state != 0 and key in self.state:
            return_value = self.state[key]
        return return_value
