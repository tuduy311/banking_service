from fastapi import FastAPI

from app.agent.orchestrator import AgentOrchestrator
from app.core.schemas import AgentResponse, CustomerRequest, SystemConfig
from app.core.settings import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)
orchestrator = AgentOrchestrator()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/config", response_model=SystemConfig)
def config() -> SystemConfig:
    return SystemConfig(
        app_name=settings.app_name,
        app_version=settings.app_version,
        intent_service_host=settings.intent_service_host,
        intent_service_port=settings.intent_service_port,
        intent_service_timeout=settings.intent_service_timeout,
        ollama_base_url=settings.ollama_base_url,
        generation_model=settings.generation_model,
        intent_model_id=settings.intent_model_id,
        intent_model_path=settings.intent_model_path,
        intent_min_confidence=settings.intent_min_confidence,
        enable_llm_drafting=settings.enable_llm_drafting,
        enable_local_intent_fallback=settings.enable_local_intent_fallback,
    )


@app.post("/v1/agent/respond", response_model=AgentResponse)
@app.post("/run-agent", response_model=AgentResponse)
def respond(request: CustomerRequest) -> AgentResponse:
    return orchestrator.run(request)
