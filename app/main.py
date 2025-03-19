from fastapi import FastAPI
from . import models
from .database import engine
from .routers import  users, auth, instances

from fastapi.middleware.cors import CORSMiddleware

#this line is not needed when using alembic
models.Base.metadata.create_all(bind=engine)


app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the API"}


app.include_router(users.router) 
app.include_router(auth.router) 
app.include_router(instances.router)