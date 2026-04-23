from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import uvicorn
import schemas
import core
from database import engine, get_db, Base

app = FastAPI(
    title="Food Ordering API (Unified Model)",
    description="Backend for food ordering demo app with unified core module.",
)

@app.on_event("startup")
def init_db():
    """Create all tables on startup if they don't already exist."""
    Base.metadata.create_all(bind=engine)


# ============= STORE ENDPOINTS =============

@app.post("/store", response_model=schemas.StoreResponse, tags=["stores"])
def create_store(item: schemas.StoreCreate, db: Session = Depends(get_db)):
    """Create a new store."""
    store = core.Store(name=item.name)
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


@app.get("/stores", response_model=list[schemas.StoreResponse], tags=["stores"])
def get_stores(db: Session = Depends(get_db)):
    """Get all stores."""
    return db.query(core.Store).all()


@app.get("/stores/{store_id}", response_model=schemas.StoreDetailResponse, tags=["stores"])
def get_store_detail(store_id: int, db: Session = Depends(get_db)):
    """Get store details with menu items."""
    store = db.query(core.Store).filter(core.Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


# ============= MENU ENDPOINTS =============

@app.post("/menu", response_model=schemas.MenuItemResponse, status_code=201, tags=["menu"])
def create_menu_item(item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    """Create a new menu item for a store."""
    store = db.query(core.Store).filter(core.Store.store_id == item.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    menu_item = core.MenuItem(
        store_id=item.store_id,
        name=item.name,
        price=item.price,
        description=item.description,
        category=item.category,
        available=item.available
    )
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)
    return menu_item


@app.get("/menu", response_model=list[schemas.MenuItemResponse], tags=["menu"])
def get_all_menu_items(db: Session = Depends(get_db)):
    """Return all available menu items from all stores."""
    return db.query(core.MenuItem).filter(core.MenuItem.available == True).all()


@app.get("/menu/{store_id}", response_model=list[schemas.MenuItemResponse], tags=["menu"])
def get_menu(store_id: int, db: Session = Depends(get_db)):
    """Return available menu items for a specific store."""
    store = db.query(core.Store).filter(core.Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    return db.query(core.MenuItem).filter(
        core.MenuItem.store_id == store_id,
        core.MenuItem.available == True
    ).all()


# ============= USER ENDPOINTS =============

@app.post("/users", response_model=schemas.UserResponse, tags=["users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    new_user = core.User(name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users/{user_id}", response_model=schemas.UserDetailResponse, tags=["users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user details with cart and order history."""
    user = db.query(core.User).filter(core.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users/{user_id}/visit-store/{store_id}", response_model=schemas.UserDetailResponse, tags=["users"])
def visit_store(user_id: int, store_id: int, db: Session = Depends(get_db)):
    """User visits a store and creates a new cart."""
    user = db.query(core.User).filter(core.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    store = db.query(core.Store).filter(core.Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    try:
        user.visit_store(store, db)
        db.commit()
        db.refresh(user)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/users/{user_id}/leave-store", response_model=schemas.UserDetailResponse, tags=["users"])
def leave_store(user_id: int, db: Session = Depends(get_db)):
    """User leaves current store."""
    user = db.query(core.User).filter(core.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        user.leave_store()
        db.commit()
        db.refresh(user)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============= CART ENDPOINTS =============

@app.post("/users/{user_id}/cart/add-item", response_model=schemas.UserDetailResponse, tags=["cart"])
def add_to_cart(user_id: int, item: schemas.OrderItemCreate, db: Session = Depends(get_db)):
    """Add an item to user's cart."""
    user = db.query(core.User).filter(core.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        user.add_to_cart(item.item_id, item.quantity, db)
        db.commit()
        db.refresh(user)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/{user_id}/cart", response_model=schemas.OrderResponse, tags=["cart"])
def get_cart(user_id: int, db: Session = Depends(get_db)):
    """Get user's current cart."""
    user = db.query(core.User).filter(core.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.cart:
        raise HTTPException(status_code=404, detail="No active cart")
    
    return user.cart


# ============= ORDER ENDPOINTS =============

@app.post("/users/{user_id}/checkout", response_model=schemas.OrderResponse, tags=["orders"])
def checkout(user_id: int, db: Session = Depends(get_db)):
    """Checkout user's cart and convert to order."""
    user = db.query(core.User).filter(core.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        order = user.checkout()
        db.commit()
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/{user_id}/orders", response_model=list[schemas.OrderResponse], tags=["orders"])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    """Get all orders for a user."""
    user = db.query(core.User).filter(core.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.orders


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
