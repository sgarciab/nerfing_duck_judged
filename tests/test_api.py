from fastapi.testclient import TestClient
from api import app
from schemas import JudgeOutput
from unittest.mock import MagicMock
from dependency_injector import providers

client = TestClient(app)

def test_analyze_mock():
    # Set config to mock via env var or modifying container in testing?
    # Since app initializes container at module level, checking environment variables logic
    # We can override the container config for the test
    
    app.container.config.llm_mode.override("mock")
    
    response = client.post("/analyze", data={"text": "This is a test"})
    
    if response.status_code != 200:
        print(f"Error Response: {response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_ai_generated"] is True
    assert "MOCK" in data["reasoning"]

def test_analyze_mock_with_url():
    # We don't want to actually download in unit test unless we mock download
    # So we should mock video_processor in container
    
    mock_video = MagicMock()
    mock_video.download_video.return_value = "mock_video.mp4"
    mock_video.process_video.return_value.metadata = "Mock Metadata"
    mock_video.process_video.return_value.frame_paths = []
    mock_video.process_video.return_value.audio_path = None
    
    app.container.video_processor.override(mock_video)
    app.container.config.llm_mode.override("mock")
    
    response = client.post("/analyze", data={"url": "http://example.com/video"})
    
    if response.status_code != 200:
        print(f"Error Response: {response.text}")
    
    assert response.status_code == 200
    mock_video.download_video.assert_called_with("http://example.com/video")
    
    # Reset override
    app.container.video_processor.reset_override()

def test_analyze_generic_exception():
    # Mock JudgeService to raise an exception
    mock_judge = MagicMock()
    mock_judge.analyze_content.side_effect = Exception("General Failure")
    
    app.container.judge_service.override(mock_judge)
    
    response = client.post("/analyze", data={"text": "Fail me"})
    
    assert response.status_code == 500
    assert "General Failure" in response.json()["detail"]
    
    app.container.judge_service.reset_override()
