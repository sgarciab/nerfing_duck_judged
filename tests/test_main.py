import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from main import app
from schemas import JudgeOutput

runner = CliRunner()

class TestMainCLI:
    
    @patch('main.JudgeService')
    @patch('main.OpenAIProvider')
    @patch('main.LocalVideoProcessor')
    def test_analyze_command_success_text(self, mock_video_cls, mock_openai_cls, mock_judge_cls):
        # Setup
        mock_judge_instance = MagicMock()
        mock_judge_cls.return_value = mock_judge_instance
        
        # Return a valid JudgeOutput
        mock_result = JudgeOutput(
            is_ai_generated=False,
            authenticity_score=0.9,
            virality_score=80.0,
            target_audience=["Everyone"],
            reasoning="Because I said so"
        )
        mock_judge_instance.analyze_content.return_value = mock_result
        
        # Mock ENV for API Key check
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            result = runner.invoke(app, ["Hello World"])
        
        assert result.exit_code == 0
        assert "Authenticity Score: 0.9" in result.stdout
        assert "Because I said so" in result.stdout
        
        # Verify dependencies wired correctly
        mock_openai_cls.assert_called_once()
        mock_video_cls.assert_called_once()
        mock_judge_cls.assert_called_once()

    @patch('main.JudgeService')
    @patch('main.MockLLMProvider')
    def test_analyze_command_mock_mode(self, mock_llm_cls, mock_judge_cls):
        mock_judge_instance = MagicMock()
        mock_judge_cls.return_value = mock_judge_instance
        mock_result = JudgeOutput(
            is_ai_generated=True, authenticity_score=0, virality_score=0, target_audience=[], reasoning=""
        )
        mock_judge_instance.analyze_content.return_value = mock_result
        
        result = runner.invoke(app, ["Test", "--mock"])
        
        assert result.exit_code == 0
        assert "Running in MOCK mode" in result.stdout
        mock_llm_cls.assert_called_once()

    def test_analyze_missing_args(self):
        result = runner.invoke(app, [])
        assert result.exit_code == 1
        assert "You must provide either text content argument or a --video path" in result.stdout

    @patch.dict('os.environ', {}, clear=True)
    def test_analyze_missing_api_key(self):
        # Ensure no API key in env
        result = runner.invoke(app, ["Test"])
        assert result.exit_code == 1
        assert "OPENAI_API_KEY not found" in result.stdout
