from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

# Maps a structured capture-requirement key to the equipment it implies.
_REQUIRES = {"locked_off": "tripod", "green_screen": "green_screen"}


@dataclass
class Capabilities:
    equipment: List[str] = field(default_factory=list)
    props: List[str] = field(default_factory=list)
    location: Optional[str] = None


def requirement_met(capture_requirements: Dict[str, Any], caps: Capabilities) -> bool:
    have = set(caps.equipment)
    for key, needed in _REQUIRES.items():
        if capture_requirements.get(key) and needed not in have:
            return False
    return True
