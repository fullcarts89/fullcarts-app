import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from vfx.models import AssetSpec
from vfx.qa import probes

# acceptance_checks we can verify deterministically; others -> manual review
_AUTOMATED = {"camera_locked_off", "min_resolution", "min_duration", "has_green_screen"}
# Vision check: same product as the reference asset (needs an API key + a ref).
_VISION = {"product_matches_reference"}


@dataclass
class Verdict:
    passed: bool
    failures: List[str] = field(default_factory=list)       # actionable fix messages
    manual_checks: List[str] = field(default_factory=list)  # need human/vision review


def _run(name: str, path: str, ref_path: Optional[str], tol: Dict) -> "probes.ProbeResult":
    if name == "camera_locked_off":
        if not ref_path:
            return probes.ProbeResult(True, "first shot — no reference to compare")
        return probes.camera_shift_px(path, ref_path, max_px=tol.get("camera_shift_px", 8.0))
    if name == "min_resolution":
        return probes.probe_resolution(path, tol.get("min_w", 720), tol.get("min_h", 1280))
    if name == "min_duration":
        return probes.probe_duration(path, tol.get("min_seconds", 1.0))
    if name == "has_green_screen":
        return probes.has_green_screen(path, tol.get("green_ratio", 0.3))
    raise KeyError(name)


def _vision_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def check_asset(spec: AssetSpec, path: str, ref_path: Optional[str] = None,
                content_client=None) -> Verdict:
    """Run the spec's acceptance checks against ``path``.

    ``ref_path`` is the comparison asset (e.g. current_pack) used by the
    camera-lock and the vision product-match checks. ``content_client`` is an
    optional injected Anthropic-style client (tests pass a fake; production
    leaves it None so the real Haiku client is built lazily).
    """
    failures: List[str] = []
    manual: List[str] = []
    for name in spec.acceptance_checks:
        if name in _VISION:
            # Same-product vision check. Needs both a reference and an API key;
            # without either, degrade to a free manual-confirm flag.
            if ref_path is None:
                manual.append(f"{name} (no reference asset to compare)")
                continue
            if content_client is None and not _vision_available():
                manual.append(
                    f"{name} (set ANTHROPIC_API_KEY to auto-verify; "
                    "for now, confirm old_pack is the same product, just larger)")
                continue
            from vfx.qa.content_check import compare_products
            v = compare_products(ref_path, path, client=content_client)
            if not v.passed:
                failures.append(f"{name}: {v.detail}")
            continue
        if name not in _AUTOMATED:
            manual.append(name)
            continue
        res = _run(name, path, ref_path, spec.variance_tolerance)
        if not res.passed:
            failures.append(f"{name}: {res.detail}")
    return Verdict(passed=not failures, failures=failures, manual_checks=manual)
