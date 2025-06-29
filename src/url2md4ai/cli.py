"""Command line interface for url2md4ai."""

import asyncio
from typing import List
import json

import click

from .config import Config
from .converter import URLToMarkdownConverter, URLHasher
from .utils import get_logger, setup_logger


def print_result_info(result, show_metadata: bool = False):
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
@click.option('--config-file', help='Path to configuration file')
@click.option('--output-dir', help='Output directory')
@click.option('--no-js', is_flag=True, help='Disable JavaScript rendering globally')
@click.option('--no-clean', is_flag=True, help='Disable content cleaning globally')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config_file, output_dir, no_js, no_clean, verbose):
    """URL2MD4AI - Convert web pages to LLM-optimized markdown."""
    config = Config.from_env()
    
    # Override config with CLI options
    if output_dir:
        config.output_dir = output_dir
    if no_js:
        config.javascript_enabled = False
    if no_clean:
        config.clean_content = False
        config.llm_optimized = False
    if verbose:
        config.log_level = "DEBUG"
    
    ctx.ensure_object(dict)
    ctx.obj = config


@click.command()
@click.argument('url')
@click.option('--output', '-o', help='Output file path')
@click.option('--output-dir', help='Output directory (overrides config)')
@click.option('--no-js', is_flag=True, help='Disable JavaScript rendering for this URL')
@click.option('--force-js', is_flag=True, help='Force JavaScript rendering for this URL')
@click.option('--no-clean', is_flag=True, help='Disable content cleaning for this URL')
@click.option('--raw', is_flag=True, help='Raw extraction without LLM optimization')
@click.option('--show-metadata', is_flag=True, help='Display conversion metadata')
@click.option('--preview', is_flag=True, help='Preview without saving to file')
@click.pass_context
def convert_cmd(ctx, url: str, output: str, output_dir: str, no_js: bool, force_js: bool, 
                no_clean: bool, raw: bool, show_metadata: bool, preview: bool):
    """Convert a single URL to markdown."""
    
    async def async_convert():
        config = ctx.obj
        
        # Override config for this conversion
        if output_dir:
            config.output_dir = output_dir
        if no_clean or raw:
            config.clean_content = False
            config.llm_optimized = False
        if raw:
            config.use_trafilatura = False
        
        # Determine JavaScript usage
        use_javascript = None
        if force_js:
            use_javascript = True
        elif no_js:
            use_javascript = False
        
        converter = URLToMarkdownConverter(config)
        
        # Convert without saving if preview mode
        output_path = None if preview else output
        
        try:
            result = await converter.convert_url(
                url,
                output_path=output_path,
                use_javascript=use_javascript,
                use_trafilatura=not raw
            )
            
            print_result_info(result, show_metadata)
            
            if preview and result.success:
                click.echo("\n📄 Content Preview (first 500 chars):")
                click.echo("─" * 60)
                preview_text = result.markdown[:500]
                if len(result.markdown) > 500:
                    preview_text += "..."
                click.echo(preview_text)
                click.echo("─" * 60)
            
        except Exception as e:
            click.echo(f"❌ Conversion failed: {e}")
            raise click.Abort()
    
    return asyncio.run(async_convert())


@click.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--output-dir', help='Output directory (overrides config)')
@click.option('--concurrency', '-c', default=3, help='Number of concurrent conversions')
@click.option('--no-js', is_flag=True, help='Disable JavaScript rendering for all URLs')
@click.option('--force-js', is_flag=True, help='Force JavaScript rendering for all URLs')
@click.option('--no-clean', is_flag=True, help='Disable content cleaning for all URLs')
@click.option('--raw', is_flag=True, help='Raw extraction without LLM optimization')
@click.option('--show-metadata', is_flag=True, help='Display conversion metadata')
@click.option('--continue-on-error', is_flag=True, help='Continue processing on individual failures')
@click.pass_context
def batch_cmd(ctx, urls: List[str], output_dir: str, concurrency: int, no_js: bool, 
              force_js: bool, no_clean: bool, raw: bool, show_metadata: bool, continue_on_error: bool):
    """Convert multiple URLs to markdown with parallel processing."""
    
    async def async_batch():
        config = ctx.obj
        
        # Override config for batch conversion
        if output_dir:
            config.output_dir = output_dir
        if no_clean or raw:
            config.clean_content = False
            config.llm_optimized = False
        if raw:
            config.use_trafilatura = False
        
        # Determine JavaScript usage
        use_javascript = None
        if force_js:
            use_javascript = True
        elif no_js:
            use_javascript = False
        
        converter = URLToMarkdownConverter(config)
        
        click.echo(f"🚀 Starting batch conversion of {len(urls)} URLs with {concurrency} concurrent workers")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrency)
        
        async def convert_single(url: str):
            async with semaphore:
                try:
                    result = await converter.convert_url(
                        url,
                        use_javascript=use_javascript,
                        use_trafilatura=not raw
                    )
                    return result
                except Exception as e:
                    if continue_on_error:
                        click.echo(f"⚠️  Error processing {url}: {e}")
                        return None
                    raise
        
        # Process all URLs concurrently
        tasks = [convert_single(url) for url in urls]
        
        if continue_on_error:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            results = await asyncio.gather(*tasks)
        
        # Display results
        successful = 0
        failed = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                click.echo(f"❌ {urls[i]}: {result}")
                failed += 1
            elif result is None:
                # None returned from convert_single when continue_on_error is True
                failed += 1
            elif hasattr(result, 'success') and result.success:
                # Valid ConversionResult object
                if show_metadata:
                    print_result_info(result, True)
                else:
                    click.echo(f"✅ {result.filename} <- {result.url}")
                successful += 1
            else:
                click.echo(f"❌ {urls[i]}: {getattr(result, 'error', 'Unknown error')}")
                failed += 1
        
        click.echo(f"\n📊 Batch conversion completed:")
        click.echo(f"   ✅ Successful: {successful}")
        click.echo(f"   ❌ Failed: {failed}")
        click.echo(f"   📁 Output directory: {config.output_dir}")
    
    return asyncio.run(async_batch())


@click.command()
@click.argument('url')
@click.option('--show-content', is_flag=True, help='Show content preview')
@click.pass_context  
def preview_cmd(ctx, url: str, show_content: bool):
    """Preview URL conversion without saving to file."""
    
    async def async_preview():
        config = ctx.obj
        converter = URLToMarkdownConverter(config)
        
        try:
            result = await converter.convert_url(url, output_path=None)
            
            if result.success:
                click.echo(f"✅ Preview for: {result.url}")
                click.echo(f"   📄 Title: {result.title}")
                click.echo(f"   📊 Size: {result.file_size:,} characters")
                click.echo(f"   ⚡ Method: {result.extraction_method}")
                click.echo(f"   📁 Would save as: {result.filename}")
                
                if show_content:
                    click.echo("\n📄 Content Preview:")
                    click.echo("─" * 60)
                    preview_text = result.markdown[:1000]
                    if len(result.markdown) > 1000:
                        preview_text += f"\n... ({len(result.markdown) - 1000} more characters)"
                    click.echo(preview_text)
                    click.echo("─" * 60)
            else:
                click.echo(f"❌ Preview failed: {result.error}")
                
        except Exception as e:
            click.echo(f"❌ Preview failed: {e}")
            raise click.Abort()
    
    return asyncio.run(async_preview())


@click.command()
@click.argument('url')
@click.option('--method', type=click.Choice(['trafilatura', 'beautifulsoup', 'both']), default='both')
@click.option('--show-diff', is_flag=True, help='Show difference between methods')
@click.pass_context
def test_extraction_cmd(ctx, url: str, method: str, show_diff: bool):
    """Test different extraction methods on a URL."""
    
    async def async_test():
        config = ctx.obj
        converter = URLToMarkdownConverter(config)
        
        click.echo(f"🧪 Testing extraction methods for: {url}")
        
        results = {}
        
        if method in ['trafilatura', 'both']:
            click.echo("\n🔍 Testing Trafilatura...")
            result = await converter.convert_url(url, output_path=None, use_trafilatura=True)
            if result.success:
                results['trafilatura'] = result
                click.echo(f"   ✅ Size: {result.file_size:,} chars")
            else:
                click.echo(f"   ❌ Failed: {result.error}")
        
        if method in ['beautifulsoup', 'both']:
            click.echo("\n🔍 Testing BeautifulSoup...")
            result = await converter.convert_url(url, output_path=None, use_trafilatura=False)
            if result.success:
                results['beautifulsoup'] = result
                click.echo(f"   ✅ Size: {result.file_size:,} chars")
            else:
                click.echo(f"   ❌ Failed: {result.error}")
        
        if show_diff and len(results) == 2:
            click.echo("\n📊 Comparison:")
            traff_result = results['trafilatura']
            bs_result = results['beautifulsoup']
            
            size_diff = traff_result.file_size - bs_result.file_size
            size_percent = (size_diff / bs_result.file_size * 100) if bs_result.file_size > 0 else 0
            
            click.echo(f"   Trafilatura: {traff_result.file_size:,} chars")
            click.echo(f"   BeautifulSoup: {bs_result.file_size:,} chars")
            click.echo(f"   Difference: {size_diff:+,} chars ({size_percent:+.1f}%)")
            
            if size_percent < -50:
                click.echo("   🎯 Trafilatura extracted significantly cleaner content!")
            elif size_percent > 50:
                click.echo("   ⚠️  Trafilatura may have missed some content")
            else:
                click.echo("   ✅ Both methods produced similar amounts of content")
    
    return asyncio.run(async_test())


@click.command()
@click.argument('url')
def hash_cmd(url: str):
    """Generate hash filename for a URL."""
    hash_value = URLHasher.generate_hash(url)
    filename = URLHasher.generate_filename(url)
    
    click.echo(f"URL: {url}")
    click.echo(f"Hash: {hash_value}")
    click.echo(f"Filename: {filename}")


@click.command()
@click.option('--format', 'output_format', type=click.Choice(['text', 'json']), default='text')
@click.pass_context
def config_info_cmd(ctx, output_format: str):
    """Show current configuration."""
    config = ctx.obj
    
    if output_format == 'json':
        click.echo(json.dumps(config.to_dict(), indent=2))
    else:
        click.echo("🔧 Current Configuration:")
        click.echo("─" * 40)
        
        # Group settings by category
        sections = {
            'Output Settings': [
                ('output_dir', 'Output Directory'),
                ('use_hash_filenames', 'Use Hash Filenames'),
            ],
            'Network Settings': [
                ('timeout', 'Timeout (seconds)'),
                ('user_agent', 'User Agent'),
                ('max_retries', 'Max Retries'),
            ],
            'Content Extraction': [
                ('javascript_enabled', 'JavaScript Enabled'),
                ('use_trafilatura', 'Use Trafilatura'),
                ('clean_content', 'Clean Content'),
                ('llm_optimized', 'LLM Optimized'),
            ],
            'Content Filtering': [
                ('remove_cookie_banners', 'Remove Cookie Banners'),
                ('remove_navigation', 'Remove Navigation'),
                ('remove_ads', 'Remove Ads'),
                ('remove_social_media', 'Remove Social Media'),
            ],
        }
        
        for section, settings in sections.items():
            click.echo(f"\n{section}:")
            for key, label in settings:
                value = getattr(config, key)
                click.echo(f"  {label}: {value}")


# Add commands to CLI group
cli.add_command(convert_cmd, name='convert')
cli.add_command(batch_cmd, name='batch')
cli.add_command(preview_cmd, name='preview')
cli.add_command(test_extraction_cmd, name='test-extraction')
cli.add_command(hash_cmd, name='hash')
cli.add_command(config_info_cmd, name='config-info')


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
