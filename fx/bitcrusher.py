import numpy as np
from .base import AudioEffect

class BitCrusher(AudioEffect):
    def __init__(self):
        super().__init__("bitcrusher")
        self.params = {
            "bits": 0.5,      # 0-1 (normalized to 1-16 bits)
            "rate": 0.5,      # 0-1 (normalized sample rate reduction)
            "mix": 0.5        # 0-1
        }
        
    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        if not self.enabled:
            return audio
            
        bits = int(self.params["bits"] * 15 + 1)  # Convert to 1-16 bits
        rate = int(self.params["rate"] * 15 + 1)  # Convert to 1-16x reduction
        mix = self.params["mix"]
        
        # Calculate bit depth reduction
        max_val = 2 ** (bits - 1)
        scale = max_val / np.max(np.abs(audio))
        
        # Apply bit reduction
        crushed = np.round(audio * scale) / scale
        
        # Apply sample rate reduction
        if rate > 1:
            # Create a new array with reduced sample rate
            new_length = len(audio) // rate
            indices = np.arange(0, len(audio), rate, dtype=int)
            indices = indices[:new_length]
            crushed = crushed[indices]
            
            # Resample back to original length
            crushed = np.interp(
                np.arange(len(audio)),
                np.linspace(0, len(audio), len(crushed)),
                crushed
            )
        
        # Mix original and crushed signal
        return audio * (1 - mix) + crushed * mix 