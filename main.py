import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.digital_cards.router import router as digital_cards_router
from database import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Chạy khi server khởi động (Startup)
    await connect_to_mongo()
    yield
    # Chạy khi server tắt (Shutdown)
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)
app.include_router(digital_cards_router)

if __name__ == "__main__":
    uvicorn.run(app, host = "0.0.0.0", port = 8000)
    