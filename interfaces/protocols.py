from typing import Protocol, Optional, Any, Dict
from pathlib import Path
from schemas import JudgeOutput

class LLMProviderProtocol(Protocol):
    """
    Interface for LLM interactions.
    """
    def generate_judgment(self, prompt: str, system_prompt: Optional[str] = None) -> JudgeOutput:
        """
        Send a prompt to the LLM and expect a structured JudgeOutput.
        """
        ...

class VideoProcessorProtocol(Protocol):
    """
    Interface for video processing.
    """
    def extract_summary(self, video_path: str | Path) -> str:
        """
        Process a video file and return a textual summary or description
        suitable for LLM consumption.
        """
        ...
