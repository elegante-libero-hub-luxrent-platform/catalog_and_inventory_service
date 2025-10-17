from __future__ import annotations

from typing import List, Literal
from pydantic import BaseModel, Field

class PhysicalItem(BaseModel):
    id: str = Field(..., description="Physical item id (e.g., 'pi-2001')")
    sku: str = Field(..., description="Parent SKU")
    size: str = Field(..., description="Size, e.g., M")
    condition: str = Field(..., description="Condition grade, e.g., A/B/C")
    status: Literal["available","held","allocated","cleaning","repair","lost","retired"] = Field(default="available")

    model_config = {"json_schema_extra": {"example": {
        "id": "pi-2001", "sku": "BAG-PRADA-001", "size": "M", "condition": "A", "status": "available"
    }}}

class PagedPhysicalItems(BaseModel):
    items: List[PhysicalItem]
    page: int
    page_size: int
    total: int
