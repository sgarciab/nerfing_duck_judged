from pathlib import Path
import os
import logging
import textwrap
from typing import Optional
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
        1. Download video if URL is provided.
        2. Process Video (if present) -> Extract Frames & Audio
        3. Transcribe Audio (if present)
        4. Construct Prompt combining text, video metadata, transcription, and context.
        5. Call LLM with text prompt + video frames.
        """
        
        downloaded_video_path = None
        
        # 0. Handle URL
        if content_input.url and not content_input.video_path:
            try:
                downloaded_video_path = self.video.download_video(content_input.url)
                content_input.video_path = downloaded_video_path
            except Exception as e:
                logging.error(f"Failed to download video: {e}")
                # We can either raise or continue without video? 
                # For this app, raising seems appropriate as video was requested.
                raise RuntimeError(f"Video download failed: {e}")

        # 1. Gather Context
        video_metadata = ""
        transcription = ""
        image_paths = []
        video_result = None
        
        try:
            if content_input.video_path:
                # Result contains metadata, frame paths, audio path
                video_result = self.video.process_video(content_input.video_path)
                
                video_metadata = video_result.metadata
                image_paths = video_result.frame_paths
                
                # 2. Transcribe Audio if available
                if video_result.audio_path:
                    try:
                        transcription = self.llm.transcribe_audio(video_result.audio_path)
                    except Exception as e:
                        transcription = f"[Audio Transcription Failed: {e}]"
            
            # 3. Construct Prompt strategy
            final_prompt = self._construct_judge_prompt(
                text=content_input.text,
                video_metadata=video_metadata,
                transcription=transcription,
                extra_context=content_input.context
            )
            
            # 4. Get Verdict (Multimodal)
            judgment = self.llm.generate_judgment(
                prompt=final_prompt,
                image_paths=image_paths
            )
            return judgment
            
        finally:
            # Cleanup frames, audio, AND downloaded video
            audio_path = video_result.audio_path if video_result else None
            self._cleanup_resources(image_paths, audio_path, downloaded_video_path)

    def _cleanup_resources(self, image_paths: list[str], audio_path: Optional[str], video_path: Optional[str] = None):
        """
        Cleans up temporary files generated during processing.
        """
        try:
            for path in image_paths:
                if os.path.exists(path):
                    os.remove(path)
            
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
                
            if video_path and os.path.exists(video_path):
                os.remove(video_path)
        except Exception as e:
            logging.warning(f"Failed to cleanup resources: {e}")

    def _construct_judge_prompt(self, text: str | None, video_metadata: str, transcription: str, extra_context: str | None) -> str:
        prompt_parts = [
            "Please evaluate the following content submission for Authenticity, Virality, and Audience Fit.",
            "\n--- CONTENT DATA ---"
        ]
        
        if text:
            prompt_parts.append(f"Text Content:\n{text}")
            
        if video_metadata:
            prompt_parts.append(f"Video Technical Metadata:\n{video_metadata}")
            
        if transcription:
            prompt_parts.append(f"Video Audio Transcription:\n{transcription}")
            
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
