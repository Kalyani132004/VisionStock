# main.py - start the FastAPI application


import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import FRONTEND_DIR
from .database import Base, engine, SessionLocal
from .models import User
from .routes import auth, products, shelves, inventory, alerts, detection
from .security import read_token
from .seed import seed_database
from .services import kafka_service
from .services.websocket_service import manager
from .vision.pipeline import pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)          # create tables if they do not exist

    db = SessionLocal()
    try:
        seed_database(db)                           # sample data for an empty database

        if db.query(User).filter(User.role == "Admin").count() == 0:
            print("\n  No Admin account yet. Create one with:")
            print("      python -m backend.create_admin\n")
    finally:
        db.close()

    manager.loop = asyncio.get_running_loop()       # needed to send WebSocket messages from threads
    kafka_service.start_consumer()                  # does nothing when Kafka is disabled

    yield

    # --- runs when the server stops ---
    pipeline.stop()


app = FastAPI(title="VisionStock API", version="1.0", lifespan=lifespan)

# Allow the frontend to call the API when it is opened from another address
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- REST API routes ----------
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(shelves.router)
app.include_router(inventory.router)
app.include_router(alerts.router)
app.include_router(detection.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# ---------- WebSocket: /ws/inventory?token=... ----------
@app.websocket("/ws/inventory")
async def inventory_socket(websocket: WebSocket, token: str = ""):
    if read_token(token) is None:
        await websocket.close(code=1008)            # not logged in
        return

    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()          # keep the connection open
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ---------- Serve the frontend at http://127.0.0.1:8000 ----------
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
