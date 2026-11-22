# websocket_service.py - send live updates to the browser dashboard

import asyncio
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.connections = []     # all open browser connections
        self.loop = None          # the main asyncio loop (set when server starts)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, message: dict):
        # send the message to every connected browser
        for connection in list(self.connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

    def broadcast_from_thread(self, message: dict):
        """Our detection code runs in a normal thread, so we use this
        function to hand the message over to the async loop."""
        if self.loop is None or not self.loop.is_running():
            return
        asyncio.run_coroutine_threadsafe(self.broadcast(message), self.loop)


manager = ConnectionManager()
