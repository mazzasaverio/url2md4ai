"""Command line interface for url2md4ai."""

import asyncio
import json
from typing import Any

import click
from loguru import logger

from .config import Config
from .converter import ConversionResult, URLHasher, URLToMarkdownConverter


def print_result_info(result: ConversionResult, show_metadata: bool = False) -> None:
    """Print conversion result information."""
    if result.success:
        click.echo(f"✅ Successfully converted: {result.url}")
        click.echo(f"   📁 File: {result.filename}")
        if result.output_path:
            click.echo(f"   💾 Saved to: {result.output_path}")
        click.echo(f"   📊 Size: {len(result.markdown):,} characters")

        if show_metadata:
            metadata: dict[str, Any] = {
                "file_size": len(result.markdown),
                "output_path": result.output_path,
            }
            click.echo(f"   🔍 Metadata: {json.dumps(metadata, indent=2)}")
    else:
        click.echo(f"❌ Failed to convert: {result.url}")
        click.echo(f"   Error: {result.error}")


@click.group()
@click.option(
    "--output-dir",
    type=click.Path(),
    help="Output directory for markdown files",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context 
def cli(
    ctx: click.Context, 
    output_dir: str | None,
    verbose: bool,
) -> None:
    """URL2MD4AI - Convert web pages to LLM-optimized markdown."""
    config = Config.from_env()

    # Apply CLI overrides
    if output_dir:
        config.output_dir = str(output_dir)

    if verbose:
        logger.remove()
        logger.add(
            lambda msg: click.echo(msg, err=True),
            level="DEBUG",
            format="<level>{level}</level> | {message}",
        )

    ctx.ensure_object(dict)
    ctx.obj = config


@click.command()
@click.argument("url")
@click.option("--output", "-o", help="Output filename (optional)")
@click.option("--show-metadata", is_flag=True, help="Show conversion metadata")
@click.option("--show-content", is_flag=True, help="Show extracted content")
@click.pass_context
def convert(
    ctx: click.Context,
    url: str,
    output: str | None,
    show_metadata: bool,
    show_content: bool,
) -> None:
    """Convert a single URL to markdown."""

    async def async_convert() -> None:
        config = ctx.obj
        converter = URLToMarkdownConverter(config)

        try:
            if show_metadata:
                click.echo("🔄 Converting URL to markdown...")

            result = await converter.convert_url(url, output_path=output)

            if result.success:
                if show_metadata:
                    click.echo("✅ Conversion successful!")
                    click.echo(f"📁 File: {result.output_path}")
                    click.echo(f"📊 Size: {len(result.markdown)} chars")

                if show_content and result.markdown:
                    click.echo("\n" + "=" * 50)
                    click.echo("EXTRACTED CONTENT:")
                    click.echo("=" * 50)
                    click.echo(result.markdown)

                if not show_metadata and not show_content:
                    click.echo(f"✅ Converted: {result.output_path}")
            else:
                click.echo(f"❌ Conversion failed: {result.error}")
                raise click.Abort from None

        except Exception as e:
            click.echo(f"❌ Conversion failed: {e}")
            raise click.Abort from e

    return asyncio.run(async_convert())


@click.command()
@click.argument("urls", nargs=-1, required=True)
@click.option("--concurrency", "-c", default=3, help="Number of parallel conversions")
@click.option(
    "--continue-on-error",
    is_flag=True,
    help="Continue processing even if some URLs fail",
)
@click.option("--show-progress", is_flag=True, help="Show progress information")
@click.pass_context
def batch(
    ctx: click.Context,
    urls: list[str],
    concurrency: int,
    continue_on_error: bool,
    show_progress: bool,
) -> None:
    """Convert multiple URLs to markdown with parallel processing."""

    async def async_batch() -> None:
        config = ctx.obj
        converter = URLToMarkdownConverter(config)

        if show_progress:
            click.echo(f"🚀 Processing {len(urls)} URLs with {concurrency} workers...")

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrency)

        async def convert_single(url: str) -> object | None:
            async with semaphore:
                try:
                    return await converter.convert_url(url)
                except Exception as e:
                    if continue_on_error:
                        if show_progress:
                            click.echo(f"⚠️  Failed {url}: {e}")
                        return None
                    raise

        # Process all URLs concurrently
        tasks = [convert_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Report results
        success_count = 0
        error_count = 0

        for result in results:
            if isinstance(result, Exception):
                error_count += 1
                if show_progress:
                    click.echo(f"❌ Error: {result}")
            elif result is None:
                error_count += 1
            elif isinstance(result, ConversionResult):
                if result.success:
                    success_count += 1
                    if show_progress:
                        click.echo(f"✅ Converted: {result.url}")
                else:
                    error_count += 1
                    if show_progress:
                        click.echo(f"❌ Failed: {result.url} - {result.error}")

        # Print summary
        total = len(urls)
        click.echo(
            f"\n📊 Summary: {success_count} succeeded, {error_count} failed"
            f" (total: {total})",
        )

        if error_count > 0 and not continue_on_error:
            raise click.Abort

    return asyncio.run(async_batch())


@click.command()
@click.argument("url")
@click.option("--show-content", is_flag=True, help="Show extracted content")
@click.option("--show-metadata", is_flag=True, help="Show conversion metadata")
@click.pass_context
def preview(
    ctx: click.Context,
    url: str,
    show_content: bool,
    show_metadata: bool,
) -> None:
    """Preview URL conversion without saving."""

    async def async_preview() -> None:
        config = ctx.obj
        converter = URLToMarkdownConverter(config)

        try:
            result = await converter.convert_url(url)

            if result.success:
                if show_metadata:
                    click.echo("✅ Preview successful!")
                    click.echo(f"📊 Size: {len(result.markdown)} chars")

                if show_content and result.markdown:
                    click.echo("\n" + "=" * 50)
                    click.echo("PREVIEW CONTENT:")
                    click.echo("=" * 50)
                    click.echo(result.markdown)

                if not show_metadata and not show_content:
                    click.echo("✅ Preview successful")
            else:
                click.echo(f"❌ Preview failed: {result.error}")
                raise click.Abort

        except Exception as e:
            click.echo(f"❌ Preview failed: {e}")
            raise click.Abort from e

    return asyncio.run(async_preview())


@click.command()
@click.argument("url")
def hash_url(url: str) -> None:
    """Generate hash-based filename for URL."""
    filename = URLHasher.generate_filename(url)
    click.echo(f"URL: {url}")
    click.echo(f"Hash: {URLHasher.generate_hash(url)}")
    click.echo(f"Filename: {filename}")


@click.command()
@click.pass_context
def config_info(ctx: click.Context) -> None:
    """Show current configuration."""
    config = ctx.obj
    click.echo("Current Configuration:")
    click.echo("-" * 20)
    for key, value in config.to_dict().items():
        click.echo(f"{key}: {value}")


def main() -> None:
    """Main entry point."""
    cli.add_command(convert)
    cli.add_command(batch)
    cli.add_command(preview)
    cli.add_command(hash_url)
    cli.add_command(config_info)
    cli()


if __name__ == "__main__":
    main()
