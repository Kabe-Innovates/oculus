from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from engine.registry import RuleRegistry
from engine.core import FraudEngine
from services.notifier import get_notifier
from routers import transactions, stats, simulator
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message):
        if hasattr(message, '__dict__'):
            data = message.__dict__.copy()
            data.pop('_sa_instance_state', None)
            for k, v in data.items():
                if hasattr(v, 'isoformat'):
                    data[k] = v.isoformat()
            msg_str = json.dumps(data)
        else:
            msg_str = json.dumps(message)
            
        for connection in list(self.active_connections):
            try:
                await connection.send_text(msg_str)
            except Exception:
                self.disconnect(connection)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    
    registry = RuleRegistry()
    registry.discover()
    print("Registered rules:", [r.name for r in registry.get_all()])
    
    app.state.registry = registry
    app.state.ws_manager = ConnectionManager()
    app.state.fraud_engine_class = FraudEngine
    app.state.notifier = get_notifier()
    
    yield

app = FastAPI(title='SentinelPay API', description='Fraud detection rule engine', version='1.0.0', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router)
app.include_router(stats.router)
app.include_router(simulator.router)

@app.websocket("/ws/transactions")
async def websocket_endpoint(websocket: WebSocket):
    manager: ConnectionManager = app.state.ws_manager
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
