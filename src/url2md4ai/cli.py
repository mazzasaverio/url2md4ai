"""Command line interface for url2md4ai."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import click
from loguru import logger

from url2md4ai.config import Config
from url2md4ai.converter import ContentExtractor


def _setup_logging(debug: bool = False) -> None:
    """Set up logging configuration."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        level="DEBUG" if debug else "INFO",
    )


def _process_result(result: dict[str, Any] | None, json_output: bool = False) -> None:
    """Process and display the conversion result."""
    if not result:
        click.echo("❌ Error: Failed to get a result.", err=True)
        return

    if json_output:
        click.echo(json.dumps(result, indent=2))
    elif result.get("output_path"):
        click.echo(f"✅ Successfully saved markdown to: {result['output_path']}")
    elif result.get("markdown"):
        click.echo("✅ Successfully converted to markdown:")
        click.echo("\n" + result["markdown"])
    else:
        click.echo("❌ Error: No markdown content found.", err=True)


@click.group()
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
def cli(debug: bool) -> None:
    """Convert webpage content to clean markdown format."""
    _setup_logging(debug)


@cli.command()
@click.argument("url")
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory to save the markdown file",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output result as JSON",
)
@click.option(
    "--no-save",
    is_flag=True,
    help="Don't save to file, just print the markdown",
)
def convert(
    url: str,
    output_dir: Path | None,
    json_output: bool,
    no_save: bool,
) -> None:
    """Convert a webpage to markdown.

    URL: The URL of the webpage to convert
    """
    config = Config()
    if output_dir:
        config.output_dir = str(output_dir)

    extractor = ContentExtractor(config)
    result = asyncio.run(extractor.extract_markdown(url, save_to_file=not no_save))
    _process_result(result, json_output)


@cli.command()
@click.argument("url")
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output result as JSON",
)
def extract_html(url: str, json_output: bool) -> None:
    """Extract raw HTML from a webpage.

    URL: The URL of the webpage to extract HTML from
    """
    extractor = ContentExtractor()
    result = extractor.extract_html_sync(url)
    if result:
        if json_output:
            click.echo(json.dumps({"url": url, "html_content": result}))
        else:
            click.echo(result)
    else:
        click.echo("❌ Error: Failed to extract HTML.", err=True)


@cli.command()
@click.argument(
    "html_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory to save the markdown file",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output result as JSON",
)
@click.option(
    "--no-save",
    is_flag=True,
    help="Don't save to file, just print the markdown",
)
@click.option(
    "--url",
    help="Original URL of the HTML content (optional)",
)
def convert_html(
    html_file: Path,
    output_dir: Path | None,
    json_output: bool,
    no_save: bool,
    url: str | None,
) -> None:
    """Convert a local HTML file to markdown.

    HTML_FILE: Path to the HTML file to convert
    """
    config = Config()
    if output_dir:
        config.output_dir = str(output_dir)

    try:
        with open(html_file, encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        logger.error(f"Failed to read HTML file: {e}")
        sys.exit(1)

    url = url or f"file://{html_file.absolute()}"
    extractor = ContentExtractor(config)
    result = extractor.extract_markdown_sync(
        url,
        html_content=html_content,
        save_to_file=not no_save,
    )
    _process_result(result, json_output)


if __name__ == "__main__":
    cli()
