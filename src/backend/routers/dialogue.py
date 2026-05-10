from fastapi import APIRouter
from src.backend.models.schemas import DialogueRequest
from src.backend.services.dialogue import process_dialogue

router = APIRouter(prefix="/api/dialogue", tags=["dialogue"])


@router.post("")
async def dialogue(req: DialogueRequest):
    return await process_dialogue(req)
