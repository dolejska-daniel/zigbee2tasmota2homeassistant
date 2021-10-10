from z2t2ha.processors.processor_base import ProcessorBase, ProcessorType
from z2t2ha.objects import Entity
from z2t2ha.utils.decorators import require_dict_argument_property


class ConnectionSignalQualitySensorExtractor(ProcessorBase):

    class Meta:
        type = ProcessorType.EntityDiscovery

    def __init__(self, *args, **kwargs):
        self.process = require_dict_argument_property(
            kwargs.pop("source_property_name", "Wifi.RSSI"),
            kwargs.pop("source_property_type", int),
        )(self.process)
        super().__init__(*args, **kwargs)

    def process(self, *args, device_id: str, mqtt_source_topic: str, payload, entity: Entity, **kwargs):
        from math import ceil
        entity.meta.is_valid = True
        entity.topic_meta.component = "sensor"
        entity.topic_meta.node_id = device_id
        entity.topic_meta.object_id = "wifi_rssi"

        entity.name = "WiFi Signal Quality"
        entity.icon = "mdi:wifi-strength-" + str(min(ceil(payload["Wifi"]["RSSI"] / 15), 4))
        entity.value_template = "{{ value_json.Wifi.RSSI }}"
        entity.unit_of_measurement = "%"
        entity.state_class = "measurement"
        entity.state_topic = mqtt_source_topic
        entity.unique_id = f"sensor/{mqtt_source_topic}/wifi/rssi"
