import cloudinary_config
from fastapi import FastAPI, status, Request
from contextlib import asynccontextmanager
from routers import auth, post, comment, tag, post_reaction, comment_reaction, bookmark, follow, search, admin_stats
from database import engine
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict
import time
from fastapi.responses import JSONResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting server")
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


rate_limit = 60
windows_start = 60
requests_count: dict = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip = request.client.host
    now = time.time()
    windows_seconds = now-windows_start
    requests_count[ip] = [ts for ts in requests_count[ip] if ts > windows_seconds]
    
    if len(requests_count[ip]) > rate_limit:
        return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={"detail": "Too many Requests"})
    
    requests_count[ip].append(now)
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(post.router)
app.include_router(comment.router)
app.include_router(tag.router)
app.include_router(post_reaction.router)
app.include_router(comment_reaction.router)
app.include_router(bookmark.router)
app.include_router(follow.router)
app.include_router(search.router)
app.include_router(admin_stats.router)

@app.get(path='/', status_code = status.HTTP_200_OK)
async def home():
    return {"Message": "Welcome to bloggolb"}