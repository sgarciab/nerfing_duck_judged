import typer
import os
import logging
from typing import Optional
from typing_extensions import Annotated
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

from containers import Container
from schemas import ContentInput, JudgeOutput

# Load env variables
load_dotenv()

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = typer.Typer(help="FeltSense Judge Agent CLI")
console = Console()

@app.command()
def analyze(
    content: Annotated[Optional[str], typer.Argument(help="Text content to analyze")] = None,
    video: Annotated[Optional[str], typer.Option("--video", "-v", help="Path to video file")] = None,
    url: Annotated[Optional[str], typer.Option("--url", "-u", help="URL to video (e.g. YouTube)")] = None,
    context: Annotated[Optional[str], typer.Option("--context", "-c", help="Additional context (author, platform, etc)")] = None,
    mock: Annotated[bool, typer.Option("--mock", help="Use Mock LLM Provider for testing")] = False,
    model: Annotated[str, typer.Option("--model", help="OpenAI model to use")] = "gpt-4o"
):
    """
    Analyze text or video content for authenticity, virality, and audience fit.
    """
    if not content and not video and not url:
        console.print("[bold red]Error:[/bold red] You must provide text content, a --video path, or a --url.")
        raise typer.Exit(code=1)

    # 1. Initialize Container
    container = Container()
    
    # Configure Container
    container.config.openai_api_key.from_env("OPENAI_API_KEY")
    container.config.model.from_value(model)
    
    # Set LLM Mode
    mode = "mock" if mock else "openai"
    container.config.llm_mode.from_value(mode)

    # Validate API Key if not mock
    if not mock and not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Error:[/bold red] OPENAI_API_KEY not found in environment. Use --mock to test without it.")
        raise typer.Exit(code=1)

    # Resolve Service
    judge = container.judge_service()

    # 2. Prepare Input
    input_data = ContentInput(
        text=content,
        video_path=video,
        url=url,
        context=context
    )

    # 3. Execute
    with console.status("[bold green]Agent is thinking (and processing video if needed)...[/bold green]"):
        try:
            result: JudgeOutput = judge.analyze_content(input_data)
        except (FileNotFoundError, RuntimeError) as e:
             console.print(f"[bold red]Analysis Error:[/bold red] {e}")
             raise typer.Exit(code=1)
        except Exception as e:
            console.print(f"[bold red]Unexpected Failure:[/bold red] {e}")
            raise typer.Exit(code=1)

    # 4. Render Output
    console.print(Panel.fit(
        f"[bold]Authenticity Score:[/bold] {result.authenticity_score}\n"
        f"[bold]Is AI Generated:[/bold] {result.is_ai_generated}\n"
        f"[bold]Virality Score:[/bold] {result.virality_score}\n"
        f"[bold]Target Audience:[/bold] {', '.join(result.target_audience)}",
        title="Judge Verdict",
        border_style="green" if result.authenticity_score > 0.5 else "red"
    ))
    
    console.print("\n[bold underline]Reasoning:[/bold underline]")
    console.print(result.reasoning)

if __name__ == "__main__":
    app()
