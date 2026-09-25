from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from enum import Enum

class FieldStatusEnum(str, Enum):
    UNKNOWN = "unknown"
    CAPTURED = "captured"
    NEEDS_CONFIRMATION = "needs_confirmation"
    CONFIRMED = "confirmed"
    CONFLICTED = "conflicted"

class FieldState(BaseModel):
    field_name: str
    value: Any = None
    status: FieldStatusEnum = FieldStatusEnum.UNKNOWN
    confidence: float = 1.0
    notes: Optional[str] = None

class ExecutorSchema(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None

class WishesStateData(BaseModel):
    full_name: Optional[str] = None
    home_address: Optional[str] = None
    covers_worldwide_assets: Optional[bool] = None
    has_children: Optional[bool] = None
    children: List[str] = []
    executor: Optional[ExecutorSchema] = Field(default_factory=ExecutorSchema)
    specific_gifts: List[str] = []
    additional_wishes: Optional[str] = None

class StructuredStateResponse(BaseModel):
    session_id: str
    data: WishesStateData
    statuses: Dict[str, FieldStatusEnum]
    completion_percentage: float
    confirmed_count: int
    total_required_count: int

class MessageCreateRequest(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str

class SessionResponse(BaseModel):
    id: str
    created_at: str
    updated_at: str
    messages: List[MessageResponse] = []
    structured_state: StructuredStateResponse

class ConflictItem(BaseModel):
    id: str
    field: str
    old_value: Optional[str]
    new_value: Optional[str]
    status: str
    created_at: str

class ConflictResolveRequest(BaseModel):
    choice: str  # "keep_old" or "use_new" or custom value string

class DirectStateUpdateRequest(BaseModel):
    field: str
    value: Any

class DocumentResponse(BaseModel):
    session_id: str
    disclaimer: str = "FICTIONAL DOCUMENT — NOT LEGAL ADVICE"
    document_text: str
    generated_at: str

class EmailSendRequest(BaseModel):
    email: str

class ExtractedInformation(BaseModel):
    full_name: Optional[str] = None
    home_address: Optional[str] = None
    covers_worldwide_assets: Optional[bool] = None
    has_children: Optional[bool] = None
    children: Optional[List[str]] = None
    executor_name: Optional[str] = None
    executor_relationship: Optional[str] = None
    specific_gifts: Optional[List[str]] = None
    additional_wishes: Optional[str] = None
    certainty: str = "certain"  # "certain", "uncertain", "ambiguous"
    unclear_fields: List[str] = []
