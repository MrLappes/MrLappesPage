"""Recipe wiki: public read (localised, searchable, auto nutrition) + admin CRUD."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from ..database import db_cursor
from ..helpers import compute_nutrition, pick_locale, require_all_locales, unique_slug
from ..sanitizer import sanitize_html
from ..schemas import RecipeIn
from ..security import get_current_admin

router = APIRouter(tags=["recipes"])

# Stable namespace so re-exporting a recipe yields the same dish id, letting the
# PlatePal Tracker app update an existing dish instead of creating duplicates.
_TRACKER_NS = uuid.uuid5(uuid.NAMESPACE_URL, "https://plate-pal.de/wiki/tracker-export")


def _validate_ingredient_ids(cur, ingredients) -> None:
    for item in ingredients:
        cur.execute("SELECT id FROM ingredients WHERE id = ?", (item.ingredient_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=422, detail=f"Unknown ingredient id {item.ingredient_id}")


@router.get("/recipes")
async def list_recipes(
    locale: str | None = Query(default=None),
    q: str | None = Query(default=None, max_length=100),
):
    loc = pick_locale(locale)
    sql = (
        "SELECT r.id, r.slug, r.servings, r.image_id, t.title, t.summary FROM recipes r "
        "JOIN recipe_translations t ON t.recipe_id = r.id AND t.locale = ? "
        "WHERE r.published = 1 "
    )
    params: list = [loc]
    if q:
        sql += "AND (t.title LIKE ? OR t.summary LIKE ?) "
        params.extend([f"%{q}%", f"%{q}%"])
    sql += "ORDER BY r.created_at DESC"
    with db_cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
        result = []
        for r in rows:
            nutrition = compute_nutrition(cur, r["id"], r["servings"])
            result.append({
                "slug": r["slug"], "title": r["title"], "summary": r["summary"],
                "servings": r["servings"], "image_id": r["image_id"],
                "kcal_per_serving": nutrition["per_serving"]["kcal"],
            })
    return result


@router.get("/recipes/{slug}")
async def get_recipe(slug: str, locale: str | None = Query(default=None)):
    loc = pick_locale(locale)
    with db_cursor() as cur:
        cur.execute(
            "SELECT r.id, r.slug, r.servings, r.image_id, t.title, t.summary, t.instructions_html "
            "FROM recipes r JOIN recipe_translations t ON t.recipe_id = r.id AND t.locale = ? "
            "WHERE r.slug = ? AND r.published = 1",
            (loc, slug),
        )
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Recipe not found")

        cur.execute(
            "SELECT ri.grams, i.id AS ingredient_id, i.slug, i.image_id, i.kcal, "
            "it.name FROM recipe_ingredients ri "
            "JOIN ingredients i ON i.id = ri.ingredient_id "
            "JOIN ingredient_translations it ON it.ingredient_id = i.id AND it.locale = ? "
            "WHERE ri.recipe_id = ? ORDER BY ri.sort_order, ri.id",
            (loc, row["id"]),
        )
        ingredients = []
        for ing in cur.fetchall():
            ingredients.append({
                "ingredient_id": ing["ingredient_id"],
                "slug": ing["slug"],
                "name": ing["name"],
                "image_id": ing["image_id"],
                "grams": ing["grams"],
                "kcal": round((ing["kcal"] or 0) * ing["grams"] / 100.0, 1),
            })
        nutrition = compute_nutrition(cur, row["id"], row["servings"])

    return {
        "slug": row["slug"], "title": row["title"], "summary": row["summary"],
        "instructions_html": row["instructions_html"], "servings": row["servings"],
        "image_id": row["image_id"], "ingredients": ingredients, "nutrition": nutrition,
    }


@router.get("/recipes/{slug}/export")
async def export_recipe(
    slug: str,
    locale: str | None = Query(default=None),
    portion: str = Query(default="serving"),
):
    """Export a recipe as a PlatePal Tracker (Flutter app) compatible dish.

    The returned object matches the tracker's ``Dish.fromJson``: a nested
    ``nutrition`` object holds the dish totals and each ingredient carries an
    ``amount`` (grams), ``unit`` and a nested per-100g ``nutrition`` object.
    Top-level macro fields and ``*Per100`` aliases are also included so the
    tracker's alternative import paths and file import all work.
    ``portion=serving`` (default) scales everything to a single serving;
    ``portion=whole`` exports the full recipe.
    """
    loc = pick_locale(locale)
    per_serving = portion != "whole"
    with db_cursor() as cur:
        cur.execute(
            "SELECT r.id, r.slug, r.servings, r.image_id, t.title, t.summary "
            "FROM recipes r JOIN recipe_translations t ON t.recipe_id = r.id AND t.locale = ? "
            "WHERE r.slug = ? AND r.published = 1",
            (loc, slug),
        )
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Recipe not found")

        servings = row["servings"] or 1
        divisor = servings if per_serving else 1

        cur.execute(
            "SELECT ri.grams, i.slug AS ingredient_slug, i.kcal, i.protein, i.carbs, i.fat, "
            "i.fiber, i.sugar, i.salt, it.name FROM recipe_ingredients ri "
            "JOIN ingredients i ON i.id = ri.ingredient_id "
            "JOIN ingredient_translations it ON it.ingredient_id = i.id AND it.locale = ? "
            "WHERE ri.recipe_id = ? ORDER BY ri.sort_order, ri.id",
            (loc, row["id"]),
        )

        ingredients = []
        totals = {"kcal": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0,
                  "fiber": 0.0, "sugar": 0.0, "salt": 0.0}
        for ing in cur.fetchall():
            grams = ing["grams"] / divisor
            factor = grams / 100.0
            # Per-100g values (as stored on the wiki ingredient). The tracker
            # multiplies these by amount/100 to get the ingredient contribution.
            kcal_100 = round(ing["kcal"] or 0, 1)
            protein_100 = round(ing["protein"] or 0, 1)
            carbs_100 = round(ing["carbs"] or 0, 1)
            fat_100 = round(ing["fat"] or 0, 1)
            fiber_100 = round(ing["fiber"], 1) if ing["fiber"] is not None else 0.0
            sugar_100 = round(ing["sugar"], 1) if ing["sugar"] is not None else 0.0
            # Wiki stores salt (g); tracker nutrition uses sodium (mg).
            sodium_100 = round(ing["salt"] / 2.5 * 1000, 1) if ing["salt"] else 0.0
            ingredients.append({
                "id": ing["ingredient_slug"],
                "name": ing["name"],
                "amount": round(grams, 1),
                "quantity": round(grams, 1),
                "unit": "g",
                "nutrition": {
                    "calories": kcal_100,
                    "protein": protein_100,
                    "carbs": carbs_100,
                    "fat": fat_100,
                    "fiber": fiber_100,
                    "sugar": sugar_100,
                    "sodium": sodium_100,
                },
                # Aliases for the tracker's raw-map import path.
                "caloriesPer100": kcal_100,
                "proteinPer100": protein_100,
                "carbsPer100": carbs_100,
                "fatPer100": fat_100,
                "fiberPer100": fiber_100,
            })
            for key in totals:
                value = ing[key]
                if value is not None:
                    totals[key] += value * factor

        totals = {k: round(v, 1) for k, v in totals.items()}
        # Recipe stores salt (g); the tracker's dish sodium is milligrams.
        sodium_mg = round(totals["salt"] / 2.5 * 1000, 1) if totals["salt"] else 0.0
        now = datetime.now(timezone.utc).isoformat()
        dish_id = str(uuid.uuid5(_TRACKER_NS, f"{row['slug']}:{loc}:{portion}"))
        nutrition = {
            "calories": totals["kcal"],
            "protein": totals["protein"],
            "carbs": totals["carbs"],
            "fat": totals["fat"],
            "fiber": totals["fiber"],
            "sugar": totals["sugar"],
            "sodium": sodium_mg,
        }

        dish = {
            "id": dish_id,
            "name": row["title"],
            "description": row["summary"] or None,
            "imageUrl": None,
            "imageUri": None,
            "category": None,
            "isFavorite": False,
            "tags": ["PlatePal Wiki"],
            "createdAt": now,
            "updatedAt": now,
            "nutrition": nutrition,
            # Top-level macro aliases for import paths that read them directly.
            "calories": nutrition["calories"],
            "protein": nutrition["protein"],
            "carbs": nutrition["carbs"],
            "fat": nutrition["fat"],
            "fiber": nutrition["fiber"],
            "sugar": nutrition["sugar"],
            "sodium": nutrition["sodium"],
            "ingredients": ingredients,
        }

    return dish



@router.get("/admin/recipes")
async def admin_list_recipes(_: str = Depends(get_current_admin)):
    with db_cursor() as cur:
        cur.execute(
            "SELECT r.id, r.slug, r.published, r.image_id, "
            "(SELECT title FROM recipe_translations WHERE recipe_id = r.id "
            " ORDER BY (locale='en') DESC LIMIT 1) AS title "
            "FROM recipes r ORDER BY r.created_at DESC"
        )
        return [dict(r) for r in cur.fetchall()]


@router.get("/admin/recipes/{recipe_id}")
async def admin_get_recipe(recipe_id: int, _: str = Depends(get_current_admin)):
    with db_cursor() as cur:
        cur.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        data = {"id": row["id"], "slug": row["slug"], "servings": row["servings"],
                "image_id": row["image_id"], "published": bool(row["published"])}
        cur.execute(
            "SELECT locale, title, summary, instructions_html FROM recipe_translations WHERE recipe_id = ?",
            (recipe_id,),
        )
        data["translations"] = [dict(t) for t in cur.fetchall()]
        cur.execute(
            "SELECT ingredient_id, grams FROM recipe_ingredients WHERE recipe_id = ? ORDER BY sort_order, id",
            (recipe_id,),
        )
        data["ingredients"] = [dict(i) for i in cur.fetchall()]
    return data


def _write_children(cur, recipe_id: int, payload: RecipeIn) -> None:
    for t in payload.translations:
        cur.execute(
            "INSERT INTO recipe_translations (recipe_id, locale, title, summary, instructions_html) "
            "VALUES (?, ?, ?, ?, ?)",
            (recipe_id, t.locale, t.title.strip(), t.summary.strip(), sanitize_html(t.instructions_html)),
        )
    for order, item in enumerate(payload.ingredients):
        cur.execute(
            "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, grams, sort_order) VALUES (?, ?, ?, ?)",
            (recipe_id, item.ingredient_id, item.grams, order),
        )


@router.post("/admin/recipes", status_code=201)
async def create_recipe(payload: RecipeIn, _: str = Depends(get_current_admin)):
    require_all_locales({t.locale for t in payload.translations})
    title_for_slug = next((t.title for t in payload.translations if t.locale == "en"), payload.translations[0].title)
    with db_cursor(commit=True) as cur:
        _validate_ingredient_ids(cur, payload.ingredients)
        slug = unique_slug(cur, "recipes", title_for_slug)
        cur.execute(
            "INSERT INTO recipes (slug, servings, image_id, published) VALUES (?, ?, ?, ?)",
            (slug, payload.servings, payload.image_id, int(payload.published)),
        )
        recipe_id = cur.lastrowid
        _write_children(cur, recipe_id, payload)
    return {"id": recipe_id, "slug": slug}


@router.put("/admin/recipes/{recipe_id}")
async def update_recipe(recipe_id: int, payload: RecipeIn, _: str = Depends(get_current_admin)):
    require_all_locales({t.locale for t in payload.translations})
    with db_cursor(commit=True) as cur:
        cur.execute("SELECT id FROM recipes WHERE id = ?", (recipe_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        _validate_ingredient_ids(cur, payload.ingredients)
        cur.execute(
            "UPDATE recipes SET servings=?, image_id=?, published=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (payload.servings, payload.image_id, int(payload.published), recipe_id),
        )
        cur.execute("DELETE FROM recipe_translations WHERE recipe_id = ?", (recipe_id,))
        cur.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
        _write_children(cur, recipe_id, payload)
    return {"id": recipe_id}


@router.delete("/admin/recipes/{recipe_id}", status_code=204)
async def delete_recipe(recipe_id: int, _: str = Depends(get_current_admin)):
    with db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Recipe not found")
    return None
