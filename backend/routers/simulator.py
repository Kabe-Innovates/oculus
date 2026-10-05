from fastapi import APIRouter, HTTPException
from services.simulator import simulator_instance

router = APIRouter(prefix="/api/simulate", tags=["simulator"])

@router.post("/start")
async def start_simulator():
    simulator_instance.running = False
    raise HTTPException(
        status_code=403,
        detail="Simulator is disabled on hosted environments to prevent unintended resource consumption."
    )

@router.post("/stop")
async def stop_simulator():
    simulator_instance.running = False
    return {"message": "Simulator stopped"}

@router.get("/status")
async def simulator_status():
    return {"running": False}
