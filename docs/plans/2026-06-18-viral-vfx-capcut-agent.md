# Viral VFX CapCut Agent — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a local, personal Python tool that takes a video idea from script
to an assembled CapCut edit, driven by a library of step-by-step VFX manuals.

**Architecture:** A single local Python package (`vfx/`) using the Anthropic SDK.
Phase 0 ingests PDF manuals into a SQLite `VFXRecipe` store. Phase 1 is the
"brain" (Script Studio → Context Intake → Recommender → Asset Director → Asset QA
Gate) plus a CapCut **draft-file writer** that emits a pre-assembled project +
finish-by-hand checklist (zero computer use). Phase 2 adds a computer-use
executor for GUI-only steps (runs on the Mac). Phase 3 adds verification + scale.

**Tech Stack:** Python 3.9 (repo convention: no `X|Y` unions, no `dict[...]`/`list[...]`
in annotations — use `typing`), Anthropic SDK (Claude Opus 4.8 + vision), SQLite
(stdlib), poppler-utils (`pdftotext`/`pdftoppm`), ffmpeg, OpenCV, pytest.

**Design doc:** `docs/plans/2026-06-18-viral-vfx-capcut-agent-design.md`

---

## Conventions for every task

- **TDD:** write the failing test, run it red, implement minimally, run it green, commit.
- **Python 3.9:** `Optional[X]`, `Union[X,Y]`, `List`, `Dict`, `Set` from `typing`. Never `X|Y`, `list[...]`.
- **Commits:** end the body with the repo's required trailers (see CLAUDE.md / existing commits). Keep messages scoped, e.g. `feat(vfx): ...`.
- **No network in unit tests:** all Anthropic calls go through a thin client wrapper that is mocked in tests. Real-API checks are separate, marked `@pytest.mark.live` and skipped by default.
- **Run tests:** `cd /home/user/fullcarts-app && python -m pytest tests/vfx/ -v`

---

## Task 0: Scaffold the `vfx/` package

**Files:**
- Create: `vfx/__init__.py`
- Create: `vfx/requirements.txt`
- Create: `tests/vfx/__init__.py`
- Create: `tests/vfx/test_smoke.py`
- Create: `pytest.ini` (only if absent at repo root)

**Step 1: Write the failing test**

```python
# tests/vfx/test_smoke.py
import vfx

def test_package_imports():
    assert hasattr(vfx, "__version__")
```

**Step 2: Run it red**

Run: `python -m pytest tests/vfx/test_smoke.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'vfx'`).

**Step 3: Implement**

```python
# vfx/__init__.py
__version__ = "0.1.0"
```

```text
# vfx/requirements.txt
anthropic>=0.92.0
opencv-python-headless>=4.9
pytest>=8.0
```

```ini
# pytest.ini  (repo root — create only if not present)
[pytest]
markers =
    live: tests that hit the real Anthropic API (skipped unless --run-live)
```

**Step 4: Run it green**

Run: `python -m pytest tests/vfx/test_smoke.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add vfx/ tests/vfx/ pytest.ini
git commit -m "feat(vfx): scaffold package"
```

---

## Task 1: Data model — `VFXRecipe` and `Channel`

**Files:**
- Create: `vfx/models.py`
- Test: `tests/vfx/test_models.py`

**Step 1: Write the failing test**

```python
# tests/vfx/test_models.py
from vfx.models import VFXRecipe, EditStep, AssetSpec, Channel

def test_channel_values():
    assert {c.value for c in Channel} == {"DRAFT", "GUI", "JUDGMENT"}

def test_recipe_roundtrips_to_dict():
    recipe = VFXRecipe(
        slug="make-object-appear",
        title="Make an Object Appear",
        difficulty="beginner",
        editor="CapCut",
        shot_on="phone",
        technique_primitive="clean_plate_mask_reveal",
        summary="Snap to make an object appear.",
        asset_spec=[
            AssetSpec(name="action_shot", type="shot",
                      capture_requirements={"locked_off": True},
                      acceptance_checks=["camera_locked_off", "object_present"],
                      variance_tolerance={"camera_shift_px": 8}),
            AssetSpec(name="clean_plate", type="shot",
                      capture_requirements={"locked_off": True},
                      acceptance_checks=["camera_locked_off", "object_absent"],
                      variance_tolerance={"camera_shift_px": 8}),
        ],
        filming_steps=["Snap, pick up cup, drink.", "Clean plate, no cup."],
        edit_steps=[
            EditStep(index=1, instruction="Split and delete the front.",
                     capcut_target="timeline/split", params={}, channel=Channel.DRAFT),
            EditStep(index=2, instruction="Select the mask tool.",
                     capcut_target="video/mask", params={"shape": "rectangle"},
                     channel=Channel.GUI, reference_screenshot="edit-07.png"),
            EditStep(index=3, instruction="Fix white balance to taste.",
                     capcut_target="adjustment/basic", params={}, channel=Channel.JUDGMENT),
        ],
    )
    d = recipe.to_dict()
    assert d["slug"] == "make-object-appear"
    assert d["edit_steps"][1]["channel"] == "GUI"
    again = VFXRecipe.from_dict(d)
    assert again == recipe
```

**Step 2: Run it red** — `python -m pytest tests/vfx/test_models.py -v` → FAIL.

**Step 3: Implement**

```python
# vfx/models.py
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any


class Channel(str, Enum):
    DRAFT = "DRAFT"        # expressible in CapCut's draft file
    GUI = "GUI"            # needs computer use
    JUDGMENT = "JUDGMENT"  # handed back to the user


@dataclass
class AssetSpec:
    name: str
    type: str  # shot | clip | audio | ai_element
    capture_requirements: Dict[str, Any] = field(default_factory=dict)
    acceptance_checks: List[str] = field(default_factory=list)
    variance_tolerance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EditStep:
    index: int
    instruction: str
    capcut_target: str
    params: Dict[str, Any] = field(default_factory=dict)
    channel: Channel = Channel.GUI
    reference_screenshot: Optional[str] = None


@dataclass
class VFXRecipe:
    slug: str
    title: str
    difficulty: str
    editor: str
    shot_on: str
    technique_primitive: str
    summary: str
    asset_spec: List[AssetSpec] = field(default_factory=list)
    filming_steps: List[str] = field(default_factory=list)
    edit_steps: List[EditStep] = field(default_factory=list)
    layers_reference: Optional[str] = None
    ingest_confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["edit_steps"] = [
            {**asdict(s), "channel": s.channel.value} for s in self.edit_steps
        ]
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "VFXRecipe":
        asset_spec = [AssetSpec(**a) for a in d.get("asset_spec", [])]
        edit_steps = []
        for s in d.get("edit_steps", []):
            s = dict(s)
            s["channel"] = Channel(s["channel"])
            edit_steps.append(EditStep(**s))
        rest = {k: v for k, v in d.items()
                if k not in ("asset_spec", "edit_steps")}
        return cls(asset_spec=asset_spec, edit_steps=edit_steps, **rest)
```

**Step 4: Run it green.**  **Step 5: Commit** `feat(vfx): VFXRecipe data model`.

---

## Task 2: SQLite store

**Files:**
- Create: `vfx/db.py`
- Test: `tests/vfx/test_db.py`

**Step 1: Failing test**

```python
# tests/vfx/test_db.py
from vfx.db import RecipeStore
from tests.vfx.test_models import test_recipe_roundtrips_to_dict  # reuse builder? -> instead inline
from vfx.models import VFXRecipe

def _recipe():
    return VFXRecipe(slug="s1", title="T", difficulty="beginner", editor="CapCut",
                     shot_on="phone", technique_primitive="clean_plate_mask_reveal",
                     summary="x")

def test_put_get_roundtrip(tmp_path):
    store = RecipeStore(tmp_path / "vfx.db")
    store.put(_recipe())
    got = store.get("s1")
    assert got.title == "T"

def test_list_and_query_by_primitive(tmp_path):
    store = RecipeStore(tmp_path / "vfx.db")
    store.put(_recipe())
    assert [r.slug for r in store.by_primitive("clean_plate_mask_reveal")] == ["s1"]
    assert store.get("missing") is None
```

**Step 2: Red.**

**Step 3: Implement**

```python
# vfx/db.py
import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Union
from vfx.models import VFXRecipe


class RecipeStore:
    def __init__(self, path: Union[str, Path]):
        self.path = str(path)
        self._conn = sqlite3.connect(self.path)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS recipes ("
            " slug TEXT PRIMARY KEY,"
            " technique_primitive TEXT,"
            " doc TEXT NOT NULL)"
        )
        self._conn.commit()

    def put(self, recipe: VFXRecipe) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO recipes VALUES (?,?,?)",
            (recipe.slug, recipe.technique_primitive,
             json.dumps(recipe.to_dict())),
        )
        self._conn.commit()

    def get(self, slug: str) -> Optional[VFXRecipe]:
        row = self._conn.execute(
            "SELECT doc FROM recipes WHERE slug=?", (slug,)).fetchone()
        return VFXRecipe.from_dict(json.loads(row[0])) if row else None

    def all(self) -> List[VFXRecipe]:
        rows = self._conn.execute("SELECT doc FROM recipes").fetchall()
        return [VFXRecipe.from_dict(json.loads(r[0])) for r in rows]

    def by_primitive(self, primitive: str) -> List[VFXRecipe]:
        rows = self._conn.execute(
            "SELECT doc FROM recipes WHERE technique_primitive=?",
            (primitive,)).fetchall()
        return [VFXRecipe.from_dict(json.loads(r[0])) for r in rows]
```

**Step 4: Green.**  **Step 5: Commit** `feat(vfx): SQLite recipe store`.

---

## Task 3: PDF reader (text + page rasters)

**Files:**
- Create: `vfx/ingest/__init__.py`
- Create: `vfx/ingest/pdf_reader.py`
- Test: `tests/vfx/test_pdf_reader.py`

Wraps `pdftotext` and `pdftoppm` (poppler). On the dev container install with
`apt-get install -y poppler-utils`. Tests use a tiny committed fixture PDF or
skip if poppler is absent.

**Step 1: Failing test**

```python
# tests/vfx/test_pdf_reader.py
import shutil
import pytest
from vfx.ingest.pdf_reader import extract_text, render_pages

pytestmark = pytest.mark.skipif(
    shutil.which("pdftotext") is None, reason="poppler-utils not installed")

FIXTURE = "tests/vfx/fixtures/sample.pdf"  # commit a 1-2 page PDF here

def test_extract_text_returns_nonempty():
    assert len(extract_text(FIXTURE).strip()) > 0

def test_render_pages_writes_pngs(tmp_path):
    pngs = render_pages(FIXTURE, tmp_path, first=1, last=1, dpi=80)
    assert len(pngs) == 1 and pngs[0].exists()
```

**Step 2: Red.**

**Step 3: Implement**

```python
# vfx/ingest/pdf_reader.py
import subprocess
from pathlib import Path
from typing import List, Union

PathLike = Union[str, Path]


def extract_text(pdf: PathLike) -> str:
    out = subprocess.run(
        ["pdftotext", str(pdf), "-"],
        capture_output=True, text=True, check=True)
    return out.stdout


def render_pages(pdf: PathLike, out_dir: PathLike, first: int, last: int,
                 dpi: int = 100) -> List[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / "page"
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(dpi), "-f", str(first), "-l", str(last),
         str(pdf), str(prefix)],
        capture_output=True, check=True)
    return sorted(out_dir.glob("page*.png"))
```

**Step 4: Green.** **Step 5: Commit** `feat(vfx): poppler PDF reader`. Also `git add tests/vfx/fixtures/sample.pdf`.

> **Note:** create the fixture by copying the first 2 pages of the user's sample, or any tiny PDF. Keep it small.

---

## Task 4: Manual text parser (deterministic sections)

The sample manual has a stable shape: a metadata header (difficulty / lessons /
shot-on / editor), `Part 1 — Filming` (numbered), `Part 2 — Editing in CapCut`
(numbered). Parse what's deterministic with regex; leave channel-classification
and screenshot-reading to Claude (Task 5).

**Files:**
- Create: `vfx/ingest/parser.py`
- Test: `tests/vfx/test_parser.py`

**Step 1: Failing test** (drive off a text fixture captured from `pdftotext`)

```python
# tests/vfx/test_parser.py
from vfx.ingest.parser import parse_manual_text

SAMPLE = open("tests/vfx/fixtures/sample.txt").read()  # commit the pdftotext dump

def test_parses_title_and_meta():
    p = parse_manual_text(SAMPLE)
    assert p["title"] == "Make an Object Appear"
    assert p["difficulty"].lower() == "beginner"
    assert p["editor"] == "CapCut"

def test_splits_filming_and_edit_steps():
    p = parse_manual_text(SAMPLE)
    assert len(p["filming_steps"]) >= 5
    assert len(p["edit_steps"]) >= 20
    assert all(isinstance(s, str) for s in p["edit_steps"])
```

**Step 2: Red.**

**Step 3: Implement** (regex-based; return a plain dict, not yet a `VFXRecipe`)

```python
# vfx/ingest/parser.py
import re
from typing import Dict, List, Any

_TITLE_RE = re.compile(r"RECREATION GUIDE\s*\n+\s*(.+)", re.IGNORECASE)
_DIFF_RE = re.compile(r"(Beginner|Intermediate|Advanced)", re.IGNORECASE)


def _numbered_block(text: str) -> List[str]:
    # Lines that are a bare integer start a step; following lines are its body.
    steps: List[str] = []
    cur: List[str] = []
    for line in text.splitlines():
        if re.fullmatch(r"\s*\d+\s*", line):
            if cur:
                steps.append(" ".join(cur).strip())
            cur = []
        elif line.strip():
            cur.append(line.strip())
    if cur:
        steps.append(" ".join(cur).strip())
    return [s for s in steps if s]


def parse_manual_text(text: str) -> Dict[str, Any]:
    title_m = _TITLE_RE.search(text)
    title = title_m.group(1).strip() if title_m else "Untitled"

    diff_m = _DIFF_RE.search(text)
    difficulty = diff_m.group(1) if diff_m else "unknown"

    # Split on the two part headers.
    filming = ""
    editing = ""
    parts = re.split(r"Part\s*1\s*[—-]\s*Filming", text, flags=re.IGNORECASE)
    if len(parts) > 1:
        rest = parts[1]
        edit_split = re.split(r"Part\s*2\s*[—-]\s*Editing[^\n]*", rest,
                              flags=re.IGNORECASE)
        filming = edit_split[0]
        editing = edit_split[1] if len(edit_split) > 1 else ""

    return {
        "title": title,
        "difficulty": difficulty,
        "editor": "CapCut" if "CapCut" in text else "unknown",
        "shot_on": "phone" if re.search(r"Shot on phone", text, re.I) else "unknown",
        "filming_steps": _numbered_block(filming),
        "edit_steps": _numbered_block(editing),
    }
```

**Step 4: Green.** **Step 5: Commit** `feat(vfx): deterministic manual parser`.

> Capture the fixture: `pdftotext sample.pdf tests/vfx/fixtures/sample.txt`.

---

## Task 5: Claude-backed enrichment (channel classification + asset spec)

This is where Claude turns parsed steps into structured `EditStep`s (assigning
`channel` DRAFT/GUI/JUDGMENT and `capcut_target`), infers the `asset_spec` +
`acceptance_checks` from the filming notes, and names the `technique_primitive`.

**Files:**
- Create: `vfx/llm.py` (thin Anthropic wrapper, mockable)
- Create: `vfx/ingest/enrich.py`
- Test: `tests/vfx/test_enrich.py`

**Step 1: Failing test (mock the LLM)**

```python
# tests/vfx/test_enrich.py
from vfx.ingest.enrich import enrich_recipe
from vfx.models import Channel

class FakeLLM:
    def json(self, system, user, schema_hint=None):
        return {
            "technique_primitive": "clean_plate_mask_reveal",
            "summary": "Snap to make an object appear.",
            "asset_spec": [
                {"name": "action_shot", "type": "shot",
                 "capture_requirements": {"locked_off": True},
                 "acceptance_checks": ["camera_locked_off", "object_present"],
                 "variance_tolerance": {"camera_shift_px": 8}},
                {"name": "clean_plate", "type": "shot",
                 "capture_requirements": {"locked_off": True},
                 "acceptance_checks": ["camera_locked_off", "object_absent"],
                 "variance_tolerance": {"camera_shift_px": 8}},
            ],
            "edit_steps": [
                {"index": 1, "instruction": "Split and delete the front.",
                 "capcut_target": "timeline/split", "params": {}, "channel": "DRAFT"},
                {"index": 2, "instruction": "Select the mask tool.",
                 "capcut_target": "video/mask", "params": {"shape": "rectangle"},
                 "channel": "GUI"},
            ],
        }

def test_enrich_builds_recipe():
    parsed = {"title": "Make an Object Appear", "difficulty": "beginner",
              "editor": "CapCut", "shot_on": "phone",
              "filming_steps": ["Snap, drink.", "Clean plate."],
              "edit_steps": ["Split and delete the front.", "Select the mask tool."]}
    recipe = enrich_recipe(parsed, slug="make-object-appear", llm=FakeLLM())
    assert recipe.technique_primitive == "clean_plate_mask_reveal"
    assert recipe.edit_steps[0].channel == Channel.DRAFT
    assert recipe.edit_steps[1].channel == Channel.GUI
    assert len(recipe.asset_spec) == 2
```

**Step 2: Red.**

**Step 3: Implement**

```python
# vfx/llm.py
import json
import os
from typing import Any, Dict, List, Optional
import anthropic

MODEL = "claude-opus-4-8"


class LLM:
    """Thin wrapper. Inject a fake in tests; this one hits the real API."""
    def __init__(self, client: Optional[anthropic.Anthropic] = None):
        self._client = client or anthropic.Anthropic()

    def json(self, system: str, user: str,
             schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = dict(
            model=MODEL, max_tokens=8000, system=system,
            messages=[{"role": "user", "content": user}],
            thinking={"type": "adaptive"},
        )
        if schema is not None:
            kwargs["output_config"] = {
                "format": {"type": "json_schema", "schema": schema}}
        resp = self._client.messages.create(**kwargs)
        text = next(b.text for b in resp.content if b.type == "text")
        return json.loads(text)
```

```python
# vfx/ingest/enrich.py
from typing import Any, Dict
from vfx.models import VFXRecipe, EditStep, AssetSpec, Channel

_SYSTEM = (
    "You convert a parsed CapCut VFX manual into structured JSON. "
    "For each edit step assign channel: DRAFT (expressible in a CapCut project "
    "file: clip in/out, splits, overlay layers, text, transitions, timing), "
    "GUI (needs direct UI manipulation: mask shape, feather drag, effect picker), "
    "or JUDGMENT (subjective taste handed to the user, e.g. color grading). "
    "Also infer the asset_spec (ordered, in capture sequence) with "
    "acceptance_checks drawn from this set: camera_locked_off, object_present, "
    "object_absent, has_green_screen, min_duration, min_resolution, framing_ok, "
    "lighting_consistent. Name a reusable technique_primitive."
)


def enrich_recipe(parsed: Dict[str, Any], slug: str, llm) -> VFXRecipe:
    user = (
        f"TITLE: {parsed['title']}\n"
        f"FILMING STEPS:\n" + "\n".join(parsed["filming_steps"]) + "\n\n"
        f"EDIT STEPS:\n" + "\n".join(
            f"{i+1}. {s}" for i, s in enumerate(parsed["edit_steps"]))
    )
    out = llm.json(_SYSTEM, user)
    asset_spec = [AssetSpec(**a) for a in out["asset_spec"]]
    edit_steps = [
        EditStep(index=s["index"], instruction=s["instruction"],
                 capcut_target=s["capcut_target"], params=s.get("params", {}),
                 channel=Channel(s["channel"]),
                 reference_screenshot=s.get("reference_screenshot"))
        for s in out["edit_steps"]
    ]
    return VFXRecipe(
        slug=slug, title=parsed["title"], difficulty=parsed["difficulty"],
        editor=parsed["editor"], shot_on=parsed["shot_on"],
        technique_primitive=out["technique_primitive"], summary=out["summary"],
        asset_spec=asset_spec, filming_steps=parsed["filming_steps"],
        edit_steps=edit_steps, ingest_confidence=out.get("confidence", 0.8))
```

**Step 4: Green.** **Step 5: Commit** `feat(vfx): LLM enrichment of parsed manuals`.

---

## Task 6: Ingest pipeline + CLI entrypoint

Glue Tasks 3-5 into one command: `python -m vfx ingest <pdf> [--slug s]` → writes
a recipe to the DB. Also `python -m vfx ingest-dir <folder>`.

**Files:**
- Create: `vfx/ingest/pipeline.py`
- Create: `vfx/__main__.py`
- Test: `tests/vfx/test_ingest_pipeline.py`

**Step 1: Failing test** (mock LLM + reuse the text fixture; skip if poppler absent)

```python
# tests/vfx/test_ingest_pipeline.py
import shutil, pytest
from vfx.ingest.pipeline import ingest_pdf
from vfx.db import RecipeStore
from tests.vfx.test_enrich import FakeLLM

pytestmark = pytest.mark.skipif(shutil.which("pdftotext") is None,
                                reason="poppler not installed")

def test_ingest_pdf_persists_recipe(tmp_path):
    store = RecipeStore(tmp_path / "vfx.db")
    slug = ingest_pdf("tests/vfx/fixtures/sample.pdf", store,
                      llm=FakeLLM(), assets_dir=tmp_path / "shots")
    r = store.get(slug)
    assert r is not None and r.technique_primitive == "clean_plate_mask_reveal"
```

**Step 2: Red.**

**Step 3: Implement**

```python
# vfx/ingest/pipeline.py
import re
from pathlib import Path
from typing import Optional, Union
from vfx.ingest.pdf_reader import extract_text, render_pages
from vfx.ingest.parser import parse_manual_text
from vfx.ingest.enrich import enrich_recipe
from vfx.db import RecipeStore

PathLike = Union[str, Path]


def _slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def ingest_pdf(pdf: PathLike, store: RecipeStore, llm,
               slug: Optional[str] = None,
               assets_dir: Optional[PathLike] = None) -> str:
    text = extract_text(pdf)
    parsed = parse_manual_text(text)
    slug = slug or _slugify(parsed["title"])
    if assets_dir:  # keep page rasters next to the recipe for later reference
        render_pages(pdf, Path(assets_dir) / slug, first=1, last=99, dpi=100)
    recipe = enrich_recipe(parsed, slug=slug, llm=llm)
    store.put(recipe)
    return slug
```

```python
# vfx/__main__.py
import argparse
from pathlib import Path
from vfx.db import RecipeStore
from vfx.llm import LLM
from vfx.ingest.pipeline import ingest_pdf

DEFAULT_DB = Path.home() / ".vfx" / "vfx.db"


def main():
    ap = argparse.ArgumentParser(prog="vfx")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ing = sub.add_parser("ingest")
    ing.add_argument("pdf")
    ing.add_argument("--slug")
    ing.add_argument("--db", default=str(DEFAULT_DB))
    args = ap.parse_args()

    if args.cmd == "ingest":
        Path(args.db).parent.mkdir(parents=True, exist_ok=True)
        store = RecipeStore(args.db)
        slug = ingest_pdf(args.pdf, store, llm=LLM(), slug=args.slug,
                          assets_dir=Path(args.db).parent / "assets")
        print(f"ingested: {slug}")


if __name__ == "__main__":
    main()
```

**Step 4: Green.** **Step 5: Commit** `feat(vfx): ingest pipeline + CLI`.

**End of Phase 0.** You can now ingest the library into a local SQLite DB.

---

## Task 7: Asset QA probes (ffmpeg + OpenCV, deterministic)

The programmatic half of the quality gate. Each probe takes a media path (or two)
and returns a `ProbeResult(passed, detail)`. These are the checks named in
`acceptance_checks`.

**Files:**
- Create: `vfx/qa/__init__.py`
- Create: `vfx/qa/probes.py`
- Test: `tests/vfx/test_probes.py` (use tiny generated clips via ffmpeg; skip if absent)

Probes to implement (one task-step each — write test, red, implement, green):
- `probe_resolution(path, min_w, min_h)` — via `ffprobe`.
- `probe_duration(path, min_seconds)` — via `ffprobe`.
- `camera_shift_px(shot_a, shot_b)` — sample first frames of each, ORB feature
  match + homography (OpenCV), return median displacement in px. Powers
  `camera_locked_off` (compare against `variance_tolerance['camera_shift_px']`).
- `object_present(shot, region=None)` / `object_absent(plate)` — frame-diff
  between the two shots in a region; large diff in the object area = present in
  one, absent in the other. (v1: heuristic; flagged for vision backup in Task 8.)

Representative implementation for the crux probe:

```python
# vfx/qa/probes.py  (excerpt)
import subprocess
from dataclasses import dataclass
from typing import Optional, Tuple
import cv2
import numpy as np


@dataclass
class ProbeResult:
    passed: bool
    detail: str
    value: Optional[float] = None


def _first_frame(path: str) -> "np.ndarray":
    cap = cv2.VideoCapture(path)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise ValueError(f"cannot read frame from {path}")
    return frame


def camera_shift_px(shot_a: str, shot_b: str, max_px: float = 8.0) -> ProbeResult:
    a = cv2.cvtColor(_first_frame(shot_a), cv2.COLOR_BGR2GRAY)
    b = cv2.cvtColor(_first_frame(shot_b), cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(1000)
    ka, da = orb.detectAndCompute(a, None)
    kb, db = orb.detectAndCompute(b, None)
    if da is None or db is None:
        return ProbeResult(False, "no features detected")
    matches = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(da, db)
    if len(matches) < 8:
        return ProbeResult(False, "too few matches")
    disp = [np.linalg.norm(np.array(ka[m.queryIdx].pt) -
                           np.array(kb[m.trainIdx].pt)) for m in matches]
    median = float(np.median(disp))
    return ProbeResult(median <= max_px,
                       f"median camera shift {median:.1f}px (max {max_px})",
                       value=median)
```

Test approach: generate two near-identical clips and one shifted clip with ffmpeg
(`testsrc`, `crop`/`pad` to offset), assert `camera_shift_px` passes on the pair
and fails on the shifted one.

**Commit** per probe, e.g. `feat(vfx): camera-lock probe`.

---

## Task 8: Asset QA Gate (probes + vision, with feedback)

Orchestrates: for an `AssetSpec`, run each named `acceptance_check` (programmatic
probe if one exists, else a Claude-vision check on a sampled frame), collect
failures, and return an actionable verdict the Asset Director can relay.

**Files:**
- Create: `vfx/qa/gate.py`
- Test: `tests/vfx/test_gate.py`

```python
# vfx/qa/gate.py  (shape)
from dataclasses import dataclass
from typing import Dict, List, Callable, Optional
from vfx.models import AssetSpec
from vfx.qa.probes import ProbeResult

@dataclass
class Verdict:
    passed: bool
    failures: List[str]      # human-readable fix instructions

# registry maps check-name -> callable(asset_paths, tolerance) -> ProbeResult
def check_asset(spec: AssetSpec, paths: Dict[str, str],
                registry: Dict[str, Callable], vision=None) -> Verdict:
    failures = []
    for name in spec.acceptance_checks:
        fn = registry.get(name)
        if fn is None and vision is not None:
            res = vision.check(name, paths, spec)     # Claude vision fallback
        elif fn is not None:
            res = fn(paths, spec.variance_tolerance)
        else:
            continue  # unknown check, no vision -> skip (logged)
        if not res.passed:
            failures.append(f"{name}: {res.detail}")
    return Verdict(passed=not failures, failures=failures)
```

Test with a fake registry (deterministic pass/fail) — no media, no API. Then a
`@pytest.mark.live` test runs one real vision check.

**Commit** `feat(vfx): asset QA gate with feedback`.

---

## Task 9: Recommender

Rank recipes by feasibility given a `capabilities` record (gear + props +
location) and the script. v1 is a deterministic scorer (does the user have what
each `capture_requirement` needs?) with an LLM tie-break/explanation. Returns top 3.

**Files:**
- Create: `vfx/intake.py` (the `Capabilities` dataclass + a guided-questions helper)
- Create: `vfx/recommender.py`
- Test: `tests/vfx/test_recommender.py`

```python
# vfx/recommender.py  (core scorer — pure, fully unit-testable)
from typing import Dict, List
from vfx.models import VFXRecipe

def feasibility_score(recipe: VFXRecipe, caps: Dict) -> float:
    needs = []
    for a in recipe.asset_spec:
        if a.capture_requirements.get("green_screen"):
            needs.append("green_screen")
        if a.capture_requirements.get("locked_off"):
            needs.append("tripod")
    have = set(caps.get("equipment", []))
    if not needs:
        return 1.0
    met = sum(1 for n in needs if n in have)
    return met / len(needs)

def top_recipes(recipes: List[VFXRecipe], caps: Dict, k: int = 3):
    ranked = sorted(recipes, key=lambda r: feasibility_score(r, caps),
                    reverse=True)
    return ranked[:k]
```

Test: build 4 recipes with differing needs, assert the achievable ones rank first.
**Commit** `feat(vfx): VFX recommender`.

---

## Task 10: CapCut draft-file writer (the precision spine)

Emit a CapCut Desktop project (`draft_content.json` + folder layout) that
realizes all `Channel.DRAFT` edit steps: place clips on tracks, set in/out points,
splits, overlay layer, transitions, text, timing. **This is the highest-risk,
highest-value buildable component.**

**Approach (de-risked):**
1. First, **capture a golden sample**: on the Mac, create a trivial 2-clip overlay
   project in CapCut, copy its draft folder into `tests/vfx/fixtures/draft_golden/`.
   Treat its JSON as the schema spec.
2. Build the writer to reproduce that golden file from a small intermediate
   `Timeline` model, asserting byte-for-byte (or normalized-JSON) equality.
3. Then extend the `Timeline` model to cover the DRAFT steps of the sample recipe.

**Files:**
- Create: `vfx/capcut/__init__.py`
- Create: `vfx/capcut/timeline.py` (editor-agnostic intermediate model: tracks, clips, in/out, transitions, text)
- Create: `vfx/capcut/draft.py` (Timeline → CapCut draft JSON)
- Create: `vfx/capcut/compile.py` (recipe DRAFT steps + accepted assets → Timeline)
- Test: `tests/vfx/test_draft.py`

**Task 10a:** `Timeline` model + tests (pure data). Commit.
**Task 10b:** `draft.py` reproduces `draft_golden` from an equivalent `Timeline`
(normalized-JSON equality, ignoring volatile fields like ids/timestamps via a
canonicalizer). Commit.
**Task 10c:** `compile.py` walks a recipe's `Channel.DRAFT` steps + the accepted
asset paths and produces a `Timeline`. Unit-test with the sample recipe + dummy
asset paths; assert the produced timeline has the expected clips/overlay/trims.
Commit `feat(vfx): CapCut draft-file writer`.

> If the golden-file schema proves unstable across CapCut versions, pin one
> version (note it in the README) and keep DRAFT scope to the stable structural
> fields; everything else falls to Phase 2 computer use.

---

## Task 11: Finish-by-hand checklist + Phase-1 orchestration

Produce the Phase-1 deliverable: write the draft project, then emit a Markdown
checklist of every `GUI` and `JUDGMENT` step (in order, with the
`reference_screenshot` path) for the user to finish manually in CapCut.

**Files:**
- Create: `vfx/capcut/checklist.py`
- Create: `vfx/session.py` (the end-to-end Phase-1 flow object)
- Create: `vfx/cli` subcommands: `script`, `make`
- Test: `tests/vfx/test_checklist.py`, `tests/vfx/test_session.py`

```python
# vfx/capcut/checklist.py
from typing import List
from vfx.models import VFXRecipe, Channel

def build_checklist(recipe: VFXRecipe) -> str:
    lines = [f"# Finish-by-hand: {recipe.title}", ""]
    n = 0
    for s in recipe.edit_steps:
        if s.channel in (Channel.GUI, Channel.JUDGMENT):
            n += 1
            ref = f"  (see {s.reference_screenshot})" if s.reference_screenshot else ""
            lines.append(f"{n}. [{s.channel.value}] {s.instruction}{ref}")
    if n == 0:
        lines.append("_All steps were assembled automatically._")
    return "\n".join(lines)
```

`session.py` ties it together: Script Studio (conversational, can be a thin
wrapper now) → intake → recommend → user pick → asset loop (Director + QA Gate) →
`compile.py` → `draft.py` → `build_checklist`. Unit-test the non-conversational
spine with fakes; gate conversational bits behind the CLI.

**Commit** `feat(vfx): Phase-1 session — assembled draft + checklist`.

**End of Phase 1.** End-to-end: idea → assembled CapCut draft + manual checklist.

---

## Task 12: Script Studio (conversational)

Flesh out the lean conversational front: co-write hook, beats, SFX cues, b-roll
list, transitions, lighting/design notes into a `Script` object the Recommender
and Director consume. Keep it functional — a guided multi-turn prompt, not a UI.

**Files:**
- Create: `vfx/studio.py`, `vfx/script_model.py`
- Test: `tests/vfx/test_studio.py` (mock LLM; assert the structured `Script` shape)

**Commit** `feat(vfx): Script Studio`.

---

## Phase 2 (runs on the Mac): computer-use executor

Lower granularity — depends on Phase 1 outputs and on real CapCut. Each is a
TDD task when reached.

- **T13:** `vfx/computer_use/driver.py` — Agent-SDK computer-use loop (self-hosted),
  screenshot → action, scoped to a single CapCut window.
- **T14:** `vfx/computer_use/anchors.py` — match a step's `reference_screenshot`
  against the live screen (template match / vision) to locate the target control.
- **T15:** GUI-step executor — consume `Channel.GUI` steps from a recipe, drive
  the app via the driver + anchors; verify each action with a follow-up screenshot.
- **T16:** Wire into `session.py` behind a `--auto-gui` flag; default stays
  Phase-1 (checklist) so a CapCut UI change degrades gracefully.

## Phase 3: verification + scale

- **T17:** Render-vs-script verifier — export the timeline, sample frames, ask
  Claude vision whether the result matches the recipe's `finished_still` + script
  beats; produce a pass/fix report.
- **T18:** Batch-ingest the full PDF library; add an ingest-confidence review queue
  for low-confidence recipes.
- **T19:** Primitive library — factor shared `technique_primitive` logic
  (clean-plate-mask-reveal, etc.) so new manuals reuse compile/QA logic.

---

## Testing strategy summary

- **Unit (default):** pure logic (models, db, parser, recommender scorer, timeline,
  checklist) + LLM/vision behind fakes. No network, no media beyond tiny fixtures.
- **Media (skipif ffmpeg/poppler absent):** probes + pdf reader against generated
  clips / a tiny fixture PDF.
- **Live (`-m live`, opt-in):** one real enrichment, one real vision QA, one real
  computer-use smoke (Mac only).
- **Golden:** CapCut draft writer against a captured `draft_golden` fixture.

## Known environment constraints

- This repo (cloud container) builds/tests **everything except** real CapCut
  driving. Phase 2 + the `draft_golden` capture require the user's Mac.
- Pin a CapCut Desktop version once draft-file work starts; record it in
  `vfx/README.md`.
