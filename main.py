from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware  # <-- ADD THIS IMPORT
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db
from pymongo import MongoClient
import os
import datetime
import asyncio

# --- SQL Database Setup ---
models.Base.metadata.create_all(bind=engine)

# --- MongoDB Setup ---
# Connect to the MongoDB container we defined in docker-compose.yml
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client["inventory_logs"]
mongo_collection = mongo_db["api_logs"] # Target collection specified in the instructions

app = FastAPI(title="Inventory Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, PUT, DELETE)
    allow_headers=["*"],  # Allows all headers
)

# --- Phase 3: MongoDB Logging Middleware ---
def map_method_to_action(method: str) -> str:
    """Helper to map HTTP methods to the required action strings."""
    mapping = {
        "POST": "ADD_INVENTORY",
        "GET": "GET/LIST_INVENTORY",
        "PUT": "EDIT_INVENTORY",
        "DELETE": "DELETE_INVENTORY"
    }
    return mapping.get(method, "UNKNOWN_ACTION")

@app.middleware("http")
async def log_requests_to_mongo(request: Request, call_next):
    # Let the API process the request first
    response = await call_next(request)
    
    # We only want to log API calls, not requests for the Swagger UI or favicon
    if request.url.path.startswith("/item"):
        # Construct the JSON document required by the instructions
        log_document = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "method": request.method,
            "endpoint": request.url.path,
            "action": map_method_to_action(request.method),
            "user_agent": request.headers.get("user-agent", "Unknown")
        }
        
        # Asynchronously insert the document so it does not block the API response
        asyncio.create_task(asyncio.to_thread(mongo_collection.insert_one, log_document))
        
    return response

# --- Phase 1: Core API Endpoints ---

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