import re

from z2t2ha.processors.processor_base import ProcessorBase, ProcessorType
from z2t2ha.objects import Entity
from z2t2ha.utils.decorators import require_dict_argument_property

devices = {}


class DeviceDetailsExtractor(ProcessorBase):

    class Meta:
        type = ProcessorType.Support

    def __init__(self, *args, **kwargs):
        super(DeviceDetailsExtractor, self).__init__(*args, **kwargs)

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

    def process(self, *args, device_id: str, payload: dict, entity: Entity, **kwargs):
        self._extract_friendly_name(device_id, payload=payload)
        entity.__dict__.update(self.get_device(device_id))

    @require_dict_argument_property("Status.FriendlyName")
    def _extract_friendly_name(self, device_id: str, *args, payload: dict):
        device = self.get_device(device_id)
        device["device"]["name"] = payload["Status"]["FriendlyName"][0]
