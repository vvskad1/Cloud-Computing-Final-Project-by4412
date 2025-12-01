"""
Pydantic schemas for request/response validation in FixIt Tech Solutions API.
These schemas define the structure of data coming in and going out of API endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models import TicketStatus, DeviceType


# ============================================================================
# Customer Schemas
# ============================================================================

class CustomerBase(BaseModel):
    """
    Base schema for Customer with common fields.
    """
    name: str = Field(..., min_length=1, max_length=100, description="Customer's full name")
    email: EmailStr = Field(..., description="Customer's email address")
    phone: str = Field(..., min_length=10, max_length=20, description="Customer's phone number")


class CustomerCreate(CustomerBase):
    """
    Schema for creating a new customer.
    """
    pass


class CustomerResponse(CustomerBase):
    """
    Schema for customer data in API responses.
    """
    customer_id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Enables ORM mode for SQLAlchemy compatibility


# ============================================================================
# Device Schemas
# ============================================================================

class DeviceBase(BaseModel):
    """
    Base schema for Device with common fields.
    """
    device_type: DeviceType = Field(..., description="Type of device (phone, laptop, etc.)")
    brand: str = Field(..., min_length=1, max_length=50, description="Device brand/manufacturer")
    model: str = Field(..., min_length=1, max_length=100, description="Device model")
    issue_description: str = Field(..., min_length=10, max_length=1000, description="Description of the issue")
    serial_number: Optional[str] = Field(None, max_length=100, description="Device serial number (optional)")


class DeviceCreate(DeviceBase):
    """
    Schema for creating a new device entry.
    """
    pass


class DeviceResponse(DeviceBase):
    """
    Schema for device data in API responses.
    """
    device_id: int

    class Config:
        from_attributes = True


# ============================================================================
# Ticket Schemas
# ============================================================================

class TicketBase(BaseModel):
    """
    Base schema for Ticket with common fields.
    """
    priority: str = Field(default="normal", description="Ticket priority: low, normal, high, urgent")
    estimated_cost: Optional[float] = Field(None, ge=0, description="Estimated repair cost")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes or comments")


class TicketCreate(BaseModel):
    """
    Schema for creating a new repair ticket.
    Includes customer and device information inline.
    """
    # Customer information
    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_email: EmailStr
    customer_phone: str = Field(..., min_length=10, max_length=20)
    
    # Device information
    device_type: DeviceType
    device_brand: str = Field(..., min_length=1, max_length=50)
    device_model: str = Field(..., min_length=1, max_length=100)
    issue_description: str = Field(..., min_length=10, max_length=1000)
    serial_number: Optional[str] = Field(None, max_length=100)
    
    # Ticket information
    priority: str = Field(default="normal")
    estimated_cost: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)


class TicketUpdate(BaseModel):
    """
    Schema for updating an existing ticket.
    All fields are optional to allow partial updates.
    """
    status: Optional[TicketStatus] = None
    priority: Optional[str] = None
    estimated_cost: Optional[float] = Field(None, ge=0)
    actual_cost: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)


class TicketResponse(TicketBase):
    """
    Schema for ticket data in API responses.
    Includes full customer and device information.
    """
    ticket_id: int
    status: TicketStatus
    customer: CustomerResponse
    device: DeviceResponse
    actual_cost: Optional[float]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class TicketSummary(BaseModel):
    """
    Lightweight schema for listing tickets (without full nested data).
    """
    ticket_id: int
    status: TicketStatus
    customer_name: str
    customer_email: str
    device_type: DeviceType
    device_brand: str
    device_model: str
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Generic Response Schemas
# ============================================================================

class MessageResponse(BaseModel):
    """
    Generic schema for simple message responses.
    """
    message: str
    detail: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """
    Schema for health check endpoint response.
    """
    status: str
    timestamp: str
    service: str


# ============================================================================
# Ticket History Schemas
# ============================================================================

class TicketHistoryResponse(BaseModel):
    """
    Schema for ticket history entries.
    """
    history_id: int
    ticket_id: int
    old_status: Optional[TicketStatus]
    new_status: TicketStatus
    changed_by: Optional[str]
    notes: Optional[str]
    changed_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Admin Dashboard Schemas
# ============================================================================

class DashboardStatistics(BaseModel):
    """
    Schema for comprehensive admin dashboard statistics.
    """
    total_tickets: int
    total_customers: int
    average_estimated_cost: float
    recent_tickets_7_days: int
    tickets_by_priority: dict
    tickets_by_device_type: dict


class BulkStatusUpdate(BaseModel):
    """
    Schema for bulk ticket status updates.
    """
    ticket_ids: List[int] = Field(..., min_length=1, description="List of ticket IDs to update")
    new_status: TicketStatus = Field(..., description="New status to apply to all tickets")
    changed_by: Optional[str] = Field(None, description="Who is making the change")


class BulkUpdateResponse(BaseModel):
    """
    Response schema for bulk update operations.
    """
    updated_count: int
    requested_count: int
    success: bool
    message: str


# ============================================================================
# Authentication Schemas
# ============================================================================

class LoginRequest(BaseModel):
    """
    Schema for admin login request.
    """
    username: str = Field(..., min_length=3, max_length=50, description="Admin username")
    password: str = Field(..., min_length=6, description="Admin password")


class TokenResponse(BaseModel):
    """
    Schema for authentication token response.
    """
    access_token: str
    token_type: str = "bearer"
    admin_username: str
    admin_full_name: str


class AdminResponse(BaseModel):
    """
    Schema for admin user data in API responses.
    """
    admin_id: int
    username: str
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# Customer Authentication Schemas
# ============================================================================

class CustomerSignupRequest(BaseModel):
    """
    Schema for customer signup/registration.
    """
    name: str = Field(..., min_length=1, max_length=100, description="Customer's full name")
    email: EmailStr = Field(..., description="Customer's email address")
    phone: str = Field(..., min_length=10, max_length=20, description="Customer's phone number")
    password: str = Field(..., min_length=6, max_length=50, description="Customer password")


class CustomerLoginRequest(BaseModel):
    """
    Schema for customer login request.
    """
    email: EmailStr = Field(..., description="Customer's email address")
    password: str = Field(..., min_length=6, description="Customer password")


class CustomerTokenResponse(BaseModel):
    """
    Schema for customer authentication token response.
    """
    access_token: str
    token_type: str = "bearer"
    customer_id: int
    customer_name: str
    customer_email: str


class CustomerProfileResponse(BaseModel):
    """
    Schema for customer profile data.
    """
    customer_id: int
    name: str
    email: EmailStr
    phone: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    unread_notifications: int = 0

    class Config:
        from_attributes = True


# ============================================================================
# Notification Schemas
# ============================================================================

class NotificationResponse(BaseModel):
    """
    Schema for notification data in API responses.
    """
    notification_id: int
    ticket_id: int
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# AI Chatbot Schemas
# ============================================================================

class ChatbotRequest(BaseModel):
    """
    Schema for chatbot message request.
    """
    message: str = Field(..., min_length=1, max_length=1000)
    conversation_history: Optional[List[dict]] = Field(default=None)


class ChatbotResponse(BaseModel):
    """
    Schema for chatbot response.
    """
    response: str
    timestamp: datetime
