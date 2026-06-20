import subprocess
from dataclasses import dataclass
from typing import Optional, Union
from pathlib import Path
import cv2
import numpy as np

PathLike = Union[str, Path]


@dataclass
class ProbeResult:
    passed: bool
    detail: str
    value: Optional[float] = None


def _first_frame(path: PathLike):
    cap = cv2.VideoCapture(str(path))
    # Apply the file's display-matrix rotation so frames are display-oriented
    # (matches probe_resolution). No-op on builds/files without the flag.
    try:
        cap.set(cv2.CAP_PROP_ORIENTATION_AUTO, 1)
    except AttributeError:
        pass
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise ValueError("cannot read a frame from " + str(path))
    return frame


def video_rotation_deg(path: PathLike) -> int:
    """Display-matrix rotation in degrees (0/90/180/270).

    iPhone clips are commonly stored as 1920x1080 with a ``rotation=-90`` (or a
    legacy ``rotate`` tag) display matrix, so they *display* vertical even though
    the encoded stream is landscape. We read that flag so the resolution check
    judges the **displayed** orientation, not the raw stream.
    """
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream_side_data=rotation:stream_tags=rotate",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=False)
    deg = 0
    for line in out.stdout.splitlines():
        tok = line.split("=", 1)[-1].strip()  # tolerate "rotation=-90" or bare "-90"
        try:
            deg = int(float(tok))
        except ValueError:
            continue
        break
    return abs(deg) % 360


def probe_resolution(path: PathLike, min_w: int, min_h: int) -> ProbeResult:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True)
    w, h = (int(x) for x in out.stdout.split())
    # Respect display-matrix rotation: a 90/270 rotation swaps display W/H.
    if video_rotation_deg(path) in (90, 270):
        w, h = h, w
    ok = w >= min_w and h >= min_h
    return ProbeResult(ok, f"{w}x{h} (min {min_w}x{min_h})", value=float(w * h))


def probe_duration(path: PathLike, min_seconds: float) -> ProbeResult:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True)
    dur = float(out.stdout.strip() or 0.0)
    return ProbeResult(dur >= min_seconds, f"{dur:.2f}s (min {min_seconds}s)", value=dur)


def camera_shift_px(shot_a: PathLike, shot_b: PathLike, max_px: float = 8.0) -> ProbeResult:
    a = cv2.cvtColor(_first_frame(shot_a), cv2.COLOR_BGR2GRAY)
    b = cv2.cvtColor(_first_frame(shot_b), cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(1000)
    ka, da = orb.detectAndCompute(a, None)
    kb, db = orb.detectAndCompute(b, None)
    if da is None or db is None:
        return ProbeResult(False, "no features detected")
    matches = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(da, db)
    if len(matches) < 8:
        return ProbeResult(False, "too few feature matches")
    disp = [float(np.linalg.norm(np.array(ka[m.queryIdx].pt) - np.array(kb[m.trainIdx].pt)))
            for m in matches]
    median = float(np.median(disp))
    return ProbeResult(median <= max_px,
                       f"median camera shift {median:.1f}px (max {max_px})", value=median)


def has_green_screen(path: PathLike, min_ratio: float = 0.3) -> ProbeResult:
    hsv = cv2.cvtColor(_first_frame(path), cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (35, 80, 40), (85, 255, 255))
    ratio = float((mask > 0).mean())
    return ProbeResult(ratio >= min_ratio,
                       f"green pixels {ratio:.0%} (min {min_ratio:.0%})", value=ratio)
