from fastapi import APIRouter
from .routes.auth_router import auth_router
from .routes.data_pipeline_router import data_pipeline_router  # UNCOMMENT
from .routes.chat_router import chat_router  # UNCOMMENT

api_router = APIRouter()

api_router.include_router(
    auth_router,
    prefix="/api/user/v1",
    tags=["user"],
)

api_router.include_router(  # UNCOMMENT
    data_pipeline_router,      # UNCOMMENT
    prefix="/api/data/v1",     # UNCOMMENT
    tags=["data"],             # UNCOMMENT
)                              # UNCOMMENT

api_router.include_router(  # UNCOMMENT
    chat_router,              # UNCOMMENT
    prefix="/api/chat/v1",    # UNCOMMENT
    tags=["chat"],            # UNCOMMENT
)                             # UNCOMMENT