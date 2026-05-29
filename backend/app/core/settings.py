import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load biến từ file .env
load_dotenv()

@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Banking AI Agent MVP")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    intent_service_host: str = os.getenv("INTENT_SERVICE_HOST", "localhost")
    intent_service_port: int = int(os.getenv("INTENT_SERVICE_PORT", "50051"))
    intent_service_timeout: float = float(os.getenv("INTENT_SERVICE_TIMEOUT", "10"))
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    generation_model: str = os.getenv("GENERATION_MODEL", "gpt-oss:20b")
    intent_model_id: str = os.getenv("INTENT_MODEL_ID", "lab2-intent-model")
    intent_model_path: str = os.getenv("INTENT_MODEL_PATH", "")
    intent_min_confidence: float = float(os.getenv("INTENT_MIN_CONFIDENCE", "0.55"))
    enable_llm_drafting: bool = os.getenv("ENABLE_LLM_DRAFTING", "false").lower() == "true"
    enable_local_intent_fallback: bool = os.getenv("ENABLE_LOCAL_INTENT_FALLBACK", "true").lower() == "true"


settings = Settings()
