import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from main import app
from schemas import JudgeOutput

runner = CliRunner()

class TestMainCLI:
    
    @patch('main.Container')
    def test_analyze_command_success_text(self, mock_container_cls):
        # Setup Dependency Injection Mocks
        mock_container = mock_container_cls.return_value
        mock_judge = MagicMock()
        mock_container.judge_service.return_value = mock_judge
        
        # Return a valid JudgeOutput
        mock_result = JudgeOutput(
            is_ai_generated=False,
            authenticity_score=0.9,
            virality_score=80.0,
            target_audience=["Everyone"],
            reasoning="Because I said so"
        )
        mock_judge.analyze_content.return_value = mock_result
        
        # Execute
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            result = runner.invoke(app, ["Hello World"])
        
        # Verify
        assert result.exit_code == 0
        assert "Authenticity Score: 0.9" in result.stdout
        assert "Because I said so" in result.stdout
        
        # Verify wiring
        mock_container.judge_service.assert_called_once()
        mock_judge.analyze_content.assert_called_once()

    @patch('main.Container')
    def test_analyze_command_mock_mode(self, mock_container_cls):
        # Setup
        mock_container = mock_container_cls.return_value
        mock_judge = MagicMock()
        mock_container.judge_service.return_value = mock_judge
        
        mock_result = JudgeOutput(
            is_ai_generated=True, authenticity_score=0, virality_score=0, target_audience=[], reasoning="Mock reasoning"
        )
        mock_judge.analyze_content.return_value = mock_result
        
        # Execute
        result = runner.invoke(app, ["Test", "--mock"])
        
        # Verify
        assert result.exit_code == 0
        # Check that configuration was set
        mock_container.config.llm_mode.from_value.assert_called_with("mock")
        mock_judge.analyze_content.assert_called_once()

    def test_analyze_missing_args(self):
        result = runner.invoke(app, [])
        assert result.exit_code == 1
        assert "You must provide text content, a --video path, or a --url" in result.stdout

    @patch.dict('os.environ', {}, clear=True)
    @patch('main.Container')
    def test_analyze_missing_api_key(self, mock_container_cls):
        # Setup container but logic fails before calling judge if no key
        # Actually logic is: instantiate container, configure, THEN check env var manually in main.py
        
        # Execute
        result = runner.invoke(app, ["Test"])
        assert result.exit_code == 1
        assert "OPENAI_API_KEY not found" in result.stdout

    @patch('main.Container')
    def test_analyze_command_url_success(self, mock_container_cls):
        # Setup
        mock_container = mock_container_cls.return_value
        mock_judge = MagicMock()
        mock_container.judge_service.return_value = mock_judge
        
        mock_result = JudgeOutput(
            is_ai_generated=False, authenticity_score=0.9, virality_score=80.0, target_audience=[], reasoning=""
        )
        mock_judge.analyze_content.return_value = mock_result
        
        # Execute with --url and --mock
        result = runner.invoke(app, ["--url", "http://example.com/video", "--mock"])
        
        # Verify
        assert result.exit_code == 0
        # Download message is gone from main.py, so we just check success
        mock_judge.analyze_content.assert_called_once()
        # Verify arguments passed to judge contain the URL
        call_args = mock_judge.analyze_content.call_args[0][0] # first arg (ContentInput)
        assert call_args.url == "http://example.com/video"

    @patch('main.Container')
    def test_analyze_command_analysis_failure(self, mock_container_cls):
        # Setup
        mock_container = mock_container_cls.return_value
        mock_judge = MagicMock()
        mock_container.judge_service.return_value = mock_judge
        
        # Simulate RuntimeError (e.g. from failed download or analysis)
        mock_judge.analyze_content.side_effect = RuntimeError("Something went wrong")

        # Execute
        result = runner.invoke(app, ["Test Content", "--mock"])
        
        # Verify
        assert result.exit_code == 1
        assert "Analysis Error:" in result.stdout
        assert "Something went wrong" in result.stdout

    @patch('main.Container')
    def test_analyze_command_unexpected_exception(self, mock_container_cls):
        # Setup
        mock_container = mock_container_cls.return_value
        mock_judge = MagicMock()
        mock_container.judge_service.return_value = mock_judge
        
        # Simulate generic Exception
        mock_judge.analyze_content.side_effect = Exception("Crash")

        # Execute
        result = runner.invoke(app, ["Test Content", "--mock"])
        
        # Verify
        assert result.exit_code == 1
        assert "Unexpected Failure:" in result.stdout
        assert "Crash" in result.stdout
