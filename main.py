from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db

# This line ensures our database tables are created automatically when the app starts
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Management System")

# 1. Create: POST /item 
@app.post("/item", response_model=schemas.ItemResponse)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = models.InventoryItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# 2. List view: GET /items 
@app.get("/items", response_model=List[schemas.ItemResponse])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(models.InventoryItem).offset(skip).limit(limit).all()
    return items

# 3. Read: GET /item/{id} 
@app.get("/item/{id}", response_model=schemas.ItemResponse)
def read_item(id: str, db: Session = Depends(get_db)):
    item = db.query(models.InventoryItem).filter(models.InventoryItem.id == id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# 4. Update: PUT /item/{id} 
@app.put("/item/{id}", response_model=schemas.ItemResponse)
def update_item(id: str, item_update: schemas.ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(models.InventoryItem).filter(models.InventoryItem.id == id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item_update.model_dump().items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

# 5. Delete: DELETE /item/{id} 
@app.delete("/item/{id}")
def delete_item(id: str, db: Session = Depends(get_db)):
    db_item = db.query(models.InventoryItem).filter(models.InventoryItem.id == id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}