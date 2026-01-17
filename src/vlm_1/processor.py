from __future__ import annotations

import base64
from pathlib import Path

import cv2
import ollama


class VideoProcessor:
    def __init__(self, model: str = "llama3.2-vision"):
        self.model = model
        self.client = ollama.Client()

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
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_b64],
                }
            ],
        )
        return response["message"]["content"]

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
            })

        return results
