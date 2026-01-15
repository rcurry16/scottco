"""CLI interface for job evaluation tools."""
import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from .comparator import PositionComparator
from .gauge import RevaluationGauge
from .classifier import FirstPassClassifier
from .pdf_processor import PDFProcessor

app = typer.Typer(
    name="job-eval",
    help="Job classification tool for analyzing position descriptions",
    add_completion=False,
)
console = Console()


@app.command()
def compare(
    old_pdf: Path = typer.Argument(
        ...,
        help="Path to original position description PDF",
        exists=True,
        dir_okay=False,
    ),
    new_pdf: Path = typer.Argument(
        ...,
        help="Path to updated position description PDF",
        exists=True,
        dir_okay=False,
    ),
    output: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Save results to JSON file",
    ),
    json_only: bool = typer.Option(
        False,
        "--json",
        help="Output only JSON (no formatted display)",
    ),
    with_gauge: bool = typer.Option(
        False,
        "--with-gauge",
        "-g",
        help="Also run revaluation gauge (Tool 1.2)",
    ),
    with_classify: bool = typer.Option(
        False,
        "--with-classify",
        "-c",
        help="Also run classifier after gauge (Tool 1.3) - implies --with-gauge",
    ),
):
    """
    Compare two position description PDFs and identify changes.

    This is Tool 1.1: Position Description Side by Side
    """
    try:
        # Initialize comparator
        comparator = PositionComparator()

        # Perform comparison
        with console.status("[bold blue]Comparing position descriptions..."):
            result = comparator.compare(old_pdf, new_pdf)

        # Output results
        if json_only:
            console.print_json(result.model_dump_json())
        else:
            _display_comparison_results(result)

        # Save to file if requested
        if output:
            with open(output, "w") as f:
                json.dump(result.model_dump(), f, indent=2)
            console.print(f"\n[green]✓[/green] Saved results to {output}")

        # Run gauge if requested (or implied by with_classify)
        if with_gauge or with_classify:
            console.print("\n" + "=" * 80)
            console.print("[bold cyan]Running Revaluation Gauge (Tool 1.2)...[/bold cyan]")
            console.print("=" * 80 + "\n")

            # Save comparison to temp file if not already saved
            gauge_input = output if output else Path(".temp_comparison.json")
            if not output:
                with open(gauge_input, "w") as f:
                    json.dump(result.model_dump(), f, indent=2)

            try:
                gauge = RevaluationGauge()
                gauge_recommendation = gauge.assess(gauge_input)
                _display_gauge_results(gauge_recommendation)

                # Save gauge results for classifier if needed
                gauge_output = None
                if with_classify:
                    gauge_output = Path(".temp_gauge.json")
                    with open(gauge_output, "w") as f:
                        json.dump(gauge_recommendation.model_dump(), f, indent=2)

                # Run classifier if requested
                if with_classify:
                    console.print("\n" + "=" * 80)
                    console.print("[bold cyan]Running First Pass Classifier (Tool 1.3)...[/bold cyan]")
                    console.print("=" * 80 + "\n")

                    try:
                        classifier = FirstPassClassifier()
                        classification = classifier.classify(
                            new_pdf,
                            comparison_data=result.model_dump(),
                            gauge_data=gauge_recommendation.model_dump()
                        )
                        _display_classification_results(classification)

                        # Clean up temp gauge file
                        if gauge_output and gauge_output.exists():
                            gauge_output.unlink()

                    except Exception as e:
                        console.print(f"[red]Classifier error:[/red] {e}", stderr=True)
                        if gauge_output and gauge_output.exists():
                            gauge_output.unlink()

                # Clean up temp comparison file
                if not output and gauge_input.exists():
                    gauge_input.unlink()

            except Exception as e:
                console.print(f"[red]Gauge error:[/red] {e}", stderr=True)
                if not output and gauge_input.exists():
                    gauge_input.unlink()

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}", stderr=True)
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}", stderr=True)
        console.print("\n[yellow]Hint:[/yellow] Set ANTHROPIC_API_KEY in .env file")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}", stderr=True)
        raise typer.Exit(1)


@app.command()
def gauge(
    comparison_json: Path = typer.Argument(
        ...,
        help="Path to comparison JSON from 'compare' command",
        exists=True,
        dir_okay=False,
    ),
    json_only: bool = typer.Option(
        False,
        "--json",
        help="Output only JSON (no formatted display)",
    ),
):
    """
    Assess if changes warrant re-evaluation (Tool 1.2: Revaluation Gauge).

    Takes comparison JSON from Tool 1.1 and determines if changes are
    material enough to warrant formal position re-evaluation.
    """
    try:
        gauge_tool = RevaluationGauge()

        with console.status("[bold blue]Assessing change materiality..."):
            recommendation = gauge_tool.assess(comparison_json)

        if json_only:
            console.print_json(recommendation.model_dump_json())
        else:
            _display_gauge_results(recommendation)

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}", stderr=True)
        console.print("\n[yellow]Hint:[/yellow] Run comparison first: job-eval compare old.pdf new.pdf -o results.json")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}", stderr=True)
        console.print("\n[yellow]Hint:[/yellow] Set ANTHROPIC_API_KEY in .env file")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}", stderr=True)
        raise typer.Exit(1)


@app.command()
def extract_text(
    pdf: Path = typer.Argument(
        ...,
        help="Path to PDF file",
        exists=True,
        dir_okay=False,
    ),
):
    """Extract text from a position description PDF."""
    try:
        processor = PDFProcessor(pdf)
        text = processor.extract_text()
        console.print(text)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", stderr=True)
        raise typer.Exit(1)


@app.command()
def info(
    pdf: Path = typer.Argument(
        ...,
        help="Path to PDF file",
        exists=True,
        dir_okay=False,
    ),
):
    """Show information about a position description PDF."""
    try:
        processor = PDFProcessor(pdf)
        metadata = processor.extract_metadata()
        page_count = processor.get_page_count()

        table = Table(title=f"PDF Information: {pdf.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("File", str(pdf))
        table.add_row("Pages", str(page_count))

        for key, value in metadata.items():
            if value:
                table.add_row(key.title(), str(value))

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", stderr=True)
        raise typer.Exit(1)


@app.command()
def init():
    """Initialize configuration (create .env template)."""
    env_path = Path(".env")

    if env_path.exists():
        overwrite = typer.confirm(".env file exists. Overwrite?")
        if not overwrite:
            console.print("[yellow]Cancelled[/yellow]")
            return

    with open(env_path, "w") as f:
        f.write("# Anthropic API Key for Claude\n")
        f.write("ANTHROPIC_API_KEY=your_api_key_here\n")

    console.print(f"[green]✓[/green] Created {env_path}")
    console.print("\n[yellow]Next steps:[/yellow]")
    console.print("1. Get API key from: https://console.anthropic.com/")
    console.print(f"2. Edit {env_path} and add your key")
    console.print("3. Run: job-eval compare <old_pdf> <new_pdf>")


def _display_comparison_results(result):
    """Display comparison results in formatted output."""
    # Summary
    console.print(Panel(
        result.summary,
        title="[bold]Comparison Summary[/bold]",
        border_style="blue"
    ))

    # Overall significance
    significance_color = {
        "minor": "green",
        "moderate": "yellow",
        "major": "red"
    }.get(result.overall_significance, "white")

    console.print(f"\n[bold]Overall Significance:[/bold] [{significance_color}]{result.overall_significance.upper()}[/{significance_color}]")

    # Changes by section
    if result.changes_by_section:
        console.print("\n[bold cyan]═══ Changes by Section ═══[/bold cyan]\n")

        for section, changes in result.changes_by_section.items():
            console.print(f"[bold]{section}[/bold]")

            if changes.additions:
                console.print("  [green]+ Additions:[/green]")
                for item in changes.additions:
                    console.print(f"    • {item}")

            if changes.deletions:
                console.print("  [red]- Deletions:[/red]")
                for item in changes.deletions:
                    console.print(f"    • {item}")

            if changes.modifications:
                console.print("  [yellow]~ Modifications:[/yellow]")
                for item in changes.modifications:
                    console.print(f"    • {item}")

            console.print()

    # Classification-relevant changes
    if result.classification_relevant_changes:
        console.print("[bold cyan]═══ Classification Impact ═══[/bold cyan]\n")

        category_names = {
            "accountabilities": "Accountabilities",
            "knowledge_experience": "Knowledge & Experience",
            "decision_making": "Decision Making",
            "customer_relationship": "Customer & Relationship Management",
            "leadership": "Leadership",
            "project_management": "Project Management"
        }

        for category, changes in result.classification_relevant_changes.items():
            if changes:
                display_name = category_names.get(category, category.replace("_", " ").title())
                console.print(f"[bold]{display_name}:[/bold]")
                for change in changes:
                    console.print(f"  • {change}")
                console.print()


def _display_gauge_results(recommendation):
    """Display revaluation gauge results in formatted output."""
    # Decision panel
    decision_color = "green" if recommendation.should_reevaluate else "yellow"
    decision_text = "YES - Re-evaluation Recommended" if recommendation.should_reevaluate else "NO - Re-evaluation Not Needed"

    console.print(Panel(
        f"[bold {decision_color}]{decision_text}[/bold {decision_color}]\n\n"
        f"[bold]Current Level:[/bold] {recommendation.current_level}\n"
        f"[bold]Expected New Range:[/bold] {recommendation.likely_new_level_range}\n"
        f"[bold]Confidence:[/bold] {recommendation.confidence}%\n\n"
        f"{recommendation.rationale}",
        title="[bold]Revaluation Recommendation[/bold]",
        border_style=decision_color
    ))

    # Risk assessment
    risk_color = {"low": "green", "medium": "yellow", "high": "red"}.get(
        recommendation.risk_assessment, "white"
    )
    console.print(f"\n[bold]Risk Assessment:[/bold] [{risk_color}]{recommendation.risk_assessment.upper()}[/{risk_color}]")

    # Categories affected
    if recommendation.categories_affected:
        console.print("\n[bold cyan]Classification Categories Affected:[/bold cyan]")
        for category in recommendation.categories_affected:
            console.print(f"  • {category}")

    # Key factors
    if recommendation.key_factors:
        console.print("\n[bold cyan]Key Factors:[/bold cyan]")
        for factor in recommendation.key_factors:
            console.print(f"  • {factor}")


@app.command()
def classify(
    pdf: Path = typer.Argument(
        ...,
        help="Path to position description PDF",
        exists=True,
        dir_okay=False,
    ),
    from_results: Path = typer.Option(
        None,
        "--from-results",
        "-r",
        help="Path to gauge/comparison JSON for context-aware classification",
        exists=True,
    ),
    output: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Save results to JSON file",
    ),
    json_only: bool = typer.Option(
        False,
        "--json",
        help="Output only JSON (no formatted display)",
    ),
):
    """
    Classify a position description (Tool 1.3: First Pass Classifier).

    Can work standalone or with context from Tools 1.1/1.2 for better accuracy.

    Examples:
      # Standalone classification
      job-eval classify position.pdf

      # With context from gauge results (recommended)
      job-eval classify position.pdf --from-results gauge_results.json

      # Or use integrated workflow
      job-eval compare old.pdf new.pdf -g --with-classify
    """
    try:
        classifier = FirstPassClassifier()

        # Load context if provided
        comparison_data = None
        gauge_data = None

        if from_results:
            with open(from_results) as f:
                results = json.load(f)

            # Detect if this is gauge or comparison data
            if "should_reevaluate" in results:
                # This is gauge data
                gauge_data = results
                console.print("[cyan]Using revaluation gauge context[/cyan]")
            elif "classification_relevant_changes" in results:
                # This is comparison data
                comparison_data = results
                console.print("[cyan]Using comparison context[/cyan]")
            else:
                console.print("[yellow]Warning: Unrecognized context format, proceeding standalone[/yellow]")

        # Classify position
        with console.status("[bold blue]Analyzing position..."):
            recommendation = classifier.classify(pdf, comparison_data, gauge_data)

        # Output results
        if json_only:
            console.print_json(recommendation.model_dump_json())
        else:
            _display_classification_results(recommendation)

        # Save to file if requested
        if output:
            with open(output, "w") as f:
                json.dump(recommendation.model_dump(), f, indent=2)
            console.print(f"\n[green]✓[/green] Saved results to {output}")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}", stderr=True)
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}", stderr=True)
        console.print("\n[yellow]Hint:[/yellow] Set ANTHROPIC_API_KEY in .env file")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}", stderr=True)
        raise typer.Exit(1)


def _display_classification_results(recommendation):
    """Display classification results in formatted output."""
    # Main recommendation panel
    context_note = ""
    if recommendation.change_context_used:
        context_note = f"\n[dim](Analysis used change context from previous tools)[/dim]"
    else:
        context_note = f"\n[dim](Standalone analysis - no change context)[/dim]"

    level_change_note = ""
    if recommendation.previous_level:
        if recommendation.previous_level == recommendation.recommended_level:
            level_change_note = f"\n[bold]Previous Level:[/bold] {recommendation.previous_level} [green]→ No change[/green]"
        else:
            level_change_note = f"\n[bold]Previous Level:[/bold] {recommendation.previous_level} → [cyan]{recommendation.recommended_level}[/cyan]"

    console.print(Panel(
        f"[bold cyan]Recommended Level: {recommendation.recommended_level}[/bold cyan]\n"
        f"[bold]Position:[/bold] {recommendation.position_title}\n"
        f"[bold]Confidence:[/bold] {recommendation.confidence}%"
        f"{level_change_note}"
        f"{context_note}\n\n"
        f"{recommendation.rationale}",
        title="[bold]Classification Recommendation[/bold]",
        border_style="cyan"
    ))

    # Category analysis table
    if recommendation.category_analysis:
        console.print("\n[bold cyan]═══ Category Analysis ═══[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Category", style="cyan", width=25)
        table.add_column("Analysis", style="white", width=55)

        category_names = {
            "accountabilities": "Accountabilities",
            "knowledge_experience": "Knowledge & Experience",
            "decision_making": "Decision Making",
            "customer_relationship": "Customer & Relationship",
            "leadership": "Leadership",
            "project_management": "Project Management"
        }

        for cat_key, analysis in recommendation.category_analysis.items():
            display_name = category_names.get(cat_key, cat_key.replace("_", " ").title())
            table.add_row(display_name, analysis)

        console.print(table)

    # Supporting evidence
    if recommendation.supporting_evidence:
        console.print("\n[bold cyan]Supporting Evidence:[/bold cyan]")
        for evidence in recommendation.supporting_evidence:
            console.print(f"  • {evidence}")

    # Alternative levels
    if recommendation.alternative_levels:
        console.print("\n[bold cyan]Alternative Levels to Consider:[/bold cyan]")
        for level in recommendation.alternative_levels:
            console.print(f"  • {level}")

    # Comparable positions
    if recommendation.comparable_positions:
        console.print("\n[bold cyan]Comparable Positions:[/bold cyan]")
        for position in recommendation.comparable_positions:
            console.print(f"  • {position}")


@app.command()
def version():
    """Show version information."""
    from . import __version__
    console.print(f"job-eval version {__version__}")


@app.command()
def serve(
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        "-h",
        help="Host to bind to (default: 0.0.0.0)",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Port to listen on (default: 8000)",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        "-r",
        help="Enable auto-reload on code changes",
    ),
):
    """Start the web interface server."""
    console.print(f"[bold green]Starting Job Evaluation Tool server...[/bold green]")
    console.print(f"[cyan]Access at: http://localhost:{port}[/cyan]")
    console.print("[yellow]Press Ctrl+C to stop[/yellow]\n")

    from .server import run_server
    run_server(host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
