from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from typing import Optional
from core import OrderStatus


class MenuItemModel(Base):
    __tablename__ = "menu_items"
    
    item_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String, default="")
    category = Column(String, default="")
    available = Column(Boolean, default=True)
    
    # Relationships
    store = relationship("StoreModel", back_populates="menu_items")
    order_items = relationship("OrderItemModel", back_populates="menu_item")


class OrderItemModel(Base):
    __tablename__ = "order_items"
    
    order_item_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("menu_items.item_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("OrderModel", back_populates="items")
    menu_item = relationship("MenuItemModel", back_populates="order_items")
    
class OrderModel(Base):
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    total = Column(Float, default=0.0)
    status = Column(Enum(OrderStatus), default=OrderStatus.IN_CART)
    
    # Relationships
    user = relationship("UserModel", back_populates="orders", foreign_keys=[user_id])
    store = relationship("StoreModel", back_populates="orders", foreign_keys=[store_id])
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")
    

class StoreModel(Base):
    __tablename__ = "stores"
    
    store_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    # Relationships
    menu_items = relationship("MenuItemModel", back_populates="store", cascade="all, delete-orphan")
    orders = relationship("OrderModel", back_populates="store", cascade="all, delete-orphan")

class UserModel(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    store_visiting_id = Column(Integer, ForeignKey("stores.store_id"), nullable=True)
    cart_id = Column(Integer, ForeignKey("orders.order_id"), nullable=True)
    
    # Relationships
    store_visiting = relationship("StoreModel", foreign_keys=[store_visiting_id])
    cart = relationship("OrderModel", foreign_keys=[cart_id], uselist=False)
    orders = relationship("OrderModel", back_populates="user", foreign_keys="OrderModel.user_id")
