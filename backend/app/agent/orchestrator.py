from app.clients.ollama_client import OllamaClient
from app.clients.grpc_intent_client import GrpcIntentClient
from app.core.schemas import AgentResponse, CustomerRequest, NodeTrace
from app.core.settings import settings
from app.nodes.draft_node import DraftNode
from app.nodes.intent_node import IntentNode
from app.nodes.policy_node import PolicyNode
from app.nodes.priority_node import PriorityNode
from app.nodes.router_node import RouterNode
from app.nodes.validation_node import ValidationNode


class AgentOrchestrator:
    def __init__(self) -> None:
        self.intent_client = GrpcIntentClient(
            host=settings.intent_service_host,
            port=settings.intent_service_port,
            timeout=settings.intent_service_timeout,
            model_id=settings.intent_model_id,
        )
        self.intent_node = IntentNode(
            model_id=settings.intent_model_id,
            model_path=settings.intent_model_path,
        )
        self.priority_node = PriorityNode()
        self.policy_node = PolicyNode()

        llm_client = None
        if settings.enable_llm_drafting:
            llm_client = OllamaClient(
                base_url=settings.ollama_base_url,
                model=settings.generation_model,
            )
        self.draft_node = DraftNode(llm_client=llm_client)

        self.validation_node = ValidationNode(
            min_intent_confidence=settings.intent_min_confidence
        )
        self.router_node = RouterNode()

    def run(self, request: CustomerRequest) -> AgentResponse:
        trace = []

        try:
            intent = self.intent_client.predict(request.message)
        except Exception:
            if not settings.enable_local_intent_fallback:
                raise
            intent = self.intent_node.run(request.message)
        trace.append(NodeTrace(node_name="intent_node", output=intent.model_dump()))

        priority = self.priority_node.run(request.message)
        trace.append(NodeTrace(node_name="priority_node", output=priority.model_dump()))

        policy = self.policy_node.run(intent.intent)
        trace.append(NodeTrace(node_name="policy_node", output=policy.model_dump()))

        draft = self.draft_node.run(
            message=request.message,
            intent=intent.intent,
            priority=priority,
            policy=policy,
        )
        trace.append(NodeTrace(node_name="draft_node", output=draft.model_dump()))

        validation = self.validation_node.run(intent=intent, draft=draft)
        trace.append(NodeTrace(node_name="validation_node", output=validation.model_dump()))

        routing = self.router_node.run(
            priority=priority,
            validation=validation,
            has_missing_info=bool(draft.missing_information),
        )
        trace.append(NodeTrace(node_name="router_node", output=routing.model_dump()))

        return AgentResponse(
            intent=intent,
            priority=priority,
            policy=policy,
            draft=draft,
            validation=validation,
            routing=routing,
            trace=trace,
        )
