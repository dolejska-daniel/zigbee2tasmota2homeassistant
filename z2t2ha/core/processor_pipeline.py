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

    def _get_current_kwargs(self, update_with: dict = None, create_copy: bool = False):
        kwargs = self.kwargs
        kwargs.update(update_with)

        if create_copy:
            kwargs = self.kwargs.copy()
            for key in self.kwargs_to_deepcopy:
                kwargs[key] = deepcopy(kwargs.get(key, None))

            return kwargs

        return kwargs

    def process_mqtt_message(self, client: Client, userdata: dict, message: MQTTMessage, *args):
        self._initialize_current_kwargs(client, message)
        kwargs_list: list[dict] = [dict()]

        logger.debug("trying to run configured processors for message from %s", message.topic)
        for processor_type in list(ProcessorType):
            results = self._run_processors_of_type_and_create_result_generator(
                processor_type,
                isolate_results=processor_type in self.processor_types_to_isolate,
                kwargs_list=kwargs_list,
            )
            kwargs_list.extend(list(results))

    def _run_processors_of_type_and_create_result_generator(self,
                                                            processor_type: ProcessorType,
                                                            kwargs_list: list[dict],
                                                            isolate_results: bool = False, ):
        if not (processors := self.processors_by_type.get(processor_type, [])):
            return

        logger.debug("starting processor pipeline for %s processors", processor_type.name)
        for kwargs_initial in kwargs_list:
            logger.debug("running %d %s processor(s)", len(processors), processor_type.name)
            for processor in processors:
                kwargs = self._get_current_kwargs(update_with=kwargs_initial, create_copy=isolate_results)
                self._run_processor_of_type(processor, kwargs, kwargs_list)
                if isolate_results:
                    yield kwargs

    def _run_processor_of_type(self, processor: ProcessorBase, kwargs: dict, kwargs_list: list[dict]):
        logger.debug("now running processor %s", processor)
        try:
            state_modification_data = processor.process(**kwargs)

        except Exception:
            logger.exception("an exception occurred while running message processor")
            return

        if isinstance(state_modification_data, dict):
            logger.debug("updating current kwargs state: %s", state_modification_data)
            kwargs.update(state_modification_data)

        elif isinstance(state_modification_data, list):
            logger.debug("updating current kwargs list state: %s", state_modification_data)
            kwargs.update(state_modification_data.pop())
            kwargs_list.extend(state_modification_data)

