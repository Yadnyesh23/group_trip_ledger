# Endpoints

## Authentication

### 1. Register User

**POST** `/api/v1/auth/register`

**Request Body**
```json
{
  "name": "user5",
  "email": "user5@example.com",
  "password": "user5"
}
```

**Response Body**
```json
{
  "statuscode": 201,
  "message": "User registered successfully",
  "data": {
    "id": "3fee2a02-e5c1-4835-994e-97a6cf012b8b",
    "name": "user5",
    "email": "user5@example.com",
    "created_at": "2026-09-10T04:50:37.402476Z",
    "updated_at": "2026-09-10T04:50:37.402480Z"
  }
}
```

---

### 2. Login User

**POST** `/api/v1/auth/login`

**Request Body**
```json
{
  "email": "user5@example.com",
  "password": "user5"
}
```

**Response Body**
```json
{
  "statuscode": 200,
  "message": "User logged in successfully",
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

### 3. Get Me

**POST** `/api/v1/auth/me`

**Response Body**
```json
{
  "status_code": 200,
  "message": "User fetched successfully",
  "data": {
    "id": "da76cbab-3787-479b-928e-1f0d09bd2d57",
    "name": "user1",
    "email": "user1@example.com",
    "created_at": "2026-09-09T18:22:48.958602Z",
    "updated_at": "2026-09-09T18:22:48.958605Z"
  }
}
```