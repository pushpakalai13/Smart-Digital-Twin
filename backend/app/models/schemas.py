from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any

# Auth Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "staff"  # admin or staff

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str

# Building Schemas
class BuildingSchema(BaseModel):
    building_id: str
    name: str
    category: str
    capacity: int
    floors: int
    area_sqft: float
    coordinates: Dict[str, float]
    status: str = "normal"  # normal, warning, critical

# Time-series schemas
class TimeSeriesRecord(BaseModel):
    building_id: str
    timestamp: str
    value: float
    unit: str
    source: str = "simulated"
    dataset_id: Optional[str] = None

# Alert Schemas
class AlertResolveRequest(BaseModel):
    resolution_notes: Optional[str] = "Resolved by user"

# Dataset Management Schemas
class DatasetItem(BaseModel):
    dataset_id: str
    filename: str
    dataset_type: str
    row_count: int
    source: str
    status: str
    created_at: str

class ColumnMappingRequest(BaseModel):
    mapping: Dict[str, str]

# Settings Schema
class DataSourceSetting(BaseModel):
    source: str = "simulated"  # "simulated" or "uploaded"
