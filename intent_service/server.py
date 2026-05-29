from __future__ import annotations

from concurrent import futures
import logging
import os

import grpc

from app.core.settings import settings
from app.nodes.intent_node import IntentNode
from intent_service import intent_service_pb2, intent_service_pb2_grpc


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentService(intent_service_pb2_grpc.IntentServiceServicer):
    def __init__(self) -> None:
        self.intent_node = IntentNode(
            model_id=settings.intent_model_id,
            model_path=settings.intent_model_path,
        )

    def IntentRecognizer(self, request, context):  # noqa: N802
        result = self.intent_node.run(request.message)
        return intent_service_pb2.IntentResponse(
            intent=result.intent,
            confidence=result.confidence,
            reason=result.reason,
        )


def serve() -> None:
    port = int(os.getenv("GRPC_PORT", str(settings.intent_service_port)))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    intent_service_pb2_grpc.add_IntentServiceServicer_to_server(IntentService(), server)
    server.add_insecure_port(f"[::]:{port}")
    logger.info("Intent service listening on port %s", port)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
