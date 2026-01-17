from __future__ import annotations

import json

import click
import ollama
import psutil

from vlm_1.processor import VideoProcessor


MODEL_MEMORY_GB = {
    "llama3.2-vision": 7.0,
    "llama3.2-vision:11b": 7.0,
    "llama3.2-vision:90b": 55.0,
}
DEFAULT_MODEL_MEMORY_GB = 8.0


def check_memory(model: str) -> None:
    """Check available memory and warn if insufficient for the model."""
    mem = psutil.virtual_memory()
    available_gb = mem.available / (1024**3)
    total_gb = mem.total / (1024**3)

    # Try to get model size from Ollama
    required_gb = MODEL_MEMORY_GB.get(model, DEFAULT_MODEL_MEMORY_GB)
    try:
        model_info = ollama.show(model)
        if "size" in model_info:
            required_gb = model_info["size"] / (1024**3)
    except Exception:
        pass

    click.echo(f"Memory: {available_gb:.1f} GB available / {total_gb:.1f} GB total")
    click.echo(f"Model {model} requires ~{required_gb:.1f} GB")

    if available_gb < required_gb:
        click.secho(
            f"Warning: Low memory! Available ({available_gb:.1f} GB) < required ({required_gb:.1f} GB)",
            fg="yellow",
        )
        click.secho("Performance may be degraded or processing may fail.\n", fg="yellow")
    else:
        click.secho("Memory check: OK\n", fg="green")


@click.command()
@click.argument("video_path", type=click.Path(exists=True))
@click.option(
    "--prompt",
    "-p",
    default="Describe what you see in this frame.",
    help="Prompt to use for each frame analysis.",
)
@click.option(
    "--interval",
    "-i",
    default=1.0,
    type=float,
    help="Interval between frames in seconds.",
)
@click.option(
    "--model",
    "-m",
    default="llama3.2-vision",
    help="Ollama model to use.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output JSON file path.",
)
def main(video_path: str, prompt: str, interval: float, model: str, output: str | None):
    """Process a video using VLM (llama3.2-vision via Ollama)."""
    click.echo(f"Processing video: {video_path}")
    click.echo(f"Using model: {model}")
    click.echo(f"Frame interval: {interval}s\n")

    check_memory(model)

    processor = VideoProcessor(model=model)

    click.echo("Extracting frames...")
    frames = processor.extract_frames(video_path, interval)
    click.echo(f"Found {len(frames)} frames to analyze\n")

    results = []
    with click.progressbar(frames, label="Analyzing frames", show_pos=True) as bar:
        for timestamp, image_bytes in bar:
            analysis = processor.analyze_frame(image_bytes, prompt)
            results.append({"timestamp": timestamp, "analysis": analysis})

    if output:
        with open(output, "w") as f:
            json.dump(results, f, indent=2)
        click.echo(f"Results saved to: {output}")
    else:
        for result in results:
            click.echo(f"\n[{result['timestamp']:.2f}s]")
            click.echo(result["analysis"])


if __name__ == "__main__":
    main()
