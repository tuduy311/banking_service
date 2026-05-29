from __future__ import annotations

import grpc

from app.core.schemas import IntentResult

from intent_service import intent_service_pb2, intent_service_pb2_grpc


class GrpcIntentClient:
    def __init__(self, host: str, port: int, timeout: float, model_id: str) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.model_id = model_id

    def predict(self, message: str) -> IntentResult:
        target = f"{self.host}:{self.port}"
        with grpc.insecure_channel(target) as channel:
            grpc.channel_ready_future(channel).result(timeout=self.timeout)
            stub = intent_service_pb2_grpc.IntentServiceStub(channel)
            response = stub.IntentRecognizer(
                intent_service_pb2.IntentRequest(message=message),
                timeout=self.timeout,
            )

        return IntentResult(
            intent=response.intent,
            confidence=response.confidence,
            model_id=self.model_id,
            reason=response.reason,
        )
