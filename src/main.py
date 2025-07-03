import uvicorn
from fastapi import FastAPI

from api import api_router


app = FastAPI(title="Modular Boilerplate")

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8008)
