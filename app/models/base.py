from app.db.base_class import Base

def register_models():
    from app.models.user import User
    from app.models.wishlist import Wishlist
    from app.models.address import Address
    from app.models.product import Product
    from app.models.category import Category
    from app.models.cart import Cart
    from app.models.order import Order
    from app.models.review import Review
