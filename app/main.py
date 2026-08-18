import logging

from fastapi import FastAPI

from app.api.routes import router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Appel d'Offres Assistant",
    description="Agent IA pour l'analyse et la réponse aux appels d'offres publics",
    version="0.1.0",
)

app.include_router(router)