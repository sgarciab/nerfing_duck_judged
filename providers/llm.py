import os
import json
import base64
from typing import Optional, List
from interfaces.protocols import LLMProviderProtocol
from schemas import JudgeOutput
from openai import OpenAI
import textwrap

class MockLLMProvider(LLMProviderProtocol):
    """
    Returns a static, valid response for testing purposes to save tokens.
    """
    def generate_judgment(self, prompt: str, system_prompt: Optional[str] = None, image_paths: Optional[list[str]] = None) -> JudgeOutput:
        return JudgeOutput(
            is_ai_generated=True,
            authenticity_score=0.15,
            virality_score=85.0,
            target_audience=["Tech Enthusiasts", "Skeptics"],
            reasoning="[MOCK] The content exhibits high structural repetition typical of early patterns."
        )

    def transcribe_audio(self, audio_path: str) -> str:
        return "[MOCK TRANSCRIPTION] This is a simulated audio transcription."

class OpenAIProvider(LLMProviderProtocol):
    """
    Production implementation using OpenAI's GPT-4o.
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def generate_judgment(self, prompt: str, system_prompt: Optional[str] = None, image_paths: Optional[list[str]] = None) -> JudgeOutput:
        
        default_system = textwrap.dedent("""
            You are 'The Judge', a content intelligence agent. 
            You evaluate content for authenticity (Human vs AI), virality potential, and audience fit.
            Return your response in strict JSON format matching the schema provided.
        """)
        
        user_content = [{"type": "text", "text": prompt}]
        
        if image_paths:
            for img_path in image_paths:
                try:
                    base64_image = self._encode_image(img_path)
                    user_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
                except Exception as e:
                    print(f"Warning: Could not process image {img_path}: {e}")

        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt or default_system},
                    {"role": "user", "content": user_content}
                ],
                response_format=JudgeOutput,
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            # In a real app, we might fallback or raise a domain exception.
            # For now, we propagate or handle basic errors.
            raise RuntimeError(f"OpenAI API Error: {str(e)}")

    def transcribe_audio(self, audio_path: str) -> str:
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file,
                    response_format="text"
                )
            return transcript
        except Exception as e:
            raise RuntimeError(f"OpenAI Whisper Error: {str(e)}")
