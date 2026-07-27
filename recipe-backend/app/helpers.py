"""Shared helpers: locale validation, slug uniqueness, nutrition maths."""
import sqlite3

from fastapi import HTTPException

from .config import get_settings
from .sanitizer import slugify

_NUTRIENT_KEYS = ("kcal", "protein", "carbs", "fat", "fiber", "sugar", "salt")


def require_all_locales(locales_present: set[str]) -> None:
    required = set(get_settings().locales_list)
    missing = required - locales_present
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing translations for locales: {', '.join(sorted(missing))}")
    extra = locales_present - required
    if extra:
        raise HTTPException(status_code=422, detail=f"Unsupported locales: {', '.join(sorted(extra))}")


def pick_locale(locale: str | None) -> str:
    locales = get_settings().locales_list
    return locale if locale and locale in locales else locales[0]


def unique_slug(cur: sqlite3.Cursor, table: str, base: str, exclude_id: int | None = None) -> str:
    # `table` is always an internal constant ("recipes"/"ingredients"), never user input.
    slug = slugify(base)
    candidate = slug
    i = 2
    while True:
        if exclude_id is not None:
            cur.execute(f"SELECT id FROM {table} WHERE slug = ? AND id != ?", (candidate, exclude_id))
        else:
            cur.execute(f"SELECT id FROM {table} WHERE slug = ?", (candidate,))
        if cur.fetchone() is None:
            return candidate
        candidate = f"{slug}-{i}"
        i += 1


def compute_nutrition(cur: sqlite3.Cursor, recipe_id: int, servings: int) -> dict:
    cur.execute(
        "SELECT ri.grams, i.kcal, i.protein, i.carbs, i.fat, i.fiber, i.sugar, i.salt "
        "FROM recipe_ingredients ri JOIN ingredients i ON i.id = ri.ingredient_id "
        "WHERE ri.recipe_id = ?",
        (recipe_id,),
    )
    totals = {k: 0.0 for k in _NUTRIENT_KEYS}
    total_grams = 0.0
    for row in cur.fetchall():
        factor = row["grams"] / 100.0
        total_grams += row["grams"]
        for k in _NUTRIENT_KEYS:
            if row[k] is not None:
                totals[k] += row[k] * factor
    totals = {k: round(v, 1) for k, v in totals.items()}
    divisor = servings if servings else 1
    per_serving = {k: round(v / divisor, 1) for k, v in totals.items()}
    return {"total": totals, "per_serving": per_serving, "total_grams": round(total_grams, 1)}
