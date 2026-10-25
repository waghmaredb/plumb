"""One module per Phase 1 research area. Each exposes
``run(subject, store, log, ctx=None) -> ModuleResult``."""
from . import annual_report, earnings_calls, financials, patents, peerset, postings  # noqa: F401
