from typing import Protocol, Optional, Any, Dict
from pathlib import Path
from schemas import JudgeOutput, VideoAnalysisResult

class LLMProviderProtocol(Protocol):
    """
    Interface for LLM interactions.
    """
    def generate_judgment(self, prompt: str, system_prompt: Optional[str] = None, image_paths: Optional[list[str]] = None) -> JudgeOutput:
        """
        Send a prompt to the LLM and expect a structured JudgeOutput.
        """
        ...
        
    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.
        """
        ...

class VideoProcessorProtocol(Protocol):
    """
    Interface for video processing.
    """
    def process_video(self, video_path: str | Path) -> VideoAnalysisResult:
        """
        Process a video file to extract metadata, frames, and audio.
        """
        ...
