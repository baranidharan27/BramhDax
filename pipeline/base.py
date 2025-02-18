from abc import ABC, abstractmethod
import logging

class PipelineComponent(ABC):
    """Base class for pipeline components with logging and configuration."""

    def __init__(self, name, config=None):
        self.name = name  # Component name
        self.config = config if config else {}  # Optional configuration dictionary
        self.logger = logging.getLogger(name)  # Logger for this component

        # Initialize common settings or configurations
        self._setup_configuration()

    def _setup_configuration(self):
        """Set up configuration or default values."""
        self.logger.setLevel(logging.INFO)
        self.logger.info(f"Initialized {self.name} component with config: {self.config}")

    @abstractmethod
    def process(self, *args, **kwargs):
        """Each component must implement this method to process data."""
        pass

    def log(self, message):
        """Common logging functionality."""
        self.logger.info(message)

    def validate(self, *args, **kwargs):
        """A common validation method to be used by all subclasses."""
        if not args or not kwargs:
            self.logger.warning(f"{self.name} received no arguments or invalid arguments.")
            return False
        return True
