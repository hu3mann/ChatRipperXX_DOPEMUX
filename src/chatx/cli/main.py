"""Main CLI entry point for ChatX."""

import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

from chatx.utils.logging import setup_logging

app = typer.Typer(
    name="chatx",
    help="Privacy-focused, local-first CLI tool for forensic chat analysis",
    add_completion=False,
)
console = Console()


@app.callback()
def main(
    verbose: int = typer.Option(0, "--verbose", "-v", count=True, help="Increase verbosity"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file path"),
) -> None:
    """ChatX - Privacy-focused chat analysis tool."""
    # Set up logging based on verbosity
    log_level = logging.WARNING
    if not quiet:
        if verbose == 1:
            log_level = logging.INFO
        elif verbose >= 2:
            log_level = logging.DEBUG
            
    setup_logging(log_level)
    
    if config:
        console.print(f"Using config: {config}")
    
    # Store config for subcommands (this is just the callback, not the actual command)
    # Subcommands will handle their own logic


@app.command()
def extract(
    source: Path = typer.Argument(..., help="Source path (e.g., iMessage chat.db)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    platform: Optional[str] = typer.Option(None, "--platform", "-p", help="Platform type"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be extracted"),
) -> None:
    """Extract chat data from various platforms.
    
    Supported platforms:
    - imessage: macOS/iOS iMessage (chat.db)
    - instagram: Instagram Direct Messages  
    - whatsapp: WhatsApp export files
    - txt: Plain text conversation files
    """
    console.print(f"[bold green]Extracting from:[/bold green] {source}")
    
    if not source.exists():
        console.print(f"[bold red]Error:[/bold red] Source path does not exist: {source}")
        raise typer.Exit(1)
    
    if dry_run:
        console.print("[yellow]Dry run mode - no files will be created[/yellow]")
    
    # TODO: Implement actual extraction logic
    console.print("[yellow]Extraction not yet implemented[/yellow]")


@app.command()
def transform(
    input_dir: Path = typer.Argument(..., help="Directory containing extracted data"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    format_type: str = typer.Option("json", "--format", help="Output format (json, jsonl)"),
) -> None:
    """Transform extracted data into canonical format."""
    console.print(f"[bold green]Transforming:[/bold green] {input_dir}")
    
    if not input_dir.exists() or not input_dir.is_dir():
        console.print(f"[bold red]Error:[/bold red] Input directory does not exist: {input_dir}")
        raise typer.Exit(1)
    
    # TODO: Implement transformation logic
    console.print("[yellow]Transformation not yet implemented[/yellow]")


@app.command() 
def redact(
    input_file: Path = typer.Argument(..., help="Input file to redact"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    policy: Optional[Path] = typer.Option(None, "--policy", help="Privacy policy file"),
    strict: bool = typer.Option(True, "--strict/--no-strict", help="Enable strict redaction"),
    report: bool = typer.Option(True, "--report/--no-report", help="Generate redaction report"),
) -> None:
    """Apply privacy redaction using Policy Shield."""
    console.print(f"[bold green]Redacting:[/bold green] {input_file}")
    
    if not input_file.exists():
        console.print(f"[bold red]Error:[/bold red] Input file does not exist: {input_file}")
        raise typer.Exit(1)
        
    if strict:
        console.print("[blue]Using strict redaction mode[/blue]")
    
    # TODO: Implement redaction logic
    console.print("[yellow]Redaction not yet implemented[/yellow]")


@app.command()
def enrich(
    input_file: Path = typer.Argument(..., help="Input file to enrich"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"), 
    provider: str = typer.Option("local", "--provider", help="LLM provider (local, openai, anthropic)"),
    model: Optional[str] = typer.Option(None, "--model", help="Specific model to use"),
    batch_size: int = typer.Option(10, "--batch-size", help="Batch size for processing"),
) -> None:
    """Enrich messages with LLM-generated metadata."""
    console.print(f"[bold green]Enriching:[/bold green] {input_file}")
    
    if not input_file.exists():
        console.print(f"[bold red]Error:[/bold red] Input file does not exist: {input_file}")
        raise typer.Exit(1)
        
    console.print(f"[blue]Using provider:[/blue] {provider}")
    if model:
        console.print(f"[blue]Using model:[/blue] {model}")
    
    # TODO: Implement enrichment logic
    console.print("[yellow]Enrichment not yet implemented[/yellow]")


@app.command()
def analyze(
    input_file: Path = typer.Argument(..., help="Enriched data file to analyze"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    analysis_type: str = typer.Option("summary", "--type", help="Analysis type"),
) -> None:
    """Analyze enriched conversation data."""
    console.print(f"[bold green]Analyzing:[/bold green] {input_file}")
    
    if not input_file.exists():
        console.print(f"[bold red]Error:[/bold red] Input file does not exist: {input_file}")
        raise typer.Exit(1)
    
    # TODO: Implement analysis logic
    console.print("[yellow]Analysis not yet implemented[/yellow]")


@app.command()
def pipeline(
    source: Path = typer.Argument(..., help="Source path to process"),
    output_dir: Path = typer.Argument(..., help="Output directory"),
    platform: Optional[str] = typer.Option(None, "--platform", "-p", help="Platform type"),
    skip_redaction: bool = typer.Option(False, "--skip-redaction", help="Skip privacy redaction"),
    skip_enrichment: bool = typer.Option(False, "--skip-enrichment", help="Skip LLM enrichment"),
    provider: str = typer.Option("local", "--provider", help="LLM provider for enrichment"),
) -> None:
    """Run the complete ChatX pipeline (extract -> transform -> redact -> enrich -> analyze)."""
    console.print(f"[bold green]Running full pipeline on:[/bold green] {source}")
    
    if not source.exists():
        console.print(f"[bold red]Error:[/bold red] Source path does not exist: {source}")
        raise typer.Exit(1)
        
    output_dir.mkdir(parents=True, exist_ok=True)
    
    console.print(f"[blue]Output directory:[/blue] {output_dir}")
    console.print(f"[blue]LLM provider:[/blue] {provider}")
    
    if skip_redaction:
        console.print("[yellow]Skipping redaction step[/yellow]")
    if skip_enrichment:
        console.print("[yellow]Skipping enrichment step[/yellow]")
    
    # TODO: Implement full pipeline
    console.print("[yellow]Pipeline not yet implemented[/yellow]")


def cli() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    cli()