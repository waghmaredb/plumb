"""plumbscore — scorer for the PLUMB Enterprise AI Maturity Instrument v0.1.

Section references (§) point at methodology/maturity-instrument.md.
"""

from .instrument import Instrument, load_instrument, DEFAULT_INSTRUMENT_PATH
from .responses import Response, load_responses
from .scoring import score_responses, ScoreResult, band_for
from .benchmark import load_benchmark, peer_percentile
from .kappa import weighted_kappa, kappa_report
from .scorecard import render_scorecard

__all__ = [
    "Instrument",
    "load_instrument",
    "DEFAULT_INSTRUMENT_PATH",
    "Response",
    "load_responses",
    "score_responses",
    "ScoreResult",
    "band_for",
    "load_benchmark",
    "peer_percentile",
    "weighted_kappa",
    "kappa_report",
    "render_scorecard",
]

__version__ = "0.1.0"
