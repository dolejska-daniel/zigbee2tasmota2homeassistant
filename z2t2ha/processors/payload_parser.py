import json

from z2t2ha.processors.processor_base import ProcessorBase, ProcessorType
from z2t2ha.utils.decorators import require_argument


class PayloadParser(ProcessorBase):

    class Meta:
        type = ProcessorType.Preprocess

    def __init__(self, *args, parse_json=True, decode_encoding="utf-8", decode_errors="strict", **kwargs):
        super().__init__(*args, **kwargs)
        self.parse_json = parse_json
        self.decode_args = {
            "encoding": decode_encoding,
            "errors": decode_errors,
        }

    @require_argument("payload", bytes)
    def process(self, *args, payload: bytes, **kwargs):
        payload = payload.decode(**self.decode_args)
        if self.parse_json and payload.startswith("{") and payload.endswith("}"):
            payload = json.loads(payload)

        return {"payload": payload}
