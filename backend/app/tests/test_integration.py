"""
Integration Test for LLM Configuration

This script tests the full integration of the LLM configuration system
with the SQL workflow to ensure models work end-to-end.

Usage:
    python -m app.tests.test_integration
"""

import sys
from typing import Dict, Any
from app.config.llm_config import LLM, DEFAULT_MODELS
from app.langgraph.agents.sql_agent import SQLAgent
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


def test_sql_agent_with_model(model_name: str) -> bool:
    """
    Test SQLAgent with a specific model.

    Args:
        model_name: Name of the model to test

    Returns:
        True if test passed, False otherwise
    """
    try:
        # Initialize LLM
        llm_instance = LLM()
        llm = llm_instance.get_model(model_name, fallback=True)

        # Initialize SQL Agent
        sql_agent = SQLAgent(llm)

        # Test conversational response (simplest test)
        test_state = {
            'question': 'Hello, how are you?'
        }

        result = sql_agent.conversational_response(test_state)

        if 'answer' in result and result['answer']:
            print_success(f"{model_name}: SQL Agent integration successful")
            print(f"  Sample response: {result['answer'][:100]}...")
            return True
        else:
            print_error(f"{model_name}: No answer in response")
            return False

    except Exception as e:
        print_error(f"{model_name}: Integration failed - {str(e)}")
        return False


def test_model_switching():
    """Test switching between different models"""
    print_header("Testing Model Switching")

    llm_instance = LLM()

    # Test switching between models
    models_to_test = []
    if OPENAI_API_KEY:
        models_to_test.append("gpt-4o-mini")
    if GROQ_API_KEY:
        models_to_test.append("gemma2-9b-it")

    if not models_to_test:
        print_error("No API keys configured - skipping model switching test")
        return

    print(f"Testing model switching with {len(models_to_test)} models...\n")

    for model_name in models_to_test:
        try:
            model = llm_instance.get_model(model_name)
            print_success(f"Switched to {model_name} (current: {llm_instance.current_model})")
        except Exception as e:
            print_error(f"Failed to switch to {model_name}: {str(e)}")


def test_task_based_selection():
    """Test getting optimal models for different tasks"""
    print_header("Testing Task-Based Model Selection")

    llm_instance = LLM()

    tasks = ["sql_generation", "data_analysis", "chat", "visualization"]

    for task in tasks:
        try:
            model = llm_instance.get_model_for_task(task)
            expected_model = DEFAULT_MODELS.get(task)
            actual_model = llm_instance.current_model

            if actual_model == expected_model or actual_model == DEFAULT_MODELS['fallback']:
                print_success(f"{task}: Got model {actual_model}")
            else:
                print_error(f"{task}: Expected {expected_model}, got {actual_model}")

        except Exception as e:
            print_error(f"{task}: Failed to get model - {str(e)}")


def test_error_handling():
    """Test error handling and fallback"""
    print_header("Testing Error Handling and Fallback")

    llm_instance = LLM()

    # Test 1: Invalid model with fallback
    print("Test 1: Invalid model with fallback enabled")
    try:
        model = llm_instance.get_model("invalid-model-12345", fallback=True)
        print_success(f"Fallback successful - using {llm_instance.current_model}")
    except Exception as e:
        print_error(f"Fallback failed: {str(e)}")

    # Test 2: Invalid model without fallback
    print("\nTest 2: Invalid model with fallback disabled")
    try:
        model = llm_instance.get_model("invalid-model-12345", fallback=False)
        print_error("Should have raised ValueError")
    except ValueError:
        print_success("Correctly raised ValueError for invalid model")
    except Exception as e:
        print_error(f"Raised unexpected error: {str(e)}")


def main():
    """Run integration tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 23 + "LLM INTEGRATION TEST SUITE" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")

    if not OPENAI_API_KEY and not GROQ_API_KEY:
        print_error("No API keys configured!")
        print("Please set OPENAI_API_KEY or GROQ_API_KEY to run integration tests.")
        sys.exit(1)

    try:
        # Test 1: Task-based selection
        test_task_based_selection()

        # Test 2: Model switching
        test_model_switching()

        # Test 3: Error handling
        test_error_handling()

        # Test 4: SQL Agent integration (optional)
        print("\n" + "=" * 80)
        response = input("Run SQL Agent integration tests with API calls? (y/N): ")
        if response.lower() == 'y':
            print_header("Testing SQL Agent Integration")

            models_to_test = []
            if OPENAI_API_KEY:
                models_to_test.append("gpt-4o-mini")
            if GROQ_API_KEY:
                models_to_test.append("gemma2-9b-it")

            success_count = 0
            for model_name in models_to_test:
                if test_sql_agent_with_model(model_name):
                    success_count += 1

            print(f"\n{'='*80}")
            print(f"SQL Agent Integration: {success_count}/{len(models_to_test)} successful")
            print(f"{'='*80}")
        else:
            print("Skipping SQL Agent integration tests")

        # Final summary
        print_header("INTEGRATION TEST SUITE COMPLETED")
        print_success("All integration tests passed!")

    except Exception as e:
        print_header("INTEGRATION TEST SUITE FAILED")
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
