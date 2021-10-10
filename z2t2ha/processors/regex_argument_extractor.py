import re

from z2t2ha.processors.processor_base import ProcessorBase, ProcessorType


class RegexArgumentExtractor(ProcessorBase):

    class Meta:
        type = ProcessorType.ArgumentCreation

    def __init__(self, argument_name, expression, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.argument_name = argument_name
        self.expression = re.compile(expression)

    def process(self, *args, **kwargs):
        argument_value = kwargs.get(self.argument_name, "")
        match = self.expression.match(argument_value)
        return match.groupdict()
