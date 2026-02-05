import os
import json
from typing import Optional
from interfaces.protocols import LLMProviderProtocol
from schemas import JudgeOutput
from openai import OpenAI
import textwrap

class MockLLMProvider(LLMProviderProtocol):
    """
    Returns a static, valid response for testing purposes to save tokens.
    """
    def generate_judgment(self, prompt: str, system_prompt: Optional[str] = None) -> JudgeOutput:
        return JudgeOutput(
            is_ai_generated=True,
            authenticity_score=0.15,
            virality_score=85.0,
            target_audience=["Tech Enthusiasts", "Skeptics"],
            reasoning="[MOCK] The content exhibits high structural repetition typical of early patterns."
        )

class OpenAIProvider(LLMProviderProtocol):
    """
    Production implementation using OpenAI's GPT-4o.
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

    def generate_judgment(self, prompt: str, system_prompt: Optional[str] = None) -> JudgeOutput:
        
        default_system = textwrap.dedent("""
            You are 'The Judge', a content intelligence agent. 
            You evaluate content for authenticity (Human vs AI), virality potential, and audience fit.
            Return your response in strict JSON format matching the schema provided.
        """)
        
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt or default_system},
                    {"role": "user", "content": prompt}
                ],
                response_format=JudgeOutput,
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            # In a real app, we might fallback or raise a domain exception.
            # For now, we propagate or handle basic errors.
            raise RuntimeError(f"OpenAI API Error: {str(e)}")
