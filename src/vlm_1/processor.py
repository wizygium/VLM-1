from __future__ import annotations

import base64
from pathlib import Path
from PIL import Image
import io
import json
import re

import cv2
import mlx_vlm
from mlx_vlm.utils import load, generate

# Monkeypatch Qwen2Tokenizer if needed for mlx_vlm slow tokenizer support
try:
    from transformers import Qwen2Tokenizer
    if not hasattr(Qwen2Tokenizer, "vocab"):
        @property
        def vocab(self):
            return self.get_vocab()
        Qwen2Tokenizer.vocab = vocab
except ImportError:
    pass


class VideoProcessor:
    def __init__(self, model_path: str = "mlx-community/Qwen2.5-VL-7B-Instruct-4bit"):
        self.model_path = model_path
        print(f"Loading model from {model_path}...")
        self.model, self.processor = load(model_path, use_fast=False)
        print("Model loaded successfully.")

    def extract_frames(
        self, video_path: str | Path, interval_seconds: float = 1.0
    ) -> list[tuple[float, bytes]]:
        """Extract frames from video at specified interval.

        Returns list of (timestamp, jpeg_bytes) tuples.
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * interval_seconds)
        frames = []
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                timestamp = frame_count / fps
                _, buffer = cv2.imencode(".jpg", frame)
                frames.append((timestamp, buffer.tobytes()))

            frame_count += 1

        cap.release()
        return frames

    def analyze_frame(self, image_bytes: bytes, prompt: str) -> str:
        """Analyze a single frame using the VLM."""
        return self.analyze_batch([image_bytes], prompt)

    def analyze_batch(self, images_bytes: list[bytes], prompt: str) -> str:
        """Analyze a sequence of frames.
        
        Note: This function now expects a SINGLE grid image containing all frames,
        not multiple individual frames. The cumulative history approach caused
        Metal buffer crashes and index errors with MLX.
        """
        print(f"DEBUG: Analyze batch called with {len(images_bytes)} images.")
        
        # Convert to PIL image(s)
        images = [Image.open(io.BytesIO(b)) for b in images_bytes]
        
        # Create a simple user message with the image(s) and prompt
        messages = [{
            "role": "user",
            "content": [
                *[{"type": "image"} for _ in images],
                {"type": "text", "text": prompt}
            ]
        }]
        
        # Apply chat template
        formatted_prompt = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        
        # Generate response
        response = generate(
            self.model,
            self.processor,
            prompt=formatted_prompt,
            image=images,
            max_tokens=3000,
            verbose=True
        )
        
        print(f"DEBUG: Response length: {len(response)} chars")
        return response

    def process_video(
        self,
        video_path: str | Path,
        prompt: str = "Describe what you see in this frame.",
        interval_seconds: float = 1.0,
        progress_callback: callable = None,
    ) -> list[dict]:
        """Process video and analyze frames at specified interval.

        Args:
            progress_callback: Optional callback(current, total, timestamp) called after each frame.

        Returns list of dicts with timestamp and analysis.
        """
        frames = self.extract_frames(video_path, interval_seconds)
        results = []
        total = len(frames)

        for i, (timestamp, image_bytes) in enumerate(frames):
            if progress_callback:
                progress_callback(i, total, timestamp)
            analysis = self.analyze_frame(image_bytes, prompt)
            results.append({
                "timestamp": timestamp,
                "analysis": analysis,
                "id": i
            })

        return results
