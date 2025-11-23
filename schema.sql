-- Catalog & Inventory Service (MS2) schema
-- Catalog items table – maps to models.item.Item

CREATE TABLE IF NOT EXISTS catalog_items (
  id              VARCHAR(32)  NOT NULL PRIMARY KEY,
  sku             VARCHAR(64)  NOT NULL UNIQUE,
  name            VARCHAR(255) NOT NULL,
  brand           VARCHAR(128) NOT NULL,
  category        VARCHAR(128) NOT NULL,
  description     TEXT         NULL,
  photos_json     JSON         NULL,
  rent_price_cents INT         NOT NULL,
  deposit_cents    INT         NOT NULL,
  attrs_json      JSON         NULL,
  status          ENUM('active','inactive') NOT NULL DEFAULT 'active',
  created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP    NULL     DEFAULT NULL
                               ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_catalog_items_brand
  ON catalog_items (brand);

CREATE INDEX idx_catalog_items_category
  ON catalog_items (category);

CREATE INDEX idx_catalog_items_price
  ON catalog_items (rent_price_cents);

CREATE INDEX idx_catalog_items_status
  ON catalog_items (status);
