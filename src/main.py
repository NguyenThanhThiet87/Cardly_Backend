import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.features.auth.router import router as auth_router
from src.features.contacts.router import router as contacts_router
from src.features.digital_cards.router import router as digital_cards_router
from src.features.enrichment.router import router as enrichment_router
from src.features.events.router import router as events_router
from src.features.scans.router import router as scans_router
from src.features.tags.router import router as tags_router
from src.features.users.router import router as users_router
from src.core.database import connect_to_mongo, close_mongo_connection
from src.core.middleware import setup_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan, debug=True, title="Cardly Backend API")

# Setup các middleware (như CORS)
setup_middleware(app)


API_PREFIX = "/api"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(digital_cards_router, prefix=API_PREFIX)
app.include_router(users_router, prefix=API_PREFIX)
app.include_router(contacts_router, prefix=API_PREFIX)
app.include_router(scans_router, prefix=API_PREFIX)
app.include_router(events_router, prefix=API_PREFIX)
app.include_router(tags_router, prefix=API_PREFIX)
app.include_router(enrichment_router, prefix=API_PREFIX)

@app.get("/")
async def root():
    return {"message": "Welcome to Cardly Backend API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
