from fastapi import APIRouter
from app.api.endpoints import sessions, state, conflicts, document, email

api_router = APIRouter(prefix="/api")

api_router.include_router(sessions.router)
api_router.include_router(state.router)
api_router.include_router(conflicts.router)
api_router.include_router(document.router)
api_router.include_router(email.router)
