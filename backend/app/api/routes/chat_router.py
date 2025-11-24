from fastapi import Path, APIRouter, Request, Depends
from app.api.controllers import chat_controller
from app.api.validators.chat_validator import AskQuestion, InitiateCinversaction
from app.dependencies.database import get_db
from app.config.db_config import DB

# Instance of APIRouter
chat_router = APIRouter()


@chat_router.post("/ask-question")
async def ask_question(request: Request, body: AskQuestion, db: DB = Depends(get_db)):
    user_id = request.state.user_id
    return await chat_controller.ask_question(user_id, body, db)


@chat_router.post("/initiate-conversations")
async def initiate_convesactions(request: Request, body: InitiateCinversaction, db: DB = Depends(get_db)):
    user_id = request.state.user_id
    return chat_controller.initiate_convesactions(user_id, body, db)


@chat_router.post("/get-conversations")
async def get_conversactions(request: Request, db: DB = Depends(get_db)):
    user_id = request.state.user_id
    return chat_controller.get_convesactions(user_id, db)   


@chat_router.post("/get-conversations-history/{conversation_id}")
async def get_conversaction_history(conversation_id: int = Path(..., title="Conversation ID"), db: DB = Depends(get_db)):
    return chat_controller.get_conversaction_history(conversation_id, db)


@chat_router.get("/models")
async def get_available_models():
    """Get list of all available LLM models with their metadata"""
    return chat_controller.get_available_llm_models()


@chat_router.get("/models/{model_name}")
async def get_model_info(model_name: str = Path(..., title="Model name")):
    """Get detailed information about a specific LLM model"""
    return chat_controller.get_llm_model_info(model_name)
