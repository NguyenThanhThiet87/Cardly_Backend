import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.auth.router import router as auth_router
from src.digital_cards.router import router as digital_cards_router
from src.users.router import router as users_router
from src.contacts.router import router as contacts_router
from src.scans.router import router as scans_router
from src.events.router import router as events_router
from src.tags.router import router as tags_router
from src.enrichment.router import router as enrichment_router
from database import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(lifespan=lifespan, debug=True, title="Cardly Backend API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
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
    """Root endpoint"""
    return {"message": "Welcome to Cardly Backend API"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
