from app.core.schemas import DraftResult, IntentResult, ValidationResult


class ValidationNode:
    def __init__(self, min_intent_confidence: float) -> None:
        self.min_intent_confidence = min_intent_confidence

    def run(self, intent: IntentResult, draft: DraftResult) -> ValidationResult:
        issues = []

        if intent.confidence < self.min_intent_confidence:
            issues.append("Low intent confidence.")

        if len(draft.draft_reply.strip()) < 60:
            issues.append("Draft response is too short.")

        if len(draft.missing_information) > 2:
            issues.append("Too many required details are missing.")

        return ValidationResult(is_valid=len(issues) == 0, issues=issues)
