import logging
from copy import deepcopy

from paho.mqtt.client import Client, MQTTMessage

from z2t2ha.core.types import ProcessorsByType
from z2t2ha.objects import Entity
from z2t2ha.processors.processor_base import ProcessorType, ProcessorBase

logger = logging.getLogger("z2t2ha.processor_controller")


class ProcessorPipeline:

    def __init__(self,
                 processors_by_type: ProcessorsByType,
                 initial_kwargs: dict = None,
                 kwargs_to_deepcopy: list = None,
                 processor_types_to_isolate: set[ProcessorType] = None):
        self.processors_by_type = processors_by_type
        self.kwargs = initial_kwargs or {}
        self.kwargs_to_deepcopy = ["entity", "payload"] + (kwargs_to_deepcopy or [])
        self.processor_types_to_isolate = processor_types_to_isolate or {ProcessorType.EntityDiscovery}

    def _initialize_current_kwargs(self, client: Client, message: MQTTMessage):
        self.kwargs.update({
            "mqtt_client": client,
            "mqtt_source_topic": str(message.topic),
            "payload": message.payload,
            "entity": Entity(),
        })

    def _get_current_kwargs(self, create_copy: bool = False):
        kwargs = self.kwargs
        if create_copy:
            for key in self.kwargs_to_deepcopy:
                kwargs[key] = deepcopy(kwargs.get(key, None))

        return kwargs

    def process_mqtt_message(self, client: Client, userdata: dict, message: MQTTMessage, *args):
        self._initialize_current_kwargs(client, message)
        kwargs_list_override: list[dict] = []

        logger.debug("trying to run configured processors for message from %s", message.topic)
        for processor_type in list(ProcessorType):
            results = self._run_processors_of_type_and_create_result_generator(
                processor_type,
                isolate_results=processor_type in self.processor_types_to_isolate,
                kwargs_list_override=kwargs_list_override,
            )
            kwargs_list_override = list(results)

    def _run_processors_of_type_and_create_result_generator(self,
                                                            processor_type: ProcessorType,
                                                            isolate_results: bool = False,
                                                            kwargs_list_override: list[dict] = None):
        if not (processors := self.processors_by_type.get(processor_type, [])):
            return

        logger.debug("running %d processor(s) with type %s", len(processors), processor_type.name)
        for kwargs in kwargs_list_override or [None]:
            for processor in processors:
                kwargs = kwargs or self._get_current_kwargs(create_copy=isolate_results)
                self._run_processor_of_type(processor, kwargs)
                if isolate_results:
                    yield kwargs

    def _run_processor_of_type(self, processor: ProcessorBase, kwargs: dict):
        logger.debug("now running processor %s", processor)
        try:
            state_modification_data = processor.process(**kwargs)

        except Exception:
            logger.exception("an exception occurred while running message processor")
            return

        kwargs.update(state_modification_data if isinstance(state_modification_data, dict) else {})
