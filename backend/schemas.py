from pydantic import BaseModel, Field
from typing import Optional

# MenuItem Schemas
class MenuItemBase(BaseModel):
    """Fields shared between create and read."""
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    category: Optional[str] = None
    available: bool = True


class MenuItemCreate(MenuItemBase):
    """Schema for POST /menu — what the client sends."""
    store_id: int


class MenuItemResponse(MenuItemBase):
    item_id: int
    store_id: int
    model_config = {"from_attributes": True}


# Store Schemas
class StoreCreate(BaseModel):
    name: str


class StoreResponse(BaseModel):
    store_id: int
    name: str
    model_config = {"from_attributes": True}


class StoreDetailResponse(StoreResponse):
    """Store with menu items included."""
    menu_items: list[MenuItemResponse] = []


# Order Item Schemas
class OrderItemCreate(BaseModel):
    item_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")


class OrderItemResponse(BaseModel):
    order_item_id: Optional[int] = None
    item_id: int
    quantity: int
    unit_price: float
    price: float
    model_config = {"from_attributes": True}


# Order Schemas
class OrderCreate(BaseModel):
    user_id: int
    store_id: int


class OrderResponse(BaseModel):
    user_id: int
    store_id: int
    total: float
    status: str
    items: list[OrderItemResponse] = []
    model_config = {"from_attributes": True}


# User Schemas
class UserCreate(BaseModel):
    email: str
    name: str


class UserResponse(BaseModel):
    user_id: Optional[int] = None
    email: str
    name: str
    model_config = {"from_attributes": True}


class UserDetailResponse(UserResponse):
    """User with cart and order history."""
    store_visiting_id: Optional[int] = None
    cart: Optional[OrderResponse] = None
    orders: list[OrderResponse] = []


class DeleteResponse(BaseModel):
    message: str = "Item deleted"
    id: int