import pytest
from unittest.mock import Mock, patch, MagicMock
from providers.video import LocalVideoProcessor
from schemas import VideoAnalysisResult
import cv2
import os

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

    @patch('providers.video.os.path.exists')
    @patch('providers.video.cv2.VideoCapture')
    def test_process_video_cv2_failure(self, mock_capture_cls, mock_exists):
        mock_exists.return_value = True
        mock_cap = MagicMock()
        mock_capture_cls.return_value = mock_cap
        mock_cap.isOpened.return_value = False
        
        processor = LocalVideoProcessor()
        with pytest.raises(FileNotFoundError):
            processor.process_video("corrupt.mp4")

    @patch('providers.video.os.path.exists')
    @patch('providers.video.cv2.VideoCapture')
    @patch('providers.video.VideoFileClip')
    @patch('providers.video.cv2.imwrite')
    def test_extract_audio_no_audio(self, mock_imwrite, mock_clip_cls, mock_capture_cls, mock_exists):
        mock_exists.return_value = True
        # Setup valid video first to bypass cv2 check
        mock_cap = MagicMock()
        mock_capture_cls.return_value = mock_cap
        mock_cap.isOpened.return_value = True
        
        # return dummy values for duration calc
        def get_side_effect(prop_id):
            if prop_id == cv2.CAP_PROP_FRAME_COUNT: return 100
            if prop_id == cv2.CAP_PROP_FPS: return 25.0
            return 0
        mock_cap.get.side_effect = get_side_effect
        mock_cap.read.return_value = (True, "frame")
        
        # Mock clip with no audio
        mock_clip = MagicMock()
        mock_clip_cls.return_value.__enter__.return_value = mock_clip
        mock_clip.audio = None
        
        processor = LocalVideoProcessor()
        result = processor.process_video("silent.mp4")
        assert result.audio_path is None

    @patch('providers.video.os.path.exists')
    @patch('providers.video.cv2.VideoCapture')
    @patch('providers.video.VideoFileClip')
    @patch('providers.video.cv2.imwrite')
    def test_extract_audio_failure(self, mock_imwrite, mock_clip_cls, mock_capture_cls, mock_exists):
        mock_exists.return_value = True
        # Setup valid video first
        mock_cap = MagicMock()
        mock_capture_cls.return_value = mock_cap
        mock_cap.isOpened.return_value = True
        
        # return dummy values for duration calc
        def get_side_effect(prop_id):
            if prop_id == cv2.CAP_PROP_FRAME_COUNT: return 100
            if prop_id == cv2.CAP_PROP_FPS: return 25.0
            return 0
        mock_cap.get.side_effect = get_side_effect
        mock_cap.read.return_value = (True, "frame")
        
        # Mock clip raising exception
        mock_clip_cls.return_value.__enter__.side_effect = Exception("Clip Error")
        
        processor = LocalVideoProcessor()
        result = processor.process_video("error.mp4")
        # Should catch exception and return None for audio_path
        assert result.audio_path is None

    @patch('providers.video.yt_dlp.YoutubeDL')
    def test_download_video_success(self, mock_ytdl_cls):
        # Setup
        mock_ytdl = MagicMock()
        mock_ytdl_cls.return_value.__enter__.return_value = mock_ytdl
        
        # Mock extract_info result
        mock_info = {'id': 'test_video', 'ext': 'mp4'}
        mock_ytdl.extract_info.return_value = mock_info
        
        # Mock prepare_filename
        expected_path = "/tmp/test_video.mp4"
        mock_ytdl.prepare_filename.return_value = expected_path
        
        # Execute
        processor = LocalVideoProcessor()
        result = processor.download_video("https://youtube.com/watch?v=123")
        
        # Verify
        assert result == expected_path
        mock_ytdl.extract_info.assert_called_with("https://youtube.com/watch?v=123", download=True)

    @patch('providers.video.yt_dlp.YoutubeDL')
    def test_download_video_failure(self, mock_ytdl_cls):
        mock_ytdl_cls.return_value.__enter__.side_effect = Exception("YT Down")
        
        processor = LocalVideoProcessor()
        with pytest.raises(RuntimeError):
            processor.download_video("https://fail.com")

    @patch('providers.video.os.path.exists')
    @patch('providers.video.cv2.VideoCapture')
    @patch('providers.video.VideoFileClip') 
    def test_extract_frames_zero_duration(self, mock_videoclip_cls, mock_capture_cls, mock_exists):
        # If duration calculation results in 0
        mock_exists.return_value = True
        mock_cap = MagicMock()
        mock_capture_cls.return_value = mock_cap
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 0 # FPS=0 -> Duration=0
        
        # Mock VideoFileClip to prevent it from crashing if called (should likely handle no audio gracefully)
        mock_videoclip_cls.return_value.__enter__.return_value.audio = None
        
        processor = LocalVideoProcessor()
        result = processor.process_video("zero.mp4")
        
        assert result.duration == 0
        assert result.frame_paths == []
