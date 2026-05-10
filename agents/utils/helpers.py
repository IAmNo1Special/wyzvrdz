"""Helper functions for the agents package."""

from google.adk.models.lite_llm import LiteLlm

from ..configs import WYZVRD_SETTINGS


def get_model(agent_name: str | None = None):
    """Get the model configuration for an agent.

    Args:
        agent_name: Name of the agent, defaults to "root".

    Returns:
        The model name or LiteLlm instance.
    """
    name = agent_name or "root"

    if bool(WYZVRD_SETTINGS.use_ollama):
        # The YAML has models.ollama.root, models.ollama.compendium, etc.
        ollama_models = getattr(
            WYZVRD_SETTINGS.models, "ollama", WYZVRD_SETTINGS.models
        )
        ollama_model_name = getattr(
            ollama_models, name, getattr(ollama_models, "root", None)
        )

        # Fallback if still None
        if ollama_model_name is None:
            ollama_model_name = getattr(
                WYZVRD_SETTINGS.models, "ollama_root", "ollama_chat/gemma4:31b"
            )

        if getattr(WYZVRD_SETTINGS.app, "ollama_mode", None) == "cloud":
            if ":" in ollama_model_name:
                ollama_model_name = f"{ollama_model_name}-cloud"
            else:
                ollama_model_name = f"{ollama_model_name}:cloud"

        return LiteLlm(model=ollama_model_name)

    # The YAML has models.gemini.root, models.gemini.compendium, etc.
    gemini_models = getattr(
        WYZVRD_SETTINGS.models, "gemini", WYZVRD_SETTINGS.models
    )
    model_name = getattr(
        gemini_models, name, getattr(gemini_models, "root", None)
    )

    if model_name is None:
        model_name = getattr(WYZVRD_SETTINGS.models, "root", "gemini-2.5-flash")

    return model_name
