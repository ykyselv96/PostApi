from fastapi import FastAPI
import uvicorn
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from core.config.system_config import settings
from endpoints import auth, posts, comments, analytics


app = FastAPI()


origins = ["http://localhost",
           "http://localhost:8000",
           ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    logger.info("App is startup")


@app.on_event("shutdown")
async def shutdown():
    logger.info("App is shutdown")


app.include_router(posts.router)
app.include_router(auth.router)
app.include_router(comments.router)
app.include_router(analytics.router)


if __name__ == "__main__":
    uvicorn.run('main:app', host=settings.app_host, port=int(settings.app_port), reload=True)
