import typer

app = typer.Typer()

@app.command()
def load(path: str, loop: bool = False, fx: list[str] = None):
    """Load and play a loop with optional effects."""
    from core.player import load_loop, play_loop
    audio = load_loop(path)
    if fx:
        audio = __import__('fx.effects', fromlist=['apply_fx']).apply_fx(audio, fx)
    play_loop(audio)

@app.command()
def gen(style: str, length: int, api: str = "openai"):
    """Generate an AI-powered loop."""
    from ai.openai_api import generate_loop
    loop_data = generate_loop(style, length, api_key="")
    print("Generated loop (data length:", len(loop_data), ")")

def start():
    """Start the live coding console."""
    app()

if __name__ == "__main__":
    start()
