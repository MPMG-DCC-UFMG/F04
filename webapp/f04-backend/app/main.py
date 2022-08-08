

from fastapi import FastAPI
from .repository import models
from .routers import tweet, user, authentication

from fastapi.middleware.cors import CORSMiddleware
import os
app = FastAPI()

origins = [
    "http://localhost",
    os.getenv("URL_FRONTEND")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# models.Base.metadata.create_all(engine)

app.include_router(authentication.router)
app.include_router(tweet.router)
app.include_router(user.router)
