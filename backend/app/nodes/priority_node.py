from app.core.schemas import PriorityLevel, PriorityResult


class PriorityNode:
    def run(self, message: str) -> PriorityResult:
        text = message.lower()

        # High priority: blocked, security, fraud, money loss
        high_signals = [
            "lost money", "mat tien",
            "fraud", "scam", "suspicious", "unauthorized",
            "blocked", "khoa", "cannot login", "locked",  # ← Thêm đây
            "tai khoan bi khoa",
        ]
        
        # Medium priority: service issues, delivery delays
        medium_signals = ["failed", "delay", "not received", "refund", "chargeback", "pending"]

        if any(token in text for token in high_signals):
            return PriorityResult(priority=PriorityLevel.high, reason="Risk or financial loss signal detected.")

        if any(token in text for token in medium_signals):
            return PriorityResult(priority=PriorityLevel.medium, reason="Service issue detected but no critical risk signal.")

        return PriorityResult(priority=PriorityLevel.low, reason="General inquiry with no urgent risk signal.")
