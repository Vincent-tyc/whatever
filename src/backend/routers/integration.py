from fastapi import APIRouter, HTTPException
from src.backend.services import integrator

router = APIRouter(prefix="/api/integration", tags=["integration"])


@router.post("/run")
async def execute_integration():
    result = await integrator.run_integration()
    return result


@router.get("/status")
async def get_integration_status():
    if integrator.integration_result_store is None:
        raise HTTPException(404, "尚未执行整合")
    return integrator.integration_result_store


@router.post("/decisions/{decision_id}")
async def modify_decision(decision_id: str, action: str, reason: str = ""):
    if integrator.integration_result_store is None:
        raise HTTPException(404, "尚未执行整合")

    for d in integrator.integration_result_store.decisions:
        if d.decision_id == decision_id:
            d.action = action
            if reason:
                d.reason = reason
            return {"status": "updated", "decision": d}

    raise HTTPException(404, "决策不存在")
