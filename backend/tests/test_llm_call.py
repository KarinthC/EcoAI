import pytest
from app.services.carbon.ecologits.llm_call import compute

# ============================================================================
# Liste exhaustive des combinaisons (provider, model) valides
# Telle que définie dans le fichier models.json fourni par Ecologits.
# ============================================================================

VALID_COMBINATIONS = [
    # ---- OpenAI ----
    ("openai", "chat-latest"),
    ("openai", "gpt-3.5-turbo"),
    ("openai", "gpt-3.5-turbo-0125"),
    ("openai", "gpt-3.5-turbo-1106"),
    ("openai", "gpt-3.5-turbo-16k"),
    ("openai", "gpt-3.5-turbo-instruct"),
    ("openai", "gpt-3.5-turbo-instruct-0914"),
    ("openai", "gpt-4"),
    ("openai", "gpt-4-0613"),
    ("openai", "gpt-4-turbo"),
    ("openai", "gpt-4-turbo-2024-04-09"),
    ("openai", "gpt-4.1"),
    ("openai", "gpt-4.1-2025-04-14"),
    ("openai", "gpt-4.1-mini"),
    ("openai", "gpt-4.1-mini-2025-04-14"),
    ("openai", "gpt-4.1-nano"),
    ("openai", "gpt-4.1-nano-2025-04-14"),
    ("openai", "gpt-4o"),
    ("openai", "gpt-4o-2024-05-13"),
    ("openai", "gpt-4o-2024-08-06"),
    ("openai", "gpt-4o-2024-11-20"),
    ("openai", "gpt-4o-mini"),
    ("openai", "gpt-4o-mini-2024-07-18"),
    ("openai", "gpt-4o-mini-search-preview"),
    ("openai", "gpt-4o-mini-search-preview-2025-03-11"),
    ("openai", "gpt-4o-mini-transcribe"),
    ("openai", "gpt-4o-mini-transcribe-2025-03-20"),
    ("openai", "gpt-4o-mini-transcribe-2025-12-15"),
    ("openai", "gpt-4o-mini-tts"),
    ("openai", "gpt-4o-mini-tts-2025-03-20"),
    ("openai", "gpt-4o-mini-tts-2025-12-15"),
    ("openai", "gpt-4o-search-preview"),
    ("openai", "gpt-4o-search-preview-2025-03-11"),
    ("openai", "gpt-5"),
    ("openai", "gpt-5-2025-08-07"),
    ("openai", "gpt-5-chat-latest"),
    ("openai", "gpt-5-codex"),
    ("openai", "gpt-5-mini"),
    ("openai", "gpt-5-mini-2025-08-07"),
    ("openai", "gpt-5-nano"),
    ("openai", "gpt-5-nano-2025-08-07"),
    ("openai", "gpt-5-pro"),
    ("openai", "gpt-5-pro-2025-10-06"),
    ("openai", "gpt-5-search-api"),
    ("openai", "gpt-5-search-api-2025-10-14"),
    ("openai", "gpt-5.1"),
    ("openai", "gpt-5.1-2025-11-13"),
    ("openai", "gpt-5.1-chat-latest"),
    ("openai", "gpt-5.1-codex"),
    ("openai", "gpt-5.1-codex-max"),
    ("openai", "gpt-5.1-codex-mini"),
    ("openai", "gpt-5.2"),
    ("openai", "gpt-5.2-2025-12-11"),
    ("openai", "gpt-5.2-chat-latest"),
    ("openai", "gpt-5.2-codex"),
    ("openai", "gpt-5.2-pro"),
    ("openai", "gpt-5.2-pro-2025-12-11"),
    ("openai", "gpt-5.3-chat-latest"),
    ("openai", "gpt-5.3-codex"),
    ("openai", "gpt-5.4"),
    ("openai", "gpt-5.4-2026-03-05"),
    ("openai", "gpt-5.4-mini"),
    ("openai", "gpt-5.4-mini-2026-03-17"),
    ("openai", "gpt-5.4-nano"),
    ("openai", "gpt-5.4-nano-2026-03-17"),
    ("openai", "gpt-5.4-pro"),
    ("openai", "gpt-5.4-pro-2026-03-05"),
    ("openai", "gpt-5.5"),
    ("openai", "gpt-5.5-2026-04-23"),
    ("openai", "gpt-5.5-pro"),
    ("openai", "gpt-5.5-pro-2026-04-23"),
    ("openai", "o1"),
    ("openai", "o1-2024-12-17"),
    ("openai", "o3-mini"),
    ("openai", "o3-mini-2025-01-31"),
    ("openai", "o4-mini"),
    ("openai", "o4-mini-2025-04-16"),
    ("openai", "o4-mini-deep-research"),
    ("openai", "o4-mini-deep-research-2025-06-26"),

    # ---- Anthropic ----
    ("anthropic", "claude-haiku-4-5-20251001"),
    ("anthropic", "claude-opus-4-1-20250805"),
    ("anthropic", "claude-opus-4-20250514"),
    ("anthropic", "claude-opus-4-5-20251101"),
    ("anthropic", "claude-opus-4-6"),
    ("anthropic", "claude-opus-4-7"),
    ("anthropic", "claude-opus-4-8"),
    ("anthropic", "claude-sonnet-4-20250514"),
    ("anthropic", "claude-sonnet-4-5-20250929"),
    ("anthropic", "claude-sonnet-4-6"),

    # ---- Google (via google_genai) ----
    ("google_genai", "gemini-2.0-flash"),
    ("google_genai", "gemini-2.0-flash-001"),
    ("google_genai", "gemini-2.0-flash-lite"),
    ("google_genai", "gemini-2.0-flash-lite-001"),
    ("google_genai", "gemini-2.5-flash"),
    ("google_genai", "gemini-2.5-flash-image"),
    ("google_genai", "gemini-2.5-flash-lite"),
    ("google_genai", "gemini-2.5-pro"),
    ("google_genai", "gemini-3-flash-preview"),
    ("google_genai", "gemini-3-pro-image-preview"),
    ("google_genai", "gemini-3-pro-preview"),
    ("google_genai", "gemini-3.1-flash-image-preview"),
    ("google_genai", "gemini-3.1-flash-lite"),
    ("google_genai", "gemini-3.1-flash-lite-preview"),
    ("google_genai", "gemini-3.1-pro-preview"),
    ("google_genai", "gemini-3.1-pro-preview-customtools"),
    ("google_genai", "gemini-3.5-flash"),
    ("google_genai", "gemini-flash-latest"),
    ("google_genai", "gemini-flash-lite-latest"),
    ("google_genai", "gemini-pro-latest"),
    ("google_genai", "gemma-4-26b-a4b-it"),
    ("google_genai", "gemma-4-31b-it"),

    # ---- Mistral (propriétaire) ----
    ("mistralai", "codestral-2405"),
    ("mistralai", "codestral-2411-rc5"),
    ("mistralai", "codestral-2412"),
    ("mistralai", "codestral-2501"),
    ("mistralai", "codestral-2508"),
    ("mistralai", "codestral-latest"),
    ("mistralai", "devstral-2512"),
    ("mistralai", "devstral-latest"),
    ("mistralai", "devstral-medium-latest"),
    ("mistralai", "magistral-medium-2509"),
    ("mistralai", "magistral-medium-latest"),
    ("mistralai", "magistral-small-2509"),
    ("mistralai", "magistral-small-latest"),
    ("mistralai", "ministral-14b-2512"),
    ("mistralai", "ministral-14b-latest"),
    ("mistralai", "ministral-3b-2512"),
    ("mistralai", "ministral-3b-latest"),
    ("mistralai", "ministral-8b-2512"),
    ("mistralai", "ministral-8b-latest"),
    ("mistralai", "mistral-large-2512"),
    ("mistralai", "mistral-large-latest"),
    ("mistralai", "mistral-medium"),
    ("mistralai", "mistral-medium-2505"),
    ("mistralai", "mistral-medium-2508"),
    ("mistralai", "mistral-medium-2604"),
    ("mistralai", "mistral-medium-3"),
    ("mistralai", "mistral-medium-3-5"),
    ("mistralai", "mistral-medium-3.5"),
    ("mistralai", "mistral-medium-latest"),
    ("mistralai", "mistral-small-2506"),
    ("mistralai", "mistral-small-2603"),
    ("mistralai", "mistral-small-latest"),
    ("mistralai", "mistral-tiny-2407"),
    ("mistralai", "mistral-tiny-latest"),
    ("mistralai", "open-mistral-7b"),
    ("mistralai", "open-mistral-nemo"),
    ("mistralai", "open-mistral-nemo-2407"),
    ("mistralai", "pixtral-12b"),
    ("mistralai", "pixtral-12b-2409"),
    ("mistralai", "pixtral-12b-latest"),
    ("mistralai", "voxtral-mini-2507"),
    ("mistralai", "voxtral-mini-2509"),
    ("mistralai", "voxtral-mini-2602"),
    ("mistralai", "voxtral-mini-latest"),
    ("mistralai", "voxtral-small-2507"),
    ("mistralai", "voxtral-small-latest"),

    # ---- Cohere ----
    ("cohere", "c4ai-aya-expanse-32b"),
    ("cohere", "c4ai-aya-vision-32b"),
    ("cohere", "command-a-03-2025"),
    ("cohere", "command-a-plus-05-2026"),
    ("cohere", "command-a-reasoning-08-2025"),
    ("cohere", "command-a-translate-08-2025"),
    ("cohere", "command-a-vision-07-2025"),
    ("cohere", "command-r-08-2024"),
    ("cohere", "command-r-plus-08-2024"),
    ("cohere", "command-r7b-12-2024"),
    ("cohere", "command-r7b-arabic-02-2025"),

    # ---- Hugging Face Hub (regroupe Meta, Microsoft, Databricks, Mistral open, Google open, Cohere open) ----
    ("huggingface_hub", "CohereForAI/aya-23-35B"),
    ("huggingface_hub", "CohereForAI/aya-23-8B"),
    ("huggingface_hub", "CohereForAI/c4ai-command-r-plus"),
    ("huggingface_hub", "CohereForAI/c4ai-command-r-plus-4bit"),
    ("huggingface_hub", "CohereForAI/c4ai-command-r-v01"),
    ("huggingface_hub", "CohereForAI/c4ai-command-r-v01-4bit"),
    ("huggingface_hub", "databricks/dbrx-base"),
    ("huggingface_hub", "databricks/dbrx-instruct"),
    ("huggingface_hub", "databricks/dolly-v1-6b"),
    ("huggingface_hub", "databricks/dolly-v2-12b"),
    ("huggingface_hub", "databricks/dolly-v2-3b"),
    ("huggingface_hub", "databricks/dolly-v2-7b"),
    ("huggingface_hub", "meta-llama/CodeLlama-13b-hf"),
    ("huggingface_hub", "meta-llama/CodeLlama-13b-Instruct-hf"),
    ("huggingface_hub", "meta-llama/CodeLlama-13b-Python-hf"),
    ("huggingface_hub", "meta-llama/CodeLlama-34b-hf"),
    ("huggingface_hub", "meta-llama/CodeLlama-34b-Instruct-hf"),
    ("huggingface_hub", "meta-llama/CodeLlama-34b-Python-hf"),
    ("huggingface_hub", "meta-llama/CodeLlama-70b-hf"),
    ("huggingface_hub", "meta-llama/CodeLlama-70b-Instruct-hf"),
    ("huggingface_hub", "meta-llama/CodeLlama-70b-Python-hf"),
    ("huggingface_hub", "meta-llama/CodeLlama-7b-hf"),
    ("huggingface_hub", "meta-llama/CodeLlama-7b-Instruct-hf"),
    ("huggingface_hub", "meta-llama/CodeLlama-7b-Python-hf"),
    ("huggingface_hub", "meta-llama/Llama-2-13b"),
    ("huggingface_hub", "meta-llama/Llama-2-13b-chat"),
    ("huggingface_hub", "meta-llama/Llama-2-13b-chat-hf"),
    ("huggingface_hub", "meta-llama/Llama-2-13b-hf"),
    ("huggingface_hub", "meta-llama/Llama-2-70b"),
    ("huggingface_hub", "meta-llama/Llama-2-70b-chat"),
    ("huggingface_hub", "meta-llama/Llama-2-70b-chat-hf"),
    ("huggingface_hub", "meta-llama/Llama-2-70b-hf"),
    ("huggingface_hub", "meta-llama/Llama-2-7b"),
    ("huggingface_hub", "meta-llama/Llama-2-7b-chat"),
    ("huggingface_hub", "meta-llama/Llama-2-7b-chat-hf"),
    ("huggingface_hub", "meta-llama/Llama-2-7b-hf"),
    ("huggingface_hub", "meta-llama/Llama-Guard-3-8B"),
    ("huggingface_hub", "meta-llama/Llama-Guard-3-8B-INT8"),
    ("huggingface_hub", "meta-llama/LlamaGuard-7b"),
    ("huggingface_hub", "meta-llama/Meta-Llama-3-70B"),
    ("huggingface_hub", "meta-llama/Meta-Llama-3-70B-Instruct"),
    ("huggingface_hub", "meta-llama/Meta-Llama-3-8B"),
    ("huggingface_hub", "meta-llama/Meta-Llama-3-8B-Instruct"),
    ("huggingface_hub", "meta-llama/Meta-Llama-3.1-405B"),
    ("huggingface_hub", "meta-llama/Meta-Llama-3.1-405B-FP8"),
    ("huggingface_hub", "meta-llama/Meta-Llama-3.1-405B-Instruct"),
    ("huggingface_hub", "meta-llama/Meta-Llama-3.1-405B-Instruct-FP8"),
    ("huggingface_hub", "meta-llama/Meta-Llama-3.1-70B"),
    ("huggingface_hub", "meta-llama/Meta-Llama-3.1-70B-Instruct"),
    ("huggingface_hub", "meta-llama/Meta-Llama-3.1-8B"),
    ("huggingface_hub", "meta-llama/Meta-Llama-3.1-8B-Instruct"),
    ("huggingface_hub", "meta-llama/Meta-Llama-Guard-2-8B"),
    ("huggingface_hub", "meta-llama/Prompt-Guard-86M"),
    ("huggingface_hub", "microsoft/phi-1"),
    ("huggingface_hub", "microsoft/phi-1_5"),
    ("huggingface_hub", "microsoft/Phi-3-medium-128k-instruct"),
    ("huggingface_hub", "microsoft/Phi-3-medium-128k-instruct-onnx-cpu"),
    ("huggingface_hub", "microsoft/Phi-3-medium-128k-instruct-onnx-cuda"),
    ("huggingface_hub", "microsoft/Phi-3-medium-128k-instruct-onnx-directml"),
    ("huggingface_hub", "microsoft/Phi-3-medium-4k-instruct"),
    ("huggingface_hub", "microsoft/Phi-3-medium-4k-instruct-onnx-cpu"),
    ("huggingface_hub", "microsoft/Phi-3-medium-4k-instruct-onnx-cuda"),
    ("huggingface_hub", "microsoft/Phi-3-medium-4k-instruct-onnx-directml"),
    ("huggingface_hub", "microsoft/Phi-3-mini-128k-instruct"),
    ("huggingface_hub", "microsoft/Phi-3-mini-128k-instruct-onnx"),
    ("huggingface_hub", "microsoft/Phi-3-mini-4k-instruct"),
    ("huggingface_hub", "microsoft/Phi-3-mini-4k-instruct-gguf"),
    ("huggingface_hub", "microsoft/Phi-3-mini-4k-instruct-onnx"),
    ("huggingface_hub", "microsoft/Phi-3-mini-4k-instruct-onnx-web"),
    ("huggingface_hub", "microsoft/Phi-3-small-128k-instruct"),
    ("huggingface_hub", "microsoft/Phi-3-small-128k-instruct-onnx-cuda"),
    ("huggingface_hub", "microsoft/Phi-3-small-8k-instruct"),
    ("huggingface_hub", "microsoft/Phi-3-small-8k-instruct-onnx-cuda"),
    ("huggingface_hub", "microsoft/Phi-3-vision-128k-instruct"),
    ("huggingface_hub", "microsoft/Phi-3-vision-128k-instruct-onnx-cpu"),
    ("huggingface_hub", "microsoft/Phi-3-vision-128k-instruct-onnx-cuda"),
    ("huggingface_hub", "microsoft/Phi-3-vision-128k-instruct-onnx-directml"),
    ("huggingface_hub", "mistral-community/Codestral-22B-v0.1"),
    ("huggingface_hub", "mistral-community/Mistral-7B-Instruct-v0.3"),
    ("huggingface_hub", "mistral-community/Mistral-7B-v0.2"),
    ("huggingface_hub", "mistral-community/Mixtral-8x22B-Instruct-v0.1-4bit"),
    ("huggingface_hub", "mistral-community/Mixtral-8x22B-v0.1"),
    ("huggingface_hub", "mistral-community/Mixtral-8x22B-v0.1-4bit"),
    ("huggingface_hub", "mistral-community/Mixtral-8x22B-v0.1-AWQ"),
    ("huggingface_hub", "mistral-community/Mixtral-8x22B-v0.1-original"),
    ("huggingface_hub", "mistral-community/mixtral-8x22B-Instruct-v0.3-original"),
    ("huggingface_hub", "mistral-community/mixtral-8x22B-v0.3"),
    ("huggingface_hub", "mistral-community/mixtral-8x22B-v0.3-original"),
]

# ============================================================================
# Paramètres par défaut pour les tests
# ============================================================================
DEFAULT_PARAMS = {
    "output_tokens": 10000,
    "request_latency": 350,
}

# ============================================================================
# Tests
# ============================================================================

def test_llm_call_valid_combinations():
    """
    Vérifie que chaque combinaison valide retourne un résultat structuré
    avec un impact >= 0 (généralement > 0).
    """
    for provider, model in VALID_COMBINATIONS:
        params = {**DEFAULT_PARAMS, "provider": provider, "model": model}
        result = compute(params)

        assert "impact_kg" in result
        assert "level" in result
        assert isinstance(result["impact_kg"], (int, float))
        # Optionnel : on peut vérifier que l'impact est strictement positif
        # pour s'assurer que les données existent.
        assert result["impact_kg"] > 0


def test_llm_call_missing_provider_or_model():
    """Vérifie qu'une exception est levée si provider ou model est manquant."""
    with pytest.raises(ValueError, match="provider et model sont obligatoires"):
        compute({"output_tokens": 100, "request_latency": 100})

    with pytest.raises(ValueError, match="provider et model sont obligatoires"):
        compute({"provider": "openai", "output_tokens": 100, "request_latency": 100})


def test_llm_call_unsupported_model_returns_zero_impact():
    """
    Vérifie que lorsqu'un modèle n'est pas reconnu par Ecologits,
    la fonction compute retourne un impact de 0 (et non une exception).
    Ce comportement doit être implémenté dans compute.
    """
    params = {
        "provider": "openai",
        "model": "modele-inexistant",
        "output_tokens": 100,
        "request_latency": 100,
    }
    result = compute(params)

    assert "impact_kg" in result
    assert result["impact_kg"] == 0.0
    assert "level" in result


def test_llm_call_unknown_provider_handled_gracefully():
    """
    Vérifie qu'un provider totalement inconnu (non présent dans models.json)
    est traité sans exception et retourne un impact de 0.
    """
    params = {
        "provider": "inconnu",
        "model": "gpt-4o",
        "output_tokens": 100,
        "request_latency": 100,
    }
    # Si compute lève une exception, adaptez ce test.
    # Ici on suppose qu'il retourne un impact 0.
    result = compute(params)
    assert result["impact_kg"] == 0.0