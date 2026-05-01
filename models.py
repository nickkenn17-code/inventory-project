from sqlalchemy import Column, String, Integer
from database import Base
import uuid

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    # Fulfilling the required fields from the project brief
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True) # Unique ID (UUID) [cite: 20]
    short_name = Column(String, index=True, nullable=False)                              # Short Name (VARCHAR) [cite: 21]
    description = Column(String, nullable=True)                                          # Description (VARCHAR) [cite: 23]
    price = Column(Integer, nullable=False)                                              # Price in IDR (INTEGER) [cite: 24]
    amount = Column(Integer, nullable=False, default=0)                                  # Amount of stock (INTEGER) [cite: 25]