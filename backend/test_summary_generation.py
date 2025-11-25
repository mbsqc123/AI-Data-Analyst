"""
Test Suite for Summary Generation Across All Models

This script validates that all configured LLM models can successfully generate
natural language summaries from test case data.

Usage:
    python test_summary_generation.py
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.config.llm_config import LLM, AVAILABLE_MODELS, DEFAULT_MODELS


async def test_all_models_summarization():
    """
    Test that all available models can generate comprehensive summaries.
    """
    # Sample test case data mimicking SQL query results
    test_data = """
    Test Case Reference: VanTC001
    Total Test Fields: 177
    Application Type: Vanquis Credit Card Application Form

    Field Categories:
    - Personal Information: 45 fields (First Name, Last Name, Date of Birth, etc.)
    - Address Details: 32 fields (Current Address, Previous Addresses, etc.)
    - Employment Information: 28 fields (Employer Name, Job Title, Income, etc.)
    - Driving History: 15 fields (License Number, Driving Experience, etc.)
    - Financial Details: 40 fields (Bank Details, Credit History, etc.)
    - Other: 17 fields (Preferences, Marketing Consent, etc.)

    Test Purpose: Validate complete customer application workflow for Vanquis credit card
    """

    prompt = f"""
    Given this test case data:
    {test_data}

    Provide a comprehensive natural language summary (2-4 paragraphs) of what this test case is testing.
    Include key statistics, the purpose of the test, and what areas it covers.
    """

    # Get list of all models
    models = list(AVAILABLE_MODELS.keys())

    print("=" * 80)
    print("SUMMARY GENERATION TEST - ALL MODELS")
    print("=" * 80)
    print(f"\nTesting {len(models)} models...\n")

    results = {
        "passed": [],
        "failed": []
    }

    for model_name in models:
        print(f"\n{'=' * 80}")
        print(f"Testing: {model_name}")
        print(f"Display Name: {AVAILABLE_MODELS[model_name].display_name}")
        print(f"Platform: {AVAILABLE_MODELS[model_name].platform.value}")
        print(f"Capability: {AVAILABLE_MODELS[model_name].capability.value}")
        print(f"{'=' * 80}")

        try:
            # Initialize LLM instance
            llm_instance = LLM()
            llm = llm_instance.get_model(model_name, fallback=False)

            # Invoke the model
            response = llm.invoke(prompt)

            # Extract response text
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)

            # Validate response
            word_count = len(response_text.split())
            paragraph_count = len([p for p in response_text.split('\n\n') if p.strip()])

            print(f"\n✅ {model_name} SUCCESS")
            print(f"   Response Length: {len(response_text)} characters")
            print(f"   Word Count: {word_count} words")
            print(f"   Paragraph Count: {paragraph_count}")
            print(f"\n   Sample Output (first 200 chars):")
            print(f"   {response_text[:200]}...")

            # Check if response is comprehensive (not just one sentence)
            if word_count >= 30 and len(response_text) >= 150:
                results["passed"].append(model_name)
                print(f"\n   ✓ Summary is comprehensive")
            else:
                results["failed"].append(model_name)
                print(f"\n   ✗ WARNING: Summary may be too short")

        except Exception as e:
            print(f"\n❌ {model_name} FAILED")
            print(f"   Error: {str(e)}")
            results["failed"].append(model_name)

    # Print summary
    print(f"\n\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}")
    print(f"\nTotal Models Tested: {len(models)}")
    print(f"✅ Passed: {len(results['passed'])} models")
    print(f"❌ Failed: {len(results['failed'])} models")

    if results["passed"]:
        print(f"\nPassed Models:")
        for model in results["passed"]:
            print(f"  - {model} ({AVAILABLE_MODELS[model].display_name})")

    if results["failed"]:
        print(f"\nFailed Models:")
        for model in results["failed"]:
            print(f"  - {model} ({AVAILABLE_MODELS[model].display_name})")

    print(f"\n{'=' * 80}")

    # Return success if all models passed
    return len(results["failed"]) == 0


async def test_default_models():
    """
    Test the default models for each task type.
    """
    print("\n\n" + "=" * 80)
    print("TESTING DEFAULT MODELS FOR EACH TASK")
    print("=" * 80)

    test_prompt = "Summarize this data: Total sales: 1000, Revenue: $50000, Top product: Widget A"

    for task_name, model_name in DEFAULT_MODELS.items():
        print(f"\nTask: {task_name}")
        print(f"Default Model: {model_name}")

        try:
            llm_instance = LLM()
            llm = llm_instance.get_model_for_task(task_name)

            response = llm.invoke(test_prompt)
            if hasattr(response, 'content'):
                response_text = response.content[:100]
            else:
                response_text = str(response)[:100]

            print(f"✅ Success - Response: {response_text}...")
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")


async def test_fallback_mechanism():
    """
    Test that fallback mechanism works when a model fails.
    """
    print("\n\n" + "=" * 80)
    print("TESTING FALLBACK MECHANISM")
    print("=" * 80)

    # Test with invalid model name
    print("\nTesting with invalid model name: 'invalid-model-xyz'")

    try:
        llm_instance = LLM()
        llm = llm_instance.get_model("invalid-model-xyz", fallback=True)

        response = llm.invoke("Hello, can you summarize data?")
        print(f"✅ Fallback mechanism works!")
        print(f"   Fell back to model: {llm_instance.current_model}")
        print(f"   Platform: {llm_instance.platform}")
    except Exception as e:
        print(f"❌ Fallback mechanism failed: {str(e)}")


async def main():
    """
    Run all tests.
    """
    print("\n" + "🔬" * 40)
    print("STARTING COMPREHENSIVE MODEL TESTING")
    print("🔬" * 40 + "\n")

    # Test 1: All models summarization
    all_passed = await test_all_models_summarization()

    # Test 2: Default models
    await test_default_models()

    # Test 3: Fallback mechanism
    await test_fallback_mechanism()

    print("\n\n" + "🎉" * 40)
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED - CHECK OUTPUT ABOVE")
    print("🎉" * 40 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
