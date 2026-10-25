"""plumbverify: PLUMB verification layer (spec PI-CV v0.1, controls CL-001..CL-024)."""
from .ingest import ingest_local, reconcile, reconcile_all  # noqa: F401
from .models import (  # noqa: F401
    ATTACHED_LABEL, Citation, CitationStatus, Claim, ClaimDecision, ClaimKind, ConfidenceLabel, HealthClass,
    Reconciliation, Source, SourceState, Tier, VerificationReport,
)
from .pipeline import Verifier, load_claims  # noqa: F401
from .report import build_sample, render_markdown  # noqa: F401

__version__ = "0.3.1"
