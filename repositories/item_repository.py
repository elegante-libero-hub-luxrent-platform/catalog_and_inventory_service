from typing import List, Optional
from db import get_conn
from models.item import ItemCreate, ItemUpdate, Item


class ItemRepository:

    @staticmethod
    def create_item(data: ItemCreate) -> str:
        conn = get_conn()
        cursor = conn.cursor()

        sql = """
        INSERT INTO catalog_items
        (sku, name, brand, category, description, photos, rent_price_cents, deposit_cents, attrs, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
        """

        cursor.execute(sql, (
            data.sku,
            data.name,
            data.brand,
            data.category,
            data.description,
            ",".join(data.photos),
            data.rent_price_cents,
            data.deposit_cents,
            str(data.attrs)
        ))

        conn.commit()
        new_id = cursor.lastrowid

        cursor.close()
        conn.close()
        return str(new_id)

    @staticmethod
    def get_item(item_id: str) -> Optional[Item]:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM catalog_items WHERE id = %s", (item_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            row["photos"] = row["photos"].split(",") if row["photos"] else []
            row["attrs"] = eval(row["attrs"]) if row["attrs"] else {}
            return Item(**row)
        return None
