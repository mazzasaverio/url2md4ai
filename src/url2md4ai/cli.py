"""Command line interface for url2md4ai."""

import asyncio
import json

import click
from loguru import logger

from .config import Config
from .converter import ConversionResult, URLHasher, URLToMarkdownConverter


def print_result_info(result: ConversionResult, show_metadata: bool = False) -> None:
    """Print conversion result information."""
    if result.success:
        click.echo(f"✅ Successfully converted: {result.url}")
        click.echo(f"   📄 Title: {result.title}")
        click.echo(f"   📁 File: {result.filename}")
        if result.output_path:
            click.echo(f"   💾 Saved to: {result.output_path}")
        click.echo(f"   📊 Size: {result.file_size:,} characters")
        click.echo(f"   ⚡ Method: {result.extraction_method}")
        click.echo(f"   ⏱️  Time: {result.processing_time:.2f}s")

        if show_metadata and result.metadata:
            click.echo(f"   🔍 Metadata: {json.dumps(result.metadata, indent=2)}")
    else:
        click.echo(f"❌ Failed to convert: {result.url}")
        click.echo(f"   Error: {result.error}")


@click.group()
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.option(
    "--output-dir",
    type=click.Path(),
    help="Output directory for markdown files",
)
@click.option("--no-js", is_flag=True, help="Disable JavaScript rendering")
@click.option("--no-clean", is_flag=True, help="Disable content cleaning")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(
    ctx: click.Context,
    config_file: str | None,  # noqa: ARG001
    output_dir: str | None,
    no_js: bool,
    no_clean: bool,
    verbose: bool,
) -> None:
    """URL2MD4AI - Convert web pages to LLM-optimized markdown."""
    config = Config.from_env()

    # Apply CLI overrides
    if output_dir:
        config.output_dir = str(output_dir)
    if no_js:
        config.javascript_enabled = False
    if no_clean:
        config.clean_content = False
        config.llm_optimized = False

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
@click.option("--js/--no-js", default=None, help="Enable/disable JavaScript rendering")
@click.option("--clean/--raw", default=None, help="Enable/disable content cleaning")
@click.pass_context
def convert(
    ctx: click.Context,
    url: str,
    output: str | None,
    show_metadata: bool,
    show_content: bool,
    js: bool | None,
    clean: bool | None,
) -> None:
    """Convert a single URL to markdown."""

    async def async_convert() -> None:
        config = ctx.obj
        converter = URLToMarkdownConverter(config)

        # Determine settings
        use_js = js if js is not None else config.javascript_enabled
        use_traff = clean if clean is not None else config.use_trafilatura

        try:
            if show_metadata:
                click.echo("🔄 Converting URL to markdown...")

            result = await converter.convert_url(
                url,
                output_path=output,
                use_javascript=use_js,
                use_trafilatura=use_traff,
            )

            if result.success:
                if show_metadata:
                    click.echo("✅ Conversion successful!")
                    click.echo(f"📁 File: {result.output_path}")
                    click.echo(f"📊 Size: {result.file_size} chars")
                    click.echo(f"⏱️  Time: {result.processing_time:.2f}s")
                    click.echo(f"🔧 Method: {result.extraction_method}")

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
@click.option("--js/--no-js", default=None, help="Enable/disable JavaScript rendering")
@click.option("--clean/--raw", default=None, help="Enable/disable content cleaning")
@click.pass_context
def batch(
    ctx: click.Context,
    urls: list[str],
    concurrency: int,
    continue_on_error: bool,
    show_progress: bool,
    js: bool | None,
    clean: bool | None,
) -> None:
    """Convert multiple URLs to markdown with parallel processing."""

    async def async_batch() -> None:
        config = ctx.obj
        converter = URLToMarkdownConverter(config)

        # Determine settings
        use_js = js if js is not None else config.javascript_enabled
        use_traff = clean if clean is not None else config.use_trafilatura

        if show_progress:
            click.echo(f"🚀 Processing {len(urls)} URLs with {concurrency} workers...")

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrency)

        async def convert_single(url: str) -> object | None:
            async with semaphore:
                try:
                    return await converter.convert_url(
                        url,
                        use_javascript=use_js,
                        use_trafilatura=use_traff,
                    )
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
        successful = sum(1 for r in results if r and getattr(r, "success", False))
        failed = len(urls) - successful

        if show_progress:
            click.echo(f"✅ Successfully converted: {successful}")
            if failed > 0:
                click.echo(f"❌ Failed: {failed}")

        if failed > 0 and not continue_on_error:
            raise click.Abort from None

    return asyncio.run(async_batch())


@click.command()
@click.argument("url")
@click.option("--show-content", is_flag=True, help="Show extracted content")
@click.option("--show-metadata", is_flag=True, help="Show conversion metadata")
@click.option("--js/--no-js", default=None, help="Enable/disable JavaScript rendering")
@click.option("--clean/--raw", default=None, help="Enable/disable content cleaning")
@click.pass_context
def preview(
    ctx: click.Context,
    url: str,
    show_content: bool,
    show_metadata: bool,
    js: bool | None,
    clean: bool | None,
) -> None:
    """Preview URL conversion without saving to file."""

    async def async_preview() -> None:
        config = ctx.obj
        converter = URLToMarkdownConverter(config)

        # Determine settings
        use_js = js if js is not None else config.javascript_enabled
        use_traff = clean if clean is not None else config.use_trafilatura

        try:
            click.echo("🔍 Previewing URL conversion...")

            # Convert without saving (output_path=None)
            result = await converter.convert_url(
                url,
                output_path=None,
                use_javascript=use_js,
                use_trafilatura=use_traff,
            )

            if result.success:
                if show_metadata:
                    click.echo("📊 Metadata:")
                    click.echo(f"  Title: {result.title}")
                    click.echo(f"  Size: {result.file_size} chars")
                    click.echo(f"  Method: {result.extraction_method}")
                    click.echo(f"  Time: {result.processing_time:.2f}s")

                if show_content or not show_metadata:
                    click.echo("\n" + "=" * 50)
                    click.echo("PREVIEW CONTENT:")
                    click.echo("=" * 50)
                    content = (
                        result.markdown[:2000] + "..."
                        if len(result.markdown) > 2000
                        else result.markdown
                    )
                    click.echo(content)
            else:
                click.echo(f"❌ Preview failed: {result.error}")
                raise click.Abort from None

        except Exception as e:
            click.echo(f"❌ Preview failed: {e}")
            raise click.Abort from e

    return asyncio.run(async_preview())


@click.command()
@click.argument("url")
@click.option(
    "--method",
    type=click.Choice(["js", "nojs", "both"]),
    default="both",
    help="Test specific extraction method",
)
@click.pass_context
def test_extraction(ctx: click.Context, url: str, method: str) -> None:
    """Test different extraction methods on a URL."""

    async def async_test() -> None:
        config = ctx.obj
        converter = URLToMarkdownConverter(config)

        methods = []
        if method in ["js", "both"]:
            methods.append(("JavaScript", True))
        if method in ["nojs", "both"]:
            methods.append(("No-JavaScript", False))

        for method_name, use_js in methods:
            try:
                click.echo(f"\n🧪 Testing {method_name} method...")
                start_time = asyncio.get_event_loop().time()

                result = await converter.convert_url(
                    url,
                    output_path=None,
                    use_javascript=use_js,
                )

                end_time = asyncio.get_event_loop().time()
                processing_time = end_time - start_time

                if result.success:
                    click.echo(f"✅ {method_name}: {result.file_size} chars")
                    click.echo(f"⏱️  Time: {processing_time:.2f}s")
                    click.echo(f"🔧 Method: {result.extraction_method}")
                else:
                    click.echo(f"❌ {method_name} failed: {result.error}")

            except Exception as e:
                click.echo(f"❌ {method_name} failed: {e}")

    return asyncio.run(async_test())


@click.command()
@click.argument("url")
def hash_url(url: str) -> None:
    """Generate hash filename for a URL."""
    hash_value = URLHasher.generate_hash(url)
    filename = URLHasher.generate_filename(url)
    click.echo(f"URL: {url}")
    click.echo(f"Hash: {hash_value}")
    click.echo(f"Filename: {filename}")


@click.command()
@click.pass_context
def config_info(ctx: click.Context) -> None:
    """Show current configuration."""
    config = ctx.obj
    click.echo("🔧 Current Configuration:")
    click.echo(f"  Output Dir: {config.output_dir}")
    click.echo(f"  JavaScript: {config.javascript_enabled}")
    click.echo(f"  Clean Content: {config.clean_content}")
    click.echo(f"  LLM Optimized: {config.llm_optimized}")
    click.echo(f"  Use Trafilatura: {config.use_trafilatura}")
    click.echo(f"  Request Timeout: {config.timeout}s")
    click.echo(f"  User Agent: {config.user_agent}")


# Add commands to CLI group
cli.add_command(convert)
cli.add_command(batch)
cli.add_command(preview)
cli.add_command(test_extraction)
cli.add_command(hash_url, name="hash")
cli.add_command(config_info)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
