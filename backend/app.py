from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.upload import router as upload_router
from api.search import router as search_router
from api.chat import router as chat_router
from api.meaning_radar import router as meaning_radar_router


app = FastAPI(
    title="ContextIQ API",
    description="Privacy-focused semantic search backend",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(upload_router)
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(meaning_radar_router)


@app.get("/")
async def root():
    return {
        "message": "ContextIQ backend is running!",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }
