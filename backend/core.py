# from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from typing import Optional
from copy import deepcopy

# TODO encapsulate functions as methods

@dataclass
class MenuItem:
    item_id:        int
    name:           str
    price:          float
    description:    Optional[str] = None
    category:       Optional[str] = None
    available:      bool = True

@dataclass
class Menu:
    store_id: int     # mirrors store id
    items: list[MenuItem] = field(default_factory=list)

@dataclass
class OrderItem:
    item_id:        int
    quantity:       int
    
@dataclass
class Order:
    user_id:        int
    store_id:       int
    items:          list[OrderItem] = field(default_factory=list)
    total:          float = 0.0
    status:         str = "in cart"  # pending | confirmed | preparing | ready | delivered

@dataclass
class User:
    user_id:        int
    name:           str
    # cart:           Order = field(init=False)
    cart:           Optional[Order] = None
    orders:         list[Order] = field(default_factory=list)
    # def __post_init__(self):
    #     self.cart = Order(user_id=self.user_id)
        
    def __str__(self):
        return f"User(id={self.user_id}, name='{self.name}', cart={self.cart}, orders={self.orders})"

@dataclass
class Store:
    store_id:       int
    name:           str
    menu:           Menu = field(init=False)
    orders:         list[Order] = field(default_factory=list)
    
    def __post_init__(self):
        self.menu = Menu(store_id=self.store_id)
        
    def __str__(self):
        return f"Store(id={self.store_id}, name='{self.name}', menu={self.menu}, orders={self.orders})"
    

# TODO remove_menu_item() remove_from_cart()?

# TODO validate price >= 0, handle collisions in menu
def add_menu_item(store: Store, menu_item: MenuItem):
    store.menu.items.append(menu_item)
    
def get_item_by_id(menu: Menu, item_id: int) -> MenuItem:
    for item in menu.items:
        if item.item_id == item_id:
            return item
    raise ValueError(f"MenuItem with id {item_id} not found")

def leave_store(user: User, store: Store):
    user.cart = None

def visit_store(user: User, store: Store):
    if user.cart != None:
        raise ValueError(f"Cannot visit a new store before leaving the current store")
    user.cart = Order(user_id=user.user_id,store_id=store.store_id)

# TODO  merge multiple OrderItems with same item_id
#       validate quantity >= 1 or use negatives to remove from cart
#       validate item exists in store
def add_to_cart(user: User, store: Store, item_id: int, quantity: int):
    if user.cart == None:
        raise ValueError("User must be visiting Store to add to cart")
    
    menu_item = GetMenuItemById(store.menu, item_id)
    if user.cart.store_id != store.store_id:
        raise ValueError(f"Can only add items from the store being visited. Expected store_id {user.cart.store_id}, got {store.store_id}")
    
    if not menu_item.available:
        raise ValueError(f"MenuItem {menu_item.name} is currently unavailable")
    
    user.cart.items.append(OrderItem(item_id=item_id, quantity=quantity))
    user.cart.total += menu_item.price * quantity

def place_order(user: User, store: Store):
    # Create a new order from the user's cart
    order = deepcopy(user.cart)
    order.status = "pending"
    store.orders.append(order)
    user.orders.append(order)
    
    user.cart.items.clear()
    user.cart.total = 0.0
    