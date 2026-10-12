"""
Handlerlar to'plami.
"""
from aiogram import Router
from .start import router as start_router
from .dreams import router as dreams_router
from .history import router as history_router

main_router = Router()
main_router.include_router(start_router)
main_router.include_router(dreams_router)
main_router.include_router(history_router)

__all__ = ["main_router"]
