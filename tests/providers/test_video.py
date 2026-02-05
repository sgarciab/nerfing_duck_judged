import pytest
from unittest.mock import Mock, patch, MagicMock
from providers.video import LocalVideoProcessor
import cv2

class TestLocalVideoProcessor:
    @patch('providers.video.cv2.VideoCapture')
    def test_extract_summary_success(self, mock_capture_cls):
        # Setup
        mock_cap = MagicMock()
        mock_capture_cls.return_value = mock_cap
        
        mock_cap.isOpened.return_value = True
        
        # Mock properties
        # CAP_PROP_FRAME_COUNT = 7 (cv2 constant)
        # CAP_PROP_FPS = 5
        # CAP_PROP_FRAME_WIDTH = 3
        # CAP_PROP_FRAME_HEIGHT = 4
        
        # We need to handle cap.get(prop_id)
        def get_side_effect(prop_id):
            if prop_id == cv2.CAP_PROP_FRAME_COUNT: return 100
            if prop_id == cv2.CAP_PROP_FPS: return 25.0
            if prop_id == cv2.CAP_PROP_FRAME_WIDTH: return 1920
            if prop_id == cv2.CAP_PROP_FRAME_HEIGHT: return 1080
            return 0
            
        mock_cap.get.side_effect = get_side_effect
        
        # Execute
        processor = LocalVideoProcessor()
        summary = processor.extract_summary("test.mp4")
        
        # Verify
        assert "Duration: 4.00 seconds" in summary  # 100 / 25
        assert "Resolution: 1920x1080" in summary
        assert "FPS: 25.00" in summary
        
        mock_cap.release.assert_called_once()

    @patch('providers.video.cv2.VideoCapture')
    def test_extract_summary_file_not_found(self, mock_capture_cls):
        mock_cap = MagicMock()
        mock_capture_cls.return_value = mock_cap
        mock_cap.isOpened.return_value = False
        
        processor = LocalVideoProcessor()
        
        with pytest.raises(FileNotFoundError):
            processor.extract_summary("bad_path.mp4")
