from dataclasses import dataclass, field
from typing import Dict, List, Optional
from vfx.models import AssetSpec
from vfx.qa import probes

# acceptance_checks we can verify deterministically; others -> manual review
_AUTOMATED = {"camera_locked_off", "min_resolution", "min_duration", "has_green_screen"}


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


def check_asset(spec: AssetSpec, path: str, ref_path: Optional[str] = None) -> Verdict:
    failures: List[str] = []
    manual: List[str] = []
    for name in spec.acceptance_checks:
        if name not in _AUTOMATED:
            manual.append(name)
            continue
        res = _run(name, path, ref_path, spec.variance_tolerance)
        if not res.passed:
            failures.append(f"{name}: {res.detail}")
    return Verdict(passed=not failures, failures=failures, manual_checks=manual)
