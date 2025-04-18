def load_loop(path):
    print(f"Loading loop: {path}")
    # TODO: Load audio file and return audio data
    return None

def play_loop(audio, fx_chain=None):
    print("Playing loop")
    if fx_chain:
        from fx.effects import apply_fx
        audio = apply_fx(audio, fx_chain)
    # TODO: Implement playback logic
