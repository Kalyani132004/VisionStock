# VisionStock - Smart Warehouse Inventory Monitoring System

Python + OpenCV + YOLO + FastAPI + MySQL + WebSocket (+ optional Kafka) with a Bootstrap dashboard.

```
Camera / video -> OpenCV -> YOLO + ByteTrack -> counting per shelf region
              -> inventory logic -> MySQL
              -> WebSocket (or Kafka -> WebSocket) -> live dashboard
```

## 1. What you need

- Python 3.10 or newer
- MySQL 8 (or MariaDB). For a quick test you can use SQLite instead (see step 3).
- Internet for the first run: the pages load Bootstrap, icons and Chart.js from a CDN,
  and YOLO downloads `yolov8n.pt` (about 6 MB) the first time detection starts.

## 2. Install

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / Mac
pip install -r backend/requirements.txt
```

`ultralytics` installs PyTorch, so this download is large. The API, login, dashboard and all
CRUD pages work without it; only the Live Camera page needs it.

## 3. Database

**MySQL (recommended)**

1. Run `database/schema.sql` in MySQL Workbench, or:
   `mysql -u root -p < database/schema.sql`
   (creates the `visionstock` database, 5 tables and sample data)
2. Copy `.env.example` to `.env` and put your MySQL password in `DATABASE_URL`.

The backend also creates the tables and sample data by itself on start if they are missing,
so you can skip step 1 and just create an empty database named `visionstock`.

If your MySQL password has special characters, write them as codes in `DATABASE_URL`:
`@` = `%40`, `#` = `%23`, `/` = `%2F`, `:` = `%3A`.

**No MySQL?** In `.env` use `DATABASE_URL=sqlite:///visionstock.db`.

## 4. Run

```bash
python -m uvicorn backend.main:app --reload
```

(or double-click `start_server.bat` on Windows, `./start_server.sh` on Linux/Mac)

Open **http://127.0.0.1:8000** - the backend serves the frontend too.
API documentation: http://127.0.0.1:8000/docs

## 4b. Accounts and login

There are no default users and no default passwords.

| Role | How to get it | Can do |
|------|---------------|--------|
| **Staff** | Click **Create an account** on the login page (`register.html`) | view, add, edit (not delete) |
| **Admin** | Only with a command (see below) | everything, including delete |

The website can only create Staff accounts. Nobody can make themselves Admin from the browser.

**Create the first Admin** (like `createsuperuser` in Django). Run this in the project folder,
with your venv active, and answer the questions (the password is hidden while you type):

```bash
python -m backend.create_admin
```

If the email already belongs to a Staff user, it asks if you want to make that user an Admin.
The server also prints a reminder at start-up while no Admin exists.

Password rules: 8 to 72 characters, with at least one letter and one number.
Passwords are stored as bcrypt hashes, and login tokens are signed with a secret key.
If you do not set `SECRET_KEY` in `.env`, a random one is created in the file `.secret_key`
(it is in `.gitignore`; do not share it).

Anyone who can open the website can register a Staff account. If the server is on a public
network, put it behind a login or firewall first.

## 5. Using real detection

1. Put a warehouse video in the `videos/` folder (or use the webcam).
2. **Shelves page**: give each shelf a camera region (X, Y, Width, Height in percent of the picture).
   Only shelves with a region are monitored.
3. **Products page**: set the **YOLO class name** of each product (the label the model gives,
   for example `bottle`). This links a detection to a product.
4. **Live Camera page**: choose the source and click Start. Quantities, shelf occupancy,
   events and low-stock alerts update in the database and on every open dashboard.

### Important: which products can be detected

The default model (`yolov8n.pt`) knows 80 generic COCO classes such as `bottle`, `cup`, `bowl`.
It does **not** know "box", "packet" or your own SKUs. The sample products use class names like
`box` and `packet` as placeholders, so only `bottle` will match with the default model.

For real warehouse products, collect and label images, train a model with Ultralytics,
and save it as `models/best.pt` - it is picked up automatically. Use the class names from
your training as the **YOLO class name** of each product.

## 6. Folder structure

```
VisionStock/
├── backend/
│   ├── main.py            app start, WebSocket, serves frontend
│   ├── config.py          settings from .env
│   ├── database.py        MySQL connection (SQLAlchemy)
│   ├── models.py          5 tables
│   ├── schemas.py         request / response shapes
│   ├── security.py        bcrypt passwords + JWT token
│   ├── validation.py      rules for name, email, password
│   ├── create_admin.py    command to create an Admin account
│   ├── seed.py            sample data for an empty database
│   ├── routes/            auth, products, shelves, inventory, alerts, detection
│   ├── vision/            camera, detection, tracking, counting, shelf_monitor, pipeline
│   └── services/          inventory_service, websocket_service, kafka_service
├── frontend/              10 pages + css/ + js/ (one js file per page)
├── database/schema.sql    tables + sample data + useful queries
├── dataset/ models/ videos/
├── .env.example
└── start_server.bat / start_server.sh
```

## 7. API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/auth/register | create a Staff account, returns token |
| POST | /api/auth/login | login, returns token |
| GET/POST | /api/products | list / add product |
| PUT/DELETE | /api/products/{id} | edit / delete (delete = Admin) |
| GET/POST | /api/shelves | list / add shelf |
| PUT/DELETE | /api/shelves/{id} | edit / delete (delete = Admin) |
| GET/POST | /api/inventory | list / save quantity by hand |
| PUT/DELETE | /api/inventory/{id} | change quantity / delete (Admin) |
| GET | /api/events | detection history |
| GET | /api/alerts | low-stock and empty-shelf alerts |
| POST | /api/detection/start, /stop | start / stop video processing |
| GET | /api/detection/status, /videos, /stream | status, video list, live picture |
| WS | /ws/inventory | live updates |

## 8. Kafka (optional, advanced)

Kafka is off by default and the project works fully without it (follow your own roadmap:
build the core first). To try it:

1. Start a Kafka broker, `pip install kafka-python`
2. In `.env` set `KAFKA_ENABLED=true`

Events are then published to the topic, a consumer thread reads them (and reconnects every
5 seconds if Kafka stops) and pushes them to the dashboard through WebSocket.

## 9. Limitations

- Detection quality depends on the model, lighting and camera angle.
- Overlapping products are hard to count.
- If a product's centre lies inside two shelf regions, it is counted on both - keep regions apart.
- The camera cannot see products that are hidden or moved out of view; use the manual
  quantity correction on the Inventory page.
- Measure your own FPS, latency and accuracy on your video before quoting numbers.
