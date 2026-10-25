"""PDF page index -> printed folio, and plain-language page citations.

The stored claims carry the PDF page index (``attrs.page_expected``: the Nth page of
the PDF). Readers look for the number printed on the page. For the GEH Annual Report
2025 the printed folio is PDF page - 2 on every page that carries one (PDF pages
6-239, RESEARCH.md section 6); pages outside that range carry no folio and are cited
by PDF page instead.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Folio:
    offset: int = -2          # printed = pdf + offset
    first_pdf: int = 6        # first PDF page that carries a printed folio
    last_pdf: int = 239       # last PDF page that carries a printed folio

    def printed(self, pdf_page: int) -> int | None:
        """Printed folio for a PDF page, or None when that page carries no folio."""
        if not isinstance(pdf_page, int) or pdf_page < 1:
            raise ValueError(f"PDF page must be a positive integer, got {pdf_page!r}")
        if self.first_pdf <= pdf_page <= self.last_pdf:
            return pdf_page + self.offset
        return None

    def label(self, pdf_page: int) -> str:
        """'p. 12' for a folio page; 'PDF p. 3' for a page with no printed number."""
        p = self.printed(pdf_page)
        return f"p. {p}" if p is not None else f"PDF p. {pdf_page}"

    def labels(self, pdf_pages: Iterable[int]) -> str:
        """'p. 12', 'pp. 12 and 38', 'pp. 12, 38 and 78' (folio pages sorted, unique)."""
        pages = sorted(set(pdf_pages))
        if not pages:
            return ""
        printed = [self.printed(p) for p in pages]
        if all(x is not None for x in printed):
            nums = [str(x) for x in printed]
            if len(nums) == 1:
                return f"p. {nums[0]}"
            return "pp. " + _join(nums)
        return _join([self.label(p) for p in pages])


def _join(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]
