from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import schemas
from database import engine, get_db, Base
import services


app = FastAPI(
    title="Food Ordering API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def init_db():
    """Create all tables on startup if they don't already exist."""
    Base.metadata.create_all(bind=engine)


# ============= DEPENDENCY INJECTION =============

def get_store_service(db: Session = Depends(get_db)) -> services.StoreService:
    """Dependency to inject StoreService."""
    return services.StoreService(db)

def get_menu_service(db: Session = Depends(get_db)) -> services.MenuService:
    """Dependency to inject MenuService."""
    return services.MenuService(db)

def get_user_service(db: Session = Depends(get_db)) -> services.UserService:
    """Dependency to inject UserService."""
    return services.UserService(db)

def get_cart_service(db: Session = Depends(get_db)) -> services.CartService:
    """Dependency to inject CartService."""
    return services.CartService(db)


# ============= STORE ENDPOINTS =============

@app.post("/store", response_model=schemas.StoreResponse, tags=["stores"])
def create_store(item: schemas.StoreCreate, store_service: services.StoreService = Depends(get_store_service)):
    """Create a new store."""
    try:
        store = store_service.create_store(item.name)
        return store
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/store/{store_id}", response_model=schemas.DeleteResponse, tags=["stores"])
def delete_store(store_id: int, store_service: services.StoreService = Depends(get_store_service)):
    try:
        store_service.delete_store(store_id)
        return schemas.DeleteResponse(id=store_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Store not found")

@app.get("/stores", response_model=list[schemas.StoreResponse], tags=["stores"])
def get_stores(store_service: services.StoreService = Depends(get_store_service)):
    """Get all stores."""
    return store_service.list_stores()


@app.get("/stores/{store_id}", response_model=schemas.StoreDetailResponse, tags=["stores"])
def get_store_detail(store_id: int, store_service: services.StoreService = Depends(get_store_service)):
    """Get store details with menu items."""
    try:
        store = store_service.get_store(store_id)
        return store
    except ValueError:
        raise HTTPException(status_code=404, detail="Store not found")


# ============= MENU ENDPOINTS =============

@app.post("/menu", response_model=schemas.MenuItemResponse, status_code=201, tags=["menu"])
def create_menu_item(item: schemas.MenuItemCreate, store_service: services.StoreService = Depends(get_store_service)):
    """Create a new menu item for a store."""
    try:
        menu_item = store_service.add_menu_item(
            store_id=item.store_id,
            name=item.name,
            price=item.price,
            description=item.description,
            category=item.category,
            available=item.available
        )
        return menu_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/menu/{item_id}", response_model=schemas.DeleteResponse, tags=["menu"])
def delete_menu_item(item_id: int, menu_service: services.MenuService = Depends(get_menu_service)):
    try:
        menu_service.delete_menu_item(item_id)
        return schemas.DeleteResponse(id=item_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Menu item not found")

@app.get("/menu", response_model=list[schemas.MenuItemResponse], tags=["menu"])
def get_all_menu_items(menu_service: services.MenuService = Depends(get_menu_service)):
    """Return all available menu items from all stores."""
    return menu_service.list_available_items()


@app.get("/menu/{store_id}", response_model=list[schemas.MenuItemResponse], tags=["menu"])
def get_menu(store_id: int, menu_service: services.MenuService = Depends(get_menu_service)):
    """Return available menu items for a specific store."""
    try:
        return menu_service.list_store_menu(store_id, available_only=True)
    except ValueError:
        raise HTTPException(status_code=404, detail="Store not found")


# ============= USER ENDPOINTS =============

@app.post("/users", response_model=schemas.UserResponse, tags=["users"])
def create_user(user_create: schemas.UserCreate, user_service: services.UserService = Depends(get_user_service)):
    """Create a new user."""
    try:
        user = user_service.create_user(user_create.email, user_create.name)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/users/{user_id}", response_model=schemas.DeleteResponse, tags=["users"])
def delete_user(user_id: int, user_service: services.UserService = Depends(get_user_service)):
    try:
        user_service.delete_user(user_id)
        return schemas.DeleteResponse(id=user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")
    
@app.get("/users/{user_id}", response_model=schemas.UserDetailResponse, tags=["users"])
def get_user(user_id: int, user_service: services.UserService = Depends(get_user_service)):
    """Get user details with cart and order history."""
    try:
        return user_service.get_user(user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/users/{user_id}/visit-store/{store_id}", response_model=schemas.UserDetailResponse, tags=["users"])
def visit_store(user_id: int, store_id: int, user_service: services.UserService = Depends(get_user_service)):
    """User visits a store and creates a new cart."""
    try:
        return user_service.visit_store(user_id, store_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/users/{user_id}/leave-store", response_model=schemas.UserDetailResponse, tags=["users"])
def leave_store(user_id: int, user_service: services.UserService = Depends(get_user_service)):
    """User leaves current store."""
    try:
        return user_service.leave_store(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============= CART ENDPOINTS =============

@app.post("/users/{user_id}/cart/add-item", response_model=schemas.UserDetailResponse, tags=["cart"])
def add_to_cart(user_id: int, item: schemas.OrderItemCreate, cart_service: services.CartService = Depends(get_cart_service)):
    """Add an item to user's cart."""
    try:
        return cart_service.add_to_cart(user_id, item.item_id, item.quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.delete("/users/{user_id}/cart/rem-item", response_model=schemas.UserDetailResponse, tags=["cart"])
def remove_from_cart(user_id: int, item: schemas.OrderItemRemove, cart_service: services.CartService = Depends(get_cart_service)):
    """Add an item to user's cart."""
    try:
        return cart_service.remove_from_cart(user_id, item.item_id, item.quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/{user_id}/cart", response_model=schemas.OrderResponse, tags=["cart"])
def get_cart(user_id: int, cart_service: services.CartService = Depends(get_cart_service)):
    """Get user's current cart."""
    try:
        return cart_service.get_cart(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============= ORDER ENDPOINTS =============

@app.post("/users/{user_id}/checkout", response_model=schemas.OrderResponse, tags=["orders"])
def checkout(user_id: int, user_service: services.UserService = Depends(get_user_service)):
    """Checkout user's cart and convert to order."""
    try:
        return user_service.checkout(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/{user_id}/orders", response_model=list[schemas.OrderResponse], tags=["orders"])
def get_user_orders(user_id: int, user_service: services.UserService = Depends(get_user_service)):
    """Get all orders for a user."""
    try:
        return user_service.get_user_orders(user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
