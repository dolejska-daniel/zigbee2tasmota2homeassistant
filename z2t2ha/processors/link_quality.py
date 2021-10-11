from math import ceil
from string import Template

from z2t2ha.processors.processor_base import ProcessorBase, ProcessorType
from z2t2ha.objects import Entity
from z2t2ha.utils.decorators import require_dict_argument_property


class LinkQualitySensorExtractor(ProcessorBase):

    class Meta:
        type = ProcessorType.EntityDiscovery

    def __init__(self, *args, **kwargs):
        self.source_property_name = kwargs.pop("source_property_name", "LinkQuality")
        self.process = require_dict_argument_property(
            self.source_property_name,
            kwargs.pop("source_property_type", int),
        )(self.process)
        super().__init__(*args, **kwargs)

    def process(self, *args, device_id: str, mqtt_source_topic: str, entity: Entity, payload: dict, **kwargs):
        """ https://tasmota.github.io/docs/Home-Assistant/#zigbee-devices """
        entity.meta.is_valid = True
        entity.topic_meta.component = "sensor"
        entity.topic_meta.node_id = device_id
        entity.topic_meta.object_id = "lqi"

        entity.name = "LQI (Link Quality Index)"
        entity.icon = "mdi:signal-cellular-" + str(min(ceil(payload["LinkQuality"] / 60), 3))
        entity.value_template = Template("""
            {% if value_json.ZbReceived is defined
                    and value_json.ZbReceived["$device_id"] is defined
                    and value_json.ZbReceived["$device_id"].$property is defined %}
                {{ value_json.ZbReceived["$device_id"].$property }}
            {% else %}
                {{ states(entity_id) }}
            {% endif %}
        """).substitute(device_id=device_id, property=self.source_property_name)
        entity.state_class = "measurement"
        entity.state_topic = mqtt_source_topic
        entity.unique_id = f"sensor/{mqtt_source_topic}/{device_id}/lqi"
