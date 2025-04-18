import numpy as np
from .base import AudioEffect

class Reverb(AudioEffect):
    def __init__(self):
        super().__init__("reverb")
        self.params = {
            "room_size": 0.5,  # 0-1
            "damping": 0.5,    # 0-1
            "wet_level": 0.5,  # 0-1
            "dry_level": 0.5   # 0-1
        }
        
    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        if not self.enabled:
            return audio
            
        room_size = self.params["room_size"]
        damping = self.params["damping"]
        wet_level = self.params["wet_level"]
        dry_level = self.params["dry_level"]
        
        # Create reverb buffer
        buffer_size = int(0.1 * sample_rate)  # 100ms buffer
        buffer = np.zeros(buffer_size)
        output = np.zeros_like(audio)
        
        for i in range(len(audio)):
            # Get reverb sample
            reverb_sample = np.mean(buffer) * (1 - damping)
            
            # Mix original and reverb signal
            output[i] = (audio[i] * dry_level + reverb_sample * wet_level)
            
            # Update reverb buffer
            buffer = np.roll(buffer, -1)
            buffer[-1] = audio[i] + reverb_sample * room_size
            
        return output 