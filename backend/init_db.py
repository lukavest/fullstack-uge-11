"""
Database initialization script - Creates tables and populates test data if none exist.
This script runs on application startup.
"""

import sys
import os

# Add the backend directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal, Base
from models import StoreModel, MenuItemModel, UserModel
import sqlalchemy as sa


def init_db():
    """Initialize database with tables and test data if empty."""
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if database already has stores
        store_count = db.query(StoreModel).count()
        
        if store_count == 0:
            print("Database is empty. Initializing with test data...")
            
            # Create test stores
            stores_data = [
                {"name": "Grill Chef Main"},
                {"name": "Grill Chef Downtown"},
            ]
            
            stores = []
            for store_data in stores_data:
                store = StoreModel(name=store_data["name"])
                db.add(store)
                db.flush()  # Get the store_id
                stores.append(store)
                print(f"✓ Created store: {store.name}")
            
            db.commit()
            
            # Create menu items for each store
            menu_data = {
                "Grill Chef Main": [
                    {"name": "Grilled Chicken Souvlaki", "price": 12.99, "description": "Tender grilled chicken skewers with yogurt sauce", "category": "Main", "available": True, "emoji": "🍗"},
                    {"name": "Lamb Kofta", "price": 14.99, "description": "Seasoned ground lamb skewers", "category": "Main", "available": True, "emoji": "🥩"},
                    {"name": "Grilled Fish", "price": 15.99, "description": "Fresh grilled Mediterranean fish", "category": "Main", "available": True, "emoji": "🐟"},
                    {"name": "Greek Salad", "price": 8.99, "description": "Tomatoes, cucumbers, olives, and feta cheese", "category": "Salad", "available": True, "emoji": "🥗"},
                    {"name": "Hummus", "price": 5.99, "description": "Creamy chickpea dip", "category": "Appetizer", "available": True, "emoji": "🫘"},
                    {"name": "Tzatziki", "price": 5.99, "description": "Yogurt and cucumber dip", "category": "Appetizer", "available": True, "emoji": "🥒"},
                    {"name": "Grilled Vegetables", "price": 7.99, "description": "Assorted grilled seasonal vegetables", "category": "Side", "available": True, "emoji": "🥦"},
                    {"name": "Falafel", "price": 6.99, "description": "Fried chickpea fritters", "category": "Appetizer", "available": True, "emoji": "🧆"},
                ],
                "Grill Chef Downtown": [
                    {"name": "Beef Steak", "price": 16.99, "description": "Grilled ribeye steak", "category": "Main", "available": True, "emoji": "🥩"},
                    {"name": "Shrimp Saganaki", "price": 13.99, "description": "Grilled shrimp with cheese", "category": "Main", "available": True, "emoji": "🍤"},
                    {"name": "Mixed Grill Platter", "price": 18.99, "description": "Combination of meats and seafood", "category": "Main", "available": True, "emoji": "🍽️"},
                    {"name": "Mediterranean Pasta", "price": 10.99, "description": "Pasta with Mediterranean vegetables", "category": "Main", "available": True, "emoji": "🍝"},
                    {"name": "Caprese Salad", "price": 9.99, "description": "Tomato, mozzarella, basil, and olive oil", "category": "Salad", "available": True, "emoji": "🥗"},
                    {"name": "Dolmades", "price": 7.99, "description": "Grape leaves stuffed with rice", "category": "Appetizer", "available": True, "emoji": "🌿"},
                    {"name": "Saganaki", "price": 8.99, "description": "Fried cheese", "category": "Appetizer", "available": True, "emoji": "🧀"},
                    {"name": "Grilled Octopus", "price": 14.99, "description": "Tender grilled octopus", "category": "Main", "available": True, "emoji": "🐙"},
                ]
            }
            
            for store in stores:
                store_menu = menu_data.get(store.name, [])
                for item_data in store_menu:
                    menu_item = MenuItemModel(
                        store_id=store.store_id,
                        name=item_data["name"],
                        price=item_data["price"],
                        emoji=item_data["emoji"],
                        description=item_data["description"],
                        category=item_data["category"],
                        available=item_data["available"]
                    )
                    db.add(menu_item)
                print(f"✓ Added {len(store_menu)} menu items to {store.name}")
            
            db.commit()
            
            # Create test users
            users_data = [
                {"email": "john@example.com", "name": "John Doe"},
                {"email": "jane@example.com", "name": "Jane Smith"},
                {"email": "test@example.com", "name": "Test User"},
            ]
            
            for user_data in users_data:
                user = UserModel(
                    email=user_data["email"],
                    name=user_data["name"]
                )
                db.add(user)
                print(f"✓ Created user: {user_data['name']} ({user_data['email']})")
            
            db.commit()
            
            print("\n✅ Database initialized successfully with test data!")
            print(f"   - {len(stores)} stores created")
            print(f"   - {len(users_data)} users created")
            total_items = sum(len(menu_data.get(store.name, [])) for store in stores)
            print(f"   - {total_items} menu items created")
        else:
            print(f"✅ Database already initialized with {store_count} store(s). Skipping initialization.")
    
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
