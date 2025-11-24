"""
Centralized LLM Configuration Module

This module provides a comprehensive configuration system for all supported LLM models
including the latest OpenAI models (o1, o1-mini, gpt-4o, gpt-4o-mini) and Groq models.

Key Features:
- Centralized model definitions with metadata
- Automatic temperature settings (o1/o1-mini require temperature=1)
- Model validation and error handling
- Fallback mechanisms
- Easy model selection for different use cases
"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_ollama.llms import OllamaLLM
from langchain_core.language_models import BaseLLM
from app.config.env import (GROQ_API_KEY, OPENAI_API_KEY)
from app.config.logging_config import get_logger

logger = get_logger(__name__)


class ModelPlatform(Enum):
    """Supported LLM platforms"""
    OPENAI = "openai"
    GROQ = "groq"
    OLLAMA = "ollama"


class ModelCapability(Enum):
    """Model capability levels"""
    REASONING = "reasoning"  # Complex reasoning tasks (SQL generation, analysis)
    GENERAL = "general"      # General-purpose tasks
    FAST = "fast"           # Speed-optimized tasks
    BALANCED = "balanced"   # Balance of speed and capability


@dataclass
class ModelConfig:
    """Configuration for a single LLM model"""
    name: str
    platform: ModelPlatform
    display_name: str
    description: str
    capability: ModelCapability
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    best_for: List[str] = None

    def __post_init__(self):
        if self.best_for is None:
            self.best_for = []


# ============================================================================
# MODEL DEFINITIONS
# ============================================================================

AVAILABLE_MODELS: Dict[str, ModelConfig] = {
    # OpenAI Models
    "o1": ModelConfig(
        name="o1",
        platform=ModelPlatform.OPENAI,
        display_name="OpenAI o1",
        description="Most advanced reasoning model for complex problem-solving",
        capability=ModelCapability.REASONING,
        temperature=1.0,  # o1 models require temperature=1
        best_for=["Complex SQL queries", "Advanced data analysis", "Multi-step reasoning"]
    ),
    "o1-mini": ModelConfig(
        name="o1-mini",
        platform=ModelPlatform.OPENAI,
        display_name="OpenAI o1-mini",
        description="Fast reasoning model optimized for STEM tasks",
        capability=ModelCapability.REASONING,
        temperature=1.0,  # o1 models require temperature=1
        best_for=["SQL query generation", "Data validation", "Quick analysis"]
    ),
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        platform=ModelPlatform.OPENAI,
        display_name="GPT-4o",
        description="Current flagship model with high intelligence and multimodal capabilities",
        capability=ModelCapability.GENERAL,
        temperature=0.0,
        best_for=["Data analysis", "Complex queries", "Report generation"]
    ),
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        platform=ModelPlatform.OPENAI,
        display_name="GPT-4o Mini",
        description="Fast and cost-effective model for everyday tasks",
        capability=ModelCapability.FAST,
        temperature=0.0,
        best_for=["Chat responses", "Formatting results", "Quick queries"]
    ),
    "gpt-3.5-turbo": ModelConfig(
        name="gpt-3.5-turbo",
        platform=ModelPlatform.OPENAI,
        display_name="GPT-3.5 Turbo",
        description="Legacy model, fast and cost-effective",
        capability=ModelCapability.FAST,
        temperature=0.0,
        best_for=["Simple queries", "Basic formatting"]
    ),

    # Groq Models (Fixed model names)
    "llama-3.1-8b-instant": ModelConfig(
        name="llama-3.1-8b-instant",
        platform=ModelPlatform.GROQ,
        display_name="Llama 3.1 8B",
        description="Fast and efficient open-source model",
        capability=ModelCapability.FAST,
        temperature=0.0,
        best_for=["Quick responses", "Simple queries", "Fallback option"]
    ),
    "gemma2-9b-it": ModelConfig(
        name="gemma2-9b-it",
        platform=ModelPlatform.GROQ,
        display_name="Gemma 2 9B",
        description="Google's efficient instruction-tuned model",
        capability=ModelCapability.BALANCED,
        temperature=0.0,
        best_for=["General queries", "Data formatting", "Visualization recommendations"]
    ),
    "mixtral-8x7b-32768": ModelConfig(
        name="mixtral-8x7b-32768",
        platform=ModelPlatform.GROQ,
        display_name="Mixtral 8x7B",
        description="High-capability mixture-of-experts model",
        capability=ModelCapability.GENERAL,
        temperature=0.0,
        best_for=["Complex analysis", "Long context tasks"]
    ),
}

# Default models for different use cases
DEFAULT_MODELS = {
    "sql_generation": "o1-mini",      # Best for generating SQL queries
    "data_analysis": "gpt-4o",         # Best for analyzing data
    "chat": "gpt-4o-mini",             # Best for chat/formatting
    "visualization": "gpt-4o-mini",    # Best for visualization decisions
    "fallback": "llama-3.1-8b-instant" # Fallback when OpenAI fails
}


# ============================================================================
# LLM CLASS
# ============================================================================

class LLM:
    """
    Main LLM class for creating and managing language model instances.

    Usage:
        llm = LLM()
        model = llm.get_model("gpt-4o-mini")  # Get specific model
        model = llm.get_model_for_task("sql_generation")  # Get optimal model for task
    """

    def __init__(self):
        self.llm: Optional[BaseLLM] = None
        self.platform: Optional[str] = None
        self.current_model: Optional[str] = None

    def groq(self, model: str, temperature: Optional[float] = None) -> BaseLLM:
        """
        Create a Groq LLM instance.

        Args:
            model: Model name (e.g., "llama-3.1-8b-instant")
            temperature: Optional temperature override

        Returns:
            ChatGroq instance
        """
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        config = AVAILABLE_MODELS.get(model)
        temp = temperature if temperature is not None else (config.temperature if config else 0.0)

        self.llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model=model,
            temperature=temp
        )
        self.platform = "Groq"
        self.current_model = model
        logger.info(f"Initialized Groq model: {model} with temperature: {temp}")
        return self.llm

    def openai(self, model: str, temperature: Optional[float] = None) -> BaseLLM:
        """
        Create an OpenAI LLM instance.

        Args:
            model: Model name (e.g., "gpt-4o-mini", "o1-mini")
            temperature: Optional temperature override

        Returns:
            ChatOpenAI instance
        """
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        config = AVAILABLE_MODELS.get(model)
        temp = temperature if temperature is not None else (config.temperature if config else 0.0)

        # Special handling for o1 models which require temperature=1
        if model in ["o1", "o1-mini"] and temperature is None:
            temp = 1.0

        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=model,
            temperature=temp
        )
        self.platform = "OpenAI"
        self.current_model = model
        logger.info(f"Initialized OpenAI model: {model} with temperature: {temp}")
        return self.llm

    def ollama(self, model: str) -> BaseLLM:
        """
        Create an Ollama LLM instance.

        Args:
            model: Model name

        Returns:
            OllamaLLM instance
        """
        self.llm = OllamaLLM(model=model)
        self.platform = "Ollama"
        self.current_model = model
        logger.info(f"Initialized Ollama model: {model}")
        return self.llm

    def get_model(self, model_name: str, fallback: bool = True) -> BaseLLM:
        """
        Get an LLM instance by model name with automatic platform detection.

        Args:
            model_name: Name of the model to instantiate
            fallback: If True, falls back to default model on error

        Returns:
            LLM instance

        Raises:
            ValueError: If model not found and fallback is False
        """
        if model_name not in AVAILABLE_MODELS:
            logger.warning(f"Model '{model_name}' not found in available models")
            if fallback:
                logger.info(f"Falling back to default model: {DEFAULT_MODELS['fallback']}")
                model_name = DEFAULT_MODELS['fallback']
            else:
                raise ValueError(f"Model '{model_name}' not found. Available models: {list(AVAILABLE_MODELS.keys())}")

        config = AVAILABLE_MODELS[model_name]

        try:
            if config.platform == ModelPlatform.OPENAI:
                return self.openai(model_name)
            elif config.platform == ModelPlatform.GROQ:
                return self.groq(model_name)
            elif config.platform == ModelPlatform.OLLAMA:
                return self.ollama(model_name)
            else:
                raise ValueError(f"Unknown platform: {config.platform}")
        except Exception as e:
            logger.error(f"Error initializing model {model_name}: {str(e)}")
            if fallback and model_name != DEFAULT_MODELS['fallback']:
                logger.info(f"Falling back to: {DEFAULT_MODELS['fallback']}")
                return self.get_model(DEFAULT_MODELS['fallback'], fallback=False)
            raise

    def get_model_for_task(self, task: str) -> BaseLLM:
        """
        Get the optimal model for a specific task.

        Args:
            task: Task name (e.g., "sql_generation", "data_analysis", "chat")

        Returns:
            LLM instance optimized for the task
        """
        model_name = DEFAULT_MODELS.get(task, DEFAULT_MODELS['chat'])
        logger.info(f"Getting model for task '{task}': {model_name}")
        return self.get_model(model_name)

    def get_llm(self) -> Optional[BaseLLM]:
        """Get the current LLM instance."""
        return self.llm

    def invoke(self, prompt: str) -> str:
        """
        Invoke the current LLM with a prompt.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            The LLM's response
        """
        if not self.llm:
            raise ValueError("No LLM initialized. Call get_model() first.")
        return self.llm.invoke(prompt)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_available_models() -> List[Dict[str, Any]]:
    """
    Get a list of all available models with their metadata.

    Returns:
        List of model information dictionaries
    """
    models = []
    for name, config in AVAILABLE_MODELS.items():
        models.append({
            "name": name,
            "display_name": config.display_name,
            "description": config.description,
            "platform": config.platform.value,
            "capability": config.capability.value,
            "best_for": config.best_for,
            "temperature": config.temperature
        })
    return models


def get_models_by_platform(platform: str) -> List[str]:
    """
    Get all model names for a specific platform.

    Args:
        platform: Platform name ("openai", "groq", or "ollama")

    Returns:
        List of model names
    """
    try:
        platform_enum = ModelPlatform(platform.lower())
        return [
            name for name, config in AVAILABLE_MODELS.items()
            if config.platform == platform_enum
        ]
    except ValueError:
        logger.error(f"Invalid platform: {platform}")
        return []


def get_models_by_capability(capability: str) -> List[str]:
    """
    Get all model names with a specific capability.

    Args:
        capability: Capability level ("reasoning", "general", "fast", "balanced")

    Returns:
        List of model names
    """
    try:
        capability_enum = ModelCapability(capability.lower())
        return [
            name for name, config in AVAILABLE_MODELS.items()
            if config.capability == capability_enum
        ]
    except ValueError:
        logger.error(f"Invalid capability: {capability}")
        return []


def validate_model(model_name: str) -> bool:
    """
    Check if a model name is valid.

    Args:
        model_name: Model name to validate

    Returns:
        True if model is available, False otherwise
    """
    return model_name in AVAILABLE_MODELS


def get_model_info(model_name: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific model.

    Args:
        model_name: Name of the model

    Returns:
        Model information dictionary or None if not found
    """
    if model_name not in AVAILABLE_MODELS:
        return None

    config = AVAILABLE_MODELS[model_name]
    return {
        "name": config.name,
        "display_name": config.display_name,
        "description": config.description,
        "platform": config.platform.value,
        "capability": config.capability.value,
        "temperature": config.temperature,
        "best_for": config.best_for
    }