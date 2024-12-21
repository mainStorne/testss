import uvicorn
import os

if __name__ == '__main__':
    uvicorn.run('application.app:app', host='0.0.0.0', port=int(os.getenv('PORT', '8080')), reload=True)
