import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.exception_handlers import register_exception_handlers
from src.core.routers import v1_router

app = FastAPI()
app.include_router(v1_router)

register_exception_handlers(app)

# Configure CORS
origins = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
    "http://localhost:3000",
    "https://wasel-black.vercel.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("server.app.main:app", host="0.0.0.0", port=8000, reload=True)