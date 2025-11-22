from __future__ import annotations

from typing import Optional, List, Dict, Literal
from datetime import datetime
from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    sku: str = Field(..., description="Unique SKU code")
    name: str = Field(..., description="Display name")
    brand: str = Field(..., description="Brand")
    category: str = Field(..., description="Category (e.g., handbag, dress)")
    description: Optional[str] = Field(default=None, description="Long description")
    photos: List[str] = Field(default_factory=list, description="Photo URLs")
    rent_price_cents: int = Field(..., ge=0, description="Rental price in cents")
    deposit_cents: int = Field(..., ge=0, description="Deposit in cents")
    attrs: Dict[str, str] = Field(default_factory=dict, description="Arbitrary attributes")

    model_config = {"json_schema_extra": {"example": {
        "sku": "BAG-PRADA-001",
        "name": "PRADA Re-Edition",
        "brand": "PRADA",
        "category": "handbag",
        "description": "Nylon mini bag",
        "photos": ["https://cdn.example.com/img/prada-1.jpg"],
        "rent_price_cents": 4999,
        "deposit_cents": 100000,
        "attrs": {"color": "black", "season": "AW24"}
    }}}

class ItemUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    photos: Optional[List[str]] = None
    rent_price_cents: Optional[int] = Field(default=None, ge=0)
    deposit_cents: Optional[int] = Field(default=None, ge=0)
    attrs: Optional[Dict[str, str]] = None

class Item(ItemCreate):
    id: str = Field(..., description="Catalog item id (string)")
    status: Literal["active", "inactive"] = Field(default="active")
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    _links: Optional[Dict[str, str]] = Field(
        default=None,
        description="HATEOAS-style links, e.g. {'rentals': '/orders?itemId=it-123'}",
    )

class PagedItems(BaseModel):
    items: List[Item]
    nextPageToken: Optional[str] = Field(default=None)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1)
    total: int = Field(0, ge=0)