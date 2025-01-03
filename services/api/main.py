import uvicorn

from fastapi import FastAPI
from src.api import r

app = FastAPI(root_path='/api')
app.include_router(r, tags=["users"])

if __name__ == '__main__':
    uvicorn.run('__main__:app', host='0.0.0.0', port=8000, reload=True)
