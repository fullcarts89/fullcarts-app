"""Zero-dependency loader for the Viral VFX instruction dataset.

    from vfx_loader import VFXData
    d = VFXData()
    eff = d.get("make_an_object_appear")
    eff["filming_steps"]; eff["editing_steps"]; eff["breakdown_images"]
    d.asset_path(eff["breakdown_images"][0])     # absolute path on disk
    d.filter(difficulty="Beginner", tag="mask")  # query helpers
"""
import json, os, sqlite3
HERE=os.path.dirname(os.path.abspath(__file__))
class VFXData:
    def __init__(self, path=None, include_external=True):
        with open(path or os.path.join(HERE,"effects.json"),encoding="utf-8") as f:
            self._doc=json.load(f)
        self.effects=list(self._doc["effects"])
        ext=os.path.join(HERE,"external_sources.json")
        if include_external and os.path.exists(ext):
            for e in json.load(open(ext,encoding="utf-8")).get("effects",[]):
                e.setdefault("source","external")
                self.effects.append(e)
        for e in self.effects: e.setdefault("source","viral_vfx_vault")
        self._by={e["slug"]:e for e in self.effects}
    def __iter__(self): return iter(self.effects)
    def __len__(self): return len(self.effects)
    def get(self,slug): return self._by.get(slug)
    def slugs(self): return list(self._by)
    def filter(self,difficulty=None,tag=None,full_only=False,kind=None,source=None):
        out=[]
        for e in self.effects:
            if difficulty and e["difficulty"]!=difficulty: continue
            if tag and tag not in e.get("tags",[]): continue
            if full_only and not e["is_full_tutorial"]: continue
            if source and e.get("source")!=source: continue
            if kind=="effect" and e["slug"].startswith("deepdive_"): continue
            if kind=="deep_dive" and not e["slug"].startswith("deepdive_"): continue
            out.append(e)
        return out
    def asset_path(self,rel): return os.path.join(HERE,rel) if rel else None
    def all_transcripts(self,slug):
        return [l["transcript"] for l in self.get(slug)["lessons"] if l.get("transcript")]
def open_sqlite(): return sqlite3.connect(os.path.join(HERE,"vfx.sqlite"))

class Manuals:
    """Loader for the machine-executable VFX *manuals* (MANUAL_SCHEMA.md).

        from vfx_loader import Manuals
        man = Manuals()
        man.get("clone_effect_talking_head")          # full manual dict
        man.filter(technique_primitive="chroma_key")   # query the catalog
        man.filter(gear="tripod", ai=False)
        man.recipe("phone_hologram")                   # inputs + ordered edit_steps
    """
    def __init__(self, manuals_dir=None):
        self.dir=manuals_dir or os.path.join(HERE,"manuals")
        idx=os.path.join(self.dir,"index.json")
        self.index=json.load(open(idx,encoding="utf-8"))["manuals"] if os.path.exists(idx) else []
        self._by={r["id"]:r for r in self.index}
    def __iter__(self): return iter(self.index)
    def __len__(self): return len(self.index)
    def ids(self): return list(self._by)
    def get(self,mid):
        """Full manual dict (loaded from disk)."""
        r=self._by.get(mid)
        if not r: return None
        return json.load(open(os.path.join(HERE,r["file"]),encoding="utf-8"))
    def filter(self,technique_primitive=None,difficulty=None,gear=None,prop=None,ai=None,drafts=True):
        out=[]
        for r in self.index:
            if technique_primitive and r.get("technique_primitive")!=technique_primitive: continue
            if difficulty and r.get("difficulty")!=difficulty: continue
            if gear and gear not in (r.get("gear_required") or []): continue
            if prop and prop not in (r.get("props_required") or []): continue
            if ai is not None and bool(r.get("is_ai_generated"))!=ai: continue
            if not drafts and r.get("draft"): continue
            out.append(r)
        return out
    def recipe(self,mid):
        """Just the executable parts: inputs + edit_steps (+ ai_generation)."""
        m=self.get(mid)
        if not m: return None
        return {k:m.get(k) for k in ("id","technique_primitive","inputs","edit_steps","ai_generation","result")}

if __name__=="__main__":
    d=VFXData(); print(len(d),"records loaded")
    print("vault:",len(d.filter(source='viral_vfx_vault')),"| external:",len(d.filter(source='instagram'))+len(d.filter(source='external')))
    print("effects:",len(d.filter(kind='effect')),"| deep dives:",len(d.filter(kind='deep_dive')))
    m=Manuals(); print(len(m),"manuals |",
        "ai:",len(m.filter(ai=True)),"| chroma_key:",len(m.filter(technique_primitive='chroma_key')),
        "| with tripod:",len(m.filter(gear='tripod')))
