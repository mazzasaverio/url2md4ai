"""Configuration management for url2md4ai."""

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class Config:
    """Configuration settings for URL2MD4AI."""

    # Output settings
    output_dir: str = "output"
    use_hash_filenames: bool = True

    # Network settings
    timeout: int = 30
    user_agent: str = "url2md4ai/1.0"
    max_retries: int = 3
    retry_delay: float = 1.0

    # Playwright settings
    javascript_enabled: bool = True
    browser_headless: bool = True
    wait_for_network_idle: bool = True
    page_wait_timeout: int = 2000

    # Content extraction settings
    use_trafilatura: bool = True
    clean_content: bool = True
    llm_optimized: bool = True

    # Content filtering settings
    remove_cookie_banners: bool = True
    remove_navigation: bool = True
    remove_ads: bool = True
    remove_social_media: bool = True
    remove_comments: bool = True

    # Advanced trafilatura settings
    favor_precision: bool = True
    favor_recall: bool = False
    include_tables: bool = True
    include_images: bool = False
    include_comments: bool = False
    include_formatting: bool = True

    # Cache settings
    enable_caching: bool = False
    cache_dir: str = ".cache"
    cache_ttl: int = 3600

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls(
            # Output settings
            output_dir=os.getenv("URL2MD_OUTPUT_DIR", "output"),
            use_hash_filenames=os.getenv("URL2MD_USE_HASH_FILENAMES", "true").lower()
            == "true",
            # Network settings
            timeout=int(os.getenv("URL2MD_TIMEOUT", "30")),
            user_agent=os.getenv("URL2MD_USER_AGENT", "url2md4ai/1.0"),
            max_retries=int(os.getenv("URL2MD_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("URL2MD_RETRY_DELAY", "1.0")),
            # Playwright settings
            javascript_enabled=os.getenv("URL2MD_JAVASCRIPT", "true").lower() == "true",
            browser_headless=os.getenv("URL2MD_HEADLESS", "true").lower() == "true",
            wait_for_network_idle=os.getenv("URL2MD_WAIT_NETWORK", "true").lower()
            == "true",
            page_wait_timeout=int(os.getenv("URL2MD_PAGE_TIMEOUT", "2000")),
            # Content extraction settings
            use_trafilatura=os.getenv("URL2MD_USE_TRAFILATURA", "true").lower()
            == "true",
            clean_content=os.getenv("URL2MD_CLEAN_CONTENT", "true").lower() == "true",
            llm_optimized=os.getenv("URL2MD_LLM_OPTIMIZED", "true").lower() == "true",
            # Content filtering settings
            remove_cookie_banners=os.getenv("URL2MD_REMOVE_COOKIES", "true").lower()
            == "true",
            remove_navigation=os.getenv("URL2MD_REMOVE_NAV", "true").lower() == "true",
            remove_ads=os.getenv("URL2MD_REMOVE_ADS", "true").lower() == "true",
            remove_social_media=os.getenv("URL2MD_REMOVE_SOCIAL", "true").lower()
            == "true",
            remove_comments=os.getenv("URL2MD_REMOVE_COMMENTS", "true").lower()
            == "true",
            # Advanced trafilatura settings
            favor_precision=os.getenv("URL2MD_FAVOR_PRECISION", "true").lower()
            == "true",
            favor_recall=os.getenv("URL2MD_FAVOR_RECALL", "false").lower() == "true",
            include_tables=os.getenv("URL2MD_INCLUDE_TABLES", "true").lower() == "true",
            include_images=os.getenv("URL2MD_INCLUDE_IMAGES", "false").lower()
            == "true",
            include_comments=os.getenv("URL2MD_INCLUDE_COMMENTS", "false").lower()
            == "true",
            include_formatting=os.getenv("URL2MD_INCLUDE_FORMATTING", "true").lower()
            == "true",
            # Cache settings
            enable_caching=os.getenv("URL2MD_ENABLE_CACHE", "false").lower() == "true",
            cache_dir=os.getenv("URL2MD_CACHE_DIR", ".cache"),
            cache_ttl=int(os.getenv("URL2MD_CACHE_TTL", "3600")),
            # Logging settings
            log_level=os.getenv("URL2MD_LOG_LEVEL", "INFO"),
            log_format=os.getenv(
                "URL2MD_LOG_FORMAT",
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }
