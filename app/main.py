from fastapi import FastAPI
import uvicorn
from app.api.v1 import user, product, category, cart, wishlist, order, address, review, admin
from app.services.redis_service import redis_service
from app.middleware.custom_middleware import add_cors_middleware
from contextlib import asynccontextmanager
import logging
# Redis 

# logger = logging.getLogger(__name__)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     try:
#         await redis_service.connect()
#     except Exception as e:
#         logger.error(f"Redis connection failed after retries: {str(e)}")
#         logger.warning("Application running without Redis")

#     yield

#     # Shutdown
#     await redis_service.close()

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


add_cors_middleware(app)


@app.get("/")
def read_root():
    return {"Hello": "Rifayet"}





@app.get("/test-redis")
async def test_redis():
    try:
        await redis_service.set("test_key", {"message": "Hello from Render to Railway Redis!"})
        value = await redis_service.get("test_key")
        return {"status": "success", "redis_value": value}
    except Exception as e:
        return {"status": "error", "message": str(e)}



# if __name__ == "__main__":
#     uvicorn.run(app, host="localhost", port=8000)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)