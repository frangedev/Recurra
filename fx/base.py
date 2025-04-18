from abc import ABC, abstractmethod
import numpy as np

class AudioEffect(ABC):
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.params = {}
        
    @abstractmethod
    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process the audio data and return modified audio."""
        pass
        
    def set_param(self, param_name: str, value: float) -> None:
        """Set a parameter value for the effect."""
        if param_name in self.params:
            self.params[param_name] = value
        else:
            raise ValueError(f"Parameter {param_name} not found in effect {self.name}")
            
    def get_param(self, param_name: str) -> float:
        """Get a parameter value from the effect."""
        if param_name in self.params:
            return self.params[param_name]
        raise ValueError(f"Parameter {param_name} not found in effect {self.name}")
        
    def enable(self) -> None:
        """Enable the effect."""
        self.enabled = True
        
    def disable(self) -> None:
        """Disable the effect."""
        self.enabled = False 