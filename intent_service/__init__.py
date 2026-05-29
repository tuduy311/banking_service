"""Intent service package."""

import sys

from . import intent_service_pb2 as _intent_service_pb2

sys.modules.setdefault("intent_service_pb2", _intent_service_pb2)
