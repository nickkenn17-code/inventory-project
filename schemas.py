from pydantic import BaseModel, Field
from typing import Optional

# Schema for what the user sends when creating/updating an item
class ItemBase(BaseModel):
    short_name: str
    description: Optional[str] = None
    price: int = Field(..., description="The price of the item in IDR")
    amount: int

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

# Schema for what the API sends back to the user
class ItemResponse(ItemBase):
    id: str

    class Config:
        from_attributes = True # Allows Pydantic to read SQLAlchemy models