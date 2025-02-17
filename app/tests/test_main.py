from fastapi.testclient import TestClient
from ..main import app
from fastapi import status


client = TestClient(app)


@app.get("/health")
async def health_check():
    return {"status": "ok"}