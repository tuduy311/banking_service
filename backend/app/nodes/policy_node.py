from app.core.schemas import PolicyResult
from app.data.policies import get_policy_by_intent


class PolicyNode:
    def run(self, intent: str) -> PolicyResult:
        policy = get_policy_by_intent(intent)
        return PolicyResult(**policy)
