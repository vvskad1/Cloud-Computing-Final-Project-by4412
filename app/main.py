"""
Main FastAPI application entry point for FixIt Tech Solutions.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from groq import Groq

from app.database import create_tables, get_db
from app import crud, schemas, models
from app.auth import (
    authenticate_admin,
    authenticate_customer,
    create_access_token, 
    get_current_admin,
    get_current_customer,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Initialize Groq client
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

app = FastAPI(
    title="FixIt Tech Solutions API",
    description="Cloud-based Device Repair Management System",
    version="0.1.0"
)

# CORS middleware configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Initialize database tables and create default admin on application startup.
    """
    create_tables()
    print("✅ Database tables initialized successfully")
    
    # Create default admin user if none exists
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        admin_exists = db.query(models.Admin).first()
        if not admin_exists:
            default_admin = models.Admin(
                username="admin",
                email="admin@fixittech.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                is_active=1
            )
            db.add(default_admin)
            db.commit()
            print("✅ Default admin created (username: admin, password: admin123)")
    except Exception as e:
        print(f"⚠️ Error creating default admin: {e}")
    finally:
        db.close()


# Mount static files directory for frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    print(f"✅ Static files mounted from: {frontend_path}")


@app.get("/")
async def root():
    """
    Serve the landing page.
    """
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # Fallback to JSON response if frontend not available
    return {
        "message": "Welcome to FixIt Tech Solutions API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/favicon.ico")
async def favicon():
    """
    Serve favicon to avoid 404 errors.
    """
    return FileResponse(os.path.join(frontend_path, "favicon.ico")) if os.path.exists(os.path.join(frontend_path, "favicon.ico")) else {"status": "no favicon"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "FixIt Tech Solutions"
    }


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/api/v1/auth/login", response_model=schemas.TokenResponse)
async def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate admin user and return JWT access token.
    """
    admin = authenticate_admin(db, login_data.username, login_data.password)
    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=403,
            detail="Admin account is inactive"
        )
    
    # Update last login timestamp
    admin.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin_username": admin.username,
        "admin_full_name": admin.full_name
    }


@app.get("/api/v1/auth/me", response_model=schemas.AdminResponse)
async def get_current_admin_info(current_admin: models.Admin = Depends(get_current_admin)):
    """
    Get current authenticated admin user information.
    """
    return current_admin


@app.post("/api/v1/auth/customer/signup", response_model=schemas.CustomerTokenResponse)
async def customer_signup(signup_data: schemas.CustomerSignupRequest, db: Session = Depends(get_db)):
    """
    Register a new customer account.
    """
    # Check if customer already exists
    existing_customer = db.query(models.Customer).filter(models.Customer.email == signup_data.email).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new customer
    new_customer = models.Customer(
        name=signup_data.name,
        email=signup_data.email,
        phone=signup_data.phone,
        hashed_password=get_password_hash(signup_data.password),
        is_active=1
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_customer.email, "type": "customer"},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "customer_id": new_customer.customer_id,
        "customer_name": new_customer.name,
        "customer_email": new_customer.email
    }


@app.post("/api/v1/auth/customer/login", response_model=schemas.CustomerTokenResponse)
async def customer_login(login_data: schemas.CustomerLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate customer and return JWT access token.
    """
    customer = authenticate_customer(db, login_data.email, login_data.password)
    if not customer:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not customer.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    # Update last login
    customer.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": customer.email, "type": "customer"},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "customer_id": customer.customer_id,
        "customer_name": customer.name,
        "customer_email": customer.email
    }


@app.get("/api/v1/customer/profile", response_model=schemas.CustomerProfileResponse)
async def get_customer_profile(current_customer: models.Customer = Depends(get_current_customer), db: Session = Depends(get_db)):
    """
    Get current customer profile with unread notification count.
    """
    unread_count = db.query(models.CustomerNotification).filter(
        models.CustomerNotification.customer_id == current_customer.customer_id,
        models.CustomerNotification.is_read == 0
    ).count()
    
    profile = schemas.CustomerProfileResponse(
        customer_id=current_customer.customer_id,
        name=current_customer.name,
        email=current_customer.email,
        phone=current_customer.phone,
        is_active=bool(current_customer.is_active),
        created_at=current_customer.created_at,
        last_login=current_customer.last_login,
        unread_notifications=unread_count
    )
    return profile


@app.get("/api/v1/customer/notifications", response_model=List[schemas.NotificationResponse])
async def get_customer_notifications(current_customer: models.Customer = Depends(get_current_customer), db: Session = Depends(get_db)):
    """
    Get all notifications for the current customer.
    """
    notifications = db.query(models.CustomerNotification).filter(
        models.CustomerNotification.customer_id == current_customer.customer_id
    ).order_by(models.CustomerNotification.created_at.desc()).all()
    
    return notifications


@app.patch("/api/v1/customer/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_customer: models.Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read.
    """
    notification = db.query(models.CustomerNotification).filter(
        models.CustomerNotification.notification_id == notification_id,
        models.CustomerNotification.customer_id == current_customer.customer_id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = 1
    db.commit()
    
    return {"message": "Notification marked as read"}


@app.get("/api/v1/customer/tickets", response_model=List[schemas.TicketResponse])
async def get_customer_tickets(current_customer: models.Customer = Depends(get_current_customer), db: Session = Depends(get_db)):
    """
    Get all tickets for the current customer.
    """
    tickets = db.query(models.Ticket).filter(
        models.Ticket.customer_id == current_customer.customer_id
    ).order_by(models.Ticket.created_at.desc()).all()
    
    return tickets


# ============================================================================
# Ticket Management Endpoints
# ============================================================================

@app.post("/api/v1/tickets", response_model=schemas.TicketResponse, status_code=201)
async def create_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new repair ticket.
    
    This endpoint:
    - Creates or reuses customer record based on email
    - Creates a new device record
    - Creates a ticket linking customer and device
    - Returns the complete ticket with ID
    """
    try:
        db_ticket = crud.create_ticket(db=db, ticket=ticket)
        return db_ticket
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ticket: {str(e)}")


@app.get("/api/v1/tickets/{ticket_id}", response_model=schemas.TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific ticket by ID.
    
    Returns complete ticket information including customer and device details.
    """
    db_ticket = crud.get_ticket(db=db, ticket_id=ticket_id)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return db_ticket


@app.get("/api/v1/tickets", response_model=List[schemas.TicketResponse])
async def list_tickets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[models.TicketStatus] = None,
    db: Session = Depends(get_db)
):
    """
    List all tickets with optional filtering and pagination.
    
    Query Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100)
    - status: Filter by ticket status (optional)
    """
    tickets = crud.get_tickets(db=db, skip=skip, limit=limit, status=status)
    return tickets


@app.patch("/api/v1/tickets/{ticket_id}", response_model=schemas.TicketResponse)
async def update_ticket(
    ticket_id: int,
    ticket_update: schemas.TicketUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a ticket's information.
    
    Allows partial updates - only provided fields will be updated.
    Automatically updates the updated_at timestamp.
    Validates status transitions according to business rules.
    """
    # Get current ticket
    db_ticket = crud.get_ticket(db=db, ticket_id=ticket_id)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    
    # Validate status transition if status is being updated
    if ticket_update.status is not None:
        from app import business_logic
        error = business_logic.validate_status_transition(db_ticket.status, ticket_update.status)
        if error:
            raise HTTPException(status_code=400, detail=error)
    
    # Validate priority if being updated
    if ticket_update.priority is not None:
        from app import business_logic
        if not business_logic.validate_priority(ticket_update.priority):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid priority. Must be one of: low, normal, high, urgent"
            )
    
    # Store old status for notification
    old_status = db_ticket.status
    
    updated_ticket = crud.update_ticket(db=db, ticket_id=ticket_id, ticket_update=ticket_update)
    
    # Create notification if status changed
    if ticket_update.status is not None and ticket_update.status != old_status:
        # Convert enum to readable string
        old_status_str = old_status.value if hasattr(old_status, 'value') else str(old_status)
        new_status_str = ticket_update.status.value if hasattr(ticket_update.status, 'value') else str(ticket_update.status)
        
        notification_message = f"Your ticket #{ticket_id} status has been updated from '{old_status_str}' to '{new_status_str}'."
        
        notification = models.CustomerNotification(
            customer_id=updated_ticket.customer_id,
            ticket_id=ticket_id,
            message=notification_message,
            is_read=0
        )
        db.add(notification)
        db.commit()
    
    return updated_ticket


@app.get("/api/v1/tickets/customer/{email}", response_model=List[schemas.TicketResponse])
async def get_customer_tickets(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve all tickets for a customer by email address.
    
    Useful for customer self-service portals where customers
    can track their repair tickets using their email.
    """
    tickets = crud.get_tickets_by_customer_email(db=db, email=email)
    return tickets


@app.get("/api/v1/tickets/stats/status")
async def get_ticket_statistics(db: Session = Depends(get_db)):
    """
    Get ticket count statistics grouped by status.
    
    Useful for admin dashboard to show overview of all tickets.
    """
    stats = crud.get_ticket_count_by_status(db=db)
    return {
        "statistics": stats,
        "total": sum(stats.values())
    }


# ============================================================================
# Phase 3: Admin & Advanced Features
# ============================================================================

@app.get("/api/v1/admin/dashboard", response_model=schemas.DashboardStatistics)
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Get comprehensive dashboard statistics for administrators.
    Requires authentication.
    
    Includes:
    - Total tickets and customers
    - Average costs
    - Recent activity (last 7 days)
    - Breakdown by priority and device type
    """
    stats = crud.get_dashboard_statistics(db=db)
    return stats


@app.get("/api/v1/tickets/{ticket_id}/history", response_model=List[schemas.TicketHistoryResponse])
async def get_ticket_history(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the complete history of status changes for a specific ticket.
    
    Returns a timeline of all status transitions with timestamps and notes.
    """
    ticket = crud.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    
    history = crud.get_ticket_history(db=db, ticket_id=ticket_id)
    return history


@app.post("/api/v1/admin/tickets/bulk-update", response_model=schemas.BulkUpdateResponse)
async def bulk_update_tickets(
    bulk_update: schemas.BulkStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Update the status of multiple tickets at once. Requires authentication.
    
    Useful for batch operations like marking multiple tickets as completed.
    """
    updated_count = crud.bulk_update_ticket_status(
        db=db,
        ticket_ids=bulk_update.ticket_ids,
        new_status=bulk_update.new_status,
        changed_by=bulk_update.changed_by
    )
    
    return {
        "updated_count": updated_count,
        "requested_count": len(bulk_update.ticket_ids),
        "success": updated_count > 0,
        "message": f"Successfully updated {updated_count} out of {len(bulk_update.ticket_ids)} tickets"
    }


@app.get("/api/v1/admin/customers", response_model=List[schemas.CustomerResponse])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    List all customers with optional search functionality. Requires authentication.
    
    Query Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    - search: Search by customer name or email (partial match)
    """
    customers = crud.get_all_customers(db=db, skip=skip, limit=limit, search=search)
    return customers


@app.get("/api/v1/admin/tickets/search", response_model=List[schemas.TicketResponse])
async def advanced_ticket_search(
    skip: int = 0,
    limit: int = 100,
    status: Optional[models.TicketStatus] = None,
    priority: Optional[str] = None,
    customer_name: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Advanced ticket search with multiple filter criteria. Requires authentication.
    
    Query Parameters:
    - skip, limit: Pagination
    - status: Filter by ticket status
    - priority: Filter by priority (low, normal, high, urgent)
    - customer_name: Search by customer name (partial match)
    - date_from: Filter tickets created after this date (ISO format: 2025-01-01)
    - date_to: Filter tickets created before this date (ISO format: 2025-12-31)
    """
    from datetime import datetime as dt
    
    # Parse date strings if provided
    parsed_date_from = dt.fromisoformat(date_from) if date_from else None
    parsed_date_to = dt.fromisoformat(date_to) if date_to else None
    
    tickets = crud.get_tickets(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        customer_name=customer_name,
        date_from=parsed_date_from,
        date_to=parsed_date_to
    )
    return tickets


@app.get("/api/v1/tickets/{ticket_id}/valid-statuses")
async def get_valid_next_statuses(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """
    Get valid next statuses for a ticket based on its current status.
    
    Useful for UI to show only valid status transitions.
    """
    from app import business_logic
    
    ticket = crud.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    
    valid_statuses = business_logic.get_valid_next_statuses(ticket.status)
    
    return {
        "ticket_id": ticket_id,
        "current_status": ticket.status.value,
        "valid_next_statuses": [status.value for status in valid_statuses],
        "is_actionable": business_logic.is_ticket_actionable(ticket.status)
    }


# ============================================================================
# AI Chatbot Endpoint
# ============================================================================

@app.post("/api/v1/chatbot", response_model=schemas.ChatbotResponse)
async def chat_with_bot(
    chat_request: schemas.ChatbotRequest,
    current_customer: models.Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    AI chatbot endpoint for customer support.
    Provides assistance with repair-related queries.
    """
    try:
        # Get customer's tickets for context
        customer_tickets = db.query(models.Ticket).filter(
            models.Ticket.customer_id == current_customer.customer_id
        ).all()
        
        # Build context about customer's tickets
        tickets_context = ""
        if customer_tickets:
            tickets_context = f"\n\nCustomer has {len(customer_tickets)} ticket(s):\n"
            for ticket in customer_tickets[:3]:  # Limit to recent 3
                tickets_context += f"- Ticket #{ticket.ticket_id}: {ticket.device.device_type} {ticket.device.brand} {ticket.device.model}, Status: {ticket.status.value}, Issue: {ticket.device.issue_description}\n"
        
        # System prompt for the AI
        system_prompt = f"""You are a helpful customer support assistant for FixIt Tech Solutions, a device repair management system. 
Your role is to assist customers with:
- Questions about their repair tickets
- General repair process information
- Device troubleshooting tips
- Status updates and timelines
- Pricing and service information

Keep responses concise, friendly, and professional. If asked about specific ticket details, refer to the information provided.
{tickets_context}

Customer name: {current_customer.name}
Customer email: {current_customer.email}"""

        # Build conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        if chat_request.conversation_history:
            messages.extend(chat_request.conversation_history[-10:])  # Last 10 messages
        
        messages.append({"role": "user", "content": chat_request.message})
        
        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=500
        )
        
        response_text = chat_completion.choices[0].message.content
        
        return {
            "response": response_text,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chatbot request: {str(e)}"
        )
