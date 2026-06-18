"""Simple Timeline model for the CapCut draft writer.

A Timeline is a flat list of Clips placed on layered tracks. The draft writer
(``vfx/capcut/draft.py``) turns this model into a CapCut Desktop project folder
via clone-and-rewrite of the bundled golden skeleton.

All time values are in microseconds (µs), matching CapCut's draft_info.json.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Clip:
    """One media clip placed on the timeline."""

    source_path: str          # absolute path to the media
    timeline_start_us: int    # position on the timeline (target_timerange.start)
    duration_us: int          # how long it plays (target & source duration)
    source_start_us: int = 0  # in-point within the source (source_timerange.start)
    track: int = 0            # layer index; 0 = bottom track
    src_width: int = 1080     # source media dimensions
    src_height: int = 1920


@dataclass
class Timeline:
    """A flat collection of clips plus canvas settings."""

    clips: List[Clip] = field(default_factory=list)
    width: int = 1080         # canvas
    height: int = 1920
    fps: float = 30.0
