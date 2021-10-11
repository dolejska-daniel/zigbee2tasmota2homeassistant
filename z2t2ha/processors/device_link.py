from z2t2ha.objects import Entity
from z2t2ha.processors.processor_base import ProcessorBase, ProcessorType

devices = {}


class DeviceLinkExtractor(ProcessorBase):

    class Meta:
        type = ProcessorType.Support

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_device(self, device_id: str) -> dict:
        if (device := devices.get(device_id, None)) is None:
            device = devices[device_id] = {
                "device": {
                    "identifiers": [
                        device_id,
                    ]
                }
            }

        return device

    def process(self, *args, device_id: str, entity: Entity, **kwargs):
        entity.__dict__.update(self.get_device(device_id))
