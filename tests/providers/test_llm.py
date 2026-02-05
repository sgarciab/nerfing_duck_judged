import pytest
from unittest.mock import Mock, MagicMock, patch
from providers.llm import MockLLMProvider, OpenAIProvider
from schemas import JudgeOutput

class TestMockLLMProvider:
    def test_generate_judgment_returns_static_response(self):
        provider = MockLLMProvider()
        result = provider.generate_judgment(prompt="test")
        
        assert isinstance(result, JudgeOutput)
        assert result.is_ai_generated is True
        assert result.virality_score == 85.0
        assert "[MOCK]" in result.reasoning

class TestOpenAIProvider:
    @patch('providers.llm.OpenAI')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'fake-key'})
    def test_generate_judgment_calls_openai(self, mock_openai_cls):
        # Setup Mock Client
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        
        mock_completion = MagicMock()
        mock_message = MagicMock()
        
        expected_output = JudgeOutput(
            is_ai_generated=False,
            authenticity_score=0.99,
            virality_score=10.0,
            target_audience=["Nerds"],
            reasoning="Looks real"
        )
        
        mock_message.parsed = expected_output
        mock_completion.choices = [MagicMock(message=mock_message)]
        mock_client.beta.chat.completions.parse.return_value = mock_completion
        
        # Execute
        provider = OpenAIProvider()
        result = provider.generate_judgment(prompt="Analyze this")
        
        # Verify
        assert result == expected_output
        mock_client.beta.chat.completions.parse.assert_called_once()
        call_kwargs = mock_client.beta.chat.completions.parse.call_args.kwargs
        assert call_kwargs['model'] == "gpt-4o"
        assert call_kwargs['messages'][1]['content'] == "Analyze this"
        assert call_kwargs['response_format'] == JudgeOutput

    @patch('providers.llm.OpenAI')
    def test_generate_judgment_propagates_error(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.beta.chat.completions.parse.side_effect = Exception("API Error")
        
        provider = OpenAIProvider(api_key="test")
        
        with pytest.raises(RuntimeError) as excinfo:
            provider.generate_judgment("test")
        
        assert "OpenAI API Error" in str(excinfo.value)
