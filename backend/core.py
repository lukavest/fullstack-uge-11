from dataclasses import dataclass, field
from typing import Optional
from copy import deepcopy
import enum

# Enum for order status
class OrderStatus(str, enum.Enum):
    IN_CART = "in cart"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"


@dataclass
class MenuItem:
    item_id:        int
    store_id:       int
    name:           str
    price:          float
    emoji:          Optional[str] = None
    description:    Optional[str] = None
    category:       Optional[str] = None
    available:      bool = True
    
    def __str__(self):
        return f"{self.item_id:02d} {self.name:<15} ${self.price:<5} {'not' if not self.available else ''} available"

# @dataclass
# class Menu:
#     store_id: int     # mirrors store id
#     items: list[MenuItem] = field(default_factory=list)

@dataclass
class OrderItem:
    item_id:        int
    quantity:       int
    unit_price:     float
    price:          float
    order_item_id:  Optional[int] = None
    order_id:       Optional[int] = None
    
    
@dataclass
class Order:
    user_id:        int
    store_id:       int
    items:          list[OrderItem] = field(default_factory=list)
    total:          float = 0.0
    status:         OrderStatus = OrderStatus.IN_CART  # pending | confirmed | preparing | ready | delivered
    
    def validate_order(self, store: "Store"):
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



@dataclass
class Store:
    store_id:       int
    name:           str
    menu_items:     list[MenuItem] = field(default_factory=list)
    orders:         list[Order] = field(default_factory=list)
        
    def __str__(self):
        return f"Store(id={self.store_id}, name='{self.name}', menu_items_count={len(self.menu_items)}, orders_count={len(self.orders)})"
    
    def get_item_by_id(self, item_id: int) -> Optional[MenuItem]:
        """Get a menu item by ID."""
        for item in self.menu_items:
            if item.item_id == item_id:
                return item
        return None
        

@dataclass
class User:
    email:          str
    name:           str
    user_id:        Optional[int] = None
    
    store_visiting_id: Optional[int] = None
    cart_id: Optional[int] = None
    
    store_visiting: Optional[Store] = None
    cart:           Optional[Order] = None
    orders:         list[Order] = field(default_factory=list)
        
    def __str__(self):
        return f"User(id={self.user_id}, name='{self.name}', cart={self.cart}, orders_count={len(self.orders)})"
    
    def visit_store(self, store: Store, new_cart: Order) -> None:
        """User visits a store with an initialized cart."""
        if self.store_visiting is not None:
            raise ValueError("Cannot visit a new store before leaving the current store")
        
        self.store_visiting = store
        self.store_visiting_id = store.store_id
        self.cart = new_cart
        self.cart_id = new_cart.order_id if hasattr(new_cart, 'order_id') else None
        
    def leave_store(self) -> None:
        """User leaves current store."""
        self.store_visiting = None
        self.store_visiting_id = None
        self.cart = None
        self.cart_id = None
        
    def add_to_cart(self, item_id: int, quantity: int, menu_item: MenuItem) -> None:
        """Add an item to cart. Uses pre-fetched menu_item to avoid DB calls."""
        if self.store_visiting is None:
            raise ValueError("User must be visiting a store to add to cart")
        if quantity < 1:
            raise ValueError("Quantity must be positive and non-zero")
        if not menu_item.available:
            raise ValueError(f"MenuItem {menu_item.name} is currently unavailable")
        
        price = menu_item.price * quantity
        self.cart.total += price
        
        # merge quantities if this MenuItem is already in cart 
        for item in self.cart.items:
            if item.item_id == item_id:
                item.quantity += quantity
                item.price += price
                return
        
        # otherwise add new item to cart
        # Note: order_item_id and order_id will be set by the database
        self.cart.items.append(OrderItem(
            item_id=item_id,
            quantity=quantity,
            unit_price=menu_item.price,
            price=price
        ))
        
    def remove_from_cart(self, item_id: int, quantity: int = 1) -> None:
        """Remove items from cart."""
        if self.cart is None:
            raise ValueError("No active cart")
        if quantity < 1:
            raise ValueError("Quantity must be positive and non-zero")
        
        for item in self.cart.items:
            if item.item_id == item_id:
                
                if item.quantity < quantity:
                    raise ValueError(f"Cannot remove {quantity} items; only {item.quantity} in cart")
                
                if item.quantity == quantity:
                    self.cart.total -= item.price
                    self.cart.items.remove(item)
                    return
                
                price_delta = quantity * item.unit_price
                item.quantity -= quantity
                item.price -= price_delta
                self.cart.total -= price_delta
                return
        
        raise ValueError(f"MenuItem with item_id {item_id} not found in cart")

