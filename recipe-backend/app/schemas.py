"""Pydantic request/response models with strict validation."""
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# --- Auth ------------------------------------------------------------------
class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class PasswordChangeRequest(BaseModel):
    new_password: str = Field(min_length=1, max_length=200)


class CodeRequest(BaseModel):
    code: str = Field(min_length=1, max_length=64)


# --- Images ----------------------------------------------------------------
class ImageUpload(BaseModel):
    data: str = Field(min_length=1, max_length=12_000_000)


# --- Ingredients -----------------------------------------------------------
class IngredientTranslationIn(BaseModel):
    locale: str = Field(min_length=2, max_length=5)
    name: str = Field(min_length=1, max_length=200)
    description_html: str = Field(default="", max_length=100_000)


class IngredientIn(BaseModel):
    kcal: float = Field(ge=0, le=1000)
    protein: float = Field(ge=0, le=100)
    carbs: float = Field(ge=0, le=100)
    fat: float = Field(ge=0, le=100)
    fiber: Optional[float] = Field(default=None, ge=0, le=100)
    sugar: Optional[float] = Field(default=None, ge=0, le=100)
    salt: Optional[float] = Field(default=None, ge=0, le=100)
    image_id: Optional[int] = Field(default=None, ge=1)
    translations: list[IngredientTranslationIn] = Field(min_length=1)

    @field_validator("translations")
    @classmethod
    def _unique_locales(cls, v):
        if len({t.locale for t in v}) != len(v):
            raise ValueError("Duplicate locale in translations")
        return v


# --- Recipes ---------------------------------------------------------------
class RecipeTranslationIn(BaseModel):
    locale: str = Field(min_length=2, max_length=5)
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(default="", max_length=500)
    instructions_html: str = Field(default="", max_length=200_000)


class RecipeIngredientIn(BaseModel):
    ingredient_id: int = Field(ge=1)
    grams: float = Field(gt=0, le=100_000)


class RecipeIn(BaseModel):
    servings: int = Field(ge=1, le=100)
    image_id: Optional[int] = Field(default=None, ge=1)
    published: bool = True
    translations: list[RecipeTranslationIn] = Field(min_length=1)
    ingredients: list[RecipeIngredientIn] = Field(default_factory=list)

    @field_validator("translations")
    @classmethod
    def _unique_locales(cls, v):
        if len({t.locale for t in v}) != len(v):
            raise ValueError("Duplicate locale in translations")
        return v
