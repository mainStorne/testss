
from fastapi import FastAPI
from .api import r

app = FastAPI(root_path='/api')
app.include_router(r, tags=["users"])


