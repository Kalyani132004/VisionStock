-- =========================================================
-- VisionStock - MySQL database
-- How to use:
--   mysql -u root -p < database/schema.sql
-- or open this file in MySQL Workbench and click Run.
--
-- Note: the backend also creates these tables by itself when it
-- starts. Use this file when you want to see / create the database
-- yourself (good for learning and for the interview).
-- =========================================================

CREATE DATABASE IF NOT EXISTS visionstock
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE visionstock;

-- Drop old tables (children first because of foreign keys)
DROP TABLE IF EXISTS detection_events;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS shelves;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

-- ---------------------------------------------------------
-- 1. users
-- ---------------------------------------------------------
CREATE TABLE users (
  user_id        INT AUTO_INCREMENT PRIMARY KEY,
  name           VARCHAR(100) NOT NULL,
  email          VARCHAR(120) NOT NULL UNIQUE,
  password_hash  VARCHAR(255) NOT NULL,
  role           VARCHAR(20)  NOT NULL DEFAULT 'Staff'     -- Admin / Staff
);

-- ---------------------------------------------------------
-- 2. products
-- detect_class = the label that YOLO gives to this product
-- ---------------------------------------------------------
CREATE TABLE products (
  product_id     INT AUTO_INCREMENT PRIMARY KEY,
  product_name   VARCHAR(100) NOT NULL,
  category       VARCHAR(50),
  minimum_stock  INT NOT NULL DEFAULT 5,                   -- alert level
  detect_class   VARCHAR(50),
  created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------
-- 3. shelves
-- roi_* = shelf region as percent of the camera frame (0-100)
-- ---------------------------------------------------------
CREATE TABLE shelves (
  shelf_id    INT AUTO_INCREMENT PRIMARY KEY,
  shelf_name  VARCHAR(50) NOT NULL,
  location    VARCHAR(100),
  status      VARCHAR(20) NOT NULL DEFAULT 'Active',       -- Active / Inactive
  occupancy   INT NOT NULL DEFAULT 0,                      -- filled area in percent
  roi_x       FLOAT NOT NULL DEFAULT 0,
  roi_y       FLOAT NOT NULL DEFAULT 0,
  roi_w       FLOAT NOT NULL DEFAULT 0,
  roi_h       FLOAT NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------
-- 4. inventory (latest detected count of a product on a shelf)
-- ---------------------------------------------------------
CREATE TABLE inventory (
  inventory_id       INT AUTO_INCREMENT PRIMARY KEY,
  product_id         INT NOT NULL,
  shelf_id           INT NOT NULL,
  detected_quantity  INT NOT NULL DEFAULT 0,
  updated_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uq_product_shelf UNIQUE (product_id, shelf_id),
  CONSTRAINT fk_inv_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
  CONSTRAINT fk_inv_shelf   FOREIGN KEY (shelf_id)   REFERENCES shelves(shelf_id)   ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- 5. detection_events (history of stock changes and alerts)
-- ---------------------------------------------------------
CREATE TABLE detection_events (
  event_id    INT AUTO_INCREMENT PRIMARY KEY,
  product_id  INT NOT NULL,
  shelf_id    INT NOT NULL,
  event_type  VARCHAR(30),                                 -- Stock update / Low stock
  quantity    INT NOT NULL DEFAULT 0,
  event_time  DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_event_time (event_time),
  CONSTRAINT fk_ev_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
  CONSTRAINT fk_ev_shelf   FOREIGN KEY (shelf_id)   REFERENCES shelves(shelf_id)   ON DELETE CASCADE
);

-- =========================================================
-- USERS
-- No users are inserted here on purpose (no default passwords).
--   Staff : register on the website (register.html)
--   Admin : python -m backend.create_admin
-- Passwords are always stored as bcrypt hashes, never as plain text.
-- =========================================================

-- =========================================================
-- SAMPLE DATA (for demo only)
-- =========================================================
INSERT INTO products (product_name, category, minimum_stock, detect_class) VALUES
('Cardboard Boxes',   'Packaging', 15, 'box'),
('Water Bottles',     'Beverages', 10, 'bottle'),
('Snack Packets',     'Food',       8, 'packet'),
('Soft Drink Cans',   'Beverages', 12, 'can'),
('Detergent Bottles', 'Household',  6, 'detergent_bottle'),
('Cereal Boxes',      'Food',      10, 'cereal_box');

INSERT INTO shelves (shelf_name, location, status, occupancy, roi_x, roi_y, roi_w, roi_h) VALUES
('Shelf A', 'Zone 1 - Aisle 1', 'Active',   88,  2,  5, 30, 40),
('Shelf B', 'Zone 1 - Aisle 2', 'Active',   62, 35,  5, 30, 40),
('Shelf C', 'Zone 2 - Aisle 1', 'Active',   24, 68,  5, 30, 40),
('Shelf D', 'Zone 2 - Aisle 2', 'Active',   71,  2, 52, 30, 40),
('Shelf E', 'Zone 3 - Aisle 1', 'Active',   15, 35, 52, 30, 40),
('Shelf F', 'Zone 3 - Aisle 2', 'Inactive',  0,  0,  0,  0,  0);

INSERT INTO inventory (product_id, shelf_id, detected_quantity, updated_at) VALUES
(1, 1, 20, NOW() - INTERVAL 6 HOUR),
(2, 2, 12, NOW() - INTERVAL 5 HOUR),
(3, 3,  5, NOW() - INTERVAL 4 HOUR),
(4, 4, 18, NOW() - INTERVAL 3 HOUR),
(5, 5,  0, NOW() - INTERVAL 2 HOUR),
(6, 1,  9, NOW() - INTERVAL 1 HOUR);

INSERT INTO detection_events (product_id, shelf_id, event_type, quantity, event_time) VALUES
(3, 3, 'Low stock',    5, NOW() - INTERVAL 5 HOUR),
(5, 5, 'Low stock',    0, NOW() - INTERVAL 4 HOUR),
(6, 1, 'Low stock',    9, NOW() - INTERVAL 3 HOUR),
(1, 1, 'Stock update', 20, NOW() - INTERVAL 6 HOUR),
(2, 2, 'Stock update', 12, NOW() - INTERVAL 5 HOUR),
(4, 4, 'Stock update', 18, NOW() - INTERVAL 4 HOUR),
(2, 2, 'Stock update', 14, NOW() - INTERVAL 20 HOUR),
(1, 1, 'Stock update', 22, NOW() - INTERVAL 21 HOUR),
(3, 3, 'Stock update',  9, NOW() - INTERVAL 23 HOUR),
(4, 4, 'Low stock',   11, NOW() - INTERVAL 26 HOUR);

-- =========================================================
-- USEFUL QUERIES (practise these for the interview)
-- =========================================================
-- Low stock products:
--   SELECT p.product_name, s.shelf_name, i.detected_quantity, p.minimum_stock
--   FROM inventory i
--   JOIN products p ON p.product_id = i.product_id
--   JOIN shelves  s ON s.shelf_id   = i.shelf_id
--   WHERE i.detected_quantity < p.minimum_stock;
--
-- Number of events per type:
--   SELECT event_type, COUNT(*) FROM detection_events GROUP BY event_type;
