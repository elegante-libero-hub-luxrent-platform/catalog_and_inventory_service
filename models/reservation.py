from __future__ import annotations

from typing import List, Literal, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

class ReservationRequest(BaseModel):
    sku: str
    start_date: date
    end_date: date
    note: Optional[str] = None

class Reservation(BaseModel):
    id: str = Field(..., description="Reservation id (e.g., r-8f6e)")
    sku: str
    item_id: str = Field(..., description="Physical item id, e.g., pi-2001")
    start_date: date
    end_date: date
    status: Literal["held","allocated","released","expired"] = "held"
    expires_at: Optional[datetime] = None

class ReservationAction(BaseModel):
    action: Literal["allocate","release"]

class PagedReservations(BaseModel):
    items: List[Reservation]
    page: int
    page_size: int
    total: int
