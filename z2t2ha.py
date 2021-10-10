import logging.config

import yaml

from z2t2ha.core import ProcessorController
from z2t2ha.mqtt.connection import Connection

with open("config/logging.yaml", "r") as fd:
    logging.config.dictConfig(yaml.safe_load(fd))

mqtt_connection = Connection()

with open("config/app.yaml", "r") as fd:
    app_config = yaml.safe_load(fd)

pc = ProcessorController(processor_topic_mapping=app_config["processors"])
pc.create_and_bind_message_handlers(mqtt_connection)

mqtt_connection.open_and_listen()
