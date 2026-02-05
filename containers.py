from dependency_injector import containers, providers
from services.judge_service import JudgeService
from providers.llm import OpenAIProvider, MockLLMProvider
from providers.video import LocalVideoProcessor
import os

class Container(containers.DeclarativeContainer):
    
    wiring_config = containers.WiringConfiguration(modules=["main", "api"])
    
    config = providers.Configuration()
    
    video_processor = providers.Singleton(LocalVideoProcessor)
    
    llm_provider = providers.Selector(
        config.llm_mode,
        mock=providers.Singleton(MockLLMProvider),
        openai=providers.Singleton(
            OpenAIProvider,
            api_key=config.openai_api_key,
            model=config.model
        ),
    )
    
    judge_service = providers.Factory(
        JudgeService,
        llm_provider=llm_provider,
        video_processor=video_processor,
    )
