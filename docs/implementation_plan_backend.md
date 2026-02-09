# Backend Basic Structure Implementation Plan

## Overview
This plan outlines the implementation of the basic backend structure using FastAPI with a User model as the initial example.

## Technology Stack
- Python 3.12
- uv for project management (pyproject.toml)
- FastAPI for web framework
- SQLAlchemy (async) for ORM
- Alembic for database migrations
- PostgreSQL for database
- Pydantic for validation
- JWT authentication with cookies
- Sentry for error tracking
- ruff for linting and formatting
- ty for CLI linting

## Project Structure

```
backend/
├── pyproject.toml              # Project dependencies managed by uv
├── alembic.ini                 # Alembic configuration
├── .env.example                # Example environment variables
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Application configuration (pydantic-settings)
│   ├── database.py             # Database connection and session management
│   ├── dependencies.py         # Dependency injection providers
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py         # JWT and password hashing utilities
│   │   ├── exceptions.py       # Custom exception classes
│   │   ├── middleware.py       # Custom middleware (error handling, etc.)
│   │   └── storage.py          # File storage utilities
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py             # SQLAlchemy base model
│   │   └── user.py             # User SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py             # Base pydantic schemas
│   │   └── user.py             # User pydantic schemas (input/output)
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py             # Base repository with CRUD operations
│   │   └── user.py             # User repository
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── user/               # User-related workflows (one file per workflow)
│   │       ├── __init__.py
│   │       ├── register.py     # RegisterWorkflow (user registration)
│   │       └── login.py        # LoginWorkflow (user login)
│   └── api/
│       ├── __init__.py
│       ├── router.py           # Main API router
│       ├── auth.py             # Auth endpoints (login, logout, register)
│       └── users.py            # User endpoints
└── alembic/
    ├── versions/               # Migration files
    └── env.py                  # Alembic environment configuration
```

## Implementation Steps

### 1. Project Initialization
**Task**: Set up Python project with uv
- Initialize project with `uv init`
- Create `pyproject.toml` with all required dependencies
- Set up ruff configuration for linting/formatting
- Create `.env.example` file with environment variable templates
- Create basic `.gitignore` for Python projects

**Dependencies to add**:
```toml
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
alembic
asyncpg
pydantic
pydantic-settings
python-jose[cryptography]
passlib[bcrypt]
python-multipart
sentry-sdk[fastapi]
aiofiles
```

### 2. Database Configuration
**Task**: Set up async database connection and session management

**Files to create**:
- `app/database.py`: 
  - Async engine creation
  - AsyncSession factory
  - Base declarative class
  - Database dependency for FastAPI

**Key implementations**:
- Use `asyncpg` as the PostgreSQL driver
- Create async session factory with proper scoping
- Implement `get_db()` dependency function

### 3. Configuration Management
**Task**: Create configuration system using pydantic-settings

**Files to create**:
- `app/config.py`:
  - Database connection URL
  - JWT secret key and algorithm
  - Sentry DSN
  - CORS settings
  - Environment-based configuration (dev/prod)

### 4. Base Models and Schemas
**Task**: Create base classes for models and schemas

**Files to create**:
- `app/models/base.py`:
  - SQLAlchemy declarative base
  - Common fields (id, created_at, updated_at)
  - Async model base class

- `app/schemas/base.py`:
  - Base Pydantic schemas with common configurations
  - Standard response models

### 5. User Model
**Task**: Implement User model with SQLAlchemy

**Files to create**:
- `app/models/user.py`:
  - User table definition
  - Fields: id (UUID), email, hashed_password, full_name, is_active, is_verified, created_at, updated_at
  - Unique constraint on email
  - Indexes for common queries

### 6. User Schemas
**Task**: Create Pydantic schemas for User

**Files to create**:
- `app/schemas/user.py`:
  - `UserCreate`: Input schema for registration
  - `UserLogin`: Input schema for login
  - `UserUpdate`: Input schema for updates
  - `UserResponse`: Output schema (exclude password)
  - `UserInDB`: Internal schema with hashed_password

### 7. Base Repository
**Task**: Implement generic base repository with CRUD operations

**Files to create**:
- `app/repositories/base.py`:
  - Generic base class with type parameters
  - Async methods: `get()`, `get_by_id()`, `get_multi()`, `create()`, `update()`, `delete()`
  - Query builder helpers
  - Pagination support

### 8. User Repository
**Task**: Implement User-specific repository

**Files to create**:
- `app/repositories/user.py`:
  - Inherit from base repository
  - Additional methods: `get_by_email()`, `exists_by_email()`
  - User-specific query filters

### 9. Security Utilities
**Task**: Implement JWT and password hashing

**Files to create**:
- `app/core/security.py`:
  - Password hashing with passlib
  - Password verification
  - JWT token creation
  - JWT token validation
  - Get current user dependency

- `app/core/storage.py`:
  - File upload handling (async)
  - File download handling
  - File deletion
  - Generate unique file paths
  - File size validation
  - MIME type validation

### 10. User Workflows
**Task**: Implement business logic for user operations

Each workflow should be in a separate file. The workflows folder contains a subfolder per related model, with one workflow per file.

**Files to create**:
- `app/workflows/user/register.py`:
  - `RegisterWorkflow`: Handle user registration
    - Input: `RegisterInput` (wraps `UserCreate` schema)
    - Output: `RegisterOutput` (wraps `UserResponse` schema)
    - Logic: Validate email uniqueness, hash password, create user
- `app/workflows/user/login.py`:
  - `LoginWorkflow`: Handle user login
    - Input: `LoginInput` (wraps `UserLogin` schema)
    - Output: `LoginOutput` (access token + `UserResponse`)
    - Logic: Verify credentials, generate token
- All workflows should receive repository via dependency injection

### 11. Dependency Injection Setup
**Task**: Create dependency providers

**Files to create**:
- `app/dependencies.py`:
  - Repository factories (inject database session)
  - Workflow factories (inject repositories)
  - Current user dependency
  - Authentication dependencies

### 12. API Endpoints - Auth
**Task**: Implement authentication endpoints

**Files to create**:
- `app/api/auth.py`:
  - POST `/api/auth/register`: User registration (inject RegisterWorkflow)
  - POST `/api/auth/login`: User login (inject LoginWorkflow, set cookie)
  - POST `/api/auth/logout`: User logout (clear cookie)
  - GET `/api/auth/me`: Get current user (inject security dependency)

### 13. API Endpoints - Users
**Task**: Implement user management endpoints

**Files to create**:
- `app/api/users.py`:
  - GET `/api/users/{user_id}`: Get user by ID (inject repository directly)
  - GET `/api/users`: List users with pagination (inject repository directly)
  - PATCH `/api/users/{user_id}`: Update user (inject workflow if needed)

### 14. Main Application
**Task**: Set up FastAPI application

**Files to create**:
- `app/main.py`:
  - Create FastAPI app instance
  - Configure CORS
  - Include API routers
  - Add middleware (error handling, logging)
  - Initialize Sentry
  - Health check endpoint

- `app/api/router.py`:
  - Create main API router
  - Include auth and users routers with prefix `/api`

### 15. Database Migrations
**Task**: Set up Alembic for migrations

**Files to create**:
- `alembic.ini`: Alembic configuration
- `alembic/env.py`:
  - Import all models
  - Configure async migrations
  - Use database URL from config

**Commands to run**:
- `alembic init alembic`
- `alembic revision --autogenerate -m "Create user table"`
- `alembic upgrade head`

### 16. Error Handling
**Task**: Implement custom exceptions and handlers

**Files to create**:
- `app/core/exceptions.py`:
  - Custom exception classes (NotFoundError, ValidationError, AuthError)
  - Exception handlers for FastAPI

- `app/core/middleware.py`:
  - Error handling middleware
  - Request logging middleware

### 17. Testing Setup (Optional for basic structure)
**Task**: Add basic test structure

**Files to create**:
- `tests/conftest.py`: Test fixtures (test database, client)
- `tests/test_auth.py`: Basic auth endpoint tests
- `tests/test_users.py`: Basic user endpoint tests

## Environment Variables Required

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/lunchtogether

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage
UPLOAD_DIR=/var/www/lunchtogether/uploads
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes

# Sentry
SENTRY_DSN=your-sentry-dsn

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Environment
ENVIRONMENT=development
```

## Validation Checklist

- [ ] All database operations are async
- [ ] Repositories are injected into workflows
- [ ] Workflows are injected into endpoints
- [ ] All endpoints have Pydantic request/response models
- [ ] JWT tokens are stored in HTTP-only cookies
- [ ] Passwords are hashed using bcrypt
- [ ] Base repository implements all basic CRUD operations
- [ ] Proper error handling with custom exceptions
- [ ] Alembic migrations work correctly
- [ ] Code passes ruff linting and formatting
- [ ] Sentry is initialized for error tracking

## Next Steps After Implementation

1. Test all endpoints with sample data
2. Verify JWT authentication flow
3. Test database migrations (up and down)
4. Add more models as needed
5. Implement additional workflows
6. Add comprehensive unit and integration tests
