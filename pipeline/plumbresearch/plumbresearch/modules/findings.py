"""Findings module (product item P5): prospect-level claims for the outside-in pre-read.

The annual-report module scores a rubric; this module lifts the passages a prospect
meeting needs, each as a plumbverify claim so the Verifier — not this module —
decides what is released:

    deploy.*      named AI applications (exact quotation; stage classified from the verb in the quote)
    opmodel.*     AI / data operating-model changes (exact quotation)
    leadership.*  AI / data seats in transition or vacated, and the successor sentence (exact quotation)
    governance.*  sentences that pair an AI term with governance language, and board-level AI references
                  (exact quotation) — the evidence that sits beside the governance observation
    reg.*         regulatory-clock facts against the regulator's primary URL (fact claims; withheld when the
                  primary source cannot be fetched, which is the case offline)

Two things are NOT claims and are never passed off as facts about the subject:

* **Observations.** A keyword absence in one document is a property of the search, not of the
  company (ghost deck §2.4; red-team review 2026-10-25 §5.1). The governance observation records
  the exact search — terms, document, SHA-256, pages, extraction engine — and its limitations, and
  carries ``presentation: question``: plumbdeck renders it only under "Questions for management".
* **Questions.** Each question is generated from evidence claims (``basis_claim_ids``) and may only be
  shown when every one of them is released; otherwise the deck shows the gap-register reference.

Everything is rule-based and offline-testable; no model call reads the document.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

import yaml

from plumbverify.fetch import EvidenceStore
from plumbverify.log import HashChainLog
from plumbverify.models import ClaimKind, ConfidenceLabel, Tier

from ..context import RunContext, default_context
from ..models import Gap, ModuleResult, ResearchClaim, confidence_for_tier
from ..subject import Subject
from ..textutil import ai_mentions, has_any, is_bio_sentence, is_fragment, norm_for_dedupe, sentences_paged
from .annual_report import (DEPARTED, HON_NAME, LEAVING, SCOPE_KEYWORDS, SPECIFICITY, SUCCESSOR, _leader_passage,
                            extract_leadership, subject_org_aliases)

MODULE = "findings"
REGULATORY_YAML = Path(__file__).resolve().parent.parent / "regulatory.yaml"

# ---------------------------------------------------------------------------------------------
# Deployment stage, classified from the verb in the quoted sentence (shown on the slide as such)
# ---------------------------------------------------------------------------------------------
STAGE_TESTING = re.compile(r"\b(?:testing|being tested|under test|piloting|pilot(?:ed|s)?|trial(?:l?ing|led|s)?|proof of concept|exploring)\b", re.I)
STAGE_DEPLOYED = re.compile(r"\b(?:deployed|rolled out|launched|implemented|introduced|delivered|went live|in production|is live|"
                            r"embedded|leveraged|scaled)\b", re.I)
STAGE_DEVELOPED = re.compile(r"\b(?:developed|built|created)\b", re.I)
OUTCOME_IN_SENTENCE = re.compile(r"\b(?:reduc(?:ing|ed|es)|strengthen(?:ed|ing|s)?|improv(?:ing|ed|es)|deliver(?:ing|ed|s))\b", re.I)
# use cases a prospect would name (label, pattern); first match wins, order matters
USE_CASES: list[tuple[str, str]] = [
    ("adviser support", r"\badvis(?:or|er|ory)"),
    ("medical-claims fraud, waste and abuse", r"\b(?:wastage|abuse|fraud)\b"),
    ("misconduct detection", r"\bmisconduct\b"),
    ("medical claims", r"\bmedical claims\b|\bclaims (?:system|processing|automation)\b"),
    ("underwriting", r"\bunderwrit"),
    ("customer segmentation", r"\bsegmentation\b"),
    ("AML / compliance monitoring", r"\banti[- ]money laundering\b|\btransaction monitoring\b"),
    ("customer service", r"\bcustomer service\b|\bcontact centre\b|\bchatbot\b|\bvirtual assistant\b"),
    ("onboarding", r"\bonboarding\b"),
    ("credit decisions", r"\bcredit (?:decision|scoring|assessment)\b"),
]
# a run-in heading glued to the sentence by layout extraction: "Leveraging Emerging Technologies and AI As AI accelerates …"
_HEADING_WORD = re.compile(r"^(?:[A-Z][\w’'&-]*|and|of|the|for|&|in)$")
_CLAUSE_START = re.compile(r"\s(?=(?:As|In|Our|We|The|This|By|With|Through)\s)")

FOLLOW_ON = re.compile(r"^(?:The|This|These)\s+(?:initiative|capability|capabilities|solution|platform|model|system|tool)s?\b")
OPMODEL = re.compile(r"\b(?:restructur\w+|reorganis\w+|reorganiz\w+|operating model|centre of excellence|center of excellence|"
                     r"(?:was|were) established|unified)\b", re.I)

# ---------------------------------------------------------------------------------------------
# Governance search (observation, not a claim). Lexicon expanded per red-team review §5.1.
# ---------------------------------------------------------------------------------------------
AI_GOVERNANCE_TERMS: list[tuple[str, str]] = [
    ("responsible AI", r"\bresponsible\s+ai\b"),
    ("AI governance", r"\bai\s+governance\b"),
    ("AI risk", r"\bai\s+risks?\b"),
    ("artificial intelligence risk", r"\bartificial\s+intelligence\s+risks?\b"),
    ("model risk", r"\bmodel\s+risks?\b"),
    ("model validation", r"\bmodel\s+validation\b"),
    ("AI policy / principles / framework", r"\bai\s+(?:policy|policies|principles|framework|guardrails|oversight|committee|council)\b"),
    ("AI ethics", r"\bai\s+ethics\b|\bethical\s+(?:use\s+of\s+)?ai\b"),
    ("FEAT", r"\bFEAT\b"),
    ("Veritas", r"\bVeritas\b"),
    ("fairness", r"\bfairness\b"),
    ("explainability", r"\bexplainab\w*"),
    ("human oversight / human-in-the-loop", r"\bhuman\s+oversight\b|\bhuman[- ]in[- ]the[- ]loop\b"),
    ("algorithm", r"\balgorithm\w*"),
    ("ISO/IEC 42001", r"\biso(?:/iec)?\s*42001\b"),
    ("NIST AI RMF", r"\bnist\s+ai\s+rmf\b"),
    ("MAS AI guidelines (AIRM)", r"\bAIRM\b|\bartificial\s+intelligence\s+risk\s+management\b|\bai\s+risk\s+management\b"),
]
BROAD_GOVERNANCE_TERMS: list[tuple[str, str]] = [
    ("governance", r"\bgovernance\b"),
    ("ethics / ethical", r"\bethic\w*"),
    ("data governance", r"\bdata\s+governance\b"),
    ("technology risk", r"\btechnology\s+risks?\b"),
    ("oversight", r"\boversight\b"),
]
AI_VOCABULARY_TERMS: list[tuple[str, str]] = [
    ("artificial intelligence", r"\bartificial\s+intelligence\b"),
    ("machine learning", r"\bmachine[- ]learning\b"),
    ("generative AI / GenAI", r"\bgenerative\s+ai\b|\bGenAI\b"),
]
GOV_ADJACENT = re.compile(r"\b(?:governance|oversight|accountab\w+)\b", re.I)
BOARD_AI = re.compile(r"\b(?:Board|Directors?|Committee|competenc\w*|fees?|receive|remuneration)\b")
CAREER = re.compile(r"\b(?:career|previously|formerly|former)\b", re.I)
_TERMINAL_PUNCT = re.compile(r"[.!?][\"”’')\]]*$")


def _words(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def near_duplicate(a: str, b: str, threshold: float = 0.6) -> bool:
    """Two quotations that report the same thing in slightly different words (a letter to shareholders
    and the business review often repeat a sentence): word-set Jaccard >= threshold."""
    wa, wb = _words(a), _words(b)
    return bool(wa and wb) and len(wa & wb) / len(wa | wb) >= threshold
SEARCH_RULE = ("case-insensitive regular expressions (FEAT, Veritas, AIRM and GenAI case-sensitive) over the whitespace-normalised "
               "stored text of every page; a hit counts as 'with an AI term' when the same sentence carries a term from the "
               "plumbresearch AI lexicon (textutil.AI_TERMS_*)")


def _flat(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def _rx(p: str) -> re.Pattern:
    cs = p.startswith(r"\bFEAT") or p.startswith(r"\bVeritas") or "AIRM" in p or "GenAI" in p
    return re.compile(p, 0 if cs else re.I)


def _trim_heading(s: str) -> str:
    """Drop a run-in heading glued in front of the sentence. The result is still an exact
    substring of the document, so the C5 quotation check applies unchanged."""
    for m in _CLAUSE_START.finditer(s[:90]):
        prefix = s[:m.start()].split()
        if 2 <= len(prefix) <= 8 and all(_HEADING_WORD.match(w) for w in prefix) and not re.search(r"[.,;:]", s[:m.start()]):
            return s[m.end():]
    return s


def _use_case(s: str) -> Optional[str]:
    for label, p in USE_CASES:
        if re.search(p, s, re.I):
            return label
    return None


def classify_stage(s: str) -> Optional[str]:
    """'testing' | 'in use' | 'developed' | 'developed; outcome stated' | None, from the verb
    in the sentence. The stage is the company's own verb, never an inference: 'developed' stays
    'developed' even when an outcome follows; the outcome is noted, not promoted to 'in use'
    (run-5 review: S04 row 7 had read 'developed …, significantly reducing …' as 'in use')."""
    if STAGE_TESTING.search(s):
        return "testing"
    if STAGE_DEPLOYED.search(s):
        return "in use"
    if STAGE_DEVELOPED.search(s):
        return "developed; outcome stated" if OUTCOME_IN_SENTENCE.search(s.split(STAGE_DEVELOPED.search(s).group(0), 1)[-1]) else "developed"
    return None


def _pct(s: str) -> list[str]:
    return re.findall(r"\b(?:approximately\s+|about\s+|around\s+|~)?\d{1,3}(?:\.\d+)?%", s)


_SENT_SPLIT = re.compile(r"([.!?][\"”’)]?)\s+(?=[A-Z0-9“\"(\[])")


def _page_sentences(text: str) -> list[tuple[str, Optional[int]]]:
    """Sentences over each page's whitespace-flattened text. Layout extraction often puts a blank line
    after every line of a narrow column, so paragraph-based splitting cuts sentences; the C5 quotation
    check is whitespace-normalised, so a sentence that spans those breaks still exact-matches."""
    paged = "\f" in (text or "")
    pages = text.split("\f") if paged else [text or ""]
    out: list[tuple[str, Optional[int]]] = []
    for i, pg in enumerate(pages, 1):
        flat = _flat(pg)
        pos = 0
        for m in _SENT_SPLIT.finditer(flat):
            out.append((flat[pos:m.end(1)].strip(), i if paged else None))
            pos = m.end()
        if flat[pos:].strip():
            out.append((flat[pos:].strip(), i if paged else None))
    return out


def _candidates(text: str) -> list[tuple[str, Optional[int]]]:
    """Whole sentences with their page, fit for quotation: not a layout fragment, not a pull quote
    (opening quote mark), not a biography line, 40–600 characters, first occurrence after
    normalisation."""
    out, seen = [], set()
    for s, page in _page_sentences(text):
        if not (40 <= len(s) <= 600) or is_fragment(s) or s[0] in "“\"‘'" or s.endswith("”") or is_bio_sentence(s) \
                or not _TERMINAL_PUNCT.search(s) or ("“" in s and "”" not in s) or re.search(r"[A-Za-z]- [a-z]", s):
            # pull quotes (unbalanced quote mark) and words broken across layout lines ("AI- powered") are not
            # evidence the body sentence does not already give
            continue
        n = norm_for_dedupe(s)
        if n in seen:
            continue
        seen.add(n)
        out.append((s, page))
    return out


# ---------------------------------------------------------------------------------------------
def _search(text: str, terms: list[tuple[str, str]]) -> list[dict[str, Any]]:
    pages = text.split("\f") if "\f" in text else [text]
    rows = []
    for label, p in terms:
        rx = _rx(p)
        pg_hits: list[int] = []
        n = with_ai = 0
        ai_pages: list[int] = []
        for i, pg in enumerate(pages, 1):
            flat = _flat(pg)
            hits = list(rx.finditer(flat))
            if not hits:
                continue
            n += len(hits)
            pg_hits.append(i)
            for s, _ in sentences_paged(flat):
                if rx.search(s) and ai_mentions(s):
                    with_ai += 1
                    if i not in ai_pages:
                        ai_pages.append(i)
        rows.append({"term": label, "pattern": p, "hits": n, "pages": pg_hits, "hits_with_ai_term": with_ai, "pages_with_ai_term": ai_pages})
    return rows


def _engine(ctx: Optional[RunContext], sha256: Optional[str]) -> Optional[str]:
    """The extraction engine plumbverify uses for this document (re-run on the stored bytes)."""
    if ctx is None or not sha256:
        return None
    try:
        from plumbverify.extract import extract_document

        raw = ctx.store.get_raw(sha256)
        return getattr(extract_document(raw, "application/pdf"), "engine", None) if raw else None
    except Exception as e:  # pragma: no cover - engine detection must never fail the run
        return f"unknown ({e.__class__.__name__})"


def analyse(subject: Subject, doc_url: str, fy: Optional[int], text: str, tier: Optional[Tier], *,
            sha256: Optional[str] = None, page_count: Optional[int] = None, engine: Optional[str] = None,
            doc_label: str = "annual report") -> dict[str, Any]:
    """Pure function over the stored text; returns the checkpoint payload (claims, observations, questions, detail)."""
    label = confidence_for_tier(tier)
    base = f"{subject.slug}.findings"
    claims: list[ResearchClaim] = []
    used: set[str] = set()
    cands = _candidates(text)

    def add(key: str, s: str, page: Optional[int], items: list[str], note: str, **attrs) -> ResearchClaim:
        c = ResearchClaim(id=f"{base}.{key}", module=MODULE, text=s, kind=ClaimKind.quote, load_bearing=False, sources=[doc_url],
                          passage=s, tier=tier, confidence_label=label, instrument_items=items, note=note,
                          attrs={"page_expected": page, "document": f"{doc_label} FY{fy}" if fy else doc_label, **attrs})
        claims.append(c)
        used.add(norm_for_dedupe(s))
        return c

    # ---- (a) named AI applications ------------------------------------------------------------
    deploy: list[ResearchClaim] = []
    for s, page in cands:
        if not ai_mentions(s) or not has_any(s, SPECIFICITY + [r"\bwastage\b", r"\bmisconduct\b", r"\bsegmentation\b", r"\bclaims system\b"]):
            continue
        q = _trim_heading(s)
        stage = classify_stage(q)
        uc = _use_case(q)
        if stage is None or uc is None or norm_for_dedupe(q) in used:
            continue
        dup = next((c for c in deploy if near_duplicate(c.text, q)), None)
        if dup is not None:  # same statement repeated elsewhere in the report: one claim, the other page recorded
            dup.attrs.setdefault("also_reported_on_pages", []).append(page)
            continue
        if len(deploy) >= 8:
            break
        k = len(deploy) + 1
        deploy.append(add(f"deploy.{k}", q, page, ["D5.4", "D1.3"] + (["D8.3"] if _pct(q) else []),
                          f"named AI application: {uc}; stage '{stage}' from the verb in the quoted sentence",
                          category="deployment", stage=stage, use_case=uc, figures=_pct(q)))
    # follow-on sentences about the same application ("This capability has …", "The initiative was awarded … in Malaysia …"):
    # kept as context claims of the application, so a market or result named there is itself a verified quotation
    for c in list(deploy):
        idx = next((i for i, (s, _) in enumerate(cands) if _trim_heading(s) == c.text), None)
        if idx is None:
            continue
        n_ctx = 0
        for nxt, pg in cands[idx + 1: idx + 3]:
            if not FOLLOW_ON.match(nxt) or norm_for_dedupe(nxt) in used:
                break
            n_ctx += 1
            add(f"deploy.{c.id.rsplit('.', 1)[-1]}.context{n_ctx}", nxt, pg, ["D5.4"],
                f"follow-on sentence for {c.id.rsplit('.', 1)[-1]} (same application)", category="deployment-context", of=c.id)

    # ---- (b) operating model --------------------------------------------------------------------
    opm: list[ResearchClaim] = []
    for s, page in cands:
        if len(opm) >= 3:
            break
        if OPMODEL.search(s) and (ai_mentions(s) or SCOPE_KEYWORDS.search(s)) and norm_for_dedupe(s) not in used \
                and not re.search(r"\b(?:Director|Mr|Ms|Dr)\b.*\bexperience\b", s):
            m = re.search(r"\bour\s+(?P<unit>[^.,;]{2,40}?)\s+operating model\b", s)
            yr = re.search(r"\b(?:In|in|since|from)\s+(?P<y>20\d\d)\b|\b(?:in|from)\s+\w+\s+(?P<y2>20\d\d)\b", s)
            opm.append(add(f"opmodel.{len(opm) + 1}", s, page, ["D1.2", "D2.1"], "AI / data / digital operating-model statement",
                           category="operating-model", unit=(m.group("unit") if m else None),
                           year=((yr.group("y") or yr.group("y2")) if yr else None)))

    # ---- (c) leadership seats in transition / vacated ---------------------------------------------
    leaders = extract_leadership(text, org_aliases=subject_org_aliases(subject))
    lead_claims: list[ResearchClaim] = []
    transition_names: list[str] = []
    seat: Optional[dict] = None
    for l in leaders:
        if not l["ai_scope"] or l["org_role"] not in ("subject", "subject-subsidiary"):
            continue
        if l["status"] not in ("leaving", "departed") and not l["seat_in_transition"]:
            continue
        p = _flat(_leader_passage(l))
        if not (40 <= len(p) <= 600):
            continue
        status = "in transition" if l["seat_in_transition"] else l["status"]
        rank = re.match(r"^(?:Group\s+)?(?:Managing Director|Executive Director|Director|Head|Chief|Senior Vice President|Vice President)\s*[,:-]?\s*(?:of\s+)?", l["title"])
        short = l["title"][rank.end():].strip() if rank else l["title"]
        short = re.sub(r"\bArtificial Intelligence\b", "AI", short)
        if norm_for_dedupe(p) in used:
            c = next(x for x in lead_claims if norm_for_dedupe(x.text) == norm_for_dedupe(p))
            c.attrs.setdefault("also", []).append(l["title"])
            continue
        ppage = next((pg for x, pg in sentences_paged(text) if norm_for_dedupe(p) in norm_for_dedupe(x)), l.get("page"))
        c = add(f"leadership.{len(lead_claims) + 1}", p, ppage, ["D1.2", "D2.1", "D5.2"],
                f"AI / data seat {status}: {l['title']}" + (f" ({', '.join(l['names'])})" if l["names"] else ""),
                category="leadership", status=status, title=l["title"], seat_short=short, names=l["names"],
                status_detail=l.get("status_detail"), effective=l.get("effective"))
        lead_claims.append(c)
        if status == "in transition":
            transition_names += l["names"]
            seat = seat or {"title": l["title"], "short": short, "claim": c.id}
    succ_claim: Optional[ResearchClaim] = None
    if transition_names:
        surnames = {n.split()[-1] for n in transition_names} | {n.split()[0] for n in transition_names}
        for s, page in cands:
            if SUCCESSOR.search(s) and any(re.search(rf"\b{re.escape(x)}\b", s) for x in surnames) and norm_for_dedupe(s) not in used:
                succ_claim = add("leadership.successor", s, page, ["D1.2"], "successor statement for the seat in transition",
                                 category="leadership", status="successor not yet named" if re.search(r"due course|later|to be named|will be named", s) else "successor named")
                break

    # ---- (d) governance: adjacent evidence (claims) and the observation (not a claim) --------------
    gov_claims: list[ResearchClaim] = []
    for s, page in cands:
        if len(gov_claims) >= 4:
            break
        if norm_for_dedupe(s) in used:
            continue
        if ai_mentions(s) and GOV_ADJACENT.search(s):
            gov_claims.append(add(f"governance.{len(gov_claims) + 1}", s, page, ["D6.1"],
                                  "sentence pairing an AI term with governance language (not an AI-governance framework statement)",
                                  category="governance-adjacent", basis="AI term + governance / oversight / accountability"))
        elif re.search(r"\bartificial\s+intelligence\b", s, re.I) and BOARD_AI.search(s) and not CAREER.search(s):
            gov_claims.append(add(f"governance.{len(gov_claims) + 1}", s, page, ["D4.4", "D6.1"],
                                  "board-level reference to artificial intelligence (directors' competencies or fees), not an AI-governance framework",
                                  category="governance-adjacent", basis="artificial intelligence named in a directors' competency or fee statement"))
    parent = (subject_org_aliases(subject).get("parent") or [None])[0]
    pages_total = page_count or ((text.count("\f") + 1) if text else 0)
    specific = _search(text, AI_GOVERNANCE_TERMS)
    broad = _search(text, BROAD_GOVERNANCE_TERMS)
    vocab = _search(text, AI_VOCABULARY_TERMS)
    zero = [r["term"] for r in specific if r["hits"] == 0]
    obs_gov = {
        "id": f"{base}.obs.governance",
        "type": "observation",
        "presentation": "question",
        "topic": "AI-governance language in the annual report",
        "statement": (f"A search of the stored {doc_label} text found {sum(r['hits'] for r in specific)} hit(s) for "
                      f"{len(specific)} AI-specific governance terms ({len(zero)} of {len(specific)} terms with zero hits) across "
                      f"{pages_total} pages. This is a property of the search, not a finding about {subject.short_name or subject.name}."),
        "search": {
            "document": f"{doc_label} FY{fy}" if fy else doc_label,
            "document_url": doc_url,
            "sha256": sha256,
            "pages_searched": f"1–{pages_total}" if pages_total else "unknown",
            "page_numbering": "PDF page index (p. N = Nth page of the PDF), as in every citation",
            "extraction_engine": engine or "not recorded",
            "rule": SEARCH_RULE,
            "ai_governance_terms": specific,
            "broad_governance_terms": broad,
            "ai_vocabulary_terms": vocab,
            "zero_hit_terms": zero,
        },
        "limitations": [
            f"Single document: only the FY{fy} {doc_label} was searched; the sustainability report, website, results materials and regulatory filings were not."
            if fy else "Single document searched.",
            "Lexicon search: exact terms only; a framework described in other words is missed, and the same lexicon approach missed a "
            "leadership title in an earlier run (red-team review §5.2).",
            "Group-level governance not examined: frameworks set by the parent group"
            + (f" ({parent})" if parent else "")
            + " may cover the subject and were not read.",
            "Extraction: PDF text extraction can split multi-word terms across columns; the governance and risk sections have not been read by eye.",
            "No independent human read yet; the two-upstream rule for load-bearing claims is not met, so this cannot be a finding.",
        ],
        "limitations_short": [
            "one document searched",
            "exact-term lexicon",
            "group-level" + (f" ({parent})" if parent else "") + " frameworks not read",
            "PDF extraction not checked by eye",
            "no independent human read; two-upstream rule not met",
        ],
        "evidence_claim_ids": [c.id for c in gov_claims],
        "basis_claim_ids": [],
    }
    observations = [obs_gov]

    # ---- (e) regulatory clock --------------------------------------------------------------------
    reg_claims: list[ResearchClaim] = []
    reg_names: list[str] = []
    for inst in load_regulatory(subject):
        reg_names.append(inst["name"])
        for rc in inst.get("claims") or []:
            reg_claims.append(ResearchClaim(
                id=f"{base}.reg.{inst['key']}.{rc['key']}", module=MODULE, text=rc["text"], kind=ClaimKind.fact, load_bearing=False,
                sources=list(inst["sources"]), passage=None, tier=Tier.T1, confidence_label=ConfidenceLabel.filed,
                instrument_items=["D6", "S12"], note=f"regulatory clock ({inst['name']}): {rc.get('clock')}; text from {inst.get('status_map')}",
                attrs={"category": "regulatory", "instrument": inst["name"], "instrument_short": inst.get("short") or inst["key"],
                       "clock": rc.get("clock"), "date": rc.get("date"),
                       "page_expected": None}))
    claims.extend(reg_claims)

    # ---- questions for management (generated from evidence; shown only when the basis is released) --
    questions: list[dict[str, Any]] = []
    who = subject.short_name or subject.name
    questions.append({"id": f"{base}.q.governance", "kind": "observation", "observation_id": obs_gov["id"],
                      "text": f"Where is the framework behind {who}'s AI governance statements documented, and who owns it?",
                      "basis_claim_ids": [c.id for c in gov_claims[:2]],
                      "basis_note": "observation: AI-specific governance terms searched, see search record; not a finding"})
    if parent:
        questions.append({"id": f"{base}.q.group", "kind": "question",
                          "text": f"Which AI risk policies does {who} set itself, and which does it adopt from {parent} group?",
                          "basis_claim_ids": [c.id for c in lead_claims if parent in c.text][:1],
                          "basis_note": f"{parent}-level frameworks were not examined (observation limitation)"})
    if seat and succ_claim:
        questions.append({"id": f"{base}.q.successor", "kind": "question",
                          "text": f"Has a successor for the {seat['short']} seat been named since the report, with the same scope?",
                          "basis_claim_ids": [seat["claim"], succ_claim.id], "basis_note": "seat in transition at the report date"})
    for c in deploy:
        if c.attrs.get("stage") == "testing":
            questions.append({"id": f"{base}.q.testing.{c.id.rsplit('.', 1)[-1]}", "kind": "question",
                              "text": f"What evidence would move the {c.attrs['use_case']} AI from testing to production, and who approves it?",
                              "basis_claim_ids": [c.id], "basis_note": "described as testing in the report"})
            break
    figs = [c for c in deploy if c.attrs.get("figures")]
    if figs:
        vals = sorted({re.sub(r"^(?:approximately|about|around|~)\s*", "", f) for c in figs for f in c.attrs["figures"]})
        aims = any(re.search(r"\baims?\b|\btarget", c.text) for c in figs)
        questions.append({"id": f"{base}.q.measurement", "kind": "question",
                          "text": (f"How are the reported {' and '.join(vals)} figures measured: baseline, period and population"
                                   + ("; which are outcomes and which aims?" if aims else "?")),
                          "basis_claim_ids": [c.id for c in figs], "basis_note": "figures as reported; method not disclosed in the report"})
    if opm:
        o = opm[0]
        unit = o.attrs.get("unit") or "AI"
        yr = o.attrs.get("year")
        questions.append({"id": f"{base}.q.opmodel", "kind": "question",
                          "text": f"What changed in the {yr + ' ' if yr else ''}{unit} operating-model restructure, and where does AI risk ownership sit?",
                          "basis_claim_ids": [o.id], "basis_note": "restructure stated; design not described"})
    if reg_claims:
        questions.append({"id": f"{base}.q.regulatory", "kind": "question",
                          "text": "Is an AI inventory with risk-materiality ratings in place ahead of the MAS guidelines' first compliance date?",
                          "basis_claim_ids": [c.id for c in reg_claims[:2]], "basis_note": "regulatory clock from the regulator's primary source"})

    detail = {
        "document": doc_url, "fy": fy, "sha256": sha256, "pages": pages_total, "engine": engine,
        "counts": {"deployments": len(deploy), "operating_model": len(opm), "leadership": len(lead_claims) + (1 if succ_claim else 0),
                   "governance_adjacent": len(gov_claims), "regulatory": len(reg_claims)},
        "seat_in_transition": seat, "regulatory_instruments": reg_names,
        "observations": observations, "questions": questions,
    }
    return {"claims": [c.model_dump(mode="json") for c in claims], "detail": detail, "doc_url": doc_url, "fy": fy}


def load_regulatory(subject: Subject, path: Path = REGULATORY_YAML) -> list[dict[str, Any]]:
    """Regulatory instruments whose applies_if matches the subject (home_market exact; sector one of)."""
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except OSError:
        return []
    out = []
    for inst in data.get("instruments") or []:
        cond = inst.get("applies_if") or {}
        if cond.get("home_market") and subject.home_market not in cond["home_market"]:
            continue
        if cond.get("sector") and subject.sector not in cond["sector"]:
            continue
        out.append(inst)
    return out


def run(subject: Subject, store: EvidenceStore, log: Optional[HashChainLog], ctx: Optional[RunContext] = None) -> ModuleResult:
    """Reads the latest annual report (the same document the annual-report module scores)."""
    ctx = ctx or default_context(subject, store, log)
    cp = ctx.checkpoint(MODULE)
    gaps: list[Gap] = []
    ars = sorted([d for d in subject.documents if d.kind == "annual_report"], key=lambda d: d.fy or 0, reverse=True)
    d = ars[0] if ars else None
    if d is None:
        return ModuleResult(module=MODULE, subject_slug=subject.slug, data_available=False,
                            detail={"observations": [], "questions": [], "note": "no annual report declared"})
    if not cp.has(d.url):
        if d.local_file and not (ctx.subject_dir / d.local_file).exists() and not ctx.fixtures and not ctx.has_attachment(d.url):
            cp.put(d.url, {"claims": [], "detail": {"observations": [], "questions": []}, "gap": f"annual report FY{d.fy} not available "
                           f"(attach it: plumbresearch ingest <subject.yaml> --file <pdf> --doc {d.document_key})"})
        else:
            src = ctx.fetch(MODULE, d.url)
            if not src.citable or not src.text_extract:
                cp.put(d.url, {"claims": [], "detail": {"observations": [], "questions": []},
                               "gap": f"annual report FY{d.fy} not readable: state={src.state.value}"})
            else:
                is_pdf = (src.detected_content_type or src.content_type or "").endswith("pdf")
                eng = _engine(ctx, src.sha256) if is_pdf else "html (plumbverify extract_main_text)"
                cp.put(d.url, analyse(subject, d.url, d.fy, src.text_extract, src.tier, sha256=src.sha256,
                                      page_count=src.page_count, engine=eng))
    payload = cp.get(d.url)
    claims = [ResearchClaim.model_validate(c) for c in payload.get("claims", [])]
    detail = payload.get("detail") or {}
    if payload.get("gap"):
        gaps.append(Gap(module=MODULE, topic=f"annual_report FY{d.fy}", detail=payload["gap"], instrument_items=["D1.1"]))
    for o in detail.get("observations") or []:
        s = o["search"]
        gaps.append(Gap(module=MODULE, topic="observation (question for management, not a finding): " + o["topic"],
                        detail=(f"{o['statement']} Zero-hit terms: {', '.join(s['zero_hit_terms']) or 'none'}. Engine {s['extraction_engine']}; "
                                f"pages {s['pages_searched']}. Limitations: " + " ".join(o["limitations"])),
                        instrument_items=["D6.1"]))
    return ModuleResult(module=MODULE, subject_slug=subject.slug, claims=claims, signals=[], gaps=gaps,
                        data_available=bool(claims), tool_calls=ctx.budget(MODULE).calls, detail=detail)
