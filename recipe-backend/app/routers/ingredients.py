"""Ingredient wiki: public read (localised, searchable) + admin CRUD.

Every ingredient must carry a translation for all supported locales.
"""
from fastapi import APIRouter, Depends, HTTPException, Query

from ..database import db_cursor
from ..helpers import pick_locale, require_all_locales, unique_slug
from ..sanitizer import sanitize_html
from ..schemas import IngredientIn
from ..security import get_current_admin

router = APIRouter(tags=["ingredients"])

_NUTRIENTS = ("kcal", "protein", "carbs", "fat", "fiber", "sugar", "salt")


def _serialise_public(row) -> dict:
    return {
        "id": row["id"],
        "slug": row["slug"],
        "image_id": row["image_id"],
        "name": row["name"],
        **{k: row[k] for k in _NUTRIENTS},
    }


@router.get("/ingredients")
async def list_ingredients(
    locale: str | None = Query(default=None),
    q: str | None = Query(default=None, max_length=100),
):
    loc = pick_locale(locale)
    sql = (
        "SELECT i.id, i.slug, i.image_id, i.kcal, i.protein, i.carbs, i.fat, i.fiber, "
        "i.sugar, i.salt, t.name FROM ingredients i "
        "JOIN ingredient_translations t ON t.ingredient_id = i.id AND t.locale = ? "
    )
    params: list = [loc]
    if q:
        sql += "WHERE t.name LIKE ? "
        params.append(f"%{q}%")
    sql += "ORDER BY t.name COLLATE NOCASE"
    with db_cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return [_serialise_public(r) for r in rows]


@router.get("/ingredients/{slug}")
async def get_ingredient(slug: str, locale: str | None = Query(default=None)):
    loc = pick_locale(locale)
    with db_cursor() as cur:
        cur.execute(
            "SELECT i.id, i.slug, i.image_id, i.kcal, i.protein, i.carbs, i.fat, i.fiber, "
            "i.sugar, i.salt, t.name, t.description_html FROM ingredients i "
            "JOIN ingredient_translations t ON t.ingredient_id = i.id AND t.locale = ? "
            "WHERE i.slug = ?",
            (loc, slug),
        )
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        data = _serialise_public(row)
        data["description_html"] = row["description_html"]

        cur.execute(
            "SELECT DISTINCT r.slug, rt.title FROM recipe_ingredients ri "
            "JOIN recipes r ON r.id = ri.recipe_id AND r.published = 1 "
            "JOIN recipe_translations rt ON rt.recipe_id = r.id AND rt.locale = ? "
            "WHERE ri.ingredient_id = ? ORDER BY rt.title COLLATE NOCASE",
            (loc, row["id"]),
        )
        data["used_in"] = [{"slug": r["slug"], "title": r["title"]} for r in cur.fetchall()]
    return data


@router.get("/admin/ingredients")
async def admin_list_ingredients(_: str = Depends(get_current_admin)):
    with db_cursor() as cur:
        cur.execute(
            "SELECT i.id, i.slug, i.image_id, "
            "(SELECT name FROM ingredient_translations WHERE ingredient_id = i.id "
            " ORDER BY (locale='en') DESC LIMIT 1) AS name "
            "FROM ingredients i ORDER BY name COLLATE NOCASE"
        )
        return [dict(r) for r in cur.fetchall()]


@router.get("/admin/ingredients/{ingredient_id}")
async def admin_get_ingredient(ingredient_id: int, _: str = Depends(get_current_admin)):
    with db_cursor() as cur:
        cur.execute("SELECT * FROM ingredients WHERE id = ?", (ingredient_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        data = {k: row[k] for k in ("id", "slug", "image_id", *_NUTRIENTS)}
        cur.execute(
            "SELECT locale, name, description_html FROM ingredient_translations WHERE ingredient_id = ?",
            (ingredient_id,),
        )
        data["translations"] = [dict(t) for t in cur.fetchall()]
    return data


def _write_translations(cur, ingredient_id: int, translations) -> None:
    for t in translations:
        cur.execute(
            "INSERT INTO ingredient_translations (ingredient_id, locale, name, description_html) "
            "VALUES (?, ?, ?, ?)",
            (ingredient_id, t.locale, t.name.strip(), sanitize_html(t.description_html)),
        )


@router.post("/admin/ingredients", status_code=201)
async def create_ingredient(payload: IngredientIn, _: str = Depends(get_current_admin)):
    require_all_locales({t.locale for t in payload.translations})
    name_for_slug = next((t.name for t in payload.translations if t.locale == "en"), payload.translations[0].name)
    with db_cursor(commit=True) as cur:
        slug = unique_slug(cur, "ingredients", name_for_slug)
        cur.execute(
            "INSERT INTO ingredients (slug, kcal, protein, carbs, fat, fiber, sugar, salt, image_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (slug, payload.kcal, payload.protein, payload.carbs, payload.fat,
             payload.fiber, payload.sugar, payload.salt, payload.image_id),
        )
        ingredient_id = cur.lastrowid
        _write_translations(cur, ingredient_id, payload.translations)
    return {"id": ingredient_id, "slug": slug}


@router.put("/admin/ingredients/{ingredient_id}")
async def update_ingredient(ingredient_id: int, payload: IngredientIn, _: str = Depends(get_current_admin)):
    require_all_locales({t.locale for t in payload.translations})
    with db_cursor(commit=True) as cur:
        cur.execute("SELECT id FROM ingredients WHERE id = ?", (ingredient_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        cur.execute(
            "UPDATE ingredients SET kcal=?, protein=?, carbs=?, fat=?, fiber=?, sugar=?, salt=?, "
            "image_id=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (payload.kcal, payload.protein, payload.carbs, payload.fat, payload.fiber,
             payload.sugar, payload.salt, payload.image_id, ingredient_id),
        )
        cur.execute("DELETE FROM ingredient_translations WHERE ingredient_id = ?", (ingredient_id,))
        _write_translations(cur, ingredient_id, payload.translations)
    return {"id": ingredient_id}


@router.delete("/admin/ingredients/{ingredient_id}", status_code=204)
async def delete_ingredient(ingredient_id: int, _: str = Depends(get_current_admin)):
    with db_cursor(commit=True) as cur:
        cur.execute("SELECT COUNT(*) AS c FROM recipe_ingredients WHERE ingredient_id = ?", (ingredient_id,))
        if cur.fetchone()["c"] > 0:
            raise HTTPException(status_code=409, detail="Ingredient is used by one or more recipes")
        cur.execute("DELETE FROM ingredients WHERE id = ?", (ingredient_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ingredient not found")
    return None
