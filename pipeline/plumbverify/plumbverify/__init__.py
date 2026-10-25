"""plumbverify: PLUMB verification layer (spec PI-CV v0.1, controls CL-001..CL-024)."""
from .models import (  # noqa: F401
    Citation, CitationStatus, Claim, ClaimDecision, ClaimKind, ConfidenceLabel, HealthClass,
    Source, SourceState, Tier, VerificationReport,
)
from .pipeline import Verifier, load_claims  # noqa: F401

__version__ = "0.1.0"
