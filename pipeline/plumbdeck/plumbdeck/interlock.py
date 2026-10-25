"""The S02 interlock (ghost deck R8/R9; evidence-pack templates §12.1; pipeline S8).

The verification statement renders only when ALL of these hold:

  (a) citation resolution rate == 1.0                     (build report metric)
  (b) every ATTACHED source reconciled MATCH              (no pending / UNAVAILABLE / MISMATCH)
  (c) build profile == "client"
  (d) a QA gate 3 sign-off file is present and valid, its decision is "approved",
      it attests reviewer independence, names this run, and the reviewer is not
      the run operator.

There is deliberately no parameter, flag, environment variable or spec key that
can bypass this function's verdict. ``compute_interlock`` takes the run and the
sign-off path and nothing else.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

from .runio import RunData

BANNER = "DRAFT — not for board use"
SIGNOFF_REQUIRED = ("qa_gate", "run_id", "reviewer", "independence_attestation", "date", "sample", "decision")


def _norm_name(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().casefold()


def _person(v: Any) -> tuple[str, str]:
    if isinstance(v, dict):
        return str(v.get("name") or "").strip(), str(v.get("role") or "").strip()
    return str(v or "").strip(), ""


@dataclass
class SignOff:
    path: Path
    data: dict[str, Any]
    problems: list[str] = field(default_factory=list)

    @property
    def reviewer(self) -> str:
        return _person(self.data.get("reviewer"))[0]

    @property
    def reviewer_role(self) -> str:
        return _person(self.data.get("reviewer"))[1]

    @property
    def approver(self) -> tuple[str, str]:
        return _person(self.data.get("approver"))

    @property
    def decision(self) -> str:
        return str(self.data.get("decision") or "").strip().lower()

    @property
    def date(self) -> str:
        return str(self.data.get("date") or "")


def load_signoff(path: Optional[Path]) -> Optional[SignOff]:
    if path is None:
        return None
    p = Path(path)
    if not p.is_file():
        return SignOff(p, {}, [f"sign-off file not found ({p.name})"])
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        return SignOff(p, {}, [f"sign-off unreadable ({e.__class__.__name__})"])
    if not isinstance(data, dict):
        return SignOff(p, {}, ["sign-off is not a mapping"])
    so = SignOff(p, data)
    missing = [k for k in SIGNOFF_REQUIRED if data.get(k) in (None, "", {})]
    if missing:
        so.problems.append("sign-off missing " + ", ".join(missing))
    if data.get("qa_gate") not in (None, 3, "3"):
        so.problems.append(f"sign-off is for QA gate {data.get('qa_gate')}, not 3")
    if "reviewer" in data and not so.reviewer:
        so.problems.append("sign-off names no reviewer")
    sample = data.get("sample")
    if sample is not None and not (isinstance(sample, dict) and isinstance(sample.get("total"), int)):
        so.problems.append("sign-off sample counts malformed (need sample.total)")
    if so.decision and so.decision not in ("approved", "returned"):
        so.problems.append(f"sign-off decision '{so.decision}' not approved/returned")
    return so


@dataclass
class Interlock:
    passed: bool
    reasons: list[str]
    build_profile: Optional[str]
    resolution: Optional[float]
    attachments_total: int
    attachments_unreconciled: int
    attachments_mismatch: int
    released: int
    withheld: int
    awaiting_reconciliation: int
    operators: list[str]
    signoff_path: Optional[str]
    signoff_status: str
    reviewer: Optional[str]
    reviewer_role: Optional[str]
    approver: Optional[str]
    approver_role: Optional[str]
    signoff_date: Optional[str]
    run_id: str

    @property
    def banner(self) -> Optional[str]:
        if self.passed:
            return None
        return f"{BANNER} ({'; '.join(self.reasons)})"

    @property
    def outcome_sentence(self) -> str:
        return f"Released: {self.released} claims. Withheld: {self.withheld} claims (listed)."

    def to_dict(self) -> dict[str, Any]:
        d = dict(self.__dict__)
        d["banner"] = self.banner
        d["outcome"] = self.outcome_sentence
        return d


def run_operators(run: RunData) -> list[str]:
    """Everyone the build report records as having operated the run or supplied its inputs."""
    names: list[str] = []
    r, v = run.report, run.verification
    for v_ in (r.get("operator"), r.get("run_operator"), v.get("operator"), v.get("run_operator")):
        if isinstance(v_, list):
            names += [str(x) for x in v_]
        elif v_:
            names.append(_person(v_)[0])
    for a in run.attached:
        if a.get("supplied_by"):
            names.append(str(a["supplied_by"]))
    for s in run.sources.values():
        if s.supplied_by:
            names.append(s.supplied_by)
    out: list[str] = []
    for n in names:
        if n and _norm_name(n) not in {_norm_name(x) for x in out}:
            out.append(n)
    return out


def _attachment_counts(run: RunData) -> tuple[int, int, int]:
    recon: dict[str, Optional[str]] = {}
    for a in run.attached:
        if a.get("url"):
            recon[a["url"]] = a.get("reconciliation")
    for s in run.sources.values():
        if (s.state or "").upper() == "ATTACHED" or s.url in recon:
            prev = recon.get(s.url)
            vals = {str(x).upper() for x in (prev, s.reconciliation) if x}
            recon[s.url] = "MISMATCH" if "MISMATCH" in vals else ("MATCH" if vals == {"MATCH"} else (s.reconciliation or prev))
    total = len(recon)
    mismatch = sum(1 for x in recon.values() if str(x or "").upper() == "MISMATCH")
    unrec = sum(1 for x in recon.values() if str(x or "").upper() not in ("MATCH", "MISMATCH"))
    # never report fewer problems than the build report's own metrics
    m = run.metrics
    unrec = max(unrec, int(m.get("attached_unreconciled") or 0))
    mismatch = max(mismatch, int(m.get("attached_mismatch") or 0))
    total = max(total, int(m.get("attached_sources") or 0), unrec + mismatch)
    return total, unrec, mismatch


def _plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def compute_interlock(run: RunData, signoff_path: Optional[Path] = None) -> Interlock:
    reasons: list[str] = []

    profile = run.build_profile
    if profile != "client":
        reasons.append(f"{profile} profile" if profile else "build profile not recorded")

    total, unrec, mismatch = _attachment_counts(run)
    if unrec:
        reasons.append(f"{_plural(unrec, 'attachment')} unreconciled")
    if mismatch:
        reasons.append(f"{_plural(mismatch, 'attachment')} mismatched")

    res = run.metrics.get("citation_resolution_rate")
    resolution = float(res) if isinstance(res, (int, float)) else None
    if resolution is None:
        reasons.append("resolution not recorded")
    elif resolution != 1.0:
        reasons.append(f"resolution {resolution:g}")

    operators = run_operators(run)
    so = load_signoff(signoff_path)
    status = "absent"
    if so is None:
        reasons.append("no QA gate 3 sign-off")
    else:
        sreasons = [f"QA gate 3 {p}" for p in so.problems]
        if not so.problems or so.data:
            if so.data.get("run_id") and str(so.data["run_id"]) != run.run_id:
                sreasons.append(f"QA gate 3 sign-off is for run {so.data['run_id']}, not {run.run_id}")
            if so.data.get("independence_attestation") is not True and "independence_attestation" in so.data:
                sreasons.append("QA gate 3 reviewer independence not attested")
            if so.decision == "returned":
                sreasons.append("QA gate 3 decision: returned")
            if so.reviewer:
                if not operators:
                    sreasons.append("run operator not recorded; QA gate 3 reviewer independence cannot be checked")
                elif _norm_name(so.reviewer) in {_norm_name(o) for o in operators}:
                    sreasons.append(f"QA gate 3 reviewer is the run operator ({so.reviewer})")
        # de-duplicate, keep order
        seen = set()
        sreasons = [x for x in sreasons if not (x in seen or seen.add(x))]
        reasons += sreasons
        if not sreasons and so.decision == "approved":
            status = "approved"
        elif so.decision == "returned":
            status = "returned"
        else:
            status = "invalid"

    released = len(run.released_ids)
    withheld = len(run.withheld_ids)
    awaiting = sum(1 for c in run.withheld_ids if run.claims[c].awaiting_reconciliation)
    appr_name, appr_role = (so.approver if so else ("", ""))
    return Interlock(
        passed=not reasons,
        reasons=reasons,
        build_profile=profile,
        resolution=resolution,
        attachments_total=total,
        attachments_unreconciled=unrec,
        attachments_mismatch=mismatch,
        released=released,
        withheld=withheld,
        awaiting_reconciliation=awaiting,
        operators=operators,
        signoff_path=str(so.path) if so else None,
        signoff_status=status,
        reviewer=(so.reviewer or None) if so else None,
        reviewer_role=(so.reviewer_role or None) if so else None,
        approver=appr_name or None,
        approver_role=appr_role or None,
        signoff_date=(so.date or None) if so else None,
        run_id=run.run_id,
    )
