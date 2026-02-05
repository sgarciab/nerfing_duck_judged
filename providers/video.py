import cv2
import tempfile
import os
from pathlib import Path
from typing import List, Optional
from moviepy import VideoFileClip
from interfaces.protocols import VideoProcessorProtocol
from schemas import VideoAnalysisResult

class LocalVideoProcessor(VideoProcessorProtocol):
    def process_video(self, video_path: str | Path) -> VideoAnalysisResult:
        """
        Extracts metadata, audio, and frames from a video file.
        """
        path_str = str(video_path)
        
        if not os.path.exists(path_str):
            raise FileNotFoundError(f"Could not open video file: {path_str}")

        # 1. Extract Metadata using OpenCV
        cap = cv2.VideoCapture(path_str)
        if not cap.isOpened():
             raise FileNotFoundError(f"Could not open video file with cv2: {path_str}")
             
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        cap.release()

        # 2. Extract Audio
        audio_path = self._extract_audio(path_str)

        # 3. Extract Frames (Sample 5 frames evenly distributed)
        frame_paths = self._extract_frames(path_str, duration, num_frames=5)
        
        metadata = (
            f"Duration: {duration:.2f}s, Resolution: {width}x{height}, FPS: {fps:.2f}, "
            f"Frames: {frame_count}"
        )

        return VideoAnalysisResult(
            video_path=path_str,
            duration=duration,
            frame_paths=frame_paths,
            audio_path=audio_path,
            metadata=metadata
        )

    def _extract_audio(self, video_path: str) -> Optional[str]:
        try:
            with VideoFileClip(video_path) as clip:
                if clip.audio is None:
                    return None
                
                temp_dir = tempfile.gettempdir()
                audio_path = os.path.join(temp_dir, f"audio_{os.path.basename(video_path)}.mp3")
                
                # Check if we should overwrite? Ideally yes for temp.
                # Write audio file
                clip.audio.write_audiofile(audio_path, logger=None)
                return audio_path
        except Exception as e:
            print(f"Warning: Audio extraction failed: {e}")
            return None

    def _extract_frames(self, video_path: str, duration: float, num_frames: int) -> List[str]:
        frames = []
        if duration <= 0:
            return frames
            
        cap = cv2.VideoCapture(video_path)
        temp_dir = tempfile.gettempdir()
        
        step = duration / (num_frames + 1)
        
        for i in range(1, num_frames + 1):
            time_point = step * i
            # Set position in milliseconds
            cap.set(cv2.CAP_PROP_POS_MSEC, time_point * 1000)
            ret, frame = cap.read()
            if ret:
                frame_path = os.path.join(temp_dir, f"frame_{i}_{os.path.basename(video_path)}.jpg")
                cv2.imwrite(frame_path, frame)
                frames.append(frame_path)
                
        cap.release()
        return frames
