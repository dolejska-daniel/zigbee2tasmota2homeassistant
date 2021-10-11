from z2t2ha.objects import Entity
from z2t2ha.processors.processor_base import ProcessorBase, ProcessorType
from z2t2ha.utils.decorators import require_dict_argument_property


class ZigbeeReceivedParser(ProcessorBase):

    class Meta:
        type = ProcessorType.Support

    @require_dict_argument_property("ZbReceived", dict)
    def process(self, *args, payload: dict, entity: Entity, **kwargs):
        received: dict = payload["ZbReceived"]
        return [{
            "device_id": device_id,
            "payload": data,
        } for device_id, data in received.items()]
