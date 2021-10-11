from z2t2ha.objects import Entity
from z2t2ha.processors.processor_base import ProcessorBase, ProcessorType
from z2t2ha.utils.decorators import require_dict_argument_property


class DeviceDetailsExtractor(ProcessorBase):

    devices = {}

    class Meta:
        type = ProcessorType.Support

    @classmethod
    def get_device(cls, device_id: str) -> dict:
        if (device := cls.devices.get(device_id, None)) is None:
            device = cls.devices[device_id] = {
                "device": {
                    "identifiers": [
                        device_id,
                    ]
                }
            }

        return device

    def process(self, *args, device_id: str, payload: dict, entity: Entity, **kwargs):
        self._extract_device_name(device_id, payload=payload)
        self._extract_friendly_name(device_id, payload=payload)
        entity.__dict__.update(self.get_device(device_id))

    @require_dict_argument_property("Status.DeviceName", str)
    def _extract_device_name(self, device_id: str, *args, payload: dict):
        device = self.get_device(device_id)
        device["device"]["model"] = payload["Status"]["DeviceName"]

    @require_dict_argument_property("Status.FriendlyName", list)
    def _extract_friendly_name(self, device_id: str, *args, payload: dict):
        device = self.get_device(device_id)
        device["device"]["name"] = payload["Status"]["FriendlyName"][0]
