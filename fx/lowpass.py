import numpy as np
from .base import AudioEffect

class LowPass(AudioEffect):
    def __init__(self):
        super().__init__("lowpass")
        self.params = {
            "cutoff": 0.5,    # 0-1 (normalized frequency)
            "resonance": 0.1, # 0-1
            "mix": 0.5        # 0-1
        }
        
    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        if not self.enabled:
            return audio
            
        cutoff = self.params["cutoff"]
        resonance = self.params["resonance"]
        mix = self.params["mix"]
        
        # Convert normalized cutoff to actual frequency
        freq = cutoff * sample_rate / 2
        
        # Calculate filter coefficients
        c = 1.0 / np.tan(np.pi * freq / sample_rate)
        resonance = resonance * 2  # Scale resonance for more effect
        r = 1.0 / (1.0 + resonance * c + c * c)
        
        # Initialize filter state
        output = np.zeros_like(audio)
        x1 = 0.0
        x2 = 0.0
        y1 = 0.0
        y2 = 0.0
        
        # Apply filter
        for i in range(len(audio)):
            x0 = audio[i]
            y0 = (x0 + x0 - 2.0 * x2) * r + (2.0 * y1 - y2) * (1.0 - r)
            
            # Update state
            x2 = x1
            x1 = x0
            y2 = y1
            y1 = y0
            
            # Mix original and filtered signal
            output[i] = audio[i] * (1 - mix) + y0 * mix
            
        return output 