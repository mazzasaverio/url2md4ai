"""Test cases for url2md4ai configuration."""

import os
from unittest.mock import patch

from url2md4ai.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()

        assert config.output_dir == "output"
        assert config.use_hash_filenames is True
        assert config.timeout == 30
        assert config.user_agent == "url2md4ai/1.0"
        assert config.javascript_enabled is True
        assert config.clean_content is True
        assert config.llm_optimized is True
        assert config.use_trafilatura is True

    def test_from_env_defaults(self):
        """Test config from environment with default values."""
        with patch.dict(os.environ, {}, clear=False):
            config = Config.from_env()

            assert config.output_dir == "output"
            assert config.timeout == 30
            assert config.javascript_enabled is True

    def test_from_env_custom_values(self):
        """Test config from environment with custom values."""
        env_vars = {
            "URL2MD_OUTPUT_DIR": "/custom/output",
            "URL2MD_TIMEOUT": "60",
            "URL2MD_JAVASCRIPT": "false",
            "URL2MD_CLEAN_CONTENT": "false",
            "URL2MD_USE_TRAFILATURA": "false",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config.from_env()

            assert config.output_dir == "/custom/output"
            assert config.timeout == 60
            assert config.javascript_enabled is False
            assert config.clean_content is False
            assert config.use_trafilatura is False

    def test_to_dict(self):
        """Test config to dictionary conversion."""
        config = Config(output_dir="/test", timeout=45, javascript_enabled=False)

        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["output_dir"] == "/test"
        assert config_dict["timeout"] == 45
        assert config_dict["javascript_enabled"] is False
        assert "use_hash_filenames" in config_dict
        assert "clean_content" in config_dict

    def test_boolean_env_parsing(self):
        """Test boolean environment variable parsing."""
        # Test true values
        with patch.dict(os.environ, {"URL2MD_JAVASCRIPT": "true"}, clear=False):
            config = Config.from_env()
            assert config.javascript_enabled is True

        # Test false values
        with patch.dict(os.environ, {"URL2MD_JAVASCRIPT": "false"}, clear=False):
            config = Config.from_env()
            assert config.javascript_enabled is False

    def test_numeric_env_parsing(self):
        """Test numeric environment variable parsing."""
        with patch.dict(
            os.environ,
            {
                "URL2MD_TIMEOUT": "120",
                "URL2MD_MAX_RETRIES": "5",
                "URL2MD_PAGE_TIMEOUT": "3000",
            },
            clear=False,
        ):
            config = Config.from_env()

            assert config.timeout == 120
            assert config.max_retries == 5
            assert config.page_wait_timeout == 3000

    def test_content_filtering_config(self):
        """Test content filtering configuration options."""
        config = Config()

        # Test defaults
        assert config.remove_cookie_banners is True
        assert config.remove_navigation is True
        assert config.remove_ads is True
        assert config.remove_social_media is True
        assert config.remove_comments is True

    def test_trafilatura_config(self):
        """Test trafilatura-specific configuration options."""
        config = Config()

        # Test trafilatura defaults
        assert config.favor_precision is True
        assert config.favor_recall is False
        assert config.include_tables is True
        assert config.include_images is False
        assert config.include_comments is False
        assert config.include_formatting is True
