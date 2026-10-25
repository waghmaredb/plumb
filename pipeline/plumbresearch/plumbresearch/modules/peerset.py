"""Peer-set funnel (framework Phase 1; alpha-targets §3; instrument §5.5).

Steps as documented: (1) seed from industry codes and the subject's own
named competitors; (2) add rivals named by competitors and sell-side
coverage lists; (3) text similarity on business descriptions; (4) filter
0.3x–3x size, same regulatory regime, similar model; (5) keep 5–12 core plus
a labelled secondary tier; (6) include exited and consolidated peers.

What is implemented in code here: steps 4–6 over the declared long list, plus
the merge of step-1 competitor names extracted by the annual-report module.
Steps 2–3 (coverage lists, TNIC-style similarity) are judgement steps
recorded in the subject YAML as ``why`` / ``reason_secondary`` per peer; the
exhibit prints them so the protocol is auditable. No network.

Size rule: a peer declared ``core`` stays core only if its size is inside
[0.3x, 3x] of the subject's; outside the band it is demoted to secondary
with the reason recorded. A core peer with an unverified or missing size is
retained but listed under "retained with unverified size" and raised as a
gap, because the filter cannot be applied numerically (alpha-targets §6.2).
Exited peers are never filtered by size: they are the survivorship control.
"""
from __future__ import annotations

from typing import Optional

from plumbverify.fetch import EvidenceStore
from plumbverify.log import HashChainLog
from plumbverify.models import ClaimKind, ConfidenceLabel

from ..context import RunContext, default_context
from ..models import Gap, ModuleResult, ResearchClaim, Signal, confidence_for_tier
from ..subject import Peer, PeerRole, PeerSet, Subject

MODULE = "peer-set"
BAND_LOW, BAND_HIGH = 0.3, 3.0
CORE_MIN, CORE_MAX = 5, 12
PERCENTILE_MIN_N = 15


def build_peer_set(subject: Subject, extra_competitors: Optional[list[str]] = None) -> PeerSet:
    size = subject.size.value_usd_bn
    low = round(size * BAND_LOW, 1) if size else None
    high = round(size * BAND_HIGH, 1) if size else None
    core: list[Peer] = []
    secondary: list[Peer] = []
    exited: list[Peer] = []
    demoted: list[tuple[str, str]] = []
    unverified: list[str] = []
    warnings: list[str] = []
    seed = [p for p in subject.peers if p.role != PeerRole.exited]
    for p in subject.peers:
        if p.role == PeerRole.exited:
            exited.append(p)
            continue
        psize = p.size.value_usd_bn
        if p.role == PeerRole.core:
            if size and psize is not None:
                if low <= psize <= high:
                    core.append(p)
                else:
                    reason = f"outside 0.3x–3x band ({psize} vs {low}–{high} US$bn)"
                    demoted.append((p.name, reason))
                    secondary.append(p.model_copy(update={"role": PeerRole.secondary, "reason_secondary": reason}))
                if p.size.verify:
                    unverified.append(p.name)
            else:
                core.append(p)
                unverified.append(p.name)
        else:
            secondary.append(p)
    if size is None:
        warnings.append("subject size missing: 0.3x–3x filter not applied; every declared core peer retained pending [VERIFY]")
    if len(core) < CORE_MIN:
        warnings.append(f"core peer count {len(core)} below the 5–12 target")
    if len(core) > CORE_MAX:
        warnings.append(f"core peer count {len(core)} above the 5–12 target; tighten the similarity rule")
    names = {p.name.lower() for p in subject.peers}
    new_names = [c for c in (extra_competitors or []) if c.lower() not in names and not any(c.lower() in n or n in c.lower() for n in names)]
    if new_names:
        warnings.append("named in the subject's own report but not in the declared long list (add or reject with reason): " + ", ".join(new_names))
    n_scored = len(core)
    note = (f"n = {n_scored} core (+{len(secondary)} secondary): below the instrument §5.5 minimum of {PERCENTILE_MIN_N}; "
            "the scorecard must print \"global, peer n insufficient\"") if n_scored < PERCENTILE_MIN_N else f"n = {n_scored} meets the §5.5 minimum"
    return PeerSet(subject_slug=subject.slug, subject_size_usd_bn=size, band_low_usd_bn=low, band_high_usd_bn=high,
                   seed_count=len(seed), core=core, secondary=secondary, exited=exited, demoted=demoted,
                   retained_unverified=unverified, warnings=warnings, percentile_note=note)


def _v(flag: bool) -> str:
    return " **[VERIFY]**" if flag else ""


def exhibit_markdown(subject: Subject, ps: PeerSet) -> str:
    L: list[str] = []
    L.append(f"# Peer-set protocol exhibit — {subject.name}")
    L.append("")
    L.append(f"Subject: {subject.name} ({subject.listing.exchange} {subject.listing.ticker or ''}); sector {subject.sector}; "
             f"codes {', '.join(subject.industry_codes) or '—'}; FY{subject.latest_fy}.")
    L.append("")
    L.append("## Funnel")
    L.append("")
    L.append("| Step | Rule | Result |")
    L.append("|---|---|---|")
    L.append(f"| 1 Seed | industry codes + competitors named by the subject | {subject.seed_description or '—'} |")
    L.append(f"| 2–3 Expand and similarity | coverage universes; business-description similarity | declared long list n = {ps.seed_count} (reasons per peer below) |")
    size_txt = (f"{ps.subject_size_usd_bn} US$bn{_v(subject.size.verify)} → band {ps.band_low_usd_bn}–{ps.band_high_usd_bn} US$bn"
                if ps.subject_size_usd_bn else "subject size not set — filter not applied")
    L.append(f"| 4 Size band 0.3x–3x | {subject.size.metric} | {size_txt} |")
    L.append(f"| 5 Core / secondary | 5–12 core, labelled secondary | core {len(ps.core)}, secondary {len(ps.secondary)}, demoted {len(ps.demoted)} |")
    L.append(f"| 6 Exited | survivorship control, never size-filtered | {len(ps.exited)} events |")
    L.append("")
    L.append(f"**Peer percentile:** {ps.percentile_note}.")
    L.append("")
    L.append("## Core peers")
    L.append("")
    L.append("| # | Peer | Listing | Size (US$bn) | Why included | Data sources |")
    L.append("|---|---|---|---|---|---|")
    for i, p in enumerate(ps.core, 1):
        s = f"{p.size.value_usd_bn if p.size.value_usd_bn is not None else '—'}{_v(p.size.verify)}"
        L.append(f"| {i} | {p.name}{(' (' + p.entity + ')') if p.entity else ''} | {p.listing or '—'} | {s} | {p.why or '—'} | {p.data_sources or '—'} |")
    L.append("")
    L.append("## Secondary tier (labelled)")
    L.append("")
    L.append("| Peer | Listing | Size (US$bn) | Why secondary |")
    L.append("|---|---|---|---|")
    for p in ps.secondary:
        s = f"{p.size.value_usd_bn if p.size.value_usd_bn is not None else '—'}{_v(p.size.verify)}"
        L.append(f"| {p.name} | {p.listing or '—'} | {s} | {p.reason_secondary or p.why or '—'} |")
    L.append("")
    L.append("## Exited / consolidated peers (survivorship control)")
    L.append("")
    L.append("| Event | Year | Status | Relevance | Source |")
    L.append("|---|---|---|---|---|")
    for p in ps.exited:
        src = ", ".join(p.sources) if p.sources else "**[VERIFY]**"
        L.append(f"| {p.event or p.name} | {p.event_year or '—'} | {p.status or '—'} | {p.why or '—'} | {src} |")
    L.append("")
    if ps.demoted:
        L.append("## Demoted by the size filter")
        L.append("")
        for n, r in ps.demoted:
            L.append(f"- {n}: {r}")
        L.append("")
    if ps.retained_unverified:
        L.append("## Core peers retained with unverified size")
        L.append("")
        L.append(", ".join(ps.retained_unverified) + " — alpha-targets §6 item 2: apply the band numerically once sizes are confirmed.")
        L.append("")
    if ps.warnings:
        L.append("## Warnings")
        L.append("")
        for w in ps.warnings:
            L.append(f"- {w}")
        L.append("")
    return "\n".join(L)


def run(subject: Subject, store: EvidenceStore, log: Optional[HashChainLog], ctx: Optional[RunContext] = None,
        extra_competitors: Optional[list[str]] = None) -> ModuleResult:
    ctx = ctx or default_context(subject, store, log)
    ps = build_peer_set(subject, extra_competitors)
    ctx.log_call(MODULE, "peer_funnel", subject.slug, "ok", core=len(ps.core), secondary=len(ps.secondary), exited=len(ps.exited))
    claims: list[ResearchClaim] = []
    # size figures with a declared source become number claims (non-load-bearing: directional until two upstreams exist)
    for p in [*ps.core, *ps.secondary]:
        if p.size.source_url and p.size.as_reported:
            tier = ctx.tier_of(p.size.source_url)
            metric = p.size.metric.replace("_", " ")
            text = f"{p.name} {p.size.as_reported}" if metric in p.size.as_reported.lower() else f"{p.name} {metric} {p.size.as_reported}"
            claims.append(ResearchClaim(id=f"{subject.slug}.peer.size.{_slug(p.name)}", module=MODULE, text=text, kind=ClaimKind.number,
                                        load_bearing=False, sources=[p.size.source_url], tier=tier, confidence_label=confidence_for_tier(tier),
                                        instrument_items=["peer-size"], signal_ids=[f"{subject.slug}.peerset.core_n"], value=p.size.value_usd_bn, unit="USD bn"))
    gaps = [Gap(module=MODULE, topic="peer size unverified", detail=f"{n}: size needed to apply the 0.3x–3x band", verify_flag=True)
            for n in ps.retained_unverified]
    gaps += [Gap(module=MODULE, topic="exited peer unsourced", detail=f"{p.event or p.name}: {p.status or ''} — no fetched source", verify_flag=True)
             for p in ps.exited if not p.sources]
    gaps += [Gap(module=MODULE, topic="funnel warning", detail=w) for w in ps.warnings]
    signals = [
        Signal(id=f"{subject.slug}.peerset.core_n", module=MODULE, name="Core peer count after funnel", instrument_items=["§5.5"],
               value=len(ps.core), unit="peers", source="subject YAML long list + annual-report competitor names",
               confidence_label=ConfidenceLabel.model_inferred, evidence_claim_ids=[c.id for c in claims],
               detail={"secondary": len(ps.secondary), "exited": len(ps.exited), "demoted": ps.demoted, "band": [ps.band_low_usd_bn, ps.band_high_usd_bn]},
               note=ps.percentile_note),
    ]
    return ModuleResult(module=MODULE, subject_slug=subject.slug, claims=claims, signals=signals, gaps=gaps,
                        exhibits={"peer-set.md": exhibit_markdown(subject, ps)}, tool_calls=ctx.budget(MODULE).calls,
                        detail=ps.model_dump(mode="json"))


def _slug(s: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
