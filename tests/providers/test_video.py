import pytest
from unittest.mock import Mock, patch, MagicMock
from providers.video import LocalVideoProcessor
from schemas import VideoAnalysisResult
import cv2

class TestLocalVideoProcessor:
    @patch('providers.video.os.path.exists')
    @patch('providers.video.VideoFileClip')
    @patch('providers.video.cv2.VideoCapture')
    @patch('providers.video.cv2.imwrite')
    def test_process_video_success(self, mock_imwrite, mock_capture_cls, mock_videoclip_cls, mock_exists):
        # Setup
        mock_exists.return_value = True
        
        # MOCK CV2
        mock_cap = MagicMock()
        mock_capture_cls.return_value = mock_cap
        mock_cap.isOpened.return_value = True
        
        def get_side_effect(prop_id):
            if prop_id == cv2.CAP_PROP_FRAME_COUNT: return 100
            if prop_id == cv2.CAP_PROP_FPS: return 25.0
            if prop_id == cv2.CAP_PROP_FRAME_WIDTH: return 1920
            if prop_id == cv2.CAP_PROP_FRAME_HEIGHT: return 1080
            return 0
        mock_cap.get.side_effect = get_side_effect
        mock_cap.read.return_value = (True, "fake_frame_data")

        # MOCK MOVIEPY
        mock_clip = MagicMock()
        mock_videoclip_cls.return_value.__enter__.return_value = mock_clip
        mock_clip.audio = MagicMock()
        
        # Execute
        processor = LocalVideoProcessor()
        result = processor.process_video("test.mp4")
        
        # Verify
        assert isinstance(result, VideoAnalysisResult)
        assert result.duration == 4.0
        assert "Resolution: 1920x1080" in result.metadata
        assert len(result.frame_paths) == 5
        assert result.audio_path is not None
        
        mock_cap.release.assert_called()
        mock_clip.audio.write_audiofile.assert_called_once()


    @patch('providers.video.os.path.exists')
    def test_process_video_file_not_found(self, mock_exists):
        mock_exists.return_value = False
        processor = LocalVideoProcessor()
        
        with pytest.raises(FileNotFoundError):
            processor.process_video("bad_path.mp4")
