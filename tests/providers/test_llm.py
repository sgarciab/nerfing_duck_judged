import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
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
        
    def test_transcribe_audio_returns_mock(self):
        provider = MockLLMProvider()
        result = provider.transcribe_audio("test.mp3")
        assert "MOCK TRANSCRIPTION" in result

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
        assert call_kwargs['messages'][1]['content'][0]['text'] == "Analyze this"
        assert call_kwargs['response_format'] == JudgeOutput

    @patch('providers.llm.OpenAI')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'fake-key'})
    def test_generate_judgment_with_images(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        
        # Mock successful response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(parsed=MagicMock()))]
        mock_client.beta.chat.completions.parse.return_value = mock_completion
        
        provider = OpenAIProvider()
        
        with patch("builtins.open", mock_open(read_data=b"fake-image-data")):
            provider.generate_judgment(prompt="Look", image_paths=["/tmp/img1.jpg"])
            
        call_kwargs = mock_client.beta.chat.completions.parse.call_args.kwargs
        content = call_kwargs['messages'][1]['content']
        
        assert len(content) == 2
        assert content[0]['type'] == 'text'
        assert content[1]['type'] == 'image_url'
        assert "base64" in content[1]['image_url']['url']

    @patch('providers.llm.OpenAI')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'fake-key'})
    def test_transcribe_audio(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.audio.transcriptions.create.return_value = "Transcribed text"
        
        provider = OpenAIProvider()
        
        with patch("builtins.open", mock_open(read_data=b"fake-audio")):
            result = provider.transcribe_audio("audio.mp3")
            
        assert result == "Transcribed text"
        mock_client.audio.transcriptions.create.assert_called_once()

    @patch('providers.llm.OpenAI')
    def test_generate_judgment_propagates_error(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.beta.chat.completions.parse.side_effect = Exception("API Error")
        
        provider = OpenAIProvider(api_key="test")
        
        with pytest.raises(RuntimeError) as excinfo:
            provider.generate_judgment("test")
        
        assert "OpenAI API Error" in str(excinfo.value)
