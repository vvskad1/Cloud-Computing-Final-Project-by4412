"""
SQLAlchemy ORM models for FixIt Tech Solutions.
These models define the database schema and relationships.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from app.database import Base


class TicketStatus(str, Enum):
    """
    Possible states of a repair ticket throughout its lifecycle.
    """
    PENDING = "pending"              # Initial state when ticket is created
    DIAGNOSED = "diagnosed"          # Issue has been identified
    IN_PROGRESS = "in_progress"      # Repair work is ongoing
    WAITING_PARTS = "waiting_parts"  # Waiting for replacement parts
    COMPLETED = "completed"          # Repair finished
    READY_PICKUP = "ready_pickup"    # Device ready for customer pickup
    DELIVERED = "delivered"          # Device returned to customer
    CANCELLED = "cancelled"          # Ticket cancelled by customer or admin


class DeviceType(str, Enum):
    """
    Types of devices that can be repaired.
    """
    PHONE = "phone"
    LAPTOP = "laptop"
    TABLET = "tablet"
    DESKTOP = "desktop"
    WATCH = "watch"
    OTHER = "other"


class Customer(Base):
    """
    Customer table - stores customer information and authentication.
    """
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for backward compatibility
    is_active = Column(Integer, default=1, nullable=False)  # 1 = active, 0 = inactive
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relationship: One customer can have many tickets
    tickets = relationship("Ticket", back_populates="customer")
    notifications = relationship("CustomerNotification", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer {self.customer_id}: {self.name} ({self.email})>"


class Device(Base):
    """
    Device table - stores information about devices brought in for repair.
    """
    __tablename__ = "devices"

    device_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    device_type = Column(SQLEnum(DeviceType), nullable=False)
    brand = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    issue_description = Column(Text, nullable=False)
    serial_number = Column(String(100), nullable=True)

    # Relationship: One device can have many tickets (repair history)
    tickets = relationship("Ticket", back_populates="device")

    def __repr__(self):
        return f"<Device {self.device_id}: {self.brand} {self.model} ({self.device_type})>"


class Ticket(Base):
    """
    Ticket table - represents a repair ticket/booking.
    This is the main entity that tracks the entire repair process.
    """
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.device_id"), nullable=False)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.PENDING, nullable=False, index=True)
    priority = Column(String(20), default="normal", nullable=False)
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="tickets")
    device = relationship("Device", back_populates="tickets")
    history = relationship("TicketHistory", back_populates="ticket", order_by="TicketHistory.changed_at.desc()")

    def __repr__(self):
        return f"<Ticket {self.ticket_id}: {self.status} - Customer ID: {self.customer_id}>"


class TicketHistory(Base):
    """
    Ticket history table - tracks all status changes and updates to tickets.
    Provides an audit trail for ticket lifecycle.
    """
    __tablename__ = "ticket_history"

    history_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"), nullable=False)
    old_status = Column(SQLEnum(TicketStatus), nullable=True)
    new_status = Column(SQLEnum(TicketStatus), nullable=False)
    changed_by = Column(String(100), nullable=True)  # For future auth: admin/customer name
    notes = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    ticket = relationship("Ticket", back_populates="history")

    def __repr__(self):
        return f"<TicketHistory {self.history_id}: Ticket {self.ticket_id} {self.old_status} → {self.new_status}>"


class Admin(Base):
    """
    Admin user model for authentication and authorization.
    """
    __tablename__ = "admins"

    admin_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Integer, default=1, nullable=False)  # 1 = active, 0 = inactive
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Admin {self.username}>"


class CustomerNotification(Base):
    """
    Customer notification model for ticket status updates.
    """
    __tablename__ = "customer_notifications"

    notification_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Integer, default=0, nullable=False)  # 0 = unread, 1 = read
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    customer = relationship("Customer", back_populates="notifications")
    ticket = relationship("Ticket")

    def __repr__(self):
        return f"<Notification {self.notification_id}: Customer {self.customer_id} - Ticket {self.ticket_id}>"
