"""Pytest configuration and fixtures."""

import os
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment."""
    # Set minimal required environment variables for tests
    test_env = {
        "OPENAI_API_KEY": "sk-test123456789abcdef",
        "LOG_LEVEL": "WARNING",  # Reduce noise in tests
    }

    with patch.dict(os.environ, test_env):
        yield


@pytest.fixture
def sample_recipe_text():
    """Sample recipe text for testing."""
    return """
    Spaghetti Carbonara
    
    A classic Italian pasta dish.
    
    Ingredients:
    - 400g spaghetti
    - 200g guanciale or pancetta
    - 4 large eggs
    - 100g Pecorino Romano cheese
    - Black pepper
    - Salt
    
    Instructions:
    1. Cook spaghetti in salted water until al dente
    2. Fry guanciale until crispy
    3. Beat eggs with grated cheese
    4. Combine hot pasta with guanciale
    5. Add egg mixture off heat, stirring quickly
    6. Season with black pepper
    
    Serves 4 people. Total time: 20 minutes.
    """


@pytest.fixture
def sample_job_text():
    """Sample job description text for testing."""
    return """
    Senior Python Developer
    
    We are looking for an experienced Python developer to join our team.
    
    Company: Tech Innovations Inc.
    Location: San Francisco, CA (Remote friendly)
    
    Requirements:
    - 5+ years of Python experience
    - Experience with Django/Flask
    - Knowledge of AWS/Docker
    - Strong problem-solving skills
    
    Responsibilities:
    - Develop backend services
    - Mentor junior developers
    - Code reviews and testing
    
    Benefits:
    - Competitive salary ($120k-160k)
    - Health insurance
    - Stock options
    - Flexible working hours
    """


@pytest.fixture
def sample_news_text():
    """Sample news article text for testing."""
    return """
    Breaking: Apple Unveils Revolutionary iPhone 15 Pro
    
    CUPERTINO, Calif. - Apple Inc. today announced the highly anticipated iPhone 15 Pro,
    featuring groundbreaking titanium design and advanced AI capabilities. CEO Tim Cook
    presented the device at Apple Park, highlighting its improved camera system and
    extended battery life.
    
    The new device, starting at $999, will be available for pre-order this Friday.
    Industry analysts predict strong sales, with some calling it "the most significant
    iPhone upgrade in years."
    """
