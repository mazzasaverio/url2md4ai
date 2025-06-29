#!/usr/bin/env python3
"""
Example usage of URL2MD4AI - Convert web pages to LLM-optimized markdown.

This script demonstrates how to use the library programmatically with different
extraction methods and content optimization settings.
"""

import asyncio
import json
from pathlib import Path

from url2md4ai import URLToMarkdownConverter, URLHasher, Config


async def main():
    """Main example function."""
    print("🚀 URL2MD4AI - LLM-Optimized Markdown Conversion Examples\n")
    
    # Example URLs to demonstrate different use cases
    example_urls = {
        "news": "https://example.com",
        "job_posting": "https://www.satispay.com/en-it/work-at-satispay/open-positions/ffe0b42e-9119-4861-945b-e849e24da206/",
        "product_page": "https://www.apple.com/iphone-15-pro/",
        "blog_post": "https://openai.com/blog/chatgpt/",
    }
    
    # Example 1: Basic Usage with Default Configuration
    print("📝 Example 1: Basic LLM-Optimized Conversion")
    print("-" * 60)
    
    config = Config.from_env()
    converter = URLToMarkdownConverter(config)
    
    url = example_urls["news"]
    print(f"Converting: {url}")
    
    result = await converter.convert_url(url, output_path=None)
    
    if result.success:
        print("✅ Conversion successful!")
        print(f"   📄 Title: {result.title}")
        print(f"   📊 Size: {result.file_size:,} characters")
        print(f"   ⚡ Method: {result.extraction_method}")
        print(f"   🎯 Filename: {result.filename}")
        print(f"   ⏱️  Time: {result.processing_time:.2f}s")
        
        # Show content preview
        preview = result.markdown[:300] + "..." if len(result.markdown) > 300 else result.markdown
        print(f"\n📄 Content Preview:\n{preview}")
    else:
        print(f"❌ Conversion failed: {result.error}")
    
    print("\n")
    
    # Example 2: Clean vs Raw Extraction Comparison
    print("🧹 Example 2: Clean vs Raw Extraction Comparison")
    print("-" * 60)
    
    # Configure for clean extraction
    clean_config = Config.from_env()
    clean_config.llm_optimized = True
    clean_config.clean_content = True
    clean_config.use_trafilatura = True
    clean_config.remove_cookie_banners = True
    
    # Configure for raw extraction
    raw_config = Config.from_env()
    raw_config.llm_optimized = False
    raw_config.clean_content = False
    raw_config.use_trafilatura = False
    
    clean_converter = URLToMarkdownConverter(clean_config)
    raw_converter = URLToMarkdownConverter(raw_config)
    
    url = example_urls["news"]
    print(f"Comparing extraction methods for: {url}")
    
    # Clean extraction
    clean_result = await clean_converter.convert_url(url, output_path=None)
    
    # Raw extraction
    raw_result = await raw_converter.convert_url(url, output_path=None)
    
    if clean_result.success and raw_result.success:
        print("\n📊 Extraction Comparison:")
        print(f"   🧹 Clean: {clean_result.file_size:,} chars via {clean_result.extraction_method}")
        print(f"   📄 Raw:   {raw_result.file_size:,} chars via {raw_result.extraction_method}")
        
        # Calculate noise reduction
        reduction = ((raw_result.file_size - clean_result.file_size) / raw_result.file_size) * 100
        print(f"   🎯 Noise reduction: {reduction:.1f}%")
        
        if reduction > 50:
            print("   ✅ Significant noise reduction - perfect for LLM processing!")
        elif reduction > 20:
            print("   ✅ Good noise reduction - suitable for LLM processing")
        else:
            print("   ⚠️  Minimal noise reduction - content may be naturally clean")
    
    print("\n")
    
    # Example 3: Advanced Configuration
    print("⚙️ Example 3: Advanced Configuration for Different Use Cases")
    print("-" * 60)
    
    # Configuration for news articles
    news_config = Config.from_env()
    news_config.remove_cookie_banners = True
    news_config.remove_ads = True
    news_config.remove_social_media = True
    news_config.remove_comments = True
    news_config.favor_precision = True
    news_config.include_images = False
    news_config.llm_optimized = True
    
    # Configuration for documentation
    docs_config = Config.from_env()
    docs_config.include_tables = True
    docs_config.include_formatting = True
    docs_config.remove_navigation = True
    docs_config.favor_recall = True
    docs_config.llm_optimized = True
    
    print("📰 News Article Configuration:")
    print(f"   Remove ads/social: {news_config.remove_ads}/{news_config.remove_social_media}")
    print(f"   Favor precision: {news_config.favor_precision}")
    print(f"   LLM optimized: {news_config.llm_optimized}")
    
    print("\n📚 Documentation Configuration:")
    print(f"   Include tables/formatting: {docs_config.include_tables}/{docs_config.include_formatting}")
    print(f"   Favor recall: {docs_config.favor_recall}")
    print(f"   Remove navigation: {docs_config.remove_navigation}")
    
    print("\n")
    
    # Example 4: Batch Processing with Different Configurations
    print("🔄 Example 4: Batch Processing with Concurrency")
    print("-" * 60)
    
    # Create a batch converter with optimized settings
    batch_config = Config.from_env()
    batch_config.javascript_enabled = True
    batch_config.llm_optimized = True
    batch_config.clean_content = True
    batch_config.timeout = 15  # Shorter timeout for batch
    
    batch_converter = URLToMarkdownConverter(batch_config)
    
    # Prepare batch URLs (using some example URLs)
    batch_urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://jsonplaceholder.typicode.com/posts/1",
    ]
    
    print(f"Processing {len(batch_urls)} URLs concurrently...")
    
    # Process all URLs concurrently
    tasks = []
    for url in batch_urls:
        task = batch_converter.convert_url(url, output_path=None)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Display results
    successful = 0
    total_size = 0
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"   ❌ {batch_urls[i]}: {result}")
        elif result.success:
            print(f"   ✅ {batch_urls[i]}: {result.file_size:,} chars")
            successful += 1
            total_size += result.file_size
        else:
            print(f"   ❌ {batch_urls[i]}: {result.error}")
    
    print(f"\n📊 Batch Results: {successful}/{len(batch_urls)} successful")
    print(f"   📄 Total content: {total_size:,} characters")
    
    print("\n")
    
    # Example 5: URL Hashing and Filename Generation
    print("🔗 Example 5: URL Hashing and Filename Generation")
    print("-" * 60)
    
    sample_urls = [
        "https://example.com/page1",
        "https://example.com/page2?param=value",
        "https://different-domain.com/path/to/page",
    ]
    
    for url in sample_urls:
        hash_value = URLHasher.generate_hash(url)
        filename = URLHasher.generate_filename(url, ".md")
        
        print(f"URL: {url}")
        print(f"   Hash: {hash_value}")
        print(f"   Filename: {filename}")
        print()
    
    # Example 6: Configuration Export/Import
    print("📤 Example 6: Configuration Management")
    print("-" * 60)
    
    # Create a custom configuration
    custom_config = Config(
        output_dir="custom_output",
        use_hash_filenames=True,
        javascript_enabled=True,
        clean_content=True,
        llm_optimized=True,
        remove_cookie_banners=True,
        remove_ads=True,
        favor_precision=True,
        include_tables=True,
        timeout=20,
    )
    
    # Export configuration to JSON
    config_dict = custom_config.to_dict()
    print("📋 Custom Configuration:")
    print(json.dumps(config_dict, indent=2))
    
    # Save to file
    config_path = Path("examples/custom_config.json")
    config_path.write_text(json.dumps(config_dict, indent=2))
    print(f"\n💾 Configuration saved to: {config_path}")
    
    print("\n🎉 All examples completed successfully!")
    print("\n💡 Pro Tips:")
    print("   • Use clean_content=True for LLM processing")
    print("   • Enable JavaScript for dynamic content")
    print("   • Use batch processing for multiple URLs")
    print("   • Configure filters based on content type")
    print("   • Monitor processing time for optimization")


if __name__ == "__main__":
    asyncio.run(main()) 