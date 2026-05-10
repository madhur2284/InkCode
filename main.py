import cloudinary_config
from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from routers import auth, post, comment, tag, post_reaction, comment_reaction, bookmark, follow, search
from database import engine
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting server")
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(post.router)
app.include_router(comment.router)
app.include_router(tag.router)
app.include_router(post_reaction.router)
app.include_router(comment_reaction.router)
app.include_router(bookmark.router)
app.include_router(follow.router)
app.include_router(search.router)

@app.get(path='/', status_code = status.HTTP_200_OK)
async def home():
    return {"Message": "Welcome to bloggolb"}