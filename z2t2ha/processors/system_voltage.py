from z2t2ha.processors.processor_base import ProcessorBase, ProcessorType
from z2t2ha.objects import Entity
from z2t2ha.utils.decorators import require_dict_argument_property


class SystemVoltageSensorExtractor(ProcessorBase):

    class Meta:
        type = ProcessorType.EntityDiscovery

    def __init__(self, *args, **kwargs):
        self.process = require_dict_argument_property(
            kwargs.pop("source_property_name", "Vcc"),
            kwargs.pop("source_property_type", float),
        )(self.process)
        super().__init__(*args, **kwargs)

    def process(self, *args, device_id: str, mqtt_source_topic: str, entity: Entity, **kwargs):
        entity.meta.is_valid = True
        entity.topic_meta.component = "sensor"
        entity.topic_meta.node_id = device_id
        entity.topic_meta.object_id = "vcc"

        entity.name = "System Voltage"
        entity.value_template = "{{ value_json.Vcc }}"
        entity.unit_of_measurement = "V"
        entity.device_class = "voltage"
        entity.state_class = "measurement"
        entity.state_topic = mqtt_source_topic
        entity.unique_id = f"sensor/{mqtt_source_topic}/vcc"
