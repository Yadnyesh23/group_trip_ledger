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
### 4. Logout

**POST** `api/v1/auth/logout`

**Request body**
No requets body

**Response body**
```json
{
  "status_code": 200,
  "message": "User logged out successfully"
}
```

### 5. Get access token using refresh token
**POST** `api/v1/auth/refresh`

**Response Body**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5NGVhMjlmNC1kY2Y3LTRhYjMtYTM0Ni1jMDgwYzZjZTQ3Y2EiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzkwODU4Njc1fQ.ce3Dh6uHIxiNyFKWIHHf7c4o8l6OdPffFtLw7i03enY",
  "token_type": "bearer"
}
```


## Trip 

### 1. Get trips owned by users

**GET** `api/v1/trips`

**Response body**

```json
[
  {
    "id": "1ad76483-91c0-46f8-afba-f3528da2c7c4",
    "name": "Trip1",
    "description": "Trip 1",
    "location": "string",
    "start_date": "2026-10-01",
    "end_date": "2026-10-03",
    "is_completed": false,
    "owner_id": "94ea29f4-dcf7-4ab3-a346-c080c6ce47ca",
    "created_at": "2026-10-01T12:12:28.992407Z",
    "updated_at": "2026-10-01T12:12:28.992417Z"
  },
  {
    "id": "61ce8601-1e33-46f1-8e6c-a32ad27febfe",
    "name": "Trip2",
    "description": "Trip 2",
    "location": "string",
    "start_date": "2026-10-10",
    "end_date": "2026-10-15",
    "is_completed": false,
    "owner_id": "94ea29f4-dcf7-4ab3-a346-c080c6ce47ca",
    "created_at": "2026-10-01T12:12:50.579298Z",
    "updated_at": "2026-10-01T12:12:50.579302Z"
  }
]
```

### 2. Create Trips
**POST** `api/v1/trips`


**Request body**

```json
{
  "name": "Trip2",
  "description": "Trip 2",
  "location": "string",
  "start_date": "2026-10-10",
  "end_date": "2026-10-15"
}
```

**Response Body**
```json
{
  "status_code": 201,
  "message": "Trip created successfully",
  "data": {
    "id": "61ce8601-1e33-46f1-8e6c-a32ad27febfe",
    "name": "Trip2",
    "description": "Trip 2",
    "location": "string",
    "start_date": "2026-10-10",
    "end_date": "2026-10-15",
    "is_completed": false,
    "owner_id": "94ea29f4-dcf7-4ab3-a346-c080c6ce47ca",
    "created_at": "2026-10-01T12:12:50.579298Z",
    "updated_at": "2026-10-01T12:12:50.579302Z"
  }
}
```

### 3. Get trip by id
**GET** `api/v1/trips/{trip_id}`

**Response Body**
```json
{
  "status_code": 200,
  "message": "Trip fecthed succesfully.",
  "data": {
    "id": "61ce8601-1e33-46f1-8e6c-a32ad27febfe",
    "name": "Trip2",
    "description": "Trip 2",
    "location": "string",
    "start_date": "2026-10-10",
    "end_date": "2026-10-15",
    "is_completed": false,
    "owner_id": "94ea29f4-dcf7-4ab3-a346-c080c6ce47ca",
    "created_at": "2026-10-01T12:12:50.579298Z",
    "updated_at": "2026-10-01T12:12:50.579302Z"
  }
}
```

### 4. Update trip

**PATCH** `api/v1/trips/{trip_id}`

**Request Body**
```json
{
  "is_completed":true
}
```

**Response body**
```json
{
  "status_code": 0,
  "message": "string",
  "data": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "string",
    "description": "string",
    "location": "string",
    "start_date": "2026-10-01",
    "end_date": "2026-10-01",
    "is_completed": true,
    "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "created_at": "2026-10-01T12:22:16.803Z",
    "updated_at": "2026-10-01T12:22:16.803Z"
  }
}
```

### 5. Delete Trip 

**DELETE** `api/v1/trips/{trip_id}`


**Response Body**
```json
{
  "status_code": 200,
  "message": "Trip deleted successfully"
}
```