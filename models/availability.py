from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field

class Availability(BaseModel):
    sku: str
    start_date: date
    end_date: date
    available_count: int = Field(..., ge=0)
