# -*- coding: utf-8 -*-
"""Discovery agent package (layer 1 brain + AG-UI/A2UI seam).

Exporta:
- ``InterviewSession`` (camada 1): segura o ``DiscoveryState`` mutável e
  expõe as tools ``segment_lookup`` / ``reflect`` / ``emit_blueprint``.
- ``DiscoverySession`` + ``TurnResult`` (re-export da Protocol de transporte
  em ``session.py``, a costura canônica com o router AG-UI/A2UI).
"""
from .session import DiscoverySession, TurnResult
from .tools import InterviewSession

__all__ = ["InterviewSession", "DiscoverySession", "TurnResult"]
