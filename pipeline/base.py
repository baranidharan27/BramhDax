from abc import ABC, abstractmethod

class PipelineComponent(ABC):
    """Base class for pipeline components."""
    
    @abstractmethod
    def process(self, *args, **kwargs):
        pass
