"""Append-only, hash-chained JSONL log (spec C12, C13; CL-012, CL-013).

Each record carries `seq`, `prev_sha256` (sha256 of the previous record's
canonical JSON, GENESIS for the first) and its own `sha256`. `verify()`
recomputes the chain so any out-of-band edit, deletion or reordering of a
record is detected (test T-11).
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

GENESIS = "0" * 64


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")


def sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


@dataclass
class ChainVerification:
    ok: bool
    records: int
    broken_at: Optional[int] = None  # seq of the first bad record
    detail: Optional[str] = None


class HashChainLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._last_hash, self._seq = self._tail()

    def _tail(self) -> tuple[str, int]:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return GENESIS, 0
        last = None
        with self.path.open("rb") as f:
            for line in f:
                if line.strip():
                    last = line
        if last is None:
            return GENESIS, 0
        rec = json.loads(last)
        return rec["sha256"], int(rec["seq"])

    def append(self, record: dict[str, Any]) -> dict[str, Any]:
        rec = dict(record)
        rec["seq"] = self._seq + 1
        rec["ts"] = rec.get("ts") or datetime.now(timezone.utc).isoformat()
        rec["prev_sha256"] = self._last_hash
        rec.pop("sha256", None)
        rec["sha256"] = sha256_hex(canonical(rec))
        line = json.dumps(rec, sort_keys=True, ensure_ascii=False, default=str) + "\n"
        # append-only: O_APPEND so concurrent writers cannot overwrite earlier bytes
        fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            os.write(fd, line.encode("utf-8"))
            os.fsync(fd)
        finally:
            os.close(fd)
        self._last_hash, self._seq = rec["sha256"], rec["seq"]
        return rec

    def log_inference(
        self,
        *,
        run_id: str,
        model_id: str,
        model_version: str,
        caller: str,
        prompt: str,
        tool_calls: list[dict[str, Any]],
        outcome: str,
        output_ref: Optional[str] = None,
        tokens_in: int = 0,
        tokens_out: int = 0,
        region_asserted: Optional[str] = None,
        extra: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Spec 3.1 `Inference` record. The prompt is stored as a hash only
        (raw prompt belongs in the encrypted run store, not here)."""
        rec = {
            "type": "inference",
            "run_id": run_id,
            "model_id": model_id,
            "model_version": model_version,
            "caller": caller,
            "prompt_sha256": sha256_hex(prompt),
            "tool_calls": tool_calls,
            "output_ref": output_ref,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "outcome": outcome,
            "region_asserted": region_asserted,
        }
        if extra:
            rec.update(extra)
        return self.append(rec)

    def records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]

    def verify(self) -> ChainVerification:
        prev = GENESIS
        n = 0
        for rec in self.records():
            n += 1
            seq = rec.get("seq")
            if seq != n:
                return ChainVerification(False, n, seq, f"sequence gap: expected {n}, found {seq}")
            if rec.get("prev_sha256") != prev:
                return ChainVerification(False, n, seq, "prev_sha256 does not match previous record")
            body = {k: v for k, v in rec.items() if k != "sha256"}
            if sha256_hex(canonical(body)) != rec.get("sha256"):
                return ChainVerification(False, n, seq, "record content does not match its sha256")
            prev = rec["sha256"]
        return ChainVerification(True, n)
