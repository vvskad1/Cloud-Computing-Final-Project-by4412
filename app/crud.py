"""
CRUD (Create, Read, Update, Delete) operations for FixIt Tech Solutions.
This module contains database operations for customers, devices, and tickets.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app import models, schemas


# ============================================================================
# Customer CRUD Operations
# ============================================================================

def get_customer_by_email(db: Session, email: str) -> Optional[models.Customer]:
    """
    Retrieve a customer by email address.
    """
    return db.query(models.Customer).filter(models.Customer.email == email).first()


def get_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    """
    Retrieve a customer by ID.
    """
    return db.query(models.Customer).filter(models.Customer.customer_id == customer_id).first()


def create_customer(db: Session, customer: schemas.CustomerCreate) -> models.Customer:
    """
    Create a new customer in the database.
    """
    db_customer = models.Customer(
        name=customer.name,
        email=customer.email,
        phone=customer.phone
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def get_or_create_customer(db: Session, customer_data: schemas.CustomerCreate) -> models.Customer:
    """
    Get existing customer by email or create a new one.
    This is useful when creating tickets - we reuse customer records.
    """
    existing_customer = get_customer_by_email(db, customer_data.email)
    if existing_customer:
        return existing_customer
    return create_customer(db, customer_data)


# ============================================================================
# Device CRUD Operations
# ============================================================================

def get_device(db: Session, device_id: int) -> Optional[models.Device]:
    """
    Retrieve a device by ID.
    """
    return db.query(models.Device).filter(models.Device.device_id == device_id).first()


def create_device(db: Session, device: schemas.DeviceCreate) -> models.Device:
    """
    Create a new device record in the database.
    """
    db_device = models.Device(
        device_type=device.device_type,
        brand=device.brand,
        model=device.model,
        issue_description=device.issue_description,
        serial_number=device.serial_number
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


# ============================================================================
# Ticket CRUD Operations
# ============================================================================

def get_ticket(db: Session, ticket_id: int) -> Optional[models.Ticket]:
    """
    Retrieve a single ticket by ID with customer and device relationships loaded.
    """
    return db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()


def get_tickets(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[models.TicketStatus] = None,
    priority: Optional[str] = None,
    customer_name: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> List[models.Ticket]:
    """
    Retrieve a list of tickets with advanced filtering options.
    Supports pagination and multiple filter criteria.
    
    Args:
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        status: Filter by ticket status
        priority: Filter by priority level
        customer_name: Search by customer name (partial match)
        date_from: Filter tickets created after this date
        date_to: Filter tickets created before this date
    """
    query = db.query(models.Ticket)
    
    if status:
        query = query.filter(models.Ticket.status == status)
    
    if priority:
        query = query.filter(models.Ticket.priority == priority)
    
    if customer_name:
        query = query.join(models.Customer).filter(
            models.Customer.name.ilike(f"%{customer_name}%")
        )
    
    if date_from:
        query = query.filter(models.Ticket.created_at >= date_from)
    
    if date_to:
        query = query.filter(models.Ticket.created_at <= date_to)
    
    return query.order_by(models.Ticket.created_at.desc()).offset(skip).limit(limit).all()


def create_ticket(db: Session, ticket: schemas.TicketCreate) -> models.Ticket:
    """
    Create a new repair ticket with associated customer and device.
    If the customer already exists (by email), reuse that record.
    """
    # Create or get existing customer
    customer_data = schemas.CustomerCreate(
        name=ticket.customer_name,
        email=ticket.customer_email,
        phone=ticket.customer_phone
    )
    db_customer = get_or_create_customer(db, customer_data)
    
    # Create device record
    device_data = schemas.DeviceCreate(
        device_type=ticket.device_type,
        brand=ticket.device_brand,
        model=ticket.device_model,
        issue_description=ticket.issue_description,
        serial_number=ticket.serial_number
    )
    db_device = create_device(db, device_data)
    
    # Create ticket
    db_ticket = models.Ticket(
        customer_id=db_customer.customer_id,
        device_id=db_device.device_id,
        status=models.TicketStatus.PENDING,
        priority=ticket.priority,
        estimated_cost=ticket.estimated_cost,
        notes=ticket.notes
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    return db_ticket


def create_ticket_history(
    db: Session,
    ticket_id: int,
    old_status: Optional[models.TicketStatus],
    new_status: models.TicketStatus,
    changed_by: Optional[str] = None,
    notes: Optional[str] = None
) -> models.TicketHistory:
    """
    Create a history record for ticket status changes.
    """
    history_entry = models.TicketHistory(
        ticket_id=ticket_id,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by or "system",
        notes=notes
    )
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)
    return history_entry


def update_ticket_status(
    db: Session,
    ticket_id: int,
    status: models.TicketStatus,
    changed_by: Optional[str] = None,
    notes: Optional[str] = None
) -> Optional[models.Ticket]:
    """
    Update the status of a ticket.
    Automatically sets completed_at when status is COMPLETED or DELIVERED.
    Records the change in ticket history.
    """
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return None
    
    old_status = db_ticket.status
    db_ticket.status = status
    db_ticket.updated_at = datetime.utcnow()
    
    # Set completion timestamp for final statuses
    if status in [models.TicketStatus.COMPLETED, models.TicketStatus.DELIVERED]:
        db_ticket.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_ticket)
    
    # Record the status change in history
    if old_status != status:
        create_ticket_history(db, ticket_id, old_status, status, changed_by, notes)
    
    return db_ticket


def update_ticket(
    db: Session,
    ticket_id: int,
    ticket_update: schemas.TicketUpdate,
    changed_by: Optional[str] = None
) -> Optional[models.Ticket]:
    """
    Update ticket fields based on provided data.
    Only updates fields that are provided (not None).
    Records status changes in history.
    """
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return None
    
    old_status = db_ticket.status
    update_data = ticket_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_ticket, field, value)
    
    db_ticket.updated_at = datetime.utcnow()
    
    # Set completion timestamp if status changed to completed/delivered
    if "status" in update_data and update_data["status"] in [
        models.TicketStatus.COMPLETED,
        models.TicketStatus.DELIVERED
    ]:
        db_ticket.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_ticket)
    
    # Record status change in history if status was updated
    if "status" in update_data and old_status != update_data["status"]:
        create_ticket_history(
            db, 
            ticket_id, 
            old_status, 
            update_data["status"], 
            changed_by,
            ticket_update.notes
        )
    
    return db_ticket


def get_tickets_by_customer_email(db: Session, email: str) -> List[models.Ticket]:
    """
    Retrieve all tickets for a customer by email address.
    Useful for customer self-service ticket tracking.
    """
    customer = get_customer_by_email(db, email)
    if not customer:
        return []
    
    return db.query(models.Ticket).filter(
        models.Ticket.customer_id == customer.customer_id
    ).order_by(models.Ticket.created_at.desc()).all()


def get_ticket_count_by_status(db: Session) -> dict:
    """
    Get count of tickets grouped by status.
    Useful for admin dashboard statistics.
    """
    from sqlalchemy import func
    
    results = db.query(
        models.Ticket.status,
        func.count(models.Ticket.ticket_id).label("count")
    ).group_by(models.Ticket.status).all()
    
    return {status.value: count for status, count in results}


def get_ticket_history(db: Session, ticket_id: int) -> List[models.TicketHistory]:
    """
    Get the complete history of status changes for a ticket.
    """
    return db.query(models.TicketHistory).filter(
        models.TicketHistory.ticket_id == ticket_id
    ).order_by(models.TicketHistory.changed_at.desc()).all()


def get_dashboard_statistics(db: Session) -> dict:
    """
    Get comprehensive statistics for admin dashboard.
    Includes ticket counts, averages, and trends.
    """
    from sqlalchemy import func
    
    total_tickets = db.query(func.count(models.Ticket.ticket_id)).scalar()
    total_customers = db.query(func.count(models.Customer.customer_id)).scalar()
    
    # Average estimated cost
    avg_cost = db.query(func.avg(models.Ticket.estimated_cost)).scalar() or 0
    
    # Count by priority
    priority_counts = db.query(
        models.Ticket.priority,
        func.count(models.Ticket.ticket_id).label("count")
    ).group_by(models.Ticket.priority).all()
    
    # Count by device type
    device_type_counts = db.query(
        models.Device.device_type,
        func.count(models.Ticket.ticket_id).label("count")
    ).join(models.Ticket).group_by(models.Device.device_type).all()
    
    # Recent tickets (last 7 days)
    from datetime import timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_tickets = db.query(func.count(models.Ticket.ticket_id)).filter(
        models.Ticket.created_at >= seven_days_ago
    ).scalar()
    
    return {
        "total_tickets": total_tickets,
        "total_customers": total_customers,
        "average_estimated_cost": round(float(avg_cost), 2),
        "recent_tickets_7_days": recent_tickets,
        "tickets_by_priority": {priority: count for priority, count in priority_counts},
        "tickets_by_device_type": {dtype.value: count for dtype, count in device_type_counts}
    }


def get_all_customers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[models.Customer]:
    """
    Get all customers with optional search by name or email.
    """
    query = db.query(models.Customer)
    
    if search:
        query = query.filter(
            (models.Customer.name.ilike(f"%{search}%")) |
            (models.Customer.email.ilike(f"%{search}%"))
        )
    
    return query.order_by(models.Customer.created_at.desc()).offset(skip).limit(limit).all()


def bulk_update_ticket_status(
    db: Session,
    ticket_ids: List[int],
    new_status: models.TicketStatus,
    changed_by: Optional[str] = None
) -> int:
    """
    Update the status of multiple tickets at once.
    Returns the number of tickets updated.
    """
    updated_count = 0
    
    for ticket_id in ticket_ids:
        ticket = update_ticket_status(db, ticket_id, new_status, changed_by)
        if ticket:
            updated_count += 1
    
    return updated_count
