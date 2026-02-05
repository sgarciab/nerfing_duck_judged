from pydantic import BaseModel, Field
from typing import List, Optional

class JudgeOutput(BaseModel):
    """
    Standardized output from the Judge Agent.
    """
    is_ai_generated: bool = Field(..., description="Classification of whether the content is AI-generated.")
    authenticity_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score for authenticity (0=Fake, 1=Authentic).")
    virality_score: float = Field(..., ge=0.0, le=100.0, description="Predicted potential for social engagement (0-100).")
    target_audience: List[str] = Field(default_factory=list, description="List of audience segments this content appeals to.")
    reasoning: str = Field(..., description="Explanation of why these scores were assigned.")

class ContentInput(BaseModel):
    """
    Input content to be judged.
    """
    text: Optional[str] = None
    video_path: Optional[str] = None
    context: Optional[str] = Field(None, description="Optional extra context about the content.")

class VideoAnalysisResult(BaseModel):
    """
    Results from local video processing.
    """
    video_path: str
    duration: float
    frame_paths: List[str] = Field(default_factory=list, description="Paths to extracted frames.")
    audio_path: Optional[str] = Field(None, description="Path to extracted audio file.")
    metadata: str = Field(..., description="Technical metadata summary.")
