from __future__ import annotations

import os
import socket
from datetime import datetime, date

from typing import Dict, List
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi import Query, Path, Header
from typing import Optional

from models.item import Item, ItemCreate, ItemUpdate, PagedItems
from models.physical_item import PagedPhysicalItems
from models.availability import Availability
from models.reservation import (
    PagedReservations,
    Reservation,
    ReservationRequest,
    ReservationAction,
)
NOT_IMPL = HTTPException(status_code=501, detail="Not implemented in Sprint 1")
port = int(os.environ.get("FASTAPIPORT", 8000))

app = FastAPI(
    title="Catalog & Inventory Service (Sprint 1 - Code First)",
    version="1.0.0",
    description="Catalog (SKU), inventory (physical items), availability & reservations. All handlers return 501 in Sprint 1."
)



@app.get("/catalog/items", response_model=PagedItems, tags=["catalog"])
def list_catalog_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    brand: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Free text query"),
    min_rent_cents: Optional[int] = Query(None, ge=0),
    max_rent_cents: Optional[int] = Query(None, ge=0),
    sort: Optional[str] = Query(None, description="name_asc|name_desc|price_asc|price_desc|created_desc"),
):
    raise NOT_IMPL

@app.post("/catalog/items", response_model=Item, status_code=201, tags=["catalog"])
def create_catalog_item(body: ItemCreate):
    raise NOT_IMPL

@app.get("/catalog/items/{id}", response_model=Item, tags=["catalog"])
def get_catalog_item(id: str = Path(..., description="Catalog item ID (string)")):
    raise NOT_IMPL

@app.put("/catalog/items/{id}", response_model=Item, tags=["catalog"])
def update_catalog_item(id: str, body: ItemUpdate):
    raise NOT_IMPL

@app.delete("/catalog/items/{id}", status_code=204, tags=["catalog"])
def delete_catalog_item(id: str):
    raise NOT_IMPL

# -----------------------------------------------------------------------------
# Inventory
# -----------------------------------------------------------------------------
@app.get("/inventory/items", response_model=PagedPhysicalItems, tags=["inventory"])
def list_physical_items(
    sku: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="available|held|allocated|cleaning|repair|lost|retired"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    raise NOT_IMPL

# availability
@app.get("/availability", response_model=Availability, tags=["inventory"])
def check_availability(
    sku: str = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
):
    raise NOT_IMPL

# -----------------------------------------------------------------------------
# Reservations
# -----------------------------------------------------------------------------
@app.get("/reservations", response_model=PagedReservations, tags=["reservations"])
def list_reservations(
    status: Optional[str] = Query(None, description="held|allocated|released|expired"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    raise NOT_IMPL

@app.post("/reservations", response_model=Reservation, status_code=201, tags=["reservations"])
def create_reservation(
    body: ReservationRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    raise NOT_IMPL

@app.patch("/reservations/{id}", response_model=Reservation, tags=["reservations"])
def transition_reservation(
    id: str = Path(..., description="Reservation id"),
    body: ReservationAction = ...,
):
    raise NOT_IMPL


@app.get("/")
def root():
    return {"service": "Catalog & Inventory", "see": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)