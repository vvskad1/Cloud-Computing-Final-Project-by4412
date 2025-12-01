# FixIt Tech Solutions

**Cloud-based Device Repair Management System**  
*CS 623 Final Project*

## 📋 Project Overview

FixIt Tech Solutions is a full-stack web application designed to streamline device repair management. The system allows customers to create repair bookings, track ticket status, and enables administrators to manage all repair tickets efficiently.

### Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML/CSS/JavaScript (to be implemented in Phase 4)
- **Database**: PostgreSQL/SQLite with SQLAlchemy ORM (to be implemented in Phase 2)

### Core Features

- ✅ Customer repair booking creation
- ✅ Ticket status tracking
- ✅ Admin ticket management dashboard
- ✅ Email notifications for bookings/updates
- ✅ AI chatbot support integration (planned)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

### Installation

1. **Clone or navigate to the project directory**:
   ```powershell
   cd "c:\Users\STSC\Desktop\Cloud Computing Final Project"
   ```

2. **Create a virtual environment** (recommended):
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

### Running the Application

Start the FastAPI development server:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

### Testing the Health Endpoint

Open your browser or use curl/Postman to test:

```
GET http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2025-11-30T12:00:00.000000",
  "service": "FixIt Tech Solutions"
}
```

---

## 📁 Project Structure

```
Cloud Computing Final Project/
├── app/
│   ├── __init__.py         # Package initialization
│   ├── main.py             # FastAPI application & endpoints
│   ├── models.py           # Domain models (Customer, Device, Ticket)
│   ├── schemas.py          # Pydantic validation schemas
│   └── config.py           # Configuration settings
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

## 🏗️ Development Phases

### ✅ Phase 1 – Backend Skeleton & Domain Model (COMPLETED)

- [x] Initialize FastAPI project structure
- [x] Define core domain models (Customer, Device, Ticket)
- [x] Create Pydantic schemas for validation
- [x] Implement health check endpoint
- [x] Set up configuration system

### ✅ Phase 2 – Database & CRUD for Tickets (COMPLETED)

- [x] Set up SQLAlchemy ORM with SQLite database
- [x] Convert domain models to database models with relationships
- [x] Implement CRUD operations (Create, Read, Update)
- [x] Create ticket management API endpoints
- [x] Add database initialization on startup

### ✅ Phase 3 – Ticket Tracking & Admin APIs (CURRENT)

- [x] Add ticket history tracking for status changes
- [x] Implement advanced filtering (date range, priority, customer search)
- [x] Create comprehensive admin dashboard with statistics
- [x] Add bulk operations for ticket status updates
- [x] Implement customer management endpoints
- [x] Add status transition validation and business rules
- [x] Create ticket history timeline endpoint

### 📋 Upcoming Phases
- **Phase 4**: Frontend Basic UI
- **Phase 5**: Integration Frontend ↔ Backend
- **Phase 6**: Email Notification Abstractions
- **Phase 7**: Basic AI Chatbot Endpoint (Optional)
- **Phase 8**: Documentation & Run Instructions

---

## 📚 API Documentation

Once the server is running, visit the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Available Endpoints

**General:**
- `GET /` - API information
- `GET /health` - Health check

**Ticket Management:**
- `POST /api/v1/tickets` - Create a new repair ticket
- `GET /api/v1/tickets` - List all tickets (with optional filtering)
- `GET /api/v1/tickets/{ticket_id}` - Get specific ticket details
- `PATCH /api/v1/tickets/{ticket_id}` - Update ticket (with validation)
- `GET /api/v1/tickets/customer/{email}` - Get all tickets for a customer
- `GET /api/v1/tickets/stats/status` - Get ticket statistics by status
- `GET /api/v1/tickets/{ticket_id}/history` - Get ticket status history
- `GET /api/v1/tickets/{ticket_id}/valid-statuses` - Get valid next statuses

**Admin Features (Phase 3):**
- `GET /api/v1/admin/dashboard` - Comprehensive dashboard statistics
- `GET /api/v1/admin/tickets/search` - Advanced ticket search with filters
- `GET /api/v1/admin/customers` - List all customers with search
- `POST /api/v1/admin/tickets/bulk-update` - Bulk status updates

---

## 👥 Contributors

CS 623 Student Project

---

## 📄 License

This project is created for educational purposes as part of CS 623.
