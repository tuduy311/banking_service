"""
Mapping từ Lab2 model labels (LABEL_0 đến LABEL_76) → intent names
Load từ checkpoints/label_mapping.json (actual Lab2 mapping)
"""
import json
import os
from pathlib import Path

# Find label_mapping.json
CHECKPOINT_DIR = Path(__file__).parent.parent.parent / "checkpoints"
LABEL_MAPPING_FILE = CHECKPOINT_DIR / "label_mapping.json"

# Cached mapping
_ID_TO_LABEL = {}

def _load_id_to_label_mapping():
    """Load LABEL_X → intent name mapping from JSON"""
    global _ID_TO_LABEL
    
    if _ID_TO_LABEL:  # Already loaded
        return _ID_TO_LABEL
    
    if not LABEL_MAPPING_FILE.exists():
        print(f"⚠️  label_mapping.json not found at {LABEL_MAPPING_FILE}")
        print("   Using empty mapping - will fallback to keyword heuristic")
        return {}
    
    try:
        with open(LABEL_MAPPING_FILE, 'r') as f:
            data = json.load(f)
            _ID_TO_LABEL = data.get("id_to_label", {})
            print(f"✅ Loaded {len(_ID_TO_LABEL)} label mappings from {LABEL_MAPPING_FILE.name}")
            return _ID_TO_LABEL
    except Exception as e:
        print(f"❌ Error loading {LABEL_MAPPING_FILE}: {e}")
        return {}


def map_label_to_intent(label: str, fallback_message: str = "") -> str:
    """
    Convert LABEL_X → intent name using Lab2 mapping or keyword heuristic
    
    Args:
        label: e.g., "LABEL_7"
        fallback_message: Customer message for keyword fallback
        
    Returns:
        Intent name (one of the 77 Lab2 intents)
    """
    
    # Load mapping if not already loaded
    id_to_label = _load_id_to_label_mapping()
    
    # Extract ID from "LABEL_7" → "7"
    if label.startswith("LABEL_"):
        label_id = label.replace("LABEL_", "")
        if label_id in id_to_label:
            intent = id_to_label[label_id]
            print(f"✅ Mapped {label} → {intent}")
            return intent
    
    # Fallback: keyword matching from message
    if fallback_message:
        msg = fallback_message.lower()
        
        if any(k in msg for k in ["transfer", "chuyen", "send money"]):
            return "failed_transfer"
        if any(k in msg for k in ["card", "the", "delivery"]):
            return "card_arrival"
        if any(k in msg for k in ["blocked", "khoa", "locked"]):
            return "pin_blocked"
        if any(k in msg for k in ["refund", "hoan"]):
            return "request_refund"
    
    # Final fallback: return label itself (preserve Lab2 name)
    if label.startswith("LABEL_"):
        # Try to get from full mapping
        intent = id_to_label.get(label.replace("LABEL_", ""), "general_inquiry")
        return intent
    
    return label
