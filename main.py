from __future__ import annotations

import base64
import json
import os
import socket
from datetime import datetime, date
from typing import Dict, List, Optional
from utils.pubsub_client import publish_event


from fastapi import FastAPI, HTTPException, Query, Path, Header, Response
from fastapi.middleware.cors import CORSMiddleware

from models.item import Item, ItemCreate, ItemUpdate, PagedItems
from models.physical_item import PagedPhysicalItems
from models.availability import Availability
from models.reservation import (
    Reservation,
    ReservationRequest,
    ReservationAction,
    PagedReservations,
)

from database import query_all, query_one, execute


# ---------------------------------------------------------------------------
# Basic app setup
# ---------------------------------------------------------------------------

port = int(os.getenv("PORT", "8000"))
NOT_IMPL = HTTPException(status_code=501, detail="Not implemented")

app = FastAPI(
    title="Catalog & Inventory Service (MS2)",
    description="Luxury rental catalog and inventory microservice.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _encode_token(last_id: Optional[str]) -> Optional[str]:
    if not last_id:
        return None
    return base64.urlsafe_b64encode(last_id.encode("utf-8")).decode("ascii")


def _decode_token(token: Optional[str]) -> Optional[str]:
    if not token:
        return None
    try:
        return base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
    except Exception:
        return None


def _row_to_item(row: Dict) -> Item:
    """Convert a DB row (dict) into an Item model."""
    photos = json.loads(row["photos_json"]) if row.get("photos_json") else []
    attrs = json.loads(row["attrs_json"]) if row.get("attrs_json") else {}

    item = Item(
        id=row["id"],
        sku=row["sku"],
        name=row["name"],
        brand=row["brand"],
        category=row["category"],
        description=row.get("description"),
        photos=photos,
        rent_price_cents=row["rent_price_cents"],
        deposit_cents=row["deposit_cents"],
        attrs=attrs,
        status=row["status"],
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )
    item.links = {
        "self": f"/catalog/items/{item.id}",
        "rentals": f"/orders?itemId={item.id}",
    }
    return item


# ---------------------------------------------------------------------------
# Catalog API – /catalog/items
# ---------------------------------------------------------------------------


@app.post("/catalog/items", response_model=Item, status_code=201, tags=["catalog"])
def create_catalog_item(body: ItemCreate, response: Response):
    """
    Create a new catalog item.

    要求：
    * 返回 201 Created
    * Location header = /catalog/items/{id}
    * body = Item（带 _links）
    """
    new_id = f"it-{os.urandom(4).hex()}"

    sql = (
        "INSERT INTO catalog_items "
        "(id, sku, name, brand, category, description, "
        " photos_json, rent_price_cents, deposit_cents, attrs_json, status) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    )
    params = (
        new_id,
        body.sku,
        body.name,
        body.brand,
        body.category,
        body.description,
        json.dumps(body.photos or []),
        body.rent_price_cents,
        body.deposit_cents,
        json.dumps(body.attrs or {}),
        "active",
    )
    execute(sql, params)

    row = query_one("SELECT * FROM catalog_items WHERE id=%s", (new_id,))
    if not row:
        raise HTTPException(status_code=500, detail="Failed to load created item")

    item = _row_to_item(row)
    response.headers["Location"] = f"/catalog/items/{item.id}"
    try:
        publish_event(
            event_type="CatalogItemCreated",
            payload={
                "itemId": item.id,main
                "sku": item.sku,
                "name": item.name,
                "brand": item.brand,
                "category": item.category,
                "rent_price_cents": item.rent_price_cents,
                "deposit_cents": item.deposit_cents,
            },
        )
    except Exception as e:
        print(f"[WARN] Failed to publish CatalogItemCreated event: {e}")
    
    return item


@app.get("/catalog/items", response_model=PagedItems, tags=["catalog"])
def list_catalog_items(
    next_page_token: Optional[str] = Query(None, alias="nextPageToken"),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None, alias="minPrice", ge=0),
    max_price: Optional[int] = Query(None, alias="maxPrice", ge=0),
    available_on: Optional[date] = Query(
        None,
        alias="availableOn",
        description="active ",
    ),
):
    """
    List catalog items with filters + cursor pagination.

    """
    last_id = _decode_token(next_page_token)

    where_clauses: List[str] = []
    params: List = []

    if category:
        where_clauses.append("category = %s")
        params.append(category)
    if brand:
        where_clauses.append("brand = %s")
        params.append(brand)
    if min_price is not None:
        where_clauses.append("rent_price_cents >= %s")
        params.append(min_price)
    if max_price is not None:
        where_clauses.append("rent_price_cents <= %s")
        params.append(max_price)
    if available_on:
    
        where_clauses.append("status = 'active'")

    if last_id:
       
        where_clauses.append("id > %s")
        params.append(last_id)

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    sql = (
        "SELECT * FROM catalog_items "
        f"{where_sql} "
        "ORDER BY id "
        "LIMIT %s"
    )
    params.append(page_size + 1)  

    rows = query_all(sql, params)

    has_more = len(rows) > page_size
    rows = rows[:page_size]

    items: List[Item] = []
    last_seen_id: Optional[str] = None
    for r in rows:
        last_seen_id = r["id"]
        items.append(_row_to_item(r))

    next_token = _encode_token(last_seen_id) if has_more else None

    return PagedItems(
        items=items,
        nextPageToken=next_token,
        page_size=page_size,
        page=1,      
        total=None,  
    )


@app.get("/catalog/items/{id}", response_model=Item, tags=["catalog"])
def get_catalog_item(
    id: str = Path(..., description="Catalog item ID (string)"),
    if_none_match: Optional[str] = Header(None, alias="If-None-Match"),
    response: Response = None,
):
    """
    Get a single catalog item.

    """
    row = query_one("SELECT * FROM catalog_items WHERE id=%s", (id,))
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")

    item = _row_to_item(row)

    updated = row.get("updated_at") or row.get("created_at")
    if updated:
        if isinstance(updated, datetime):
            ts = int(updated.timestamp())
        else:
            ts = 0
        etag_value = f'W/"{id}-{ts}"'
        if if_none_match == etag_value:
            response.status_code = 304
            return
        response.headers["ETag"] = etag_value

    return item


@app.put("/catalog/items/{id}", response_model=Item, tags=["catalog"])
def update_catalog_item(id: str, body: ItemUpdate):
    """
    Full update for a catalog item.
    """
    row = query_one("SELECT * FROM catalog_items WHERE id=%s", (id,))
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")

    existing = _row_to_item(row)
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(existing, k, v)

    sql = (
        "UPDATE catalog_items SET "
        "name=%s, brand=%s, category=%s, description=%s, "
        "photos_json=%s, rent_price_cents=%s, deposit_cents=%s, attrs_json=%s, status=%s "
        "WHERE id=%s"
    )
    params = (
        existing.name,
        existing.brand,
        existing.category,
        existing.description,
        json.dumps(existing.photos or []),
        existing.rent_price_cents,
        existing.deposit_cents,
        json.dumps(existing.attrs or {}),
        existing.status,
        id,
    )
    execute(sql, params)

    row = query_one("SELECT * FROM catalog_items WHERE id=%s", (id,))
    return _row_to_item(row)


@app.delete("/catalog/items/{id}", status_code=204, tags=["catalog"])
def delete_catalog_item(id: str):
    """
    Delete a catalog item. 
    """
    row = query_one("SELECT * FROM catalog_items WHERE id=%s", (id,))
    if not row:
        return

    execute("DELETE FROM catalog_items WHERE id=%s", (id,))
    return


# ---------------------------------------------------------------------------
# Inventory & Reservation – 
# ---------------------------------------------------------------------------


@app.get("/physical-items", response_model=PagedPhysicalItems, tags=["inventory"])
def list_physical_items():
    raise NOT_IMPL


@app.get("/availability", response_model=Availability, tags=["inventory"])
def get_availability(
    sku: str = Query(..., description="SKU to check availability for"),
    start_date: date = Query(...),
    end_date: date = Query(...),
):
    raise NOT_IMPL


@app.post("/reservations", response_model=Reservation, status_code=201, tags=["reservations"])
def create_reservation(body: ReservationRequest):
    raise NOT_IMPL


@app.get("/reservations", response_model=PagedReservations, tags=["reservations"])
def list_reservations():
    raise NOT_IMPL


@app.patch("/reservations/{id}", response_model=Reservation, tags=["reservations"])
def transition_reservation(
    id: str = Path(..., description="Reservation id"),
    body: ReservationAction = ...,
):
    raise NOT_IMPL


@app.get("/")
def root():
    return {
        "service": "Catalog & Inventory",
        "hostname": socket.gethostname(),
        "see": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
