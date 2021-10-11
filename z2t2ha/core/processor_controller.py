from __future__ import annotations

import logging
from collections import defaultdict
from pydoc import locate
from typing import Type

from z2t2ha.core.types import ProcessorsByType
from z2t2ha.mqtt import Connection
from z2t2ha.processors.processor_base import ProcessorBase

logger = logging.getLogger("z2t2ha.processor_controller")


class ProcessorController:

    def __init__(self, processor_topic_mapping: dict[str, list[dict]]):
        self._mapping_configuration = processor_topic_mapping
        self.topic_patterns_with_processors: dict[str, ProcessorsByType] = defaultdict(lambda: defaultdict(list))

        self.setup_configured_processors()

    def create_and_bind_message_handlers(self, connection: Connection):
        from z2t2ha.core import ProcessorPipeline
        for topic_pattern, processor_list in self.topic_patterns_with_processors.items():
            pipeline = ProcessorPipeline(processor_list)
            connection.set_topic_handler(topic_pattern, pipeline.process_mqtt_message)

    def setup_configured_processors(self):
        logger.debug("setting up configured topic processors")
        for topic_pattern, processor_configurations in self._mapping_configuration.items():
            logger.debug("parsing %d processor configurations for topic %s",
                         len(processor_configurations), topic_pattern)

            for processor_configuration in processor_configurations:
                cls_name = processor_configuration.pop("cls", None)
                if (cls := self._return_only_valid_processor_class(cls_name)) is None:
                    continue

                processor = self._initialize_processor_class(cls, processor_configuration)
                self.topic_patterns_with_processors[topic_pattern][processor.Meta.type].append(processor)

    def _return_only_valid_processor_class(self, cls_name: str) -> Type[ProcessorBase] | None:
        if (cls := locate(cls_name)) is None or not isinstance(cls, type):
            logger.error("configured processor class '%s' could not be located", cls_name)
            return None

        if not issubclass(cls, ProcessorBase):
            logger.error("configured processor class %s is not valid subclass of ProcessorBase", cls)
            return None

        return cls

    def _initialize_processor_class(self, cls: Type[ProcessorBase], config_details: dict) -> ProcessorBase:
        args, kwargs = config_details.get("args", []), config_details.get("kwargs", {})
        logger.debug("initializing processor class %s, args=%s, kwargs=%s", cls, args, kwargs)
        return cls(*args, **kwargs)
