"""Offline fixtures. Nothing in this suite touches the network: the fixture web
is served by plumbresearch.context.LocalDocTransport from fixtures/acme-bank/web.yaml."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from plumbresearch.context import RunContext
from plumbresearch.subject import load_subject

PKG = Path(__file__).resolve().parents[1] / "plumbresearch"
FIXTURES = PKG / "fixtures"
ACME = FIXTURES / "acme-bank" / "subject.yaml"
AS_OF = date(2026, 10, 25)


@pytest.fixture
def acme():
    return load_subject(ACME)


@pytest.fixture
def ctx(acme, tmp_path):
    c = RunContext.build(acme, tmp_path / "out", FIXTURES, fixtures=True, cap=40, as_of=AS_OF)
    yield c
    c.store.close()
