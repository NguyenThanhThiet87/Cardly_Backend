import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.digital_cards.router import router as digital_cards_router
from src.users.router import router as users_router
from src.contacts.router import router as contacts_router
from src.scans.router import router as scans_router
from database import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(lifespan=lifespan, debug=True)

app.include_router(digital_cards_router)
app.include_router(users_router)
app.include_router(contacts_router)
app.include_router(scans_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
