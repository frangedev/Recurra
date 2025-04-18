import numpy as np
from .base import AudioEffect

class Delay(AudioEffect):
    def __init__(self):
        super().__init__("delay")
        self.params = {
            "time": 0.5,  # seconds
            "feedback": 0.5,  # 0-1
            "mix": 0.5  # 0-1
        }
        
    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        if not self.enabled:
            return audio
            
        delay_samples = int(self.params["time"] * sample_rate)
        feedback = self.params["feedback"]
        mix = self.params["mix"]
        
        # Create delay buffer
        output = np.zeros_like(audio)
        delay_buffer = np.zeros(delay_samples)
        
        for i in range(len(audio)):
            # Get delayed sample
            delayed_sample = delay_buffer[0] if len(delay_buffer) > 0 else 0
            
            # Mix original and delayed signal
            output[i] = audio[i] * (1 - mix) + delayed_sample * mix
            
            # Update delay buffer
            delay_buffer = np.roll(delay_buffer, -1)
            delay_buffer[-1] = audio[i] + delayed_sample * feedback
            
        return output 