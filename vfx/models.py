from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any


class Channel(str, Enum):
    DRAFT = "DRAFT"
    GUI = "GUI"
    JUDGMENT = "JUDGMENT"


@dataclass
class AssetSpec:
    name: str
    type: str
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
    action: Optional[str] = None     # raw verb, e.g. "overlay", "duplicate"
    target: Optional[str] = None     # raw target, e.g. "stepin_clip"


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
    gear: Optional[str] = None
    reference_images: List[str] = field(default_factory=list)
    ingest_confidence: float = 1.0
    is_ai_generated: bool = False
    ai_generation: List[Dict[str, Any]] = field(default_factory=list)

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
