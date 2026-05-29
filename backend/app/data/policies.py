from typing import Dict

# Intent-to-policy category mapping for 77 Lab2 intents
INTENT_CATEGORY_MAP = {
    # Transfer-related intents
    "beneficiary_not_allowed": "transfer_failure",
    "failed_transfer": "transfer_failure",
    "declined_transfer": "transfer_failure",
    "pending_transfer": "transfer_failure",
    "transfer_not_received_by_recipient": "transfer_failure",
    "transfer_timing": "transfer_failure",
    "cancel_transfer": "transfer_failure",
    "transfer_fee_charged": "transfer_failure",
    "transfer_into_account": "transfer_failure",
    "balance_not_updated_after_bank_transfer": "transfer_failure",
    "balance_not_updated_after_cheque_or_cash_deposit": "transfer_failure",
    "top_up_failed": "transfer_failure",
    "top_up_reverted": "transfer_failure",
    "top_up_by_bank_transfer_charge": "general_inquiry",
    "top_up_by_card_charge": "general_inquiry",
    "top_up_by_cash_or_cheque": "transfer_failure",
    "topping_up_by_card": "transfer_failure",
    "declined_cash_withdrawal": "transfer_failure",
    "receiving_money": "transfer_failure",
    "pending_cash_withdrawal": "refund_request",
    "cash_withdrawal_not_recognised": "refund_request",
    "cash_withdrawal_charge": "general_inquiry",
    "wrong_amount_of_cash_received": "refund_request",
    "wrong_exchange_rate_for_cash_withdrawal": "refund_request",
    
    # Card-related intents
    "card_arrival": "card_not_received",
    "card_delivery_estimate": "card_not_received",
    "card_not_working": "card_not_received",
    "activate_my_card": "card_not_received",
    "lost_or_stolen_card": "card_not_received",
    "compromised_card": "card_not_received",
    "card_about_to_expire": "card_not_received",
    "card_payment_not_recognised": "card_not_received",
    "card_payment_fee_charged": "card_not_received",
    "card_payment_wrong_exchange_rate": "card_not_received",
    "declined_card_payment": "card_not_received",
    "contactless_not_working": "card_not_received",
    "card_swallowed": "card_not_received",
    "getting_virtual_card": "card_not_received",
    "getting_spare_card": "card_not_received",
    "order_physical_card": "card_not_received",
    "get_physical_card": "card_not_received",
    "get_disposable_virtual_card": "card_not_received",
    "virtual_card_not_working": "card_not_received",
    "visa_or_mastercard": "card_not_received",
    "pending_card_payment": "refund_request",
    
    # Blocked/Security-related intents
    "pin_blocked": "blocked_account",
    "passcode_forgotten": "blocked_account",
    "unable_to_verify_identity": "blocked_account",
    "verify_my_identity": "blocked_account",
    "why_verify_identity": "blocked_account",
    "verify_source_of_funds": "blocked_account",
    "verify_top_up": "blocked_account",
    "terminate_account": "blocked_account",
    "lost_or_stolen_phone": "blocked_account",
    "change_pin": "blocked_account",
    
    # Refund/Dispute-related intents
    "request_refund": "refund_request",
    "Refund_not_showing_up": "refund_request",
    "refund_not_showing_up": "refund_request",
    "reverted_card_payment?": "refund_request",
    "transaction_charged_twice": "refund_request",
    "direct_debit_payment_not_recognised": "refund_request",
    "extra_charge_on_statement": "refund_request",
    "pending_top_up": "refund_request",
    
    # General inquiry / info intents
    "age_limit": "general_inquiry",
    "apple_pay_or_google_pay": "general_inquiry",
    "atm_support": "general_inquiry",
    "automatic_top_up": "general_inquiry",
    "card_acceptance": "general_inquiry",
    "card_linking": "general_inquiry",
    "country_support": "general_inquiry",
    "disposable_card_limits": "general_inquiry",
    "edit_personal_details": "general_inquiry",
    "exchange_charge": "general_inquiry",
    "exchange_rate": "general_inquiry",
    "exchange_via_app": "general_inquiry",
    "fiat_currency_support": "general_inquiry",
    "supported_cards_and_currencies": "general_inquiry",
}


POLICIES: Dict[str, dict] = {
    "transfer_failure": {
        "policy_id": "POL-001",
        "title": "Transfer Failure Handling",
        "snippet": "If a transfer fails, verify transaction status, receiver details, and available balance before retrying.",
        "required_fields": ["transaction_time", "amount", "receiver_account"],
        "escalation_hint": "Escalate if money was debited but receiver did not get funds after 30 minutes.",
    },
    "card_not_received": {
        "policy_id": "POL-002",
        "title": "Card Delivery Delay",
        "snippet": "Cards are usually delivered in 5-7 business days. Confirm shipping address and issue date.",
        "required_fields": ["card_type", "issue_date", "delivery_address"],
        "escalation_hint": "Escalate if delivery exceeds 10 business days.",
    },
    "blocked_account": {
        "policy_id": "POL-003",
        "title": "Blocked Account Security",
        "snippet": "For blocked accounts, verify identity and recent suspicious activity before unblocking.",
        "required_fields": ["last_successful_login", "registered_phone"],
        "escalation_hint": "Always escalate if suspicious login or fraud concern is mentioned.",
    },
    "refund_request": {
        "policy_id": "POL-004",
        "title": "Refund Request Process",
        "snippet": "Collect transaction reference and merchant details. Standard refund review takes 3-10 business days.",
        "required_fields": ["transaction_id", "merchant_name", "amount"],
        "escalation_hint": "Escalate if dispute involves unauthorized transactions.",
    },
    "general_inquiry": {
        "policy_id": "POL-000",
        "title": "General Inquiry",
        "snippet": "Provide concise guidance and request missing details for account-specific support.",
        "required_fields": [],
        "escalation_hint": "Escalate only if customer reports urgent risk or financial loss.",
    },
}


def get_policy_by_intent(intent: str) -> dict:
    intent_normalized = intent.lower().strip()
    
    # Try direct match in policy (5 main intents)
    if intent_normalized in POLICIES:
        return POLICIES[intent_normalized]
    
    # Try category mapping (77 Lab2 intents → 5 categories)
    category = INTENT_CATEGORY_MAP.get(intent_normalized)
    if category and category in POLICIES:
        return POLICIES[category]
    
    # Fallback to general inquiry
    return POLICIES["general_inquiry"]
