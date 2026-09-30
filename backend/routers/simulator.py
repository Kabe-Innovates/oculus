from fastapi import APIRouter, BackgroundTasks
from services.simulator import simulator_instance
import httpx
import asyncio

router = APIRouter(prefix="/api/simulate", tags=["simulator"])

async def run_simulator():
    async for tx_data in simulator_instance.stream():
        async with httpx.AsyncClient() as client:
            try:
                await client.post("http://127.0.0.1:8000/api/transactions", json=tx_data)
            except Exception:
                pass

@router.post("/start")
async def start_simulator(background_tasks: BackgroundTasks):
    if not simulator_instance.running:
        background_tasks.add_task(run_simulator)
    return {"message": "Simulator started"}

@router.post("/stop")
async def stop_simulator():
    simulator_instance.running = False
    return {"message": "Simulator stopped"}

@router.get("/status")
async def simulator_status():
    return {"running": simulator_instance.running}
