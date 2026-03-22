from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from apis.fastapi.routes.auth import UsersAuthAPIRouter
from apis.fastapi.routes.video import VideoGenerationAPIRouter
from core.generations.service import GenerationService
from core.users.auth import AuthService
from core.users.service import UserService
from dbs.inmemory.engine import cleanup_connections, test_connection
from dbs.inmemory.generations.dao import GenerationDAO
from dbs.inmemory.users.dao import UserDAO
from middlewares.jwt_bearer import JWTCookie


@asynccontextmanager
async def lifespan(app: FastAPI):
    await test_connection()
    yield
    await cleanup_connections()


app = FastAPI(
    title="Video Generation POC with Temporal",
    description="Proof of concept for orchestrating an AI video generation pipeline (video generation → S3 → token deduction → DB) using Temporal workflows and activities with FastAPI.",
    author={
        "name": "Abram",
        "url": "https://github.com/aybruhm/ai-video-generation-poc-with-temporal",
    },
    lifespan=lifespan,
    root_path="/api",
)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Initialize middlewares
jwt_cookie = JWTCookie()

# Initialize DAOs
user_dao = UserDAO()
generation_dao = GenerationDAO()

# Initialize services
user_service = UserService(dao=user_dao)
auth_service = AuthService(user_service=user_service)
generation_service = GenerationService(dao=generation_dao)

# Initialize routers
auth_router = UsersAuthAPIRouter(
    jwt_cookie=jwt_cookie,
    auth_service=auth_service,
)
video_router = VideoGenerationAPIRouter(
    generation_service=generation_service,
)

# Mount routers to app
app.include_router(auth_router.router)
app.include_router(video_router.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
