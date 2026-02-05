from pathlib import Path
import textwrap
from schemas import JudgeOutput, ContentInput
from interfaces.protocols import LLMProviderProtocol, VideoProcessorProtocol

class JudgeService:
    def __init__(self, llm_provider: LLMProviderProtocol, video_processor: VideoProcessorProtocol):
        # Dependency Injection
        self.llm = llm_provider
        self.video = video_processor

    def analyze_content(self, content_input: ContentInput) -> JudgeOutput:
        """
        Orchestrates the analysis flow.
        1. Process Video (if present)
        2. Construct Prompt combining text, video summary, and context.
        3. Call LLM.
        """
        
        # 1. Gather Context
        video_summary = ""
        if content_input.video_path:
            # We validate existence here or inside the processor.
            # Ideally strict validation happens before service, but service checks logic.
            # LocalVideoProcessor raises FileNotFoundError if invalid.
            video_summary = self.video.extract_summary(content_input.video_path)
            
        # 2. Construct Prompt strategy
        # We use a chain-of-thought style prompt construction.
        final_prompt = self._construct_judge_prompt(
            text=content_input.text,
            video_summary=video_summary,
            extra_context=content_input.context
        )
        
        # 3. Get Verdict
        judgment = self.llm.generate_judgment(prompt=final_prompt)
        
        return judgment

    def _construct_judge_prompt(self, text: str | None, video_summary: str, extra_context: str | None) -> str:
        prompt_parts = [
            "Please evaluate the following content submission for Authenticity, Virality, and Audience Fit.",
            "\n--- CONTENT DATA ---"
        ]
        
        if text:
            prompt_parts.append(f"Text Content:\n{text}")
            
        if video_summary:
            prompt_parts.append(f"Video Analysis:\n{video_summary}")
            
        if extra_context:
            prompt_parts.append(f"Additional Context:\n{extra_context}")
            
        prompt_parts.append("\n--- END CONTENT ---")
        prompt_parts.append(textwrap.dedent("""
            Provide a judgment based on these factors:
            1. Authenticity: Look for signs of AI generation (repetitive patterns, hallucinations, unnatural cadence).
            2. Virality: Assess emotional hook, shareability, and trending relevance.
            3. Audience: Define who this is for.
            
            Return the JSON response.
        """))
        
        return "\n".join(prompt_parts)
