from fastapi import FastAPI
import uvicorn
from app.api.v1 import user, product



app = FastAPI()


# connect all router here 
app.include_router(user.router)
app.include_router(product.router)



@app.get("/")
def read_root():
    return {"Hello": "World"}



if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)