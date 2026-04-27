"""
Service layer - contains business logic orchestration.
Services use repositories for data access and core entities for business objects.
This layer is framework-agnostic and tests easily.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

import core
import repositories


class StoreService:
    """Business logic for stores."""
    
    def __init__(self, db: Session):
        self.db = db
        self.store_repo = repositories.StoreRepository(db)
        self.menu_repo = repositories.MenuItemRepository(db)
    
    def create_store(self, name: str) -> core.Store:
        """Create a new store."""
        if not name or not name.strip():
            raise ValueError("Store name cannot be empty")
        return self.store_repo.create(name)
    
    def delete_store(self, store_id: int) -> bool:
        success = self.store_repo.delete(store_id)
        if not success:
            raise ValueError(f"Store with id {store_id} not found")
        return success
    
    def get_store(self, store_id: int) -> core.Store:
        """Get store by ID."""
        store = self.store_repo.get_by_id(store_id)
        if not store:
            raise ValueError(f"Store with id {store_id} not found")
        return store
    
    def list_stores(self) -> List[core.Store]:
        """Get all stores."""
        return self.store_repo.get_all()
    
    def add_menu_item(self, store_id: int, name: str, price: float, 
                     description: str = "", category: str = "", 
                     available: bool = True) -> core.MenuItem:
        """Add a menu item to a store."""
        # Verify store exists
        store = self.store_repo.get_by_id(store_id)
        if not store:
            raise ValueError(f"Store with id {store_id} not found")
        
        # Validate price
        if price <= 0:
            raise ValueError("Price must be positive and non-zero")
        
        # Create menu item
        return self.menu_repo.create(
            store_id=store_id,
            name=name,
            price=price,
            description=description,
            category=category,
            available=available
        )


class MenuService:
    """Business logic for menu items."""
    
    def __init__(self, db: Session):
        self.db = db
        self.menu_repo = repositories.MenuItemRepository(db)
        self.store_repo = repositories.StoreRepository(db)
    
    def get_menu_item(self, item_id: int) -> core.MenuItem:
        """Get a menu item by ID."""
        item = self.menu_repo.get_by_id(item_id)
        if not item:
            raise ValueError(f"Menu item with id {item_id} not found")
        return item
    
    def delete_menu_item(self, item_id: int) -> bool:
        success = self.menu_repo.delete(item_id)
        if not success:
            raise ValueError(f"Menu item with id {item_id} not found")
        return success
    
    def list_available_items(self) -> List[core.MenuItem]:
        """Get all available menu items."""
        return self.menu_repo.get_all_available()
    
    def list_store_menu(self, store_id: int, available_only: bool = True) -> List[core.MenuItem]:
        """Get menu for a specific store."""
        # Verify store exists
        store = self.store_repo.get_by_id(store_id)
        if not store:
            raise ValueError(f"Store with id {store_id} not found")
        
        return self.menu_repo.get_by_store(store_id, available_only)


class CartService:
    """Business logic for shopping cart operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = repositories.UserRepository(db)
        self.store_repo = repositories.StoreRepository(db)
        self.menu_repo = repositories.MenuItemRepository(db)
        self.order_repo = repositories.OrderRepository(db)
    
    def add_to_cart(self, user_id: int, item_id: int, quantity: int = 1) -> core.User:
        """Add item to user's cart."""
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        
        # Get user
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        if not user.store_visiting:
            raise ValueError("User is not visiting any store")
        
        if not user.cart:
            raise ValueError("User has no active cart")
        
        # Get menu item
        menu_item = self.menu_repo.get_by_id(item_id)
        if not menu_item:
            raise ValueError(f"Menu item with id {item_id} not found")
        
        # Verify item belongs to the store user is visiting
        if menu_item.available is False:
            raise ValueError(f"Menu item '{menu_item.name}' is not available")
        
        # Add to cart in core logic
        user.add_to_cart(item_id, quantity, menu_item)
        
        # Persist to database
        price = menu_item.price * quantity
        self.order_repo.add_item_to_order(
            order_id=user.cart_id,
            item_id=item_id,
            quantity=quantity,
            unit_price=menu_item.price,
            total_price=price
        )
        
        # Update order total
        self.order_repo.update_order_total(user.cart_id, user.cart.total)
        self.db.commit()
        
        # Refresh to get updated state
        return self.user_repo.get_by_id(user_id)
    
    def remove_from_cart(self, user_id: int, item_id: int, quantity: int = 1) -> core.User:
        """Remove item from user's cart."""
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        
        # Get user
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        if not user.cart:
            raise ValueError("User has no active cart")
        
        # Remove from cart in core logic
        user.remove_from_cart(item_id, quantity)
        
        # Persist to database
        self.order_repo.remove_item_from_order(user.cart_id, item_id, quantity)
        self.order_repo.update_order_total(user.cart_id, user.cart.total)
        self.db.commit()
        
        # Refresh to get updated state
        return self.user_repo.get_by_id(user_id)
    
    def get_cart(self, user_id: int) -> core.Order:
        """Get user's current cart."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        if not user.cart:
            raise ValueError("User has no active cart")
        
        return user.cart


class UserService:
    """Business logic for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = repositories.UserRepository(db)
        self.store_repo = repositories.StoreRepository(db)
        self.order_repo = repositories.OrderRepository(db)
    
    def create_user(self, email: str, name: str) -> core.User:
        """Create a new user."""
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        if not email or not email.strip():
            raise ValueError("Email cannot be empty")
        
        return self.user_repo.create(email, name)
    
    def delete_user(self, user_id: int) -> bool:
        success = self.user_repo.delete(user_id)
        if not success:
            raise ValueError(f"User with id {user_id} not found")
        return success
    
    def get_user(self, user_id: int) -> core.User:
        """Get user by ID."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        return user
    
    def visit_store(self, user_id: int, store_id: int) -> core.User:
        """User visits a store."""
        # Get user
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        # Get store
        store = self.store_repo.get_by_id(store_id)
        if not store:
            raise ValueError(f"Store with id {store_id} not found")
        
        # Check if user is already visiting a store
        if user.store_visiting is not None:
            raise ValueError("User is already visiting a store. Leave first before visiting another.")
        
        # Create new cart in database
        new_cart = self.order_repo.create_cart(user_id, store_id)
        
        # Update user in core logic
        user.visit_store(store, new_cart)
        
        # Update store_visiting_id
        self.user_repo.update_visiting_store(user_id, store_id)
        self.db.commit()
        
        # Refresh to get updated state
        return self.user_repo.get_by_id(user_id)
    
    def leave_store(self, user_id: int) -> core.User:
        """User leaves current store."""
        # Get user
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        if user.store_visiting is None:
            raise ValueError("User is not currently visiting any store")
        
        # Update user in core logic
        user.leave_store()
        
        # Update database
        self.user_repo.update_visiting_store(user_id, None)
        self.db.commit()
        
        # Refresh to get updated state
        return self.user_repo.get_by_id(user_id)
    
    def checkout(self, user_id: int) -> core.Order:
        """User checks out their cart."""
        # Get user
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        if not user.cart:
            raise ValueError("User has no active cart")
        
        if not user.cart.items:
            raise ValueError("Cannot checkout with an empty cart")
        
        # Validate order against store items
        user.cart.validate_order(user.store_visiting)
        
        # Update order status to pending
        order = self.order_repo.update_status(user.cart_id, core.OrderStatus.PENDING)
        
        # Update user state - leave store and clear cart
        user.leave_store()
        self.user_repo.update_visiting_store(user_id, None)
        self.user_repo.clear_cart(user_id)
        self.db.commit()
        
        return order
    
    def get_user_orders(self, user_id: int) -> List[core.Order]:
        """Get all orders for a user."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        return user.orders

    def clear_user_orders(self, user_id: int) -> None:
        self.user_repo.clear_user_orders(user_id)