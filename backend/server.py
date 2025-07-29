from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, date
from enum import Enum
import shutil

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Goods Receipt & Issue Management System")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Enums
class MovementType(str, Enum):
    GOODS_RECEIPT = "101"  # Goods Receipt
    GOODS_ISSUE_CONSUMPTION = "201"  # Goods Issue for Consumption
    GOODS_ISSUE_SALES = "601"  # Goods Issue for Sales
    STOCK_TRANSFER = "311"  # Stock Transfer
    RETURN_TO_VENDOR = "122"  # Return to Vendor
    RETURN_FROM_CUSTOMER = "161"  # Return from Customer

class InvoiceStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    BLOCKED = "blocked"
    POSTED = "posted"

class UnitOfMeasure(str, Enum):
    PC = "PC"  # Pieces
    KG = "KG"  # Kilograms
    LT = "LT"  # Liters
    MT = "MT"  # Meters
    EA = "EA"  # Each

# Models
class Location(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plant_code: str
    plant_name: str
    storage_location: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LocationCreate(BaseModel):
    plant_code: str
    plant_name: str
    storage_location: str
    description: Optional[str] = None

class Material(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    material_code: str
    material_description: str
    material_group: Optional[str] = None
    unit_of_measure: UnitOfMeasure
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MaterialCreate(BaseModel):
    material_code: str
    material_description: str
    material_group: Optional[str] = None
    unit_of_measure: UnitOfMeasure

class PurchaseOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    po_number: str
    vendor_code: str
    vendor_name: str
    po_date: date
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PurchaseOrderCreate(BaseModel):
    po_number: str
    vendor_code: str
    vendor_name: str
    po_date: date

class Invoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str
    vendor_code: str
    vendor_name: str
    invoice_date: date
    invoice_amount: float
    status: InvoiceStatus = InvoiceStatus.PENDING
    file_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InvoiceCreate(BaseModel):
    invoice_number: str
    vendor_code: str
    vendor_name: str
    invoice_date: date
    invoice_amount: float

class GoodsReceiptItem(BaseModel):
    material_id: str
    material_code: str
    quantity: float
    unit_price: Optional[float] = None
    total_amount: Optional[float] = None

class GoodsReceipt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_number: str = Field(default_factory=lambda: f"GR{str(uuid.uuid4())[:8].upper()}")
    po_id: Optional[str] = None
    po_number: Optional[str] = None
    invoice_id: Optional[str] = None
    vendor_code: str
    vendor_name: str
    location_id: str
    plant_code: str
    storage_location: str
    posting_date: date
    document_date: date
    items: List[GoodsReceiptItem]
    header_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GoodsReceiptCreate(BaseModel):
    po_id: Optional[str] = None
    po_number: Optional[str] = None
    invoice_id: Optional[str] = None
    vendor_code: str
    vendor_name: str
    location_id: str
    posting_date: date
    document_date: date
    items: List[GoodsReceiptItem]
    header_text: Optional[str] = None

class GoodsIssueItem(BaseModel):
    material_id: str
    material_code: str
    quantity: float
    cost_center: Optional[str] = None

class GoodsIssue(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_number: str = Field(default_factory=lambda: f"GI{str(uuid.uuid4())[:8].upper()}")
    movement_type: MovementType
    location_id: str
    plant_code: str
    storage_location: str
    posting_date: date
    document_date: date
    items: List[GoodsIssueItem]
    header_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GoodsIssueCreate(BaseModel):
    movement_type: MovementType
    location_id: str
    posting_date: date
    document_date: date
    items: List[GoodsIssueItem]
    header_text: Optional[str] = None

class StockMovement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    material_id: str
    material_code: str
    location_id: str
    plant_code: str
    storage_location: str
    movement_type: MovementType
    document_number: str
    quantity: float
    unit_of_measure: str
    posting_date: date
    reference_document: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CurrentStock(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    material_id: str
    material_code: str
    material_description: str
    location_id: str
    plant_code: str
    storage_location: str
    current_quantity: float
    unit_of_measure: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# Helper Functions
async def update_stock(material_id: str, location_id: str, quantity: float, movement_type: MovementType, unit_of_measure: str):
    """Update current stock based on movement"""
    material = await db.materials.find_one({"id": material_id})
    location = await db.locations.find_one({"id": location_id})
    
    if not material or not location:
        raise HTTPException(status_code=404, detail="Material or Location not found")
    
    # Find existing stock record
    stock_record = await db.current_stock.find_one({
        "material_id": material_id,
        "location_id": location_id
    })
    
    # Calculate new quantity based on movement type
    quantity_change = quantity
    if movement_type in [MovementType.GOODS_ISSUE_CONSUMPTION, MovementType.GOODS_ISSUE_SALES, MovementType.RETURN_TO_VENDOR]:
        quantity_change = -quantity
    
    if stock_record:
        new_quantity = stock_record["current_quantity"] + quantity_change
        await db.current_stock.update_one(
            {"id": stock_record["id"]},
            {"$set": {"current_quantity": new_quantity, "last_updated": datetime.utcnow()}}
        )
    else:
        # Create new stock record
        new_stock = CurrentStock(
            material_id=material_id,
            material_code=material["material_code"],
            material_description=material["material_description"],
            location_id=location_id,
            plant_code=location["plant_code"],
            storage_location=location["storage_location"],
            current_quantity=quantity_change,
            unit_of_measure=unit_of_measure
        )
        await db.current_stock.insert_one(new_stock.dict())

# API Routes

# Locations
@api_router.post("/locations", response_model=Location)
async def create_location(location: LocationCreate):
    location_obj = Location(**location.dict())
    await db.locations.insert_one(location_obj.dict())
    return location_obj

@api_router.get("/locations", response_model=List[Location])
async def get_locations():
    locations = await db.locations.find().to_list(1000)
    return [Location(**location) for location in locations]

# Materials
@api_router.post("/materials", response_model=Material)
async def create_material(material: MaterialCreate):
    # Check if material code already exists
    existing = await db.materials.find_one({"material_code": material.material_code})
    if existing:
        raise HTTPException(status_code=400, detail="Material code already exists")
    
    material_obj = Material(**material.dict())
    await db.materials.insert_one(material_obj.dict())
    return material_obj

@api_router.get("/materials", response_model=List[Material])
async def get_materials():
    materials = await db.materials.find().to_list(1000)
    return [Material(**material) for material in materials]

@api_router.get("/materials/{material_id}", response_model=Material)
async def get_material(material_id: str):
    material = await db.materials.find_one({"id": material_id})
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return Material(**material)

# Purchase Orders
@api_router.post("/purchase-orders", response_model=PurchaseOrder)
async def create_purchase_order(po: PurchaseOrderCreate):
    po_obj = PurchaseOrder(**po.dict())
    await db.purchase_orders.insert_one(po_obj.dict())
    return po_obj

@api_router.get("/purchase-orders", response_model=List[PurchaseOrder])
async def get_purchase_orders():
    pos = await db.purchase_orders.find().to_list(1000)
    return [PurchaseOrder(**po) for po in pos]

# Invoices
@api_router.post("/invoices", response_model=Invoice)
async def create_invoice(invoice: InvoiceCreate):
    invoice_obj = Invoice(**invoice.dict())
    await db.invoices.insert_one(invoice_obj.dict())
    return invoice_obj

@api_router.post("/invoices/{invoice_id}/upload")
async def upload_invoice_file(invoice_id: str, file: UploadFile = File(...)):
    invoice = await db.invoices.find_one({"id": invoice_id})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    file_path = UPLOAD_DIR / f"{invoice_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    await db.invoices.update_one(
        {"id": invoice_id},
        {"$set": {"file_path": str(file_path)}}
    )
    
    return {"message": "File uploaded successfully"}

@api_router.get("/invoices", response_model=List[Invoice])
async def get_invoices():
    invoices = await db.invoices.find().to_list(1000)
    return [Invoice(**invoice) for invoice in invoices]

@api_router.put("/invoices/{invoice_id}/status")
async def update_invoice_status(invoice_id: str, status: InvoiceStatus):
    result = await db.invoices.update_one(
        {"id": invoice_id},
        {"$set": {"status": status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"message": "Status updated successfully"}

# Goods Receipts
@api_router.post("/goods-receipts", response_model=GoodsReceipt)
async def create_goods_receipt(gr: GoodsReceiptCreate):
    # Get location details
    location = await db.locations.find_one({"id": gr.location_id})
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    gr_dict = gr.dict()
    gr_dict["plant_code"] = location["plant_code"]
    gr_dict["storage_location"] = location["storage_location"]
    
    gr_obj = GoodsReceipt(**gr_dict)
    await db.goods_receipts.insert_one(gr_obj.dict())
    
    # Update stock for each item
    for item in gr_obj.items:
        material = await db.materials.find_one({"id": item.material_id})
        if material:
            await update_stock(
                item.material_id, 
                gr.location_id, 
                item.quantity, 
                MovementType.GOODS_RECEIPT,
                material["unit_of_measure"]
            )
            
            # Create stock movement record
            movement = StockMovement(
                material_id=item.material_id,
                material_code=item.material_code,
                location_id=gr.location_id,
                plant_code=location["plant_code"],
                storage_location=location["storage_location"],
                movement_type=MovementType.GOODS_RECEIPT,
                document_number=gr_obj.document_number,
                quantity=item.quantity,
                unit_of_measure=material["unit_of_measure"],
                posting_date=gr.posting_date,
                reference_document=gr.po_number
            )
            await db.stock_movements.insert_one(movement.dict())
    
    return gr_obj

@api_router.get("/goods-receipts", response_model=List[GoodsReceipt])
async def get_goods_receipts():
    receipts = await db.goods_receipts.find().to_list(1000)
    return [GoodsReceipt(**receipt) for receipt in receipts]

# Goods Issues
@api_router.post("/goods-issues", response_model=GoodsIssue)
async def create_goods_issue(gi: GoodsIssueCreate):
    # Get location details
    location = await db.locations.find_one({"id": gi.location_id})
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    gi_dict = gi.dict()
    gi_dict["plant_code"] = location["plant_code"]
    gi_dict["storage_location"] = location["storage_location"]
    
    gi_obj = GoodsIssue(**gi_dict)
    await db.goods_issues.insert_one(gi_obj.dict())
    
    # Update stock for each item
    for item in gi_obj.items:
        material = await db.materials.find_one({"id": item.material_id})
        if material:
            await update_stock(
                item.material_id, 
                gi.location_id, 
                item.quantity, 
                gi.movement_type,
                material["unit_of_measure"]
            )
            
            # Create stock movement record
            movement = StockMovement(
                material_id=item.material_id,
                material_code=item.material_code,
                location_id=gi.location_id,
                plant_code=location["plant_code"],
                storage_location=location["storage_location"],
                movement_type=gi.movement_type,
                document_number=gi_obj.document_number,
                quantity=-item.quantity,  # Negative for issues
                unit_of_measure=material["unit_of_measure"],
                posting_date=gi.posting_date
            )
            await db.stock_movements.insert_one(movement.dict())
    
    return gi_obj

@api_router.get("/goods-issues", response_model=List[GoodsIssue])
async def get_goods_issues():
    issues = await db.goods_issues.find().to_list(1000)
    return [GoodsIssue(**issue) for issue in issues]

# Stock Overview
@api_router.get("/stock-overview", response_model=List[CurrentStock])
async def get_stock_overview():
    stock = await db.current_stock.find().to_list(1000)
    return [CurrentStock(**item) for item in stock]

@api_router.get("/stock-movements", response_model=List[StockMovement])
async def get_stock_movements():
    movements = await db.stock_movements.find().sort("created_at", -1).to_list(1000)
    return [StockMovement(**movement) for movement in movements]

# Dashboard Stats
@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    total_materials = await db.materials.count_documents({})
    total_locations = await db.locations.count_documents({})
    pending_invoices = await db.invoices.count_documents({"status": "pending"})
    total_receipts = await db.goods_receipts.count_documents({})
    total_issues = await db.goods_issues.count_documents({})
    
    return {
        "total_materials": total_materials,
        "total_locations": total_locations,
        "pending_invoices": pending_invoices,
        "total_receipts": total_receipts,
        "total_issues": total_issues
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()