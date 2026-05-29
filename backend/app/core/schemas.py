from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PriorityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RouteAction(str, Enum):
    reply = "reply"
    ask_more_info = "ask_more_info"
    escalate = "escalate"


class CustomerRequest(BaseModel):
    customer_id: Optional[str] = None
    message: str = Field(..., min_length=3)


class IntentResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    intent: str
    confidence: float
    model_id: str
    reason: str


class PriorityResult(BaseModel):
    priority: PriorityLevel
    reason: str


class PolicyResult(BaseModel):
    policy_id: str
    title: str
    snippet: str
    required_fields: List[str]
    escalation_hint: str


class DraftResult(BaseModel):
    draft_reply: str
    missing_information: List[str]
    next_action: str
    used_llm: bool


class ValidationResult(BaseModel):
    is_valid: bool
    issues: List[str]


class RoutingResult(BaseModel):
    action: RouteAction
    reason: str


class NodeTrace(BaseModel):
    node_name: str
    output: dict


class AgentResponse(BaseModel):
    intent: IntentResult
    priority: PriorityResult
    policy: PolicyResult
    draft: DraftResult
    validation: ValidationResult
    routing: RoutingResult
    trace: List[NodeTrace]


class SystemConfig(BaseModel):
    app_name: str
    app_version: str
    intent_service_host: str
    intent_service_port: int
    intent_service_timeout: float
    ollama_base_url: str
    generation_model: str
    intent_model_id: str
    intent_model_path: str
    intent_min_confidence: float
    enable_llm_drafting: bool
    enable_local_intent_fallback: bool
