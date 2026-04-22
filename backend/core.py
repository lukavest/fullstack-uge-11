# from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from typing import Optional
from copy import deepcopy

@dataclass
class MenuItem:
    item_id:        int
    name:           str
    price:          float
    description:    Optional[str] = None
    category:       Optional[str] = None
    available:      bool = True
    
    def __str__(self):
        return f"{self.item_id:02d} {self.name:<15} ${self.price:<5} {'not' if not self.available else ''} available"

@dataclass
class Menu:
    store_id: int     # mirrors store id
    items: list[MenuItem] = field(default_factory=list)

@dataclass
class OrderItem:
    item_id:        int
    quantity:       int
    unit_price:     float
    price:          float
    
    
@dataclass
class Order:
    user_id:        int
    store_id:       int
    items:          list[OrderItem] = field(default_factory=list)
    total:          float = 0.0
    status:         str = "in cart"  # pending | confirmed | preparing | ready | delivered


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
    
    def get_item_by_id(self, item_id: int) -> MenuItem:
        for item in self.menu.items:
            if item.item_id == item_id:
                return item
        return None
    
    def add_menu_item(self, menu_item: MenuItem):
        if menu_item.price <= 0.0:
            raise ValueError("Price must be positive and non-zero")
        
        item = self.get_item_by_id(menu_item.item_id)
        if item is not None:
            raise ValueError(f"MenuItem with item_id {menu_item.item_id} already exists in menu: {item}")
        
        self.menu.items.append(menu_item)
        
    def remove_menu_item(self,item_id):
        for item in self.menu.items:
            if item.item_id == item_id :
                self.menu.items.remove(item)
                return
        raise ValueError(f"MenuItem with item_id {item_id} not found, could not remove from menu")
        
    def validate_order(self, order:Order):
        total = 0.0
        for item in order.items:
            menu_item = self.get_item_by_id(item.item_id)
            if menu_item is None:
                raise ValueError(f"MenuItem with item_id {item.item_id} no longer exists in menu")
            if not menu_item.available:
                raise ValueError(f"MenuItem with item_id {item.item_id} no longer available")
            total += menu_item.price * item.quantity
        
        if total != order.total:
            raise ValueError(f"Order total mismatch: {order.total} in cart vs. {total} upon validation")
        

@dataclass
class User:
    user_id:        int
    name:           str
    store_visiting: Optional[Store] = None
    cart:           Optional[Order] = None
    orders:         list[Order] = field(default_factory=list)
        
    def __str__(self):
        return f"User(id={self.user_id}, name='{self.name}', cart={self.cart}, orders={self.orders})"
    
    def visit_store(self, store: Store):
        if self.store_visiting is not None:
            raise ValueError(f"Cannot visit a new store before leaving the current store")
        self.store_visiting = store
        self.cart = Order(user_id=self.user_id,store_id=store.store_id)
        
    # possibly retire this and implicitly leave when visiting new store?
    def leave_store(self):
        self.store_visiting = None
        self.cart = None
        
    # use negatives to remove from cart?
    def add_to_cart(self, item_id: int, quantity: int = 1):
        if self.store_visiting is None:
            raise ValueError("User must be visiting Store to add to cart")
        if quantity < 1:
            raise ValueError("Quantity must be positive and non-zero")
        
        menu_item = self.store_visiting.get_item_by_id(item_id)
        if menu_item is None:
            raise ValueError(f"MenuItem with item_id {item_id} does not exist in {self.store_visiting.name}'s menu.")
        if not menu_item.available:
            raise ValueError(f"MenuItem {menu_item.name} is currently unavailable")
        
        price = menu_item.price * quantity
        self.cart.total += price # change pricing system later
        
        # merge quantities if this MenuItem is already in cart 
        for item in self.cart.items:
            if item.item_id == item_id:
                item.quantity += quantity
                item.price += price
                return
        # otherwise add new item to cart
        self.cart.items.append(OrderItem(item_id=item_id, quantity=quantity, unit_price=menu_item.price, price=price))
        
    def remove_from_cart(self, item_id: int, quantity: int = 1):
        if self.store_visiting is None:
            raise ValueError("User must be visiting Store to modify to cart")
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
        
        
    def place_order(self):
        if self.store_visiting is None:
            raise ValueError("Not visiting store, cannot place order")
        
        self.store_visiting.validate_order(self.cart)
        
        # Create a new order from the user's cart
        order = deepcopy(self.cart)
        order.status = "pending"
        self.store_visiting.orders.append(order)
        self.orders.append(order)
        
        self.cart.items.clear()
        self.cart.total = 0.0
        
