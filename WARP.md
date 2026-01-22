# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a **Flask web application** for tracking Dangote Cement execution activities. The system manages outlets, field agents, and execution records with image capture capabilities. It's designed for field agents to record their visits to cement outlets and for administrators to manage the entire system.

## Application Architecture

### Core Structure
- **`app.py`** - Main Flask application entry point, initializes database and routes
- **`pykes/`** - Main application package containing:
  - `models.py` - Database initialization and schema definitions
  - `routes.py` - Core application routes (login, outlets, executions)
  - `config.py` - Application configuration
  - `utils.py` - Utility functions for file handling and image processing
- **`app_admin.py`** - Administrative blueprint for user and system management
- **`app_reports.py`** - Reporting blueprint for analytics and data visualization
- **`templates/`** - Jinja2 HTML templates
- **`uploads/`** - Directory for uploaded images (before/after execution photos)

### Database Design
Uses **SQLite** with three main tables:
- **`outlets`** - Cement retail outlets (URN, name, location, contact info)
- **`users`** - System users (field agents and administrators) with role-based access
- **`executions`** - Execution records linking agents to outlets with photos and metadata

### Key Features
- **Role-based access control** (admin vs field_agent)
- **Geolocation tracking** for executions
- **Image capture** (before/after photos)
- **Regional filtering** based on user permissions
- **Execution scoring system**
- **Comprehensive reporting** with product availability analytics

## Development Commands

### Running the Application
```bash
python app.py
```
The application runs on `http://localhost:5000` with debug mode enabled.

### Database Management
The database is automatically initialized on first run. To reset or fix schema issues:
```bash
python fix_database_schema.py
```

### Backup Operations
```bash
python bacup.py  # Creates database backups
```

## Key Development Patterns

### Authentication & Authorization
- All routes (except login) require authentication via Flask sessions
- Role-based access using `@admin_required` decorator for admin functions
- Regional restrictions for field agents based on their assigned region

### File Upload Handling
- Base64 image encoding for mobile-friendly photo capture
- Secure filename generation using UUID
- File type validation for image uploads
- Images stored in `uploads/` directory with unique naming

### Database Connection Pattern
```python
def get_db_connection():
    db_path = os.environ.get('DATABASE_PATH', 'dangote_execution.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
```
Always use this pattern for database access and ensure connections are properly closed.

### Blueprint Architecture
The application uses Flask blueprints for modularity:
- Main routes in `pykes/routes.py` 
- Admin routes in `app_admin.py` with `/admin` prefix
- Reporting routes in `app_reports.py` with `/reports` prefix

## Data Flow

### Execution Workflow
1. Field agent logs in and views assigned outlets (filtered by region)
2. Selects outlet and creates new execution record (status: "Pending")
3. Captures before/after photos with geolocation
4. Records product availability and execution notes
5. Submits execution (status: "Completed")
6. Data becomes available in admin reports and analytics

### Product Tracking
The system tracks specific Dangote products defined in `pykes/utils.py`:
- Tables, Chairs, Parasols, Parasol Stands
- Tarpaulins, Hawker Jackets, Cups

## Common Development Tasks

### Adding New Routes
Add routes to the appropriate blueprint:
- General app routes: `pykes/routes.py` 
- Admin functionality: `app_admin.py`
- Reporting features: `app_reports.py`

### Database Schema Changes
1. Modify table definitions in `pykes/models.py`
2. Create migration script or use `fix_database_schema.py`
3. Test with sample data

### Template Development
Templates use Bootstrap 4 framework with base template in `templates/base.html`. All templates extend the base template for consistent styling.

## Regional Configuration

The system supports multiple regions (SW, SE, NC, NW, NE) with state and LGA subdivision. Field agents are restricted to their assigned regions while administrators have full access.

## Security Considerations

- Plain text password storage (should be hashed in production)
- Session-based authentication
- File upload validation
- SQL injection protection via parameterized queries