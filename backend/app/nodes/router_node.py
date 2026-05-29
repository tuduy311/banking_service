from app.core.schemas import PriorityLevel, PriorityResult, RouteAction, RoutingResult, ValidationResult


class RouterNode:
    def run(self, priority: PriorityResult, validation: ValidationResult, has_missing_info: bool) -> RoutingResult:
        if priority.priority == PriorityLevel.high:
            return RoutingResult(action=RouteAction.escalate, reason="High-risk case requires human support.")

        if not validation.is_valid:
            if has_missing_info:
                return RoutingResult(action=RouteAction.ask_more_info, reason="Need additional customer details before final reply.")
            return RoutingResult(action=RouteAction.escalate, reason="Validation failed without clear recovery path.")

        if has_missing_info:
            return RoutingResult(action=RouteAction.ask_more_info, reason="Missing required details from customer.")

        return RoutingResult(action=RouteAction.reply, reason="Response is valid and can be sent automatically.")
