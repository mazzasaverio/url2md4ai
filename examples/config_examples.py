#!/usr/bin/env python3
"""
Advanced configuration examples for URL2MD4AI.

This module demonstrates different configuration profiles optimized
for various website types and use cases.
"""

from url2md4ai import Config
import json
from pathlib import Path


def get_news_config():
    """Configuration optimized for news articles and blog posts."""
    return Config(
        # Content extraction settings
        javascript_enabled=True,
        use_trafilatura=True,
        llm_optimized=True,
        clean_content=True,
        
        # Aggressive noise removal for news
        remove_cookie_banners=True,
        remove_ads=True,
        remove_social_media=True,
        remove_comments=True,
        remove_navigation=True,
        
        # Trafilatura settings for news
        favor_precision=True,  # Quality over quantity
        favor_recall=False,
        include_images=False,  # Focus on text content
        include_tables=True,   # News often has data tables
        include_formatting=True,
        
        # Network settings
        timeout=25,
        page_wait_timeout=2000,
        max_retries=3,
        
        # Output settings
        output_dir="news_output",
        use_hash_filenames=True,
    )


def get_documentation_config():
    """Configuration optimized for technical documentation."""
    return Config(
        # Content extraction settings
        javascript_enabled=True,
        use_trafilatura=True,
        llm_optimized=True,
        clean_content=True,
        
        # Selective filtering for docs
        remove_cookie_banners=True,
        remove_ads=True,
        remove_navigation=True,  # Remove nav but keep content structure
        remove_social_media=False,  # Sometimes useful for docs
        remove_comments=False,  # Code comments are important
        
        # Trafilatura settings for documentation
        favor_precision=False,
        favor_recall=True,      # Completeness is important for docs
        include_images=False,   # Focus on text and code
        include_tables=True,    # Critical for API docs, specs
        include_formatting=True, # Preserve code blocks, lists
        include_comments=False,  # HTML comments usually not needed
        
        # Network settings
        timeout=30,  # Docs can be large
        page_wait_timeout=3000,
        max_retries=2,
        
        # Output settings
        output_dir="docs_output",
        use_hash_filenames=True,
    )


def get_ecommerce_config():
    """Configuration optimized for e-commerce product pages."""
    return Config(
        # Content extraction settings
        javascript_enabled=True,  # Product pages often use JS heavily
        use_trafilatura=True,
        llm_optimized=True,
        clean_content=True,
        
        # E-commerce specific filtering
        remove_cookie_banners=True,
        remove_ads=True,
        remove_social_media=True,
        remove_navigation=True,
        remove_comments=True,  # Remove user reviews noise
        
        # Trafilatura settings for products
        favor_precision=True,   # Quality product info
        favor_recall=False,
        include_images=False,   # Focus on product details
        include_tables=True,    # Product specification tables
        include_formatting=True,
        
        # Network settings
        timeout=20,
        page_wait_timeout=2500, # Wait for product details to load
        max_retries=3,
        
        # Output settings
        output_dir="ecommerce_output",
        use_hash_filenames=True,
    )


def get_research_config():
    """Configuration optimized for academic/research content."""
    return Config(
        # Content extraction settings
        javascript_enabled=True,
        use_trafilatura=True,
        llm_optimized=True,
        clean_content=True,
        
        # Minimal filtering for research content
        remove_cookie_banners=True,
        remove_ads=True,
        remove_social_media=False,  # May contain relevant links
        remove_navigation=True,
        remove_comments=False,  # May contain important citations
        
        # Trafilatura settings for research
        favor_precision=False,
        favor_recall=True,      # Don't miss important content
        include_images=False,   # Focus on text and data
        include_tables=True,    # Research data tables are crucial
        include_formatting=True, # Preserve academic formatting
        include_comments=True,   # May contain metadata
        
        # Network settings
        timeout=45,  # Academic sites can be slow
        page_wait_timeout=4000,
        max_retries=2,
        
        # Output settings
        output_dir="research_output",
        use_hash_filenames=True,
    )


def get_social_media_config():
    """Configuration optimized for social media posts."""
    return Config(
        # Content extraction settings
        javascript_enabled=True,  # Essential for social media
        use_trafilatura=True,
        llm_optimized=True,
        clean_content=True,
        
        # Light filtering for social content
        remove_cookie_banners=True,
        remove_ads=True,
        remove_social_media=False,  # This IS social media
        remove_navigation=True,
        remove_comments=False,  # Comments are part of social content
        
        # Trafilatura settings for social media
        favor_precision=True,
        favor_recall=False,
        include_images=False,   # Focus on text content
        include_tables=False,   # Rare in social media
        include_formatting=True,
        
        # Network settings
        timeout=15,  # Social media should be fast
        page_wait_timeout=3000,  # Wait for dynamic loading
        max_retries=3,
        
        # Output settings
        output_dir="social_output",
        use_hash_filenames=True,
    )


def get_bulk_processing_config():
    """Configuration optimized for fast bulk processing."""
    return Config(
        # Speed-optimized settings
        javascript_enabled=False,  # Faster without JS
        use_trafilatura=True,      # Still use trafilatura for quality
        llm_optimized=True,
        clean_content=True,
        
        # Standard filtering
        remove_cookie_banners=True,
        remove_ads=True,
        remove_social_media=True,
        remove_navigation=True,
        remove_comments=True,
        
        # Fast trafilatura settings
        favor_precision=True,
        favor_recall=False,
        include_images=False,
        include_tables=True,
        include_formatting=False,  # Faster without formatting
        
        # Aggressive timeout settings
        timeout=10,  # Short timeout
        page_wait_timeout=1000,
        max_retries=1,  # Fewer retries
        
        # Output settings
        output_dir="bulk_output",
        use_hash_filenames=True,
    )


def get_development_config():
    """Configuration for development and testing."""
    return Config(
        # Development settings
        javascript_enabled=True,
        use_trafilatura=True,
        llm_optimized=False,  # Keep raw content for debugging
        clean_content=False,  # No cleaning for debugging
        
        # No filtering for development
        remove_cookie_banners=False,
        remove_ads=False,
        remove_social_media=False,
        remove_navigation=False,
        remove_comments=False,
        
        # Conservative trafilatura settings
        favor_precision=False,
        favor_recall=True,  # Get everything for testing
        include_images=True,
        include_tables=True,
        include_formatting=True,
        include_comments=True,
        
        # Generous timeout settings
        timeout=60,  # Long timeout for debugging
        page_wait_timeout=5000,
        max_retries=3,
        
        # Output settings
        output_dir="dev_output",
        use_hash_filenames=False,  # Human-readable names for dev
        log_level="DEBUG",
    )


def export_all_configs():
    """Export all configuration profiles to JSON files."""
    configs = {
        "news": get_news_config(),
        "documentation": get_documentation_config(),
        "ecommerce": get_ecommerce_config(),
        "research": get_research_config(),
        "social_media": get_social_media_config(),
        "bulk_processing": get_bulk_processing_config(),
        "development": get_development_config(),
    }
    
    # Create output directory
    output_dir = Path("examples/configs")
    output_dir.mkdir(exist_ok=True)
    
    print("📤 Exporting configuration profiles...")
    
    # Export individual configs
    for name, config in configs.items():
        config_data = {
            "name": name,
            "description": f"URL2MD4AI configuration optimized for {name.replace('_', ' ')} content",
            "use_cases": _get_use_cases(name),
            "config": config.to_dict()
        }
        
        config_file = output_dir / f"{name}.json"
        config_file.write_text(json.dumps(config_data, indent=2))
        print(f"✅ {config_file}")
    
    # Export combined config
    combined_data = {
        "url2md4ai_configs": {
            name: {
                "description": f"Optimized for {name.replace('_', ' ')} content",
                "config": config.to_dict()
            }
            for name, config in configs.items()
        }
    }
    
    combined_file = output_dir / "all_configs.json"
    combined_file.write_text(json.dumps(combined_data, indent=2))
    print(f"✅ {combined_file} (combined)")
    
    print(f"\n📁 All configurations exported to: {output_dir}")
    return configs


def _get_use_cases(config_name):
    """Get use cases for each configuration type."""
    use_cases = {
        "news": [
            "News articles",
            "Blog posts", 
            "Press releases",
            "Editorial content",
            "Online magazines"
        ],
        "documentation": [
            "API documentation",
            "Technical guides",
            "Software manuals",
            "Code repositories",
            "Knowledge bases"
        ],
        "ecommerce": [
            "Product pages",
            "Product catalogs",
            "Shopping sites",
            "Marketplace listings",
            "Product reviews"
        ],
        "research": [
            "Academic papers",
            "Research articles",
            "Scientific journals",
            "Study reports",
            "Educational content"
        ],
        "social_media": [
            "Social media posts",
            "Forum discussions",
            "Community content",
            "User-generated content",
            "Comments and threads"
        ],
        "bulk_processing": [
            "Large-scale crawling",
            "Data collection",
            "Content aggregation",
            "Batch processing",
            "High-volume extraction"
        ],
        "development": [
            "Testing and debugging",
            "Content analysis",
            "Development workflows",
            "Experimentation",
            "Quality assurance"
        ]
    }
    return use_cases.get(config_name, [])


def demo_configurations():
    """Demonstrate different configuration profiles."""
    print("🔧 URL2MD4AI Configuration Profiles Demo")
    print("=" * 60)
    
    configs = {
        "News Articles": get_news_config(),
        "Documentation": get_documentation_config(), 
        "E-commerce": get_ecommerce_config(),
        "Research Papers": get_research_config(),
        "Social Media": get_social_media_config(),
        "Bulk Processing": get_bulk_processing_config(),
        "Development": get_development_config(),
    }
    
    for name, config in configs.items():
        print(f"\n📋 {name} Configuration:")
        print(f"   JavaScript: {config.javascript_enabled}")
        print(f"   Trafilatura: {config.use_trafilatura}")
        print(f"   LLM Optimized: {config.llm_optimized}")
        print(f"   Remove Ads: {config.remove_ads}")
        print(f"   Remove Cookies: {config.remove_cookie_banners}")
        print(f"   Timeout: {config.timeout}s")
        print(f"   Output: {config.output_dir}")
    
    print("\n💡 Usage Example:")
    print("```python")
    print("from examples.config_examples import get_news_config")
    print("from url2md4ai import URLToMarkdownConverter")
    print("")
    print("config = get_news_config()")
    print("converter = URLToMarkdownConverter(config)")
    print("result = await converter.convert_url('https://news-site.com/article')")
    print("```")


if __name__ == "__main__":
    demo_configurations()
    print("\n" + "="*60)
    export_all_configs() 