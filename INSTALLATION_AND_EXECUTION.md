# FixIt Tech Solutions - Installation and Execution Guide

**CS 623 Final Project**  
**Cloud-based Device Repair Management System**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Architecture](#system-architecture)
3. [Installation Steps](#installation-steps)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [Accessing the Application](#accessing-the-application)
7. [Default Credentials](#default-credentials)
8. [Troubleshooting](#troubleshooting)
9. [Application Features](#application-features)

---

## Prerequisites

### Required Software

- **Python**: Version 3.9 or higher
  - Check version: `python --version`
  - Download from: https://www.python.org/downloads/ (if not installed)
  
- **pip**: Python package installer (included with Python)
  - Check version: `pip --version`

### Operating System

- **Windows**: PowerShell or Command Prompt
- **macOS/Linux**: Terminal with bash/zsh

### Hardware Requirements

- **RAM**: Minimum 4GB
- **Disk Space**: ~500MB for dependencies and database

---

## System Architecture

### Tech Stack

- **Backend Framework**: FastAPI 0.104.1
- **Web Server**: Uvicorn (ASGI server)
- **Database**: SQLite (embedded, no separate installation needed)
- **Authentication**: JWT (JSON Web Tokens) with bcrypt password hashing
- **AI Assistant**: Groq API (llama-3.3-70b-versatile model)
- **Frontend**: Vanilla HTML/CSS/JavaScript

### Project Structure

```
Cloud Computing Final Project/
├── app/
│   ├── .env                    # Environment configuration
│   ├── main.py                 # FastAPI application entry point
│   ├── models.py               # SQLAlchemy database models
│   ├── schemas.py              # Pydantic schemas for validation
│   ├── crud.py                 # Database operations
│   ├── auth.py                 # JWT authentication logic
│   ├── database.py             # Database connection setup
│   ├── business_logic.py       # Status transition rules
│   └── config.py               # Configuration settings
├── frontend/
│   ├── index.html              # Landing page
│   ├── login.html              # Unified login page
│   ├── signup.html             # Customer registration
│   ├── admin.html              # Admin dashboard
│   ├── customer-portal.html    # Customer portal with AI chatbot
│   ├── new-booking.html        # Create repair booking
│   ├── track-ticket.html       # Track ticket status
│   ├── css/
│   │   └── styles.css          # Application styles
│   └── js/
│       ├── admin.js            # Admin dashboard logic
│       ├── customer-portal.js  # Customer portal with chatbot
│       ├── booking.js          # Booking form logic
│       ├── login.js            # Authentication logic
│       └── tracking.js         # Ticket tracking logic
├── fixit_tech.db               # SQLite database (auto-generated)
├── migrate_db.py               # Database migration script
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## Installation Steps

### Step 1: Extract Project Files

Extract the project ZIP file to a directory on your machine:

```powershell
# Windows PowerShell
cd C:\Users\YourUsername\Desktop
# Extract the ZIP file to this location
```

```bash
# macOS/Linux
cd ~/Desktop
# Extract the ZIP file to this location
```

### Step 2: Navigate to Project Directory

```powershell
# Windows
cd "C:\Users\YourUsername\Desktop\Cloud Computing Final Project"
```

```bash
# macOS/Linux
cd ~/Desktop/"Cloud Computing Final Project"
```

### Step 3: Create Virtual Environment

Creating a virtual environment isolates project dependencies:

```powershell
# Windows PowerShell
python -m venv venv
```

```bash
# macOS/Linux
python3 -m venv venv
```

### Step 4: Activate Virtual Environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Verification:** After activation, your prompt should show `(venv)` prefix.

### Step 5: Install Python Dependencies

Install all required packages from requirements.txt:

```powershell
pip install -r requirements.txt
```

**Expected packages to be installed:**
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- sqlalchemy==2.0.36
- pydantic==2.12.5
- python-jose[cryptography]==3.5.0
- passlib[bcrypt]==1.7.4
- bcrypt==4.0.1
- python-dotenv==1.2.1
- groq==0.36.0
- email-validator==2.1.0
- python-dateutil==2.8.2
- alembic==1.14.0

**Installation time:** ~2-3 minutes depending on internet speed.

---

## Database Setup

### Database Configuration

The application uses **SQLite**, which requires no separate installation. The database file (`fixit_tech.db`) is automatically created on first run.

### Environment Configuration

The `.env` file in the `app/` directory contains configuration settings. You can use the existing file or create a new one:

**Location:** `app/.env`

**Template:**
```env
# JWT Authentication
JWT_SECRET=your-secret-key-here

# Groq AI API (Optional - for chatbot functionality)
GROQ_API_KEY=your-groq-api-key-here

# Email Configuration (Optional - currently not used)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
MAIL_FROM=your-email@gmail.com
```

**Important Notes:**

1. **JWT_SECRET**: Can be any random string. Default is already set.
2. **GROQ_API_KEY**: Required for AI chatbot. Get free API key from https://console.groq.com
   - If you don't have an API key, the chatbot feature won't work but the rest of the application will function normally.
3. **Email settings**: Currently not implemented in the application. You can ignore these settings.

### Database Initialization

The database is **automatically initialized** when you first start the application. The startup process:

1. Creates all required tables (customers, admins, tickets, devices, notifications, etc.)
2. Creates a default admin account (username: `admin`, password: `admin123`)
3. Sets up indexes for performance

**No manual database setup is required!**

### Optional: Database Migration (If Needed)

If you need to update an existing database schema, run:

```powershell
python migrate_db.py
```

This script adds authentication columns and notification tables to existing databases.

---

## Running the Application

### Starting the Backend Server

From the project root directory (with virtual environment activated):

```powershell
uvicorn app.main:app --reload --port 8081
```

**Command Breakdown:**
- `uvicorn`: ASGI server for FastAPI
- `app.main:app`: Import path (app folder, main.py file, app instance)
- `--reload`: Auto-reload on code changes (development mode)
- `--port 8081`: Server port (default: 8000, but we use 8081)

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8081 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
✅ Database tables initialized successfully
✅ Default admin created (username: admin, password: admin123)
✅ Static files mounted from: C:\...\frontend
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Important:** Keep this terminal window open while using the application.

### Alternative Port (If 8081 is in use)

```powershell
uvicorn app.main:app --reload --port 8080
```

Then access the application at `http://localhost:8080` instead.

---

## Accessing the Application

Once the server is running, open a web browser and navigate to:

### Main Application URLs

| Page | URL | Description |
|------|-----|-------------|
| **Home Page** | http://localhost:8081 | Landing page with overview |
| **Customer Login** | http://localhost:8081/static/login.html | Customer login (tab 1) |
| **Admin Login** | http://localhost:8081/static/login.html | Admin login (tab 2) |
| **Customer Signup** | http://localhost:8081/static/signup.html | New customer registration |
| **Book Repair** | http://localhost:8081/static/new-booking.html | Create new repair ticket |
| **Track Ticket** | http://localhost:8081/static/track-ticket.html | Track ticket by ID/email |
| **Admin Dashboard** | http://localhost:8081/static/admin.html | Admin panel (requires login) |
| **Customer Portal** | http://localhost:8081/static/customer-portal.html | Customer dashboard with AI chatbot |
| **API Documentation** | http://localhost:8081/docs | Interactive API docs (Swagger UI) |
| **Alternative API Docs** | http://localhost:8081/redoc | ReDoc API documentation |

### Recommended Test Workflow

1. **Start at Home Page**: http://localhost:8081
2. **Create Customer Account**: Click "Sign Up" or go to signup page
3. **Login as Customer**: Use your new credentials
4. **Explore Customer Portal**: View tickets, chat with AI assistant
5. **Create Booking**: Submit a repair request
6. **Login as Admin**: Use default admin credentials (see below)
7. **Manage Tickets**: Update status, view analytics

---

## Default Credentials

### Admin Account (Pre-created)

- **Username:** `admin`
- **Password:** `admin123`
- **Email:** admin@fixittech.com
- **Access:** Full system access via Admin Dashboard

**Login URL:** http://localhost:8081/static/login.html (Admin tab)

### Customer Account (Must Create)

No default customer accounts exist. To create one:

1. Go to http://localhost:8081/static/signup.html
2. Fill out the registration form
3. Use any email (doesn't need to be real)
4. Login with your created credentials

**Example Customer:**
- Name: John Doe
- Email: john@example.com
- Phone: 1234567890
- Password: password123

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use

**Error:**
```
ERROR:    [Errno 10048] Only one usage of each socket address is normally permitted
```

**Solution:**
- Use a different port:
  ```powershell
  uvicorn app.main:app --reload --port 8082
  ```
- Or kill the process using the port:
  ```powershell
  # Windows
  netstat -ano | findstr :8081
  taskkill /PID <process_id> /F
  ```

#### 2. Module Not Found Error

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
- Ensure virtual environment is activated (look for `(venv)` in prompt)
- Reinstall dependencies:
  ```powershell
  pip install -r requirements.txt
  ```

#### 3. Python Version Incompatibility

**Error:**
```
ERROR: Package requires Python '>=3.9'
```

**Solution:**
- Check Python version: `python --version`
- Upgrade Python to 3.9 or higher
- Recreate virtual environment with correct Python version

#### 4. Database Locked Error

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
- Close all other connections to the database
- Restart the application
- If persistent, delete `fixit_tech.db` (will reset all data)

#### 5. AI Chatbot Not Responding

**Error:** Chatbot shows error or doesn't respond

**Solution:**
- Check if `GROQ_API_KEY` is set in `app/.env`
- Verify API key is valid (test at https://console.groq.com)
- Check server logs for specific error messages
- The rest of the application works without Groq API

#### 6. Static Files Not Loading (404 errors)

**Error:** CSS/JS files return 404, page looks broken

**Solution:**
- Verify `frontend/` folder exists in project directory
- Check server startup logs for:
  ```
  ✅ Static files mounted from: <path>
  ```
- Restart the server

#### 7. Cannot Login (Invalid Credentials)

**Issue:** Admin/customer login fails

**Solution:**
- For admin: Use exactly `admin` / `admin123`
- For customer: Ensure you created the account first via signup
- Check browser console for errors (F12 → Console tab)
- Clear browser cache/cookies

#### 8. Database Migration Errors

**Error:** Migration script fails

**Solution:**
- Backup `fixit_tech.db`
- Delete `fixit_tech.db`
- Restart server to recreate fresh database
- Re-create customer accounts

#### 9. Uvicorn Command Not Found

**Error:**
```
'uvicorn' is not recognized as an internal or external command
```

**Solution:**
- Ensure virtual environment is activated
- Reinstall uvicorn:
  ```powershell
  pip install uvicorn[standard]==0.24.0
  ```

#### 10. CORS Errors in Browser Console

**Error:**
```
Access to fetch at 'http://localhost:8081/api/...' from origin has been blocked by CORS
```

**Solution:**
- This shouldn't happen as CORS is configured for all origins
- Clear browser cache
- Try a different browser
- Check if you're accessing via correct URL (localhost:8081)

---

## Application Features

### Customer Features

1. **Registration & Authentication**
   - Create account with email/password
   - Secure JWT-based authentication
   - Profile management

2. **Repair Booking**
   - Submit repair requests with device details
   - Specify device type (phone, laptop, tablet, desktop, watch, other)
   - Add issue description and priority
   - Auto-generates ticket ID

3. **Customer Portal**
   - View all repair tickets
   - Real-time status updates
   - Statistics dashboard (total, active, completed tickets)
   - Notification system for status changes
   - Modern gradient UI design

4. **AI Chatbot Assistant** 🤖
   - Context-aware support using Groq AI
   - Answers questions about repair process
   - Provides ticket status information
   - Device troubleshooting tips
   - 24/7 availability

5. **Ticket Tracking**
   - Track ticket by ID or email
   - View detailed repair progress
   - See estimated costs and timelines

### Admin Features

1. **Secure Authentication**
   - Username/password login
   - Role-based access control
   - Session management

2. **Admin Dashboard**
   - Real-time statistics (total tickets, pending, completed)
   - Ticket filtering by status/priority/device type
   - Search functionality
   - Analytics overview

3. **Ticket Management**
   - View all customer tickets
   - Update ticket status (with validation rules)
   - Add notes and cost estimates
   - Status transition tracking
   - Automatic customer notifications

4. **Status Workflow**
   - Valid status transitions enforced:
     - pending → diagnosed
     - diagnosed → in_progress OR ready_pickup
     - in_progress → ready_pickup
     - ready_pickup → delivered
     - Any status → cancelled

5. **Notification System**
   - Automatic notifications on status changes
   - Customer can view notification history
   - Read/unread status tracking

### Technical Features

1. **Security**
   - JWT token-based authentication
   - Bcrypt password hashing
   - Secure admin/customer separation
   - Token expiration (8 hours)

2. **Database**
   - SQLite with SQLAlchemy ORM
   - Automatic schema creation
   - Migration support
   - Data validation with Pydantic

3. **API**
   - RESTful API design
   - Interactive documentation (Swagger/ReDoc)
   - Comprehensive error handling
   - Request validation

4. **UI/UX**
   - Responsive design
   - Modern gradient aesthetics (purple theme)
   - Glass-morphism effects
   - Smooth animations
   - Intuitive navigation

---

## Testing the Application

### Quick Test Scenario

1. **Start Server:**
   ```powershell
   uvicorn app.main:app --reload --port 8081
   ```

2. **Create Customer Account:**
   - Go to http://localhost:8081/static/signup.html
   - Register with: test@example.com / test123

3. **Create Ticket:**
   - Login at http://localhost:8081/static/login.html
   - Go to "Book Repair"
   - Submit laptop repair request

4. **View in Customer Portal:**
   - Click "My Portal"
   - See your ticket listed
   - Try AI chatbot by clicking 💬 button

5. **Admin Management:**
   - Logout from customer account
   - Login as admin (admin/admin123)
   - Go to http://localhost:8081/static/admin.html
   - Find the test ticket
   - Update status to "diagnosed"

6. **Check Notification:**
   - Logout and login as customer again
   - Check notifications in portal
   - Should see status update message

---

## API Endpoints (For Testing)

### Authentication
- POST `/api/v1/auth/login` - Admin login
- POST `/api/v1/auth/customer/signup` - Customer registration
- POST `/api/v1/auth/customer/login` - Customer login

### Tickets
- GET `/api/v1/tickets` - Get all tickets (admin)
- POST `/api/v1/tickets` - Create ticket
- GET `/api/v1/tickets/{ticket_id}` - Get ticket details
- PUT `/api/v1/tickets/{ticket_id}` - Update ticket (admin)
- DELETE `/api/v1/tickets/{ticket_id}` - Delete ticket (admin)

### Customer
- GET `/api/v1/customer/profile` - Get customer profile
- GET `/api/v1/customer/tickets` - Get customer's tickets
- GET `/api/v1/customer/notifications` - Get notifications
- PUT `/api/v1/customer/notifications/{id}/read` - Mark as read

### AI Chatbot
- POST `/api/v1/chatbot` - Chat with AI assistant

**Full API documentation:** http://localhost:8081/docs

---

## Stopping the Application

To stop the server:

1. Go to the terminal running uvicorn
2. Press `CTRL+C`
3. Wait for graceful shutdown message
4. Deactivate virtual environment (optional):
   ```powershell
   deactivate
   ```

---

## Additional Notes

### Database Location
- File: `fixit_tech.db` (in project root)
- Type: SQLite database
- Backup: Simply copy this file to backup all data

### Log Files
- Application logs appear in terminal output
- No separate log files created by default

### Development vs Production
- This setup is for **development/testing**
- For production:
  - Change `--reload` to without reload
  - Use proper secrets in `.env`
  - Consider PostgreSQL instead of SQLite
  - Deploy with Gunicorn/Docker
  - Use HTTPS/SSL certificates

### Browser Compatibility
- Tested on: Chrome, Firefox, Edge
- Requires: JavaScript enabled
- Recommended: Latest browser version

---

## Support

For issues or questions during evaluation:

1. Check this document's Troubleshooting section
2. Review server console output for error messages
3. Check browser console (F12 → Console) for frontend errors
4. Verify all installation steps were followed
5. Ensure Python 3.9+ and all dependencies are installed

---

## Summary Checklist

Before running the application, ensure:

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] In project root directory
- [ ] Port 8081 available
- [ ] `.env` file exists in `app/` folder
- [ ] Run: `uvicorn app.main:app --reload --port 8081`
- [ ] Access: http://localhost:8081

**Expected time to set up: 5-10 minutes**

---

*Document Version: 1.0*  
*Last Updated: December 2025*  
*Course: CS 623 - Cloud Computing*
