import json
import logging

from paho.mqtt.client import Client

from z2t2ha.objects import Entity
from z2t2ha.processors.processor_base import ProcessorBase, ProcessorType

logger = logging.getLogger("z2t2ha.processors.publish_valid_entities")


class PublishValidEntities(ProcessorBase):

    class Meta:
        type = ProcessorType.Postprocess

    def process(self, *args, mqtt_client: Client, entity: Entity, **kwargs):
        if not entity.meta.is_valid:
            return
        
        target_topic = "/".join(filter(None, [
            "homeassistant",
            entity.topic_meta.component,
            entity.topic_meta.node_id,
            entity.topic_meta.object_id,
            "config"
        ]))
        data = json.dumps(entity.serializable_data())

        logger.debug("publishing entity to '%s': %s", target_topic, data)
        mqtt_client.publish(
            topic=target_topic,
            payload=data,
        )
