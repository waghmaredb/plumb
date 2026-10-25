"""End to end on fixtures: four outputs, at least one claim BLOCKED by plumbverify,
the rest released; C10 cap termination / checkpoint restart / escalation; CLI."""
import json

from plumbverify.log import HashChainLog
from plumbverify.models import CitationStatus

from plumbresearch.cli import main
from plumbresearch.context import RunContext, ToolCapExceeded
from plumbresearch.models import ModuleResult
from plumbresearch.orchestrator import run_module_with_cap, run_subject

from .conftest import ACME, AS_OF, FIXTURES


def test_end_to_end_on_fixtures(acme, tmp_path):
    out = run_subject(acme, tmp_path / "out" / acme.slug, FIXTURES, fixtures=True, as_of=AS_OF)
    d = out.out_dir
    for name in ("claims.json", "report.json", "peer-set.md", "signals.md", "gap-register.md"):
        assert (d / name).exists(), name

    decisions = {x.claim_id: x for x in out.report.decisions}
    blocked = {cid for cid, x in decisions.items() if x.blocked}
    released = {cid for cid, x in decisions.items() if not x.blocked}
    # exactly the Zeta Bank KPI claims block (their source page is absent from the fixture web -> DEAD)
    assert blocked and all(cid.startswith("acme-bank.fin.zeta-bank.") for cid in blocked)
    assert len(blocked) == 4 and len(released) == len(out.claims) - 4
    assert not out.report.build_pass  # block-not-flag: the build gate fails while any claim is BLOCKED
    assert {g.claim_id for g in out.report.gap_register} == blocked
    assert all("DEAD" in r for g in out.report.gap_register for r in g.reasons[1:2])

    # every module produced claims and the subject's load-bearing KPIs passed the two-upstream rule
    mods = {m.module: m for m in out.modules}
    assert set(mods) == {"annual-report", "peer-set", "postings", "earnings-calls", "patents", "financials", "findings"}
    assert all(m.claims for m in mods.values()) and not any(m.escalated for m in mods.values())
    subj_kpis = [c for c in out.claims if c.id.startswith("acme-bank.fin.acme-bank.") and c.load_bearing]
    assert subj_kpis and all(decisions[c.id].independent_upstreams >= 2 for c in subj_kpis)
    # quotations lifted from the stored text exact-match (C5)
    quotes = [c for c in out.claims if c.kind.value == "quote"]
    assert quotes and all(not decisions[c.id].blocked for c in quotes)
    assert out.report.metrics["quotation_pass_rate"] == 1.0

    # signals carry value / source / tier / status and the rubric landed on L4 for the fixture report
    sig = {s.id: s for s in out.signals}
    rub = sig["acme-bank.ar.annual_report.2025.rubric"]
    assert rub.value == 4 and rub.status == "released" and rub.tier.value == "T2"
    assert sig["acme-bank.postings.share"].value == 30.0 and sig["acme-bank.postings.share"].status == "released"
    assert sig["acme-bank.call.density"].status == "released" and sig["acme-bank.call.density"].value > 0
    assert sig["acme-bank.fin.pct.npat"].status.startswith("partial")  # one of four evidence claims (Zeta) blocked
    assert sig["acme-bank.fin.economic_profit"].status == "not-available"
    names = sig["acme-bank.ar.annual_report.2025.competitors"].detail["names"]
    assert [n["name"] for n in names] == ["Beta Bank", "Gamma Financial", "Delta Bank"]
    assert sig["acme-bank.ar.annual_report.2025.leadership"].detail["titles"][0]["title"] == "Group Chief Data and AI Officer"

    # outputs: claims.json is plumbverify input shape; report.json has the register; markdown mentions the gaps
    claims_json = json.loads((d / "claims.json").read_text())
    assert {"id", "text", "kind", "sources", "passage", "tier", "confidence_label"} <= set(claims_json["claims"][0])
    rep = json.loads((d / "report.json").read_text())
    assert rep["gap_register"]["blocked_claims"] and rep["log_chain_ok"] is True
    assert "Delta Bank" in (d / "peer-set.md").read_text() and "Iota Bank" in (d / "peer-set.md").read_text()
    assert "| Status |" in (d / "signals.md").read_text()
    gap_md = (d / "gap-register.md").read_text()
    assert "zeta-bank" in gap_md and "[VERIFY]" in gap_md

    # C12/C13: every module call and verification step is in the hash chain, intact, region asserted
    log = HashChainLog(d / "inference.jsonl")
    recs = log.records()
    assert log.verify().ok
    callers = {r["caller"] for r in recs}
    assert {"plumbresearch.annual-report", "plumbresearch.postings", "plumbresearch.earnings-calls", "plumbresearch.patents",
            "plumbresearch.orchestrator", "pipeline.resolve_source", "pipeline.policy"} <= callers
    assert all(r.get("region_asserted") == "asia-southeast1" for r in recs)
    assert all("prompt_sha256" in r for r in recs)
    # the cap was respected
    assert all(m.tool_calls <= 40 for m in out.modules)


def test_cap_terminates_checkpoint_restart_and_escalation(acme, tmp_path):
    """Spec T-08 in miniature: a synthetic module that needs 7 fetches under a cap of 3."""
    ctx = RunContext.build(acme, tmp_path / "out", FIXTURES, fixtures=True, cap=3, as_of=AS_OF)
    urls = [f"https://ir.acme-bank.example/results-fy2025.html?i={i}" for i in range(7)]
    attempts = {"n": 0}

    def greedy(c: RunContext) -> ModuleResult:
        attempts["n"] += 1
        cp = c.checkpoint("greedy")
        for u in urls:
            if cp.has(u):
                continue
            c.fetch("greedy", u)
            cp.put(u, {"done": True})
        return ModuleResult(module="greedy", subject_slug=acme.slug)

    res = run_module_with_cap(ctx, "greedy", greedy)
    # first run stops at 3 calls, restarts from checkpoint (3 done), hits the cap again at 6 -> escalated
    assert attempts["n"] == 2 and res.escalated and res.restarts == 2
    assert len(ctx.checkpoint("greedy").items) == 6
    assert any(g.topic == "tool-call cap" for g in res.gaps)
    recs = HashChainLog(ctx.out_dir / "inference.jsonl").records()
    assert sum(1 for r in recs if r["outcome"] == "CAP_HIT") == 2 and any(r["outcome"] == "ESCALATED" for r in recs)

    # with 4 fetches it completes after exactly one restart
    ctx2 = RunContext.build(acme, tmp_path / "out2", FIXTURES, fixtures=True, cap=3, as_of=AS_OF)
    urls[:] = urls[:4]
    attempts["n"] = 0
    res2 = run_module_with_cap(ctx2, "greedy", greedy)
    assert not res2.escalated and res2.restarts == 1 and res2.tool_calls == 1
    ctx.store.close(); ctx2.store.close()


def test_budget_raises_before_the_call_is_made(acme, tmp_path):
    ctx = RunContext.build(acme, tmp_path / "out", FIXTURES, fixtures=True, cap=1, as_of=AS_OF)
    ctx.fetch("m", "https://ir.acme-bank.example/results-fy2025.html")
    try:
        ctx.fetch("m", "https://ir.acme-bank.example/annual-report-2025.html")
        assert False, "cap not enforced"
    except ToolCapExceeded as e:
        assert e.calls == 1 and e.cap == 1
    assert "https://ir.acme-bank.example/annual-report-2025.html" not in ctx._source_cache
    ctx.store.close()


def test_cli_run_fixtures(tmp_path, capsys):
    rc = main(["run", str(ACME), "--out", str(tmp_path), "--fixtures", "--as-of", "2026-10-25"])
    out = capsys.readouterr().out
    assert rc == 1 and "4 BLOCKED" in out and "build FAIL" in out  # blocked claims -> non-zero exit, like plumbverify
    assert (tmp_path / "acme-bank" / "signals.md").exists()
    rc2 = main(["run", str(ACME), "--out", str(tmp_path / "sub"), "--fixtures", "--as-of", "2026-10-25", "--modules", "peer-set,financials"])
    assert rc2 == 1 and (tmp_path / "sub" / "acme-bank" / "peer-set.md").exists()
    assert main(["run", str(ACME), "--out", str(tmp_path), "--cap", "61"]) == 2


def test_subset_run_without_blocked_claims_passes(acme, tmp_path):
    out = run_subject(acme, tmp_path / "o", FIXTURES, fixtures=True, as_of=AS_OF, modules=["annual-report", "earnings-calls"])
    assert out.report.build_pass and all(d.status == CitationStatus.verified for d in out.report.decisions)
