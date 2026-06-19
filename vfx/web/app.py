"""Local FastAPI backend wrapping the VFX engine.

Single local user: session state (selected recipe slug + accepted asset paths)
lives in ``app.state`` so the front-end can drive the
recommend -> plan -> upload -> build flow without a database.

Nothing here calls an external service. ``create_app`` is a factory so tests can
inject a temp store, work/out dirs, and a fake QA check.
"""

import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import vfx
from vfx.capcut.compile import compile_timeline
from vfx.capcut.draft import write_project
from vfx.db import RecipeStore
from vfx.intake import Capabilities
from vfx.models import AssetSpec, VFXRecipe
from vfx.qa.gate import check_asset
from vfx.recommender import recommend_for_script

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


_BUNDLED_DB = Path(vfx.__file__).parent / "data" / "recipes.db"
_USER_DB = Path.home() / ".vfx" / "vfx.db"
_DEFAULT_PROJECTS = (Path.home() / "Movies" / "CapCut" / "User Data" /
                     "Projects" / "com.lveditor.draft")


class RecommendBody(BaseModel):
    script: str = ""
    equipment: List[str] = []
    props: List[str] = []
    location: Optional[str] = None
    k: int = 3


class PlanBody(BaseModel):
    slug: str


class BuildBody(BaseModel):
    slug: str
    out_dir: Optional[str] = None


def _store_for(path: str) -> RecipeStore:
    """A fresh store bound to ``path``.

    ``RecipeStore`` holds a single sqlite connection that is pinned to the thread
    that created it; FastAPI dispatches sync endpoints on a worker thread, so we
    reopen per request rather than reuse the connection created at app build time.
    """
    return RecipeStore(path)


def _merged_recipes(store_path: str) -> List[VFXRecipe]:
    """Bundled recipes, with user-ingested recipes overriding by slug."""
    by_slug: Dict[str, VFXRecipe] = {r.slug: r for r in _store_for(store_path).all()}
    if _USER_DB.exists() and str(_USER_DB) != store_path:
        try:
            user_store = RecipeStore(_USER_DB)
            for r in user_store.all():
                by_slug[r.slug] = r
        except Exception:  # noqa: BLE001 - a bad user db must not break the app
            pass
    return list(by_slug.values())


def _filming_step_for(recipe: VFXRecipe, asset_name: str) -> str:
    """Return the "<name>: ..." filming-step text for an asset, else ""."""
    prefix = asset_name.lower() + ":"
    for step in recipe.filming_steps:
        if step.lower().startswith(prefix):
            return step.split(":", 1)[1].strip()
    return ""


def create_app(store: Optional[RecipeStore] = None,
               recipes_provider: Optional[Callable[[], List[VFXRecipe]]] = None,
               work_dir: Optional[Any] = None,
               out_dir: Optional[Any] = None,
               qa_check: Optional[Callable[..., Any]] = None) -> FastAPI:
    store_path = store.path if store is not None else None
    if work_dir is None:
        work_dir = Path(tempfile.mkdtemp(prefix="vfx-web-"))
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    if out_dir is None:
        out_dir = _DEFAULT_PROJECTS if _DEFAULT_PROJECTS.exists() else work_dir / "builds"
    out_dir = Path(out_dir)
    if qa_check is None:
        qa_check = check_asset

    app = FastAPI(title="Viral VFX CapCut Agent")
    app.state.session = {"slug": None, "assets": {}}
    app.state.store_path = store_path
    app.state.work_dir = work_dir
    app.state.out_dir = out_dir
    app.state.qa_check = qa_check

    def _resolve_recipes() -> List[VFXRecipe]:
        """Per-request recipe list from the active source.

        Reloaded each request so newly-added manuals show up live.
        """
        if recipes_provider is not None:
            return list(recipes_provider())
        if store_path is not None:
            return list(_merged_recipes(store_path))
        from vfx.ingest import manuals_source
        return manuals_source.all_recipes()

    def _recipes_and_index():
        """Return ``(recipes_list, by_slug_dict)`` for the active source."""
        recipes = _resolve_recipes()
        by_slug: Dict[str, VFXRecipe] = {r.slug: r for r in recipes}
        return recipes, by_slug

    static_dir = Path(__file__).parent / "static"
    if static_dir.is_dir():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/api/health")
    def health() -> Dict[str, Any]:
        recipes, _ = _recipes_and_index()
        return {"status": "ok", "recipes": len(recipes)}

    @app.post("/api/recommend")
    def recommend(body: RecommendBody) -> Dict[str, Any]:
        app.state.session = {"slug": None, "assets": {}}
        caps = Capabilities(equipment=body.equipment, props=body.props,
                            location=body.location)
        recipes, _ = _recipes_and_index()
        matches = recommend_for_script(recipes, body.script, caps, k=body.k)
        return {"candidates": [
            {"slug": m.recipe.slug, "title": m.recipe.title,
             "technique_primitive": m.recipe.technique_primitive,
             "score": m.score, "why": m.why, "feasible": m.feasible,
             "ai": m.recipe.is_ai_generated}
            for m in matches]}

    @app.post("/api/plan")
    def plan(body: PlanBody) -> Dict[str, Any]:
        _, by_slug = _recipes_and_index()
        recipe = by_slug.get(body.slug)
        if recipe is None:
            raise HTTPException(status_code=404, detail=f"no recipe {body.slug!r}")
        app.state.session = {"slug": body.slug, "assets": {}}
        inputs = [{
            "name": a.name,
            "what_to_film": _filming_step_for(recipe, a.name),
            "requirements": a.capture_requirements,
            "acceptance_checks": a.acceptance_checks,
        } for a in recipe.asset_spec]
        return {"slug": recipe.slug, "title": recipe.title,
                "gear": recipe.gear, "inputs": inputs,
                "is_ai_generated": recipe.is_ai_generated,
                "ai_generation": recipe.ai_generation}

    @app.post("/api/upload")
    async def upload(file: UploadFile = File(...),
                     slug: str = Form(...),
                     asset_name: str = Form(...)) -> Dict[str, Any]:
        _, by_slug = _recipes_and_index()
        recipe = by_slug.get(slug)
        if recipe is None:
            raise HTTPException(status_code=400, detail=f"unknown slug {slug!r}")
        spec: Optional[AssetSpec] = next(
            (a for a in recipe.asset_spec if a.name == asset_name), None)
        if spec is None:
            raise HTTPException(status_code=400,
                                detail=f"unknown asset {asset_name!r}")

        dest_dir = work_dir / slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        filename = file.filename or "upload"
        saved = dest_dir / f"{asset_name}__{filename}"
        saved.write_bytes(await file.read())

        session = app.state.session
        ref_path = next(iter(session["assets"].values()), None)
        verdict = qa_check(spec, str(saved), ref_path)
        if verdict.passed:
            session["assets"][asset_name] = str(saved)
        return {"accepted": bool(verdict.passed),
                "failures": list(verdict.failures),
                "manual_checks": list(verdict.manual_checks),
                "path": str(saved)}

    @app.post("/api/build")
    def build(body: BuildBody) -> Dict[str, Any]:
        _, by_slug = _recipes_and_index()
        recipe = by_slug.get(body.slug)
        if recipe is None:
            raise HTTPException(status_code=400, detail=f"unknown slug {body.slug!r}")
        assets = app.state.session.get("assets", {})
        if not assets:
            raise HTTPException(status_code=400, detail="no assets uploaded yet")
        dest_out = Path(body.out_dir) if body.out_dir else out_dir
        dest_out.mkdir(parents=True, exist_ok=True)
        res = compile_timeline(recipe, assets)
        dest = write_project(res.timeline, dest_out, body.slug)
        notes = list(res.manual_notes or [])
        if recipe.is_ai_generated:
            for gen in recipe.ai_generation:
                tool = gen.get("tool") or gen.get("provider") or "AI tool"
                what = gen.get("operation") or gen.get("prompt_strategy") or "generate asset"
                notes.append(f"AI step: generate via {tool} — {what}")
        checklist_md = "# Finish by hand\n\n" + (
            "\n".join("- [ ] " + n for n in notes) if notes
            else "Nothing flagged — the draft assembled cleanly.")
        (dest / "FINISH_BY_HAND.md").write_text(checklist_md, encoding="utf-8")
        return {"project_path": str(dest), "checklist": notes,
                "out_dir": str(dest_out)}

    @app.get("/")
    def root() -> Any:
        index = static_dir / "index.html"
        if index.exists():
            return FileResponse(str(index))
        return {"status": "backend ok — front-end not built yet"}

    return app


app = create_app()
