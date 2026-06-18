import shutil
import pytest
from vfx.ingest.pdf_reader import extract_text, render_pages

pytestmark = pytest.mark.skipif(
    shutil.which("pdftotext") is None, reason="poppler-utils not installed")

FIXTURE = "tests/vfx/fixtures/sample.pdf"

def test_extract_text_returns_nonempty():
    assert len(extract_text(FIXTURE).strip()) > 0

def test_render_pages_writes_pngs(tmp_path):
    pngs = render_pages(FIXTURE, tmp_path, first=1, last=1, dpi=80)
    assert len(pngs) == 1 and pngs[0].exists()
