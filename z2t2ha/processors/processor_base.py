from abc import ABCMeta, abstractmethod
from enum import Enum, auto


class ProcessorType(Enum):
    Preprocess = auto()
    ArgumentCreation = auto()
    Support = auto()
    EntityDiscovery = auto()
    Postprocess = auto()


class ProcessorBase(metaclass=ABCMeta):

    class Meta:
        type: ProcessorType = None

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def process(self, *args, **kwargs):
        pass
