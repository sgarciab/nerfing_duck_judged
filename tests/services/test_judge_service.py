import pytest
from unittest.mock import Mock, MagicMock
from services.judge_service import JudgeService
from schemas import ContentInput, JudgeOutput
from interfaces.protocols import LLMProviderProtocol, VideoProcessorProtocol

class TestJudgeService:
    @pytest.fixture
    def mock_llm(self):
        return Mock(spec=LLMProviderProtocol)

    @pytest.fixture
    def mock_video(self):
        return Mock(spec=VideoProcessorProtocol)

    @pytest.fixture
    def judge_service(self, mock_llm, mock_video):
        return JudgeService(llm_provider=mock_llm, video_processor=mock_video)

    def test_analyze_content_text_only(self):
        # Setup
        mock_llm = Mock(spec=LLMProviderProtocol)
        mock_video = Mock(spec=VideoProcessorProtocol)
        service = JudgeService(mock_llm, mock_video)
        
        input_data = ContentInput(text="Test content", video_path=None)
        expected_output = JudgeOutput(
            is_ai_generated=False,
            authenticity_score=0.9,
            virality_score=50.0,
            target_audience=["General"],
            reasoning="Test reasoning"
        )
        mock_llm.generate_judgment.return_value = expected_output

        # Execute
        result = service.analyze_content(input_data)

        # Verify
        assert result == expected_output
        mock_video.extract_summary.assert_not_called()
        
        # Verify prompt construction contains text but not video
        args, _ = mock_llm.generate_judgment.call_args
        prompt = args[0] if args else list(mock_llm.generate_judgment.call_args.kwargs.values())[0] # handle positional or keyword
        # actually generate_judgment takes prompt as kwarg or pos.
        # Let's check call_args strictly if possible
        assert "Text Content:\nTest content" in prompt
        assert "Video Analysis:" not in prompt

    def test_analyze_content_with_video(self):
        # Setup
        mock_llm = Mock(spec=LLMProviderProtocol)
        mock_video = Mock(spec=VideoProcessorProtocol)
        service = JudgeService(mock_llm, mock_video)
        
        video_path = "test_video.mp4"
        input_data = ContentInput(text=None, video_path=video_path)
        video_summary = "A video of a cat."
        
        mock_video.extract_summary.return_value = video_summary
        mock_llm.generate_judgment.return_value = JudgeOutput(
            is_ai_generated=False,
            authenticity_score=0.8,
            virality_score=90.0,
            target_audience=["Cat Lovers"],
            reasoning="Cute cat"
        )

        # Execute
        service.analyze_content(input_data)

        # Verify
        mock_video.extract_summary.assert_called_once_with(video_path)
        
        # Check prompt contains video summary
        call_args = mock_llm.generate_judgment.call_args
        prompt = call_args[1].get('prompt') or call_args[0][0]
        assert f"Video Analysis:\n{video_summary}" in prompt

    def test_analyze_content_with_context(self):
        # Setup
        mock_llm = Mock(spec=LLMProviderProtocol)
        mock_video = Mock(spec=VideoProcessorProtocol)
        service = JudgeService(mock_llm, mock_video)
        
        input_data = ContentInput(text="Hi", context="Posted on TikTok")
        mock_llm.generate_judgment.return_value = JudgeOutput(
            is_ai_generated=False, authenticity_score=0.1, virality_score=0.1, target_audience=[], reasoning=""
        )

        # Execute
        service.analyze_content(input_data)

        # Verify
        call_args = mock_llm.generate_judgment.call_args
        prompt = call_args[1].get('prompt') or call_args[0][0]
        assert "Additional Context:\nPosted on TikTok" in prompt
