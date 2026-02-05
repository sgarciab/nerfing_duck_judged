import typer
import os
from typing import Optional
from typing_extensions import Annotated
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON
from dotenv import load_dotenv

from services.judge_service import JudgeService
from providers.llm import OpenAIProvider, MockLLMProvider
from providers.video import LocalVideoProcessor
from schemas import ContentInput, JudgeOutput

# Load env variables (e.g. OPENAI_API_KEY)
load_dotenv()

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

    # 1. Wire Dependencies (Composition Root)
    video_processor = LocalVideoProcessor()
    
    if mock:
        console.print("[yellow]Running in MOCK mode. No API tokens will be used.[/yellow]")
        llm_provider = MockLLMProvider()
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            console.print("[bold red]Error:[/bold red] OPENAI_API_KEY not found in environment. Use --mock to test without it.")
            raise typer.Exit(code=1)
        llm_provider = OpenAIProvider(api_key=api_key, model=model)

    judge = JudgeService(llm_provider=llm_provider, video_processor=video_processor)

    # Handle Video Download if URL provided
    video_path = video
    if url:
        if video:
            console.print("[bold yellow]Warning:[/bold yellow] Both --video and --url provided. Ignoring --video and using URL.")
        
        with console.status(f"[bold green]Downloading video from {url}...[/bold green]"):
            try:
                video_path = video_processor.download_video(url)
                console.print(f"[green]Video downloaded to: {video_path}[/green]")
            except Exception as e:
                console.print(f"[bold red]Download Failed:[/bold red] {e}")
                raise typer.Exit(code=1)

    # 2. Prepare Input
    input_data = ContentInput(
        text=content,
        video_path=video_path,
        context=context
    )

    # 3. Execute
    with console.status("[bold green]Agent is thinking...[/bold green]"):
        try:
            result: JudgeOutput = judge.analyze_content(input_data)
        except Exception as e:
            console.print(f"[bold red]Analysis Failed:[/bold red] {e}")
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
