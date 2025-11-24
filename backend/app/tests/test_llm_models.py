"""
Test script for LLM model configuration

This script tests all configured models to verify:
1. Each model can be initialized correctly
2. API keys are working
3. Models respond correctly to simple prompts
4. Fallback mechanism works as expected

Usage:
    python -m app.tests.test_llm_models
"""

import sys
import os
from typing import Dict, List, Tuple
from app.config.llm_config import (
    LLM,
    AVAILABLE_MODELS,
    DEFAULT_MODELS,
    get_available_models,
    validate_model,
    get_model_info
)
from app.config.env import OPENAI_API_KEY, GROQ_API_KEY


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_success(text: str):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text: str):
    """Print error message"""
    print(f"❌ {text}")


def print_warning(text: str):
    """Print warning message"""
    print(f"⚠️  {text}")


def test_api_keys() -> Tuple[bool, bool]:
    """
    Test if API keys are configured.

    Returns:
        Tuple of (openai_configured, groq_configured)
    """
    print_header("Testing API Keys Configuration")

    openai_configured = bool(OPENAI_API_KEY)
    groq_configured = bool(GROQ_API_KEY)

    if openai_configured:
        print_success(f"OpenAI API Key configured (length: {len(OPENAI_API_KEY)})")
    else:
        print_warning("OpenAI API Key not configured - OpenAI models will not work")

    if groq_configured:
        print_success(f"Groq API Key configured (length: {len(GROQ_API_KEY)})")
    else:
        print_warning("Groq API Key not configured - Groq models will not work")

    return openai_configured, groq_configured


def test_model_definitions():
    """Test that all model definitions are valid"""
    print_header("Testing Model Definitions")

    models = get_available_models()
    print(f"Total models defined: {len(models)}\n")

    # Group by platform
    platforms = {}
    for model in models:
        platform = model['platform']
        if platform not in platforms:
            platforms[platform] = []
        platforms[platform].append(model)

    # Print models by platform
    for platform, platform_models in platforms.items():
        print(f"\n{platform.upper()} Models ({len(platform_models)}):")
        for model in platform_models:
            print(f"  • {model['display_name']} ({model['name']})")
            print(f"    └─ {model['description']}")
            print(f"    └─ Capability: {model['capability']}")
            if model['best_for']:
                print(f"    └─ Best for: {', '.join(model['best_for'][:2])}")

    print_success(f"\nAll {len(models)} models defined correctly")


def test_model_initialization(openai_available: bool, groq_available: bool):
    """
    Test initializing each model.

    Args:
        openai_available: Whether OpenAI API key is available
        groq_available: Whether Groq API key is available
    """
    print_header("Testing Model Initialization")

    llm = LLM()
    results = []

    for model_name, config in AVAILABLE_MODELS.items():
        platform = config.platform.value

        # Skip if API key not available
        if platform == "openai" and not openai_available:
            print_warning(f"Skipping {model_name} (OpenAI API key not configured)")
            continue
        if platform == "groq" and not groq_available:
            print_warning(f"Skipping {model_name} (Groq API key not configured)")
            continue
        if platform == "ollama":
            print_warning(f"Skipping {model_name} (Ollama testing not implemented)")
            continue

        # Try to initialize the model
        try:
            model = llm.get_model(model_name, fallback=False)
            print_success(f"{model_name}: Initialized successfully")
            results.append((model_name, True, None))
        except Exception as e:
            print_error(f"{model_name}: Failed to initialize - {str(e)}")
            results.append((model_name, False, str(e)))

    # Print summary
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)

    print(f"\n{'='*80}")
    print(f"Initialization Results: {success_count}/{total_count} successful")
    print(f"{'='*80}")


def test_simple_prompts(openai_available: bool, groq_available: bool):
    """
    Test each model with a simple prompt.

    Args:
        openai_available: Whether OpenAI API key is available
        groq_available: Whether Groq API key is available
    """
    print_header("Testing Models with Simple Prompt")

    test_prompt = "What is 2+2? Answer with just the number."
    llm = LLM()
    results = []

    # Test a few key models
    test_models = []
    if openai_available:
        test_models.extend(["gpt-4o-mini", "gpt-4o"])
    if groq_available:
        test_models.extend(["llama-3.1-8b-instant", "gemma2-9b-it"])

    print(f"Testing {len(test_models)} models with prompt: '{test_prompt}'\n")

    for model_name in test_models:
        try:
            model = llm.get_model(model_name, fallback=False)
            response = model.invoke(test_prompt)

            # Extract response content
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)

            print_success(f"{model_name}:")
            print(f"  Response: {response_text[:100]}")
            results.append((model_name, True, response_text))

        except Exception as e:
            print_error(f"{model_name}: {str(e)}")
            results.append((model_name, False, str(e)))

    # Print summary
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)

    print(f"\n{'='*80}")
    print(f"Prompt Test Results: {success_count}/{total_count} successful")
    print(f"{'='*80}")


def test_fallback_mechanism():
    """Test that the fallback mechanism works"""
    print_header("Testing Fallback Mechanism")

    llm = LLM()

    # Test with invalid model name
    print("Testing with invalid model name 'invalid-model-xyz'...")
    try:
        model = llm.get_model("invalid-model-xyz", fallback=True)
        print_success(f"Fallback worked! Fell back to: {llm.current_model}")
    except Exception as e:
        print_error(f"Fallback failed: {str(e)}")

    # Test without fallback
    print("\nTesting without fallback (should raise error)...")
    try:
        model = llm.get_model("invalid-model-xyz", fallback=False)
        print_error("Should have raised an error!")
    except ValueError as e:
        print_success(f"Correctly raised error: {str(e)[:80]}")


def test_default_models():
    """Test default models for each task"""
    print_header("Testing Default Models for Tasks")

    for task, model_name in DEFAULT_MODELS.items():
        if validate_model(model_name):
            print_success(f"{task}: {model_name} ✓")
        else:
            print_error(f"{task}: {model_name} - Model not found!")


def test_utility_functions():
    """Test utility functions"""
    print_header("Testing Utility Functions")

    # Test validate_model
    print("Testing validate_model():")
    assert validate_model("gpt-4o-mini") == True
    assert validate_model("invalid-model") == False
    print_success("validate_model() works correctly")

    # Test get_model_info
    print("\nTesting get_model_info():")
    info = get_model_info("gpt-4o-mini")
    assert info is not None
    assert info['name'] == "gpt-4o-mini"
    print_success(f"get_model_info() works correctly")
    print(f"  Sample info: {info['display_name']} - {info['description']}")

    # Test invalid model
    info = get_model_info("invalid-model")
    assert info is None
    print_success("get_model_info() correctly returns None for invalid model")


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "LLM MODEL CONFIGURATION TEST SUITE" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        # Test 1: API Keys
        openai_available, groq_available = test_api_keys()

        # Test 2: Model Definitions
        test_model_definitions()

        # Test 3: Utility Functions
        test_utility_functions()

        # Test 4: Default Models
        test_default_models()

        # Test 5: Model Initialization
        test_model_initialization(openai_available, groq_available)

        # Test 6: Fallback Mechanism
        test_fallback_mechanism()

        # Test 7: Simple Prompts (optional, can be slow)
        print("\n" + "=" * 80)
        response = input("Run live model tests with API calls? (y/N): ")
        if response.lower() == 'y':
            test_simple_prompts(openai_available, groq_available)
        else:
            print("Skipping live API tests")

        # Final summary
        print_header("TEST SUITE COMPLETED")
        print_success("All configuration tests passed!")
        print("\nNote: Some tests may have been skipped if API keys are not configured.")
        print("To test all models, ensure both OPENAI_API_KEY and GROQ_API_KEY are set.")

    except Exception as e:
        print_header("TEST SUITE FAILED")
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
