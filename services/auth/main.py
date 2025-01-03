import uvicorn
import os
from pathlib import Path
from fastapi import FastAPI
from src.api import api

app = FastAPI(root_path='/api/auth')
app.include_router(api, prefix='/api')

log_config = Path(__file__).parent / 'log_config.yml'

if __name__ == '__main__':
    uvicorn.run('__main__:app', host='0.0.0.0', port=int(os.getenv('PORT', '8080')), reload=True,
                # log_config=str(log_config.absolute())
                )
