from abc import ABC, abstractmethod


class GenerationStrategy(ABC):
    """Abstract base class for generation strategies."""

    @abstractmethod
    def generate(self) -> str:
        """Generates the circuit code."""
        pass
