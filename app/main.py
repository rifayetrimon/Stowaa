from fastapi import FastAPI
import uvicorn
from app.api.v1 import user, product, category, cart, wishlist, order, address, review, admin



app = FastAPI()


# connect all router here 
app.include_router(user.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(wishlist.router)
app.include_router(order.router)
app.include_router(address.router)
app.include_router(review.router)
app.include_router(admin.router)



@app.get("/")
def read_root():
    return {"Hello": "World"}



if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)