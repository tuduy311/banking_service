from typing import List, Optional
import logging

from app.clients.base import BaseLLMClient
from app.core.schemas import DraftResult, PolicyResult, PriorityResult

logger = logging.getLogger(__name__)


class DraftNode:
    def __init__(self, llm_client: Optional[BaseLLMClient] = None) -> None:
        self.llm_client = llm_client

    def _extract_missing_fields(self, message: str, required_fields: List[str]) -> List[str]:
        text = message.lower()
        missing = []
        for field in required_fields:
            if field.lower().replace("_", " ") not in text:
                missing.append(field)
        return missing

    def _template_draft(self, message: str, intent: str, priority: str, policy: PolicyResult, missing_info: List[str]) -> str:
        missing_text = (
            " To help you faster, please share: " + ", ".join(missing_info) + "."
            if missing_info
            else ""
        )
        return (
            f"Thanks for reaching out about '{intent}'. "
            f"We see this is a '{priority}' priority case. "
            f"Based on '{policy.title}', {policy.snippet}{missing_text}"
        )

    def _build_llm_prompt(
        self,
        message: str,
        intent: str,
        priority: PriorityResult,
        policy: PolicyResult,
        missing_info: List[str],
    ) -> str:
        missing_text = ", ".join(missing_info) if missing_info else "none"
        return (
            "You are a helpful banking support assistant.\n"
            "Rewrite the response in a warm, concise, and natural tone.\n"
            "Do not sound like a template.\n"
            "If information is missing, politely ask for it in the same reply.\n"
            "Keep the response short and practical.\n\n"
            f"Customer message: {message}\n"
            f"Intent: {intent}\n"
            f"Priority: {priority.priority.value}\n"
            f"Policy title: {policy.title}\n"
            f"Policy snippet: {policy.snippet}\n"
            f"Missing information: {missing_text}\n"
            "\nWrite the final customer-facing reply:"
        )

    def run(self, message: str, intent: str, priority: PriorityResult, policy: PolicyResult) -> DraftResult:
        missing_info = self._extract_missing_fields(message, policy.required_fields)

        if self.llm_client is not None:
            prompt = self._build_llm_prompt(
                message=message,
                intent=intent,
                priority=priority,
                policy=policy,
                missing_info=missing_info,
            )
            try:
                logger.info(f"[DraftNode] Calling LLM with prompt (intent={intent})")
                draft_reply = self.llm_client.generate(prompt)
                if draft_reply:
                    logger.info(f"[DraftNode] ✅ LLM generated successfully")
                    return DraftResult(
                        draft_reply=draft_reply,
                        missing_information=missing_info,
                        next_action="collect_missing_info" if missing_info else "send_reply",
                        used_llm=True,
                    )
                else:
                    logger.warning(f"[DraftNode] LLM returned empty response")
            except Exception as e:
                logger.error(f"[DraftNode] ❌ LLM call failed: {type(e).__name__}: {e}")

        return DraftResult(
            draft_reply=self._template_draft(
                message=message,
                intent=intent,
                priority=priority.priority.value,
                policy=policy,
                missing_info=missing_info,
            ),
            missing_information=missing_info,
            next_action="collect_missing_info" if missing_info else "send_reply",
            used_llm=False,
        )
