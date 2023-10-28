from .base import AbstractModel
from sqlalchemy import BigInteger, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship, mapped_column, Mapped

class User(AbstractModel):
    __tablename__ = "users"
    name = mapped_column(String, nullable=False, unique=False)
    phone = mapped_column(String, nullable=False)
    chatId = mapped_column(BigInteger,  unique=True, nullable=False, primary_key=True)
    address = mapped_column(String, nullable=True)
    cart = relationship("Cart", back_populates="user", lazy='selectin')

class Cart(AbstractModel):
    __tablename__ = "carts"
    id = mapped_column(Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
    sum = mapped_column(Integer, nullable=False)
    chatId = mapped_column(BigInteger, ForeignKey("users.chatId"))
    dataCreate = mapped_column(Date, nullable=True)
    knox = mapped_column(Integer)
    user = relationship("User", back_populates="cart", lazy='selectin')
    product = relationship("Product", back_populates="cart", lazy="selectin")

class Product(AbstractModel):
    __tablename__ = "products"
    id = mapped_column(Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    price = mapped_column(String, nullable=False)
    dataCreatePost = mapped_column(String, nullable=False)
    description = mapped_column(String, nullable=False)
    photo = mapped_column(String, nullable=False, unique=True)
    cart_id = mapped_column(Integer, ForeignKey("carts.id"), nullable=False)
    cart = relationship("Cart", back_populates="product", lazy="selectin")