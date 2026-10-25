"""Run context shared by every module: tool-call budget (spec C10), module
checkpoints, the fetch path (plumbverify Fetcher + EvidenceStore, with a PDF
shim and a local-document / fixture transport), and the hash-chained log.

Spec C10 (CL-010): "Cap tool calls per module run; checkpoint module state;
terminate and restart from checkpoint on cap; one module per run context.
Default cap 40 tool calls per module run; hard ceiling 60 with recorded
override; runs that hit the cap twice on one module are escalated."
"""
from __future__ import annotations

import json
import mimetypes
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Callable, Optional

import httpx
import yaml

from plumbverify.fetch import EvidenceStore, Fetcher
from plumbverify.log import HashChainLog
from plumbverify.models import Source, SourceState, Tier
from plumbverify.tier import TierRules, assign_tier, load_tier_rules

from .subject import Subject

DEFAULT_CAP = 40
HARD_CEILING = 60
MODEL_ID = "plumbresearch-rules"
MODEL_VERSION = "0.1.0"


# --------------------------------------------------------------------------
# C10: tool-call budget
# --------------------------------------------------------------------------
class ToolCapExceeded(RuntimeError):
    def __init__(self, module: str, cap: int, calls: int):
        super().__init__(f"module {module}: tool-call cap {cap} reached after {calls} calls (C10)")
        self.module, self.cap, self.calls = module, cap, calls


@dataclass
class ToolBudget:
    module: str
    cap: int = DEFAULT_CAP
    calls: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)

    def spend(self, tool: str, **detail: Any) -> int:
        """Charge one tool call. Raises ToolCapExceeded when the cap is hit; the
        call that would exceed the cap is NOT performed."""
        if self.calls >= self.cap:
            raise ToolCapExceeded(self.module, self.cap, self.calls)
        self.calls += 1
        self.history.append({"n": self.calls, "tool": tool, **detail})
        return self.calls


# --------------------------------------------------------------------------
# C10: checkpoints (per module, keyed by work item)
# --------------------------------------------------------------------------
class Checkpoint:
    """Append-only map work-item key -> JSON payload, persisted after every put
    so a restart after ToolCapExceeded resumes at the next item."""

    def __init__(self, path: Optional[Path]):
        self.path = path
        self.items: dict[str, Any] = {}
        if path and path.exists():
            try:
                self.items = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                self.items = {}

    def has(self, key: str) -> bool:
        return key in self.items

    def get(self, key: str) -> Any:
        return self.items.get(key)

    def put(self, key: str, payload: Any) -> None:
        self.items[key] = payload
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.items, default=str, ensure_ascii=False), encoding="utf-8")

    def values(self) -> list[Any]:
        return list(self.items.values())

    def clear(self) -> None:
        self.items = {}
        if self.path and self.path.exists():
            self.path.unlink()


# --------------------------------------------------------------------------
# PDF text: plumbverify 0.2 extracts page-aware text (pages joined by PAGE_SEP);
# this layer only unwraps hard-wrapped lines so sentences survive passage splitting.
# --------------------------------------------------------------------------
try:
    from plumbverify.extract import PAGE_SEP
except ImportError:  # plumbverify 0.1
    PAGE_SEP = "\f"


def unwrap_lines(text: str) -> str:
    """PDF text comes hard-wrapped. Join wrapped lines inside a paragraph with a
    space and repair end-of-line hyphenation, keeping blank lines as paragraph
    breaks and PAGE_SEP as page breaks, so plumbverify's passage splitter
    (which splits on single newlines) sees whole sentences and a number claim
    is not cut from its context. Idempotent on already-unwrapped text."""
    import re

    from plumbverify.extract import normalize_text

    pages = (text or "").split(PAGE_SEP)
    out_pages = []
    for page in pages:
        paras = re.split(r"\n\s*\n", page)
        out = []
        for p in paras:
            p = re.sub(r"(\w)-\n(\w)", r"\1\2", p)  # de-hyphenate "govern-\nance"
            p = re.sub(r"\s*\n\s*", " ", p).strip()
            if p:
                out.append(p)
        out_pages.append(normalize_text("\n\n".join(out)))
    return f"\n{PAGE_SEP}\n".join(out_pages) if len(out_pages) > 1 else (out_pages[0] if out_pages else "")


def extract_pdf_text(raw: bytes) -> str:
    """Fallback PDF extraction (pypdf, then pdfminer.six) for a plumbverify
    that returned no text; unwrapped. '' when no engine is installed."""
    import io

    text = ""
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(io.BytesIO(raw))
        text = f"\n{PAGE_SEP}\n".join((pg.extract_text() or "") for pg in reader.pages)
    except Exception:
        text = ""
    if not text.strip():
        try:
            from pdfminer.high_level import extract_text  # type: ignore

            text = extract_text(io.BytesIO(raw)) or ""
        except Exception:
            text = ""
    return unwrap_lines(text)


class ResearchFetcher(Fetcher):
    """plumbverify Fetcher with PDF line unwrapping. The hash and the stored
    bytes are plumbverify's; only ``text_extract`` is post-processed (and
    written back to the store) so that the module lifting a sentence and the
    Verifier matching it see the same unwrapped text. If plumbverify returned
    no PDF text (v0.1, or an engine failure) and the PDF is not flagged
    ``needs_ocr``, a local pypdf/pdfminer pass is tried.

    Attached documents (plumbverify 0.3): when the evidence store holds an
    ATTACHED source for the URL, the base fetcher prefers it over a 404/DEAD
    result and, when ``reconcile_on_fetch`` is on (online runs), re-fetches
    the declared URL and reconciles the hashes in passing. Attached PDFs get
    the same line unwrapping as fetched ones."""

    def fetch(self, url: str) -> Source:
        src = super().fetch(url)
        ctype = (getattr(src, "detected_content_type", None) or src.content_type or "").lower()
        is_pdf = "pdf" in ctype or (src.url_final or url).lower().endswith(".pdf")
        if src.state not in (SourceState.FETCHED, SourceState.ARCHIVED, SourceState.ATTACHED) or not is_pdf or not src.sha256:
            return src
        if getattr(src, "needs_ocr", False):
            return src
        text = src.text_extract or ""
        if not text.strip():
            raw = self.store.get_raw(src.sha256) if self.store else None
            text = extract_pdf_text(raw) if raw else ""
        else:
            text = unwrap_lines(text)
        if text and text != src.text_extract:
            src.text_extract = text
            if self.store is not None:
                self.store.db.execute("UPDATE sources SET text_extract=? WHERE sha256=? AND url=?", (text, src.sha256, src.url))
                self.store.db.commit()
        return src


PdfAwareFetcher = ResearchFetcher  # backwards-compatible name


# --------------------------------------------------------------------------
# Transports: fixture web (offline) and local documents over the real web
# --------------------------------------------------------------------------
def _guess_type(path: Path, declared: Optional[str]) -> str:
    if declared:
        return declared
    t, _ = mimetypes.guess_type(str(path))
    return t or ("application/pdf" if path.suffix.lower() == ".pdf" else "text/plain; charset=utf-8")


class LocalDocTransport(httpx.BaseTransport):
    """Serves registered URLs from local files; everything else goes to
    ``fallback`` (a real HTTPTransport in production, None for offline runs,
    which yields 404 so unknown URLs classify DEAD)."""

    def __init__(self, registry: dict[str, tuple[Path, Optional[str]]], fallback: Optional[httpx.BaseTransport] = None):
        self.registry = dict(registry)
        self.fallback = fallback

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        hit = self.registry.get(url) or self.registry.get(url.rstrip("/"))
        if hit is not None:
            path, ctype = hit
            if not path.exists():
                return httpx.Response(404, request=request, content=b"local file missing: " + str(path).encode())
            body = b"" if request.method == "HEAD" else path.read_bytes()
            return httpx.Response(200, headers={"content-type": _guess_type(path, ctype)}, content=body, request=request)
        if self.fallback is not None:
            return self.fallback.handle_request(request)
        return httpx.Response(404, request=request, content=b"offline: not in fixture web")


def load_fixture_web(web_yaml: Path) -> dict[str, tuple[Path, Optional[str]]]:
    """web.yaml: list of {url, file, content_type?}; files relative to the yaml."""
    data = yaml.safe_load(web_yaml.read_text(encoding="utf-8")) or []
    out: dict[str, tuple[Path, Optional[str]]] = {}
    for row in data:
        out[row["url"]] = (web_yaml.parent / row["file"], row.get("content_type"))
    return out


# --------------------------------------------------------------------------
# Run context
# --------------------------------------------------------------------------
@dataclass
class RunContext:
    subject: Subject
    store: EvidenceStore
    log: Optional[HashChainLog]
    data_dir: Path  # <data_dir>/<slug>/ holds this subject's files
    out_dir: Path
    fetcher: Fetcher
    tier_rules: TierRules
    run_id: str
    cap: int = DEFAULT_CAP
    fixtures: bool = False
    as_of: date = field(default_factory=date.today)
    region: str = "asia-southeast1"
    budgets: dict[str, ToolBudget] = field(default_factory=dict)
    _source_cache: dict[str, Source] = field(default_factory=dict)

    # -- construction -----------------------------------------------------
    @classmethod
    def build(
        cls,
        subject: Subject,
        out_dir: str | Path,
        data_dir: str | Path,
        *,
        fixtures: bool = False,
        cap: int = DEFAULT_CAP,
        log: Optional[HashChainLog] = None,
        store: Optional[EvidenceStore] = None,
        run_id: Optional[str] = None,
        as_of: Optional[date] = None,
        offline: bool = False,
    ) -> "RunContext":
        import uuid

        out_dir, data_dir = Path(out_dir), Path(data_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        store = store or EvidenceStore(out_dir / "evidence")
        log = log if log is not None else HashChainLog(out_dir / "inference.jsonl")
        subj_dir = data_dir / subject.slug
        registry: dict[str, tuple[Path, Optional[str]]] = {}
        if fixtures and (subj_dir / "web.yaml").exists():
            registry.update(load_fixture_web(subj_dir / "web.yaml"))
        for d in subject.documents:
            # a declared local file is served under its URL only when it exists; otherwise the URL
            # goes to the network (or the attached copy in the store), so reconciliation can reach the publisher
            if d.local_file and ((subj_dir / d.local_file).exists() or fixtures or offline):
                registry[d.url] = (subj_dir / d.local_file, None)
        tidx = subj_dir / "transcripts" / "index.yaml"
        if tidx.exists():
            for row in yaml.safe_load(tidx.read_text(encoding="utf-8")) or []:
                if row.get("url") and row.get("file"):
                    registry[row["url"]] = (tidx.parent / row["file"], "text/plain; charset=utf-8")
        fallback = None if (fixtures or offline) else httpx.HTTPTransport(retries=0)
        client = httpx.Client(transport=LocalDocTransport(registry, fallback), follow_redirects=True, timeout=20.0,
                              headers={"User-Agent": "plumbresearch/0.1 (+PLUMB Phase 1 research; citation verification)"})
        import time

        sleep = (lambda s: None) if (fixtures or offline) else time.sleep
        # attached documents: online runs re-fetch the declared URL and reconcile the hash in passing;
        # offline / fixture runs use the attachment as is (labelled) and never touch the network for it
        fetcher = ResearchFetcher(store=store, client=client, sleep=sleep, reconcile_on_fetch=not (fixtures or offline))
        rules = load_tier_rules(overrides={"tiers": {k: {"domains": v} for k, v in subject.tier_overrides.items()}}) \
            if subject.tier_overrides else load_tier_rules()
        return cls(subject=subject, store=store, log=log, data_dir=data_dir, out_dir=out_dir, fetcher=fetcher,
                   tier_rules=rules, run_id=run_id or f"research-{uuid.uuid4().hex[:12]}", cap=cap, fixtures=fixtures,
                   as_of=as_of or date.today())

    # -- paths ------------------------------------------------------------
    @property
    def subject_dir(self) -> Path:
        return self.data_dir / self.subject.slug

    def checkpoint(self, module: str) -> Checkpoint:
        return Checkpoint(self.out_dir / "checkpoints" / f"{module}.json")

    def budget(self, module: str) -> ToolBudget:
        if module not in self.budgets:
            self.budgets[module] = ToolBudget(module=module, cap=self.cap)
        return self.budgets[module]

    def reset_budget(self, module: str) -> ToolBudget:
        self.budgets[module] = ToolBudget(module=module, cap=self.cap)
        return self.budgets[module]

    # -- logging (C12) ----------------------------------------------------
    def log_call(self, module: str, tool: str, prompt: str, outcome: str, **detail: Any) -> None:
        if self.log is None:
            return
        self.log.log_inference(run_id=self.run_id, model_id=MODEL_ID, model_version=MODEL_VERSION,
                               caller=f"plumbresearch.{module}", prompt=prompt,
                               tool_calls=[{"tool": tool, **detail}], outcome=outcome,
                               region_asserted=self.region)

    # -- the one network-touching primitive -------------------------------
    def fetch(self, module: str, url: str) -> Source:
        """Fetch through plumbverify (hash + store) under the module's budget.
        Cached per run so the Verifier's later resolve is the only second fetch."""
        b = self.budget(module)
        b.spend("fetch", url=url)
        if url in self._source_cache:
            src = self._source_cache[url]
        else:
            src = self.fetcher.fetch(url)
            src.tier = assign_tier(src.url_final or url, self.tier_rules).tier
            self._source_cache[url] = src
        self.log_call(module, "fetch", url, src.state.value, url=url, sha256=src.sha256, tier=src.tier.value,
                      budget=f"{b.calls}/{b.cap}")
        return src

    def tier_of(self, url: str) -> Tier:
        return assign_tier(url, self.tier_rules).tier

    def has_attachment(self, url: str) -> bool:
        """True when a person attached a document for this URL into the run's evidence store."""
        return self.store.get_attachment(url) is not None

    def attached_documents(self) -> list[dict]:
        """Reconciliation status per attached document, joined to the subject's declared documents."""
        by_url = {d.url: d for d in self.subject.documents}
        out = []
        for att in self.store.list_attachments():
            d = by_url.get(att["url"])
            out.append({**att, "document_key": att.get("document_key") or (d.document_key if d else None),
                        "kind": d.kind if d else None, "fy": d.fy if d else None,
                        "label": None if att["state"] != SourceState.ATTACHED.value else "attached; publisher hash unreconciled"})
        return out

    def charge(self, module: str, tool: str, **detail: Any) -> None:
        """Charge a non-fetch external call (a data-source query) to the budget."""
        b = self.budget(module)
        b.spend(tool, **detail)
        self.log_call(module, tool, json.dumps(detail, default=str, sort_keys=True), "ok", budget=f"{b.calls}/{b.cap}", **detail)


def default_context(subject: Subject, store: EvidenceStore, log: Optional[HashChainLog], **kw) -> RunContext:
    """Context for the bare ``run(subject, store, log)`` signature: data under
    ./data, output under ./out/<slug>, real network, default cap."""
    out_dir = kw.pop("out_dir", Path("out") / subject.slug)
    data_dir = kw.pop("data_dir", Path("data"))
    return RunContext.build(subject, out_dir, data_dir, store=store, log=log, **kw)
