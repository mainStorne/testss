
from fastapi import FastAPI
from .api import r

app = FastAPI()
app.include_router(r, tags=["users"])


