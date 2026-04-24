"""
Repository layer - handles all database operations.
This layer abstracts SQLAlchemy details from business logic.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import models
import core


class StoreRepository:
    """Repository for Store database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, name: str) -> core.Store:
        """Create a new store in the database."""
        db_store = models.StoreModel(name=name)
        self.db.add(db_store)
        self.db.commit()
        self.db.refresh(db_store)
        return self._to_core_store(db_store)
    
    def delete(self, item_id: int):
        db_store = self.db.query(models.StoreModel).filter(
            models.StoreModel.store_id == item_id
        ).first()
        
        if db_store:
            self.db.delete(db_store)
            self.db.commit()
            return True
        return False
    
    def get_by_id(self, store_id: int) -> Optional[core.Store]:
        """Retrieve a store by ID with all menu items."""
        db_store = self.db.query(models.StoreModel).filter(
            models.StoreModel.store_id == store_id
        ).first()
        return self._to_core_store(db_store) if db_store else None
    
    def get_all(self) -> List[core.Store]:
        """Retrieve all stores."""
        db_stores = self.db.query(models.StoreModel).all()
        return [self._to_core_store(store) for store in db_stores]
    
    def _to_core_store(self, db_store: models.StoreModel) -> core.Store:
        """Convert SQLAlchemy StoreModel to core.Store."""
        if not db_store:
            return None
        menu_items = [
            core.MenuItem(
                item_id=item.item_id,
                store_id=item.store_id,
                name=item.name,
                price=item.price,
                description=item.description,
                category=item.category,
                available=item.available
            )
            for item in db_store.menu_items
        ]
        return core.Store(
            store_id=db_store.store_id,
            name=db_store.name,
            menu_items=menu_items
        )


class MenuItemRepository:
    """Repository for MenuItem database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, store_id: int, name: str, price: float, 
               description: str = "", category: str = "", available: bool = True) -> core.MenuItem:
        """Create a new menu item."""
        db_item = models.MenuItemModel(
            store_id=store_id,
            name=name,
            price=price,
            description=description,
            category=category,
            available=available
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return self._to_core_menu_item(db_item)
    
    def delete(self, item_id: int):
        db_item = self.db.query(models.MenuItemModel).filter(
            models.MenuItemModel.item_id == item_id
        ).first()
        
        if db_item:
            self.db.delete(db_item)
            self.db.commit()
            return True
        return False
        
    
    def get_by_id(self, item_id: int) -> Optional[core.MenuItem]:
        """Retrieve a menu item by ID."""
        db_item = self.db.query(models.MenuItemModel).filter(
            models.MenuItemModel.item_id == item_id
        ).first()
        return self._to_core_menu_item(db_item) if db_item else None
    
    def get_all_available(self) -> List[core.MenuItem]:
        """Get all available menu items from all stores."""
        db_items = self.db.query(models.MenuItemModel).filter(
            models.MenuItemModel.available == True
        ).all()
        return [self._to_core_menu_item(item) for item in db_items]
    
    def get_by_store(self, store_id: int, available_only: bool = True) -> List[core.MenuItem]:
        """Get menu items for a specific store."""
        query = self.db.query(models.MenuItemModel).filter(
            models.MenuItemModel.store_id == store_id
        )
        if available_only:
            query = query.filter(models.MenuItemModel.available == True)
        
        db_items = query.all()
        return [self._to_core_menu_item(item) for item in db_items]
    
    def _to_core_menu_item(self, db_item: models.MenuItemModel) -> core.MenuItem:
        """Convert SQLAlchemy MenuItemModel to core.MenuItem."""
        if not db_item:
            return None
        return core.MenuItem(
            item_id=db_item.item_id,
            store_id=db_item.store_id,
            name=db_item.name,
            price=db_item.price,
            description=db_item.description,
            category=db_item.category,
            available=db_item.available
        )


class UserRepository:
    """Repository for User database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, email: str, name: str) -> core.User:
        """Create a new user."""
        db_user = models.UserModel(email=email,name=name)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_core_user(db_user)
    
    def delete(self, user_id: int) -> bool:
        db_user = self.db.query(models.UserModel).filter(
            models.UserModel.user_id == user_id
        ).first()
        
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False
    
    def get_by_id(self, user_id: int) -> Optional[core.User]:
        """Retrieve a user by ID with cart and orders."""
        db_user = self.db.query(models.UserModel).filter(
            models.UserModel.user_id == user_id
        ).first()
        return self._to_core_user(db_user) if db_user else None
    
    def update_visiting_store(self, user_id: int, store_id: Optional[int]) -> core.User:
        """Update the store a user is currently visiting."""
        db_user = self.db.query(models.UserModel).filter(
            models.UserModel.user_id == user_id
        ).first()
        if db_user:
            db_user.store_visiting_id = store_id
            self.db.commit()
            self.db.refresh(db_user)
        return self._to_core_user(db_user) if db_user else None
    
    def clear_cart(self, user_id: int) -> None:
        """Clear the user's cart by setting cart_id to None."""
        db_user = self.db.query(models.UserModel).filter(
            models.UserModel.user_id == user_id
        ).first()
        if db_user:
            db_user.cart_id = None
            self.db.commit()
    
    def _to_core_user(self, db_user: models.UserModel) -> core.User:
        """Convert SQLAlchemy UserModel to core.User."""
        if not db_user:
            return None
        
        cart = None
        if db_user.cart:
            cart = self._db_order_to_core(db_user.cart)
        
        orders = [self._db_order_to_core(order) for order in db_user.orders]
        
        store_visiting = None
        if db_user.store_visiting:
            store_visiting = StoreRepository(self.db)._to_core_store(db_user.store_visiting)
        
        return core.User(
            user_id=db_user.user_id,
            email=db_user.email,
            name=db_user.name,
            store_visiting_id=db_user.store_visiting_id,
            cart_id=db_user.cart_id,
            store_visiting=store_visiting,
            cart=cart,
            orders=orders
        )
    
    def _db_order_to_core(self, db_order: models.OrderModel) -> core.Order:
        """Convert SQLAlchemy OrderModel to core.Order."""
        if not db_order:
            return None
        
        items = [
            core.OrderItem(
                order_item_id=item.order_item_id,
                order_id=item.order_id,
                item_id=item.item_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
            for item in db_order.items
        ]
        
        return core.Order(
            user_id=db_order.user_id,
            store_id=db_order.store_id,
            items=items,
            total=db_order.total,
            status=db_order.status
        )


class OrderRepository:
    """Repository for Order database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_cart(self, user_id: int, store_id: int) -> core.Order:
        """Create a new cart (order with IN_CART status)."""
        db_order = models.OrderModel(
            user_id=user_id,
            store_id=store_id,
            status=core.OrderStatus.IN_CART
        )
        self.db.add(db_order)
        self.db.commit()
        self.db.refresh(db_order)
        
        # Link cart to user
        db_user = self.db.query(models.UserModel).filter(
            models.UserModel.user_id == user_id
        ).first()
        if db_user:
            db_user.cart_id = db_order.order_id
            self.db.commit()
        
        return self._to_core_order(db_order)
    
    def add_item_to_order(self, order_id: int, item_id: int, 
                         quantity: int, unit_price: float, total_price: float) -> core.OrderItem:
        """Add or update an item in an order."""
        db_item = self.db.query(models.OrderItemModel).filter(
            models.OrderItemModel.order_id == order_id,
            models.OrderItemModel.item_id == item_id
        ).first()
        
        if db_item:
            db_item.quantity += quantity
            db_item.price += total_price
        else:
            db_item = models.OrderItemModel(
                order_id=order_id,
                item_id=item_id,
                quantity=quantity,
                unit_price=unit_price,
                price=total_price
            )
            self.db.add(db_item)
        
        self.db.commit()
        self.db.refresh(db_item)
        
        return core.OrderItem(
            order_item_id=db_item.order_item_id,
            order_id=db_item.order_id,
            item_id=db_item.item_id,
            quantity=db_item.quantity,
            unit_price=db_item.unit_price,
            price=db_item.price
        )
    
    def remove_item_from_order(self, order_id: int, item_id: int, quantity: int) -> None:
        """Remove items from an order."""
        db_item = self.db.query(models.OrderItemModel).filter(
            models.OrderItemModel.order_id == order_id,
            models.OrderItemModel.item_id == item_id
        ).first()
        
        if db_item:
            if db_item.quantity <= quantity:
                self.db.delete(db_item)
            else:
                db_item.quantity -= quantity
                db_item.price -= quantity * db_item.unit_price
            
            self.db.commit()
    
    def update_order_total(self, order_id: int, total: float) -> None:
        """Update order total."""
        db_order = self.db.query(models.OrderModel).filter(
            models.OrderModel.order_id == order_id
        ).first()
        if db_order:
            db_order.total = total
            self.db.commit()
    
    def get_by_id(self, order_id: int) -> Optional[core.Order]:
        """Retrieve an order by ID."""
        db_order = self.db.query(models.OrderModel).filter(
            models.OrderModel.order_id == order_id
        ).first()
        return self._to_core_order(db_order) if db_order else None
    
    def update_status(self, order_id: int, status: core.OrderStatus) -> core.Order:
        """Update order status."""
        db_order = self.db.query(models.OrderModel).filter(
            models.OrderModel.order_id == order_id
        ).first()
        if db_order:
            db_order.status = status
            self.db.commit()
            self.db.refresh(db_order)
        return self._to_core_order(db_order) if db_order else None
    
    def _to_core_order(self, db_order: models.OrderModel) -> core.Order:
        """Convert SQLAlchemy OrderModel to core.Order."""
        if not db_order:
            return None
        
        items = [
            core.OrderItem(
                order_item_id=item.order_item_id,
                order_id=item.order_id,
                item_id=item.item_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
            for item in db_order.items
        ]
        
        return core.Order(
            user_id=db_order.user_id,
            store_id=db_order.store_id,
            items=items,
            total=db_order.total,
            status=db_order.status
        )
