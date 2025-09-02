"""Main CLI entry point for ChatX."""

import logging
from pathlib import Path
from datetime import datetime

import typer
from rich.console import Console

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
    config: str = typer.Option("", "--config", "-c", help="Configuration file path"),
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

    # TODO: Fix config parameter bug - currently prints Option object instead of value
    # if config:
    #     console.print(f"Using config: {config}")


@app.command()
def extract(
    source: Path = typer.Argument(..., help="Source path (e.g., iMessage chat.db)"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output directory"),
    platform: str | None = typer.Option(None, "--platform", "-p", help="Platform type"),
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
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file path"),
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
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file path"),
    policy: Path | None = typer.Option(None, "--policy", help="Privacy policy file"),
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
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file path"),
    provider: str = typer.Option(
        "local", "--provider", help="LLM provider (local, openai, anthropic)"
    ),
    model: str | None = typer.Option(None, "--model", help="Specific model to use"),
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
    output_dir: Path | None = typer.Option(None, "--output", "-o", help="Output directory"),
    analysis_type: str = typer.Option("summary", "--type", help="Analysis type"),
) -> None:
    """Analyze enriched conversation data."""
    console.print(f"[bold green]Analyzing:[/bold green] {input_file}")

    if not input_file.exists():
        console.print(f"[bold red]Error:[/bold red] Input file does not exist: {input_file}")
        raise typer.Exit(1)

    # TODO: Implement analysis logic
    console.print("[yellow]Analysis not yet implemented[/yellow]")


# iMessage Commands
imessage_app = typer.Typer(help="iMessage extraction commands")
app.add_typer(imessage_app, name="imessage")


@imessage_app.command("pull")
def imessage_pull(
    contact: str = typer.Option(..., "--contact", help="Contact identifier (phone, email, or name)"),
    db: Path = typer.Option(
        Path.home() / "Library/Messages/chat.db",
        "--db",
        help="Path to Messages database"
    ),
    from_backup: Path | None = typer.Option(
        None,
        "--from-backup",
        help="Path to iPhone backup directory (Finder/iTunes MobileSync)"
    ),
    backup_password: str | None = typer.Option(
        None,
        "--backup-password",
        help="Password for encrypted backups (input is not echoed)",
        prompt=False,
        hide_input=True,
    ),
    out: Path = typer.Option(Path("./out"), "--out", help="Output directory"),
    include_attachments: bool = typer.Option(False, "--include-attachments", help="Extract attachment metadata"),
    copy_binaries: bool = typer.Option(False, "--copy-binaries", help="Copy attachment files to output"),
    transcribe_audio: str = typer.Option(
        "off",
        "--transcribe-audio",
        help="Audio transcription mode (local|off). Example: --transcribe-audio local",
    ),
    report_missing: bool = typer.Option(True, "--report-missing/--no-report-missing", help="Generate missing attachments report"),
) -> None:
    """Extract iMessage conversations for a contact."""
    from chatx.imessage import extract_messages
    from chatx.imessage.backup import ensure_backup_accessible, stage_sms_db
    
    console.print(f"[bold green]Extracting iMessage conversations for:[/bold green] {contact}")
    if from_backup:
        console.print(f"[blue]Backup dir:[/blue] {from_backup}")
    else:
        console.print(f"[blue]Database:[/blue] {db}")
    console.print(f"[blue]Output:[/blue] {out}")
    
    # Preflight
    staged_db_path: Path | None = None
    if from_backup:
        if not from_backup.exists() or not from_backup.is_dir():
            console.print(f"[bold red]Error:[/bold red] Backup directory not found: {from_backup}")
            raise typer.Exit(1)
        try:
            ensure_backup_accessible(from_backup, backup_password)
        except Exception as e:
            console.print(f"[bold red]Backup validation failed:[/bold red] {e}")
            raise typer.Exit(1)
    else:
        if not db.exists():
            console.print(f"[bold red]Error:[/bold red] Messages database not found: {db}")
            console.print("[yellow]Tip:[/yellow] Grant Full Disk Access to your terminal in System Settings > Privacy & Security")
            raise typer.Exit(1)
    
    # Create output directory
    out.mkdir(parents=True, exist_ok=True)
    
    try:
        started_at = datetime.now()
        # Stage DB if reading from backup, else use provided db
        if from_backup:
            with stage_sms_db(from_backup) as staged_db:
                staged_db_path = staged_db
                messages = list(extract_messages(
                    db_path=staged_db,
                    contact=contact,
                    include_attachments=include_attachments,
                    copy_binaries=copy_binaries,
                    transcribe_audio=transcribe_audio,
                    out_dir=out,
                ))
        else:
            messages = list(extract_messages(
                db_path=db,
                contact=contact,
                include_attachments=include_attachments,
                copy_binaries=copy_binaries,
                transcribe_audio=transcribe_audio,
                out_dir=out,
            ))
        finished_at = datetime.now()
        
        message_count = len(messages)
        console.print(f"[bold green]Extracted {message_count} messages[/bold green]")
        
        if message_count > 0:
            # Write JSON output with schema validation
            from chatx.utils.json_output import write_messages_with_validation
            
            output_file = out / f"messages_{contact.replace('@', '_at_').replace('+', '_plus_')}.json"
            write_messages_with_validation(messages, output_file)
            console.print(f"[bold green]Messages written to:[/bold green] {output_file}")
            
            # Report transcription statistics if audio transcription was enabled
            if transcribe_audio != "off" and include_attachments:
                from chatx.imessage.transcribe import collect_transcription_stats
                
                stats = collect_transcription_stats(messages)
                total_transcripts = stats["total_transcripts"]
                
                if total_transcripts > 0:
                    console.print(f"[blue]Audio transcription:[/blue] {total_transcripts} voice message(s) transcribed")
                    
                    # Show breakdown by confidence if available
                    confidence_counts = stats["by_confidence"]
                    confidence_breakdown = []
                    for level in ["high", "medium", "low"]:
                        count = confidence_counts.get(level, 0)
                        if count > 0:
                            confidence_breakdown.append(f"{count} {level}")
                    
                    if confidence_breakdown:
                        console.print(f"[blue]Confidence levels:[/blue] {', '.join(confidence_breakdown)}")
                    
                    # Show engines used
                    engines = stats["by_engine"]
                    if engines:
                        engine_list = [f"{count} {engine}" for engine, count in engines.items()]
                        console.print(f"[blue]Engines:[/blue] {', '.join(engine_list)}")
                elif transcribe_audio == "local":
                    console.print("[yellow]No voice messages found to transcribe[/yellow]")
        
        # Generate missing attachments report if requested and attachments enabled
        if report_missing and include_attachments:
            from chatx.imessage.db import copy_db_for_readonly, open_ro
            from chatx.imessage.report import generate_missing_attachments_report
            
            console.print("[blue]Checking for missing attachments...[/blue]")
            
            with copy_db_for_readonly(db) as temp_db:
                conn = open_ro(temp_db)
                try:
                    missing_counts = generate_missing_attachments_report(conn, out, contact)
                    total_missing = sum(missing_counts.values())
                    
                    if total_missing > 0:
                        console.print(f"[yellow]Found {total_missing} missing attachment(s) across {len(missing_counts)} conversation(s)[/yellow]")
                        console.print(f"[yellow]Report written to:[/yellow] {out / 'missing_attachments_report.json'}")
                    else:
                        console.print("[green]All attachment files found on disk[/green]")
                finally:
                    conn.close()

        # Compute and emit run report + perf soft floor warning
        try:
            from chatx.utils.run_report import write_extract_run_report
            # Compute simple counters
            attachments_total = sum(len(m.attachments) for m in messages)
            elapsed = max((finished_at - started_at).total_seconds(), 0.0)
            rate = (len(messages) / elapsed * 60.0) if elapsed > 0 else 0.0

            # Artifacts
            artifacts = [str(out / f"messages_{contact.replace('@', '_at_').replace('+', '_plus_')}.json")]
            missing_path = out / 'missing_attachments_report.json'
            if missing_path.exists():
                artifacts.append(str(missing_path))

            # Optional soft floor warning via env var
            import os
            warn_msgs = []
            soft_floor = os.environ.get("CHATX_SOFT_FLOOR_MSGS_MIN")
            if soft_floor:
                try:
                    floor = float(soft_floor)
                    if rate < floor:
                        warn = f"Throughput below soft floor: {rate:.0f} < {floor:.0f} msgs/min"
                        console.print(f"[yellow]{warn}[/yellow]")
                        warn_msgs.append(warn)
                except ValueError:
                    # Ignore invalid value
                    pass

            report_path = write_extract_run_report(
                out_dir=out,
                started_at=started_at,
                finished_at=finished_at,
                messages_total=len(messages),
                attachments_total=attachments_total,
                throughput_msgs_min=rate,
                artifacts=artifacts,
                warnings=warn_msgs,
            )
            console.print(f"[blue]Run report written to:[/blue] {report_path}")
        except Exception:
            # Do not fail extraction if metrics writing fails
            pass
        
    except Exception as e:
        console.print(f"[bold red]Error during extraction:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def pipeline(
    source: Path = typer.Argument(..., help="Source path to process"),
    output_dir: Path = typer.Argument(..., help="Output directory"),
    platform: str | None = typer.Option(None, "--platform", "-p", help="Platform type"),
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

# Instagram Commands
instagram_app = typer.Typer(help="Instagram extraction commands")
app.add_typer(instagram_app, name="instagram")


@instagram_app.command("pull")
def instagram_pull(
    zip: Path = typer.Option(..., "--zip", help="Path to Instagram official data ZIP"),
    out: Path = typer.Option(Path("./out"), "--out", help="Output directory"),
    user: str = typer.Option(..., "--user", help="Your Instagram display name (filters threads; also marks is_me)"),
    author_only: list[str] = typer.Option([], "--author-only", help="Include only messages authored by these usernames (repeatable)"),
) -> None:
    """Extract Instagram DMs from the official data ZIP export."""
    from chatx.instagram.extract import extract_messages_from_zip
    from chatx.utils.json_output import write_messages_with_validation

    console.print(f"[bold green]Extracting Instagram from ZIP:[/bold green] {zip}")
    console.print(f"[blue]Output:[/blue] {out}")

    if not zip.exists():
        console.print(f"[bold red]Error:[/bold red] ZIP file not found: {zip}")
        raise typer.Exit(1)

    out.mkdir(parents=True, exist_ok=True)

    try:
        messages = extract_messages_from_zip(
            zip,
            include_threads_with=[user],
            authors_only=author_only or None,
            me_username=user,
        )
        output_file = out / "instagram_messages.json"
        write_messages_with_validation(messages, output_file)
        console.print(f"[bold green]Messages written to:[/bold green] {output_file}")
    except ValueError as ve:
        console.print(f"[bold red]ZIP validation error:[/bold red] {ve}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error during extraction:[/bold red] {e}")
        raise typer.Exit(1)
