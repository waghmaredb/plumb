"""plumbresearch: PLUMB Phase 1 outside-in research modules (framework Phase 1;
instrument outside-in proxies; verification spec PI-CV v0.1 C10/C12)."""
from .models import Gap, ModuleResult, ResearchClaim, Signal  # noqa: F401
from .subject import Peer, PeerRole, PeerSet, Subject, load_subject  # noqa: F401
from .context import RunContext, ToolBudget, ToolCapExceeded  # noqa: F401
from .orchestrator import run_subject  # noqa: F401

__version__ = "0.1.0"
