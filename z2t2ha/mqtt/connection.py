import logging
from typing import Callable, Any
from uuid import uuid4

from paho.mqtt.client import Client, MQTTMessage, ReasonCodes

logger = logging.getLogger("z2t2mqtt.mqtt.connection")

OnMessageHandler = Callable[[Client, dict, MQTTMessage], Any]


class Connection:

    def __init__(self, userdata: dict = None):
        self._client = Client(
            client_id="z2t2ha-" + uuid4().hex,
            userdata=userdata or {},
        )
        self._setup_internal_callbacks()

    @staticmethod
    def _on_connect(client: Client, userdata: dict, flags, code: ReasonCodes):
        logger.debug("current connection status: %s", code)
        client.subscribe("tele/#")
        client.subscribe("stat/#")
        client.subscribe("cmnd/#")

    @staticmethod
    def _on_message(client: Client, userdata: dict, message: MQTTMessage):
        logger.info("detected message without any processors in %s", message.topic)
        logger.debug("message contents: %s", message.payload)

    def _setup_internal_callbacks(self):
        logger.debug("setting up MQTT client callbacks")
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

    def set_topic_handler(self, topic_name_pattern: str, handler: OnMessageHandler):
        logger.debug("setting handler of %s to %s", topic_name_pattern, handler)
        self._client.message_callback_add(topic_name_pattern, handler)

    def open_and_listen(self):
        connection_config = {
            "host": "127.0.0.1",
            "port": 1883,
        }
        logger.debug("establishing connection to MQTT broker: %s", connection_config)
        self._client.connect(**connection_config)

        logger.info("starting infinite MQTT client connection loop")
        self._client.loop_forever()

