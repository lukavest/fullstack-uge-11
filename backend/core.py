from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from typing import Optional
import enum

# Enum for order status
class OrderStatus(str, enum.Enum):
    IN_CART = "in cart"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"


class MenuItem(Base):
    """Unified MenuItem model with validation logic."""
    __tablename__ = "menu_items"
    
    item_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String, default="")
    category = Column(String, default="")
    available = Column(Boolean, default=True)
    
    # Relationships
    store = relationship("Store", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")
    
    def __str__(self):
        return f"{self.item_id:02d} {self.name:<15} ${self.price:<5} {'not' if not self.available else ''} available"
    
    def validate_price(self):
        """Validate that price is positive."""
        if self.price <= 0.0:
            raise ValueError("Price must be positive and non-zero")


class OrderItem(Base):
    """Order line item linking orders to menu items."""
    __tablename__ = "order_items"
    
    order_item_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("menu_items.item_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")
    
    def __str__(self):
        return f"OrderItem(item_id={self.item_id}, qty={self.quantity}, unit_price=${self.unit_price}, total=${self.price})"


class Order(Base):
    """Unified Order model with validation logic."""
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    total = Column(Float, default=0.0)
    status = Column(Enum(OrderStatus), default=OrderStatus.IN_CART)
    
    # Relationships
    user = relationship("User", back_populates="orders", foreign_keys=[user_id])
    store = relationship("Store", back_populates="orders", foreign_keys=[store_id])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __str__(self):
        return f"Order(id={self.order_id}, user={self.user_id}, store={self.store_id}, total=${self.total}, status={self.status})"
    
    def validate_order(self, store: "Store"):
        """Validate order against store's current menu."""
        total = 0.0
        for item in self.items:
            menu_item = store.get_item_by_id(item.item_id)
            if menu_item is None:
                raise ValueError(f"MenuItem with item_id {item.item_id} no longer exists in menu")
            if not menu_item.available:
                raise ValueError(f"MenuItem with item_id {item.item_id} no longer available")
            total += menu_item.price * item.quantity
        
        if total != self.total:
            raise ValueError(f"Order total mismatch: {self.total} in order vs. {total} upon validation")


class Store(Base):
    """Unified Store model with menu management and validation."""
    __tablename__ = "stores"
    
    store_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    # Relationships
    menu_items = relationship("MenuItem", back_populates="store", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="store", cascade="all, delete-orphan")
    
    def __str__(self):
        return f"Store(id={self.store_id}, name='{self.name}', items={len(self.menu_items)}, orders={len(self.orders)})"
    
    def get_item_by_id(self, item_id: int) -> Optional[MenuItem]:
        """Get menu item by ID."""
        for item in self.menu_items:
            if item.item_id == item_id:
                return item
        return None
    
    def add_menu_item(self, menu_item: MenuItem):
        """Add a menu item to the store's menu."""
        menu_item.validate_price()
        
        if self.get_item_by_id(menu_item.item_id):
            raise ValueError(f"MenuItem with item_id {menu_item.item_id} already exists in menu")
        
        self.menu_items.append(menu_item)
    
    def remove_menu_item(self, item_id: int):
        """Remove a menu item from the store's menu."""
        for item in self.menu_items:
            if item.item_id == item_id:
                self.menu_items.remove(item)
                return
        raise ValueError(f"MenuItem with item_id {item_id} not found, could not remove from menu")
    
    # def validate_order(self, order: Order):
    #     """Validate an order against current menu."""
    #     order.validate_order(self)


class User(Base):
    """Unified User model with cart and order management."""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    store_visiting_id = Column(Integer, ForeignKey("stores.store_id"), nullable=True)
    cart_id = Column(Integer, ForeignKey("orders.order_id"), nullable=True)
    
    # Relationships
    store_visiting = relationship("Store", foreign_keys=[store_visiting_id])
    cart = relationship("Order", foreign_keys=[cart_id], uselist=False)
    orders = relationship("Order", back_populates="user", foreign_keys="Order.user_id")
    
    def __str__(self):
        return f"User(id={self.user_id}, name='{self.name}', cart={self.cart_id}, orders={len(self.orders)})"
    
    def visit_store(self, store: Store, session):
        """User visits a store and creates a new cart."""
        if self.store_visiting is not None:
            raise ValueError("Cannot visit a new store before leaving the current store")
        
        self.store_visiting = store
        new_cart = Order(user_id=self.user_id, store_id=store.store_id, status=OrderStatus.IN_CART)
        session.add(new_cart)
        session.flush()  # Flush to get order_id
        self.cart = new_cart
    
    def leave_store(self):
        """User leaves the current store."""
        self.store_visiting = None
        self.cart = None
    
    def add_to_cart(self, item_id: int, quantity: int = 1, session=None):
        """Add an item to the user's cart."""
        if self.store_visiting is None:
            raise ValueError("User must be visiting Store to add to cart")
        if quantity < 1:
            raise ValueError("Quantity must be positive and non-zero")
        
        menu_item = self.store_visiting.get_item_by_id(item_id)
        if menu_item is None:
            raise ValueError(f"MenuItem with item_id {item_id} not found in store")
        if not menu_item.available:
            raise ValueError(f"MenuItem with item_id {item_id} is not available")
        
        # Check if item already in cart
        existing_item = None
        for order_item in self.cart.items:
            if order_item.item_id == item_id:
                existing_item = order_item
                break
        
        if existing_item:
            existing_item.quantity += quantity
            existing_item.price = existing_item.unit_price * existing_item.quantity
        else:
            new_order_item = OrderItem(
                order_id=self.cart.order_id,
                item_id=item_id,
                quantity=quantity,
                unit_price=menu_item.price,
                price=menu_item.price * quantity
            )
            self.cart.items.append(new_order_item)
            if session:
                session.add(new_order_item)
        
        self._recalculate_cart_total()
    
    def _recalculate_cart_total(self):
        """Recalculate the total price of items in cart."""
        self.cart.total = sum(item.price for item in self.cart.items)
    
    def checkout(self):
        """Convert cart to a confirmed order."""
        if self.cart is None:
            raise ValueError("No active cart to checkout")
        if not self.cart.items:
            raise ValueError("Cannot checkout with empty cart")
        
        # Validate order before checkout
        # self.store_visiting.validate_order(self.cart)
        self.cart.validate_order(self.store_visiting)
        
        # Mark order as pending (the order already has user_id, so it's automatically in orders)
        self.cart.status = OrderStatus.PENDING
        completed_order = self.cart
        
        # Clear cart and store references
        self.cart = None
        self.store_visiting = None
        
        return completed_order