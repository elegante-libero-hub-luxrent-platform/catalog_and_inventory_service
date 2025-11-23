from __future__ import annotations

from typing import Optional, List, Dict, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ItemCreate(BaseModel):
    """Request body for creating a catalog item."""

    sku: str = Field(..., description="Unique SKU code")
    name: str = Field(..., description="Display name of the item")
    brand: str = Field(..., description="Brand name")
    category: str = Field(..., description="Category, e.g., handbag, dress")
    description: Optional[str] = Field(
        default=None, description="Long description of the item"
    )
    photos: List[str] = Field(
        default_factory=list, description="List of photo URLs"
    )
    rent_price_cents: int = Field(
        ..., ge=0, description="Rental price in cents"
    )
    deposit_cents: int = Field(
        ..., ge=0, description="Deposit amount in cents"
    )
    attrs: Dict[str, str] = Field(
        default_factory=dict, description="Arbitrary attributes (color, material, etc.)"
    )


class ItemUpdate(BaseModel):
    """Partial update for a catalog item."""

    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    photos: Optional[List[str]] = None
    rent_price_cents: Optional[int] = Field(default=None, ge=0)
    deposit_cents: Optional[int] = Field(default=None, ge=0)
    attrs: Optional[Dict[str, str]] = None
    status: Optional[Literal["active", "inactive"]] = None


class Item(ItemCreate):
    """Full catalog item representation as stored in DB / returned by API."""

    id: str = Field(..., description="Catalog item id (e.g., 'it-1234abcd')")
    status: Literal["active", "inactive"] = Field(
        default="active", description="Item status"
    )
    created_at: Optional[datetime] = Field(
        default=None, description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="Last update timestamp"
    )
    
    links: Optional[Dict[str, str]] = Field(
        default=None,
        alias="_links",
        description="HATEOAS-style links, e.g. {'rentals': '/orders?itemId=it-1234'}",
    )

    
    model_config = ConfigDict(populate_by_name=True)

class PagedItems(BaseModel):
    """Paginated response for GET /catalog/items."""

    items: List[Item]
    # Sprint2 
    nextPageToken: Optional[str] = Field(
        default=None,
        description="Opaque cursor for the next page; null/omitted if no more pages.",
    )
    #for frontend
    page: int = Field(
        default=1, ge=1, description="Current page number (for UI; not part of cursor)"
    )
    page_size: int = Field(
        ..., ge=1, description="Number of items returned in this page"
    )
    total: Optional[int] = Field(
        default=None,
        description="Optional total number of items; can be None if not computed.",
    )
