"""Tiny zero-dependency loader for the Viral VFX instruction dataset.

    from vfx_loader import VFXData
    data = VFXData()                      # loads effects.json next to this file
    eff  = data.get("make_an_object_appear")
    print(eff["filming_steps"], eff["editing_steps"])
    for e in data.filter(difficulty="Beginner", tag="mask"): ...
    img = data.asset_path(eff["breakdown_images"][0])   # absolute path on disk
"""
import json, os, sqlite3
HERE = os.path.dirname(os.path.abspath(__file__))

class VFXData:
    def __init__(self, path=None):
        with open(path or os.path.join(HERE, "effects.json"), encoding="utf-8") as f:
            self._doc = json.load(f)
        self.effects = self._doc["effects"]
        self._by_slug = {e["slug"]: e for e in self.effects}
    def __iter__(self):  return iter(self.effects)
    def __len__(self):   return len(self.effects)
    def get(self, slug): return self._by_slug.get(slug)
    def slugs(self):     return list(self._by_slug)
    def filter(self, difficulty=None, tag=None, full_only=False):
        out=[]
        for e in self.effects:
            if difficulty and e["difficulty"]!=difficulty: continue
            if tag and tag not in e.get("tags",[]): continue
            if full_only and not e["is_full_tutorial"]: continue
            out.append(e)
        return out
    def asset_path(self, rel): return os.path.join(HERE, rel) if rel else None
    def all_transcripts(self, slug):
        return [l["transcript"] for l in self.get(slug)["lessons"] if l.get("transcript")]

def open_sqlite(): return sqlite3.connect(os.path.join(HERE, "vfx.sqlite"))

if __name__ == "__main__":
    d=VFXData(); print(f"{len(d)} effects loaded")
    e=d.effects[0]
    print("example:",e["slug"],"| filming:",len(e["filming_steps"]),"| editing:",len(e["editing_steps"]),"| tags:",e["tags"])
