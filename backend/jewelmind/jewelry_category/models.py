"""CategoryCapability — the machine-readable declaration of what JewelMind
can actually do for one jewelry category, mirrored at
`specs/jewelry-architecture/v1/category-registry.json`. Never advertise a
`planned` category as generatable (see 520-jewelry-category-architecture.md,
JEWELRY-ARCH-GOV rules)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CategoryStatus = Literal["current", "planned"]


class CategoryCapability(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str
    status: CategoryStatus
    definitionVersion: str
    generationSupported: bool
    validationSupported: bool
    previewSupported: bool
    exportSupported: bool
    supportedFamilies: list[str] = Field(default_factory=list)
    sharedSystems: list[str] = Field(default_factory=list)
    categorySpecificSystems: list[str] = Field(default_factory=list)
    message: str = ""
