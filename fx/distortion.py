import numpy as np
from .base import AudioEffect

class Distortion(AudioEffect):
    def __init__(self):
        super().__init__("distortion")
        self.params = {
            "drive": 0.5,    # 0-1
            "tone": 0.5,     # 0-1
            "mix": 0.5,      # 0-1
            "level": 0.5     # 0-1
        }
        
    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        if not self.enabled:
            return audio
            
        drive = self.params["drive"] * 10  # Scale drive for more effect
        tone = self.params["tone"]
        mix = self.params["mix"]
        level = self.params["level"]
        
        # Apply drive (soft clipping)
        distorted = np.tanh(audio * drive)
        
        # Apply tone control (simple low-pass filter)
        if tone < 0.5:
            # Low-pass filter
            alpha = tone * 2
            filtered = np.zeros_like(distorted)
            filtered[0] = distorted[0]
            for i in range(1, len(distorted)):
                filtered[i] = alpha * distorted[i] + (1 - alpha) * filtered[i-1]
        else:
            # High-pass filter
            alpha = (tone - 0.5) * 2
            filtered = np.zeros_like(distorted)
            filtered[0] = distorted[0]
            for i in range(1, len(distorted)):
                filtered[i] = alpha * distorted[i] + (1 - alpha) * filtered[i-1]
        
        # Mix original and distorted signal
        output = audio * (1 - mix) + filtered * mix
        
        # Apply level control
        return output * level 