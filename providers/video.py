import cv2
from pathlib import Path
from interfaces.protocols import VideoProcessorProtocol

class LocalVideoProcessor(VideoProcessorProtocol):
    def extract_summary(self, video_path: str | Path) -> str:
        """
        Uses OpenCV to extract basic metadata and a sampling of frames.
        NOTE: In a real system, we would use a Multimodal LLM to describe frames,
        or use a transcription service (Whisper). 
        For this challenge, we will simulate the 'description' by extracting metadata.
        """
        path_str = str(video_path)
        cap = cv2.VideoCapture(path_str)
        
        if not cap.isOpened():
            raise FileNotFoundError(f"Could not open video file: {path_str}")
            
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps if fps > 0 else 0
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        cap.release()
        
        # In a real implementation, we would extract N frames and pass them to GPT-4o-vision.
        # Here we return technical metadata as a proxy for the visual content description.
        summary = (
            f"Video Metadata:\n"
            f"- Duration: {duration:.2f} seconds\n"
            f"- Resolution: {width}x{height}\n"
            f"- FPS: {fps:.2f}\n"
            f"- Total Frames: {frame_count}\n"
            f"(Note: Visual content analysis requires Vision API, using metadata proxy for this layer)."
        )
        return summary
