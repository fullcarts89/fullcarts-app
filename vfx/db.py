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
