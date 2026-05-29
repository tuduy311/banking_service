import logging
import os
from typing import Optional

from app.core.schemas import IntentResult
from app.data.label_intent_map import map_label_to_intent

logger = logging.getLogger(__name__)


class IntentNode:
    def __init__(self, model_id: str, model_path: str = "") -> None:
        self.model_id = model_id
        self.model_path = model_path.strip()
        self._model = None  # ← Cached model (don't reload)
        self._tokenizer = None  # ← Cached tokenizer (don't reload)
        self._load_error: Optional[str] = None

        if self.model_path:
            logger.info(f"[IntentNode] Attempting to load model from: {self.model_path}")
            self._load_model_and_tokenizer()  # ← Load ONCE at startup
            if self._load_error:
                logger.error(f"[IntentNode] Model load failed: {self._load_error}")
            else:
                logger.info("[IntentNode] Model loaded successfully!")
        else:
            logger.warning("[IntentNode] No model path provided, will use fallback rules only")

    def _load_model_and_tokenizer(self) -> None:
        """Load model & tokenizer ONCE at startup (cached for all requests)"""
        if not os.path.exists(self.model_path):
            self._load_error = f"Model path does not exist: {self.model_path}"
            logger.error(f"[IntentNode._load_model_and_tokenizer] {self._load_error}")
            return

        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            
            logger.info("[IntentNode._load_model_and_tokenizer] Loading model & tokenizer...")
            
            # Load tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            logger.info("[IntentNode._load_model_and_tokenizer] ✅ Tokenizer loaded")
            
            # Load model
            self._model = AutoModelForSequenceClassification.from_pretrained(
                self.model_path,
                low_cpu_mem_usage=True,
            )
            self._model.eval()  # Set to evaluation mode
            logger.info("[IntentNode._load_model_and_tokenizer] ✅ Model loaded & set to eval mode")
            
        except Exception as exc:
            self._load_error = str(exc)
            logger.error(f"[IntentNode._load_model_and_tokenizer] Exception: {type(exc).__name__}: {exc}")

    def _predict_by_hf(self, message: str) -> Optional[IntentResult]:
        """Use cached model & tokenizer (no reload!)"""
        if self._model is None or self._tokenizer is None:
            return None

        try:
            import torch
            
            # Tokenize (reuse cached tokenizer)
            inputs = self._tokenizer(
                message,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            
            # Remove token_type_ids (DistilBERT doesn't support it)
            if "token_type_ids" in inputs:
                del inputs["token_type_ids"]
            
            # Forward pass (reuse cached model - no reload!)
            with torch.no_grad():
                outputs = self._model(**inputs)
            
            # Get prediction using TOP-2 MARGIN (better than raw softmax for 77 classes)
            logits = outputs.logits
            
            # Get top 2 predictions
            top2_logits = torch.topk(logits, k=2, dim=1)
            top1_logit = top2_logits.values[0, 0].item()
            top2_logit = top2_logits.values[0, 1].item() if top2_logits.values.shape[1] > 1 else -float('inf')
            
            # Confidence = margin (top1 - top2), normalized to 0-1
            margin = top1_logit - top2_logit
            # Use sigmoid to normalize margin to (0.5, 1.0) range
            # Raw margin can be large, so we scale it
            confidence = float(torch.sigmoid(torch.tensor(margin / 2.0)).item())
            
            predicted_idx = int(top2_logits.indices[0, 0].item())
            
            # Map to label
            id2label = self._model.config.id2label
            raw_label = id2label.get(str(predicted_idx), f"LABEL_{predicted_idx}")
            
            # Convert LABEL_7 → actual intent name (using mapping or heuristic)
            intent_label = map_label_to_intent(raw_label, message)
            
            logger.info(
                f"[IntentNode._predict_by_hf] Raw: {raw_label} → Intent: {intent_label} "
                f"(confidence: {confidence:.4f}, margin: {margin:.4f})"
            )
            
            return IntentResult(
                intent=intent_label,
                confidence=confidence,
                model_id=self.model_id,
                reason="Predicted by Lab2 model checkpoint",
            )
        except Exception as exc:
            logger.error(f"[IntentNode._predict_by_hf] Exception: {type(exc).__name__}: {exc}")
            return None

    def run(self, message: str) -> IntentResult:
        hf_result = self._predict_by_hf(message)
        if hf_result is not None:
            return hf_result

        text = message.lower()
        if any(k in text for k in ["transfer", "chuyen khoan", "failed", "khong nhan"]):
            return IntentResult(
                intent="transfer_failure",
                confidence=0.84,
                model_id=self.model_id,
                reason="Fallback rules used (Lab2 model unavailable). Matched transfer failure related keywords.",
            )

        if any(k in text for k in ["card", "the", "not received", "delivery"]):
            return IntentResult(
                intent="card_not_received",
                confidence=0.8,
                model_id=self.model_id,
                reason="Fallback rules used (Lab2 model unavailable). Matched card delivery keywords.",
            )

        if any(k in text for k in ["blocked", "khoa", "cannot login", "tai khoan bi khoa"]):
            return IntentResult(
                intent="blocked_account",
                confidence=0.86,
                model_id=self.model_id,
                reason="Fallback rules used (Lab2 model unavailable). Matched account blocked keywords.",
            )

        if any(k in text for k in ["refund", "hoan tien", "chargeback", "unauthorized"]):
            return IntentResult(
                intent="refund_request",
                confidence=0.78,
                model_id=self.model_id,
                reason="Fallback rules used (Lab2 model unavailable). Matched refund or dispute keywords.",
            )

        fallback_reason = "Fallback rules used (Lab2 model unavailable)."
        if self._load_error:
            fallback_reason = f"{fallback_reason} Load error: {self._load_error}"

        return IntentResult(
            intent="general_inquiry",
            confidence=0.5,
            model_id=self.model_id,
            reason=f"{fallback_reason} No strong intent match; defaulted to general inquiry.",
        )
