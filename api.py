from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from dependency_injector.wiring import inject, Provide
from containers import Container
from services.judge_service import JudgeService
from schemas import ContentInput, JudgeOutput
import os

app = FastAPI(title="FeltSense Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize and configure container
container = Container()
container.config.openai_api_key.from_env("OPENAI_API_KEY")
container.config.llm_mode.from_env("LLM_MODE", "openai")
container.config.model.from_env("OPENAI_MODEL", "gpt-4o")

app.container = container

@app.post("/analyze", response_model=JudgeOutput)
@inject
async def analyze_content(
    text: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    context: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    judge: JudgeService = Depends(Provide[Container.judge_service])
):
    temp_file_path = None
    try:
        # Handle file upload if present
        if file:
            temp_file_path = f"temp_{file.filename}"
            with open(temp_file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        
        # Create input object
        input_data = ContentInput(
            text=text,
            url=url,
            context=context,
            video_path=temp_file_path
        )

        return judge.analyze_content(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp file if it was created and still exists
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                # Log error but don't fail the request (though request is already done)
                print(f"Failed to delete temp file {temp_file_path}: {e}")

container.wire(modules=[__name__])
