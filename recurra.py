#!/usr/bin/env python3

import os
import json
import argparse
import sounddevice as sd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Type
import threading
import time
import importlib.util
import sys

# Import effects
from fx.base import AudioEffect
from fx.delay import Delay
from fx.reverb import Reverb
from fx.distortion import Distortion
from fx.lowpass import LowPass
from fx.highpass import HighPass
from fx.bitcrusher import BitCrusher

class Recurra:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.loop_dir = Path(self.config.get("loop_dir", "./loops"))
        self.bpm = self.config.get("default_bpm", 120)
        self.current_loop = None
        self.is_playing = False
        self.audio_thread = None
        self.effects: List[AudioEffect] = []
        self.effect_classes = {
            "delay": Delay,
            "reverb": Reverb,
            "distortion": Distortion,
            "lowpass": LowPass,
            "highpass": HighPass,
            "bitcrusher": BitCrusher
        }
        
        # Create loop directory if it doesn't exist
        self.loop_dir.mkdir(exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        if not os.path.exists(config_path):
            return {
                "loop_dir": "./loops",
                "default_bpm": 120,
                "api_keys": {}
            }
        with open(config_path, 'r') as f:
            return json.load(f)
            
    def load_loop(self, file_path: str) -> None:
        """Load an audio file as a loop."""
        try:
            import soundfile as sf
            self.current_loop, self.sample_rate = sf.read(file_path)
            print(f"Loaded loop: {file_path}")
        except Exception as e:
            print(f"Error loading loop: {e}")
            
    def play(self) -> None:
        """Start playing the current loop."""
        if self.current_loop is None:
            print("No loop loaded. Use 'load' command first.")
            return
            
        self.is_playing = True
        self.audio_thread = threading.Thread(target=self._playback_loop)
        self.audio_thread.start()
        
    def stop(self) -> None:
        """Stop playback."""
        self.is_playing = False
        if self.audio_thread:
            self.audio_thread.join()
            
    def _playback_loop(self) -> None:
        """Internal playback loop."""
        while self.is_playing:
            audio = self.current_loop.copy()
            
            # Apply effects
            for effect in self.effects:
                if effect.enabled:
                    audio = effect.process(audio, self.sample_rate)
            
            sd.play(audio, self.sample_rate)
            sd.wait()
            
    def set_bpm(self, bpm: int) -> None:
        """Set the playback BPM."""
        self.bpm = bpm
        print(f"BPM set to {bpm}")
        
    def add_effect(self, effect_name: str) -> None:
        """Add an audio effect to the current loop."""
        if effect_name in self.effect_classes:
            effect = self.effect_classes[effect_name]()
            self.effects.append(effect)
            print(f"Added effect: {effect_name}")
        else:
            print(f"Effect {effect_name} not found")
            
    def remove_effect(self, effect_name: str) -> None:
        """Remove an effect from the current loop."""
        for i, effect in enumerate(self.effects):
            if effect.name == effect_name:
                del self.effects[i]
                print(f"Removed effect: {effect_name}")
                return
        print(f"Effect {effect_name} not found")
        
    def set_effect_param(self, effect_name: str, param: str, value: float) -> None:
        """Set a parameter for an effect."""
        for effect in self.effects:
            if effect.name == effect_name:
                try:
                    effect.set_param(param, value)
                    print(f"Set {effect_name}.{param} = {value}")
                except ValueError as e:
                    print(e)
                return
        print(f"Effect {effect_name} not found")
        
    def clear_effects(self) -> None:
        """Clear all effects."""
        self.effects = []
        print("Cleared all effects")
        
    def list_effects(self) -> None:
        """List all available effects and their parameters."""
        print("\nAvailable effects:")
        for name, effect_class in self.effect_classes.items():
            effect = effect_class()
            print(f"\n{name}:")
            for param, value in effect.params.items():
                print(f"  {param}: {value}")
                
    def list_active_effects(self) -> None:
        """List currently active effects and their parameters."""
        if not self.effects:
            print("No active effects")
            return
            
        print("\nActive effects:")
        for effect in self.effects:
            print(f"\n{effect.name}:")
            for param, value in effect.params.items():
                print(f"  {param}: {value}")

def main():
    parser = argparse.ArgumentParser(description="Recurra - Terminal-based Loop Player")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Load command
    load_parser = subparsers.add_parser("load", help="Load and play a loop")
    load_parser.add_argument("--file", required=True, help="Audio file to load")
    load_parser.add_argument("--fx", help="Add effect")
    
    # BPM command
    bpm_parser = subparsers.add_parser("bpm", help="Set BPM")
    bpm_parser.add_argument("value", type=int, help="BPM value")
    
    # Stop command
    subparsers.add_parser("stop", help="Stop playback")
    
    # Effect commands
    effect_parser = subparsers.add_parser("effect", help="Effect commands")
    effect_subparsers = effect_parser.add_subparsers(dest="effect_command")
    
    # Add effect
    add_effect_parser = effect_subparsers.add_parser("add", help="Add an effect")
    add_effect_parser.add_argument("name", help="Effect name")
    
    # Remove effect
    remove_effect_parser = effect_subparsers.add_parser("remove", help="Remove an effect")
    remove_effect_parser.add_argument("name", help="Effect name")
    
    # Set effect parameter
    set_param_parser = effect_subparsers.add_parser("set", help="Set effect parameter")
    set_param_parser.add_argument("effect", help="Effect name")
    set_param_parser.add_argument("param", help="Parameter name")
    set_param_parser.add_argument("value", type=float, help="Parameter value")
    
    # List effects
    effect_subparsers.add_parser("list", help="List available effects")
    effect_subparsers.add_parser("active", help="List active effects")
    
    # Clear effects
    effect_subparsers.add_parser("clear", help="Clear all effects")
    
    args = parser.parse_args()
    recurra = Recurra()
    
    if args.command == "load":
        recurra.load_loop(args.file)
        if args.fx:
            recurra.add_effect(args.fx)
        recurra.play()
    elif args.command == "bpm":
        recurra.set_bpm(args.value)
    elif args.command == "stop":
        recurra.stop()
    elif args.command == "effect":
        if args.effect_command == "add":
            recurra.add_effect(args.name)
        elif args.effect_command == "remove":
            recurra.remove_effect(args.name)
        elif args.effect_command == "set":
            recurra.set_effect_param(args.effect, args.param, args.value)
        elif args.effect_command == "list":
            recurra.list_effects()
        elif args.effect_command == "active":
            recurra.list_active_effects()
        elif args.effect_command == "clear":
            recurra.clear_effects()
    else:
        parser.print_help()
        
if __name__ == "__main__":
    main()
