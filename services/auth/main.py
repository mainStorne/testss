import uvicorn
import os
from pathlib import Path

log_config = Path(__file__).parent / 'log_config.yml'

if __name__ == '__main__':
    uvicorn.run('application.app:app', host='0.0.0.0', port=int(os.getenv('PORT', '8080')), reload=True,
                log_config=str(log_config.absolute())
                )
