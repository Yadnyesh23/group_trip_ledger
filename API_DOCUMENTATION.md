# GroupTrip Ledger API Documentation

> **Note for Frontend Developers:** This documentation is generated directly from the active codebase of the GroupTrip Ledger FastAPI backend. It reflects all actual route definitions, authentication requirements, request payloads, response schemas, and membership-based financial abstractions (supporting both registered users and guest members).

---

## Complete API Summary Table

| # | Title | Method | Endpoint | Auth Required | Success Status |
|---|-------|--------|----------|---------------|----------------|
| 1 | Health Check | `GET` | `/api/v1/health` | No | `200 OK` |
| 2 | Register User | `POST` | `/api/v1/auth/register` | No | `200 OK` *(body: 201)* |
| 3 | Login User | `POST` | `/api/v1/auth/login` | No | `200 OK` |
| 4 | Get Current User Profile | `GET` | `/api/v1/auth/me` | Bearer JWT | `200 OK` |
| 5 | Logout User | `POST` | `/api/v1/auth/logout` | Bearer JWT | `200 OK` |
| 6 | Refresh Access Token | `POST` | `/api/v1/auth/refresh` | Refresh Token JWT | `200 OK` |
| 7 | Create Trip | `POST` | `/api/v1/trips` | Bearer JWT | `200 OK` *(body: 201)* |
| 8 | Get Trip by ID | `GET` | `/api/v1/trips/{trip_id}` | Bearer JWT | `200 OK` |
| 9 | Get All Trips Owned by User | `GET` | `/api/v1/trips` | Bearer JWT | `200 OK` |
| 10 | Update Trip | `PATCH` | `/api/v1/trips/{trip_id}` | Bearer JWT | `200 OK` *(body: 201)* |
| 11 | Delete Trip | `DELETE` | `/api/v1/trips/{trip_id}` | Bearer JWT | `200 OK` |
| 12 | Add Member to Trip | `POST` | `/api/v1/trips/{trip_id}/members` | Bearer JWT | `201 Created` |
| 13 | Get All Trip Members | `GET` | `/api/v1/trips/{trip_id}/members` | Bearer JWT | `200 OK` |
| 14 | Get Trip Member by ID | `GET` | `/api/v1/trips/{trip_id}/members/{member_id}` | Bearer JWT | `200 OK` |
| 15 | Remove Member from Trip | `DELETE` | `/api/v1/trips/{trip_id}/members/{member_id}` | Bearer JWT | `200 OK` |
| 16 | Create Expense | `POST` | `/api/v1/trips/{trip_id}/expenses` | Bearer JWT | `201 Created` |
| 17 | Get All Expenses for Trip | `GET` | `/api/v1/trips/{trip_id}/expenses` | Bearer JWT | `200 OK` |
| 18 | Get Expense by ID | `GET` | `/api/v1/trips/{trip_id}/expenses/{expense_id}` | Bearer JWT | `200 OK` |
| 19 | List Trip Balances | `GET` | `/trips/{trip_id}/balances/` | Bearer JWT | `200 OK` |
| 20 | Get Settlement Suggestions | `GET` | `/trips/{trip_id}/settlements/` | Bearer JWT | `200 OK` |
| 21 | Get Trip Report | `GET` | `/api/v1/trip/{trip_id}/reports/` | Bearer JWT | `200 OK` |
| 22 | Download Trip Report PDF | `GET` | `/api/v1/trip/{trip_id}/reports/pdf` | Bearer JWT | `200 OK` *(PDF Stream)* |

---

## Key Frontend Architecture Notes

### 1. Membership-Based Identification (`member_id` vs `user_id`)
In GroupTrip Ledger, financial transactions (expenses, splits, allocations, balances, settlements) operate on **Trip Membership IDs (`member_id`)**, not raw User IDs.
* **Registered Members**: Have both a `user_id` (UUID) and a `member_id` (UUID) for that trip.
* **Guest Members**: Have `user_id: null` and a `member_id` (UUID).
* When calling financial endpoints (e.g. creating expenses or listing allocations), **always use the `member_id`** returned by `/api/v1/trips/{trip_id}/members`.

### 2. Name Resolution (`user_name` / `display_name`)
The backend automatically resolves display names:
* If the member is a registered user, `user_name` contains the registered user's full name (`UserModel.name`).
* If the member is a guest, `user_name` contains the guest's `display_name`.

---

## 1. Health API

### 1.1 Health Check

- **Method:** `GET`
- **Endpoint:** `/api/v1/health`
- **Authentication:** None (Public)

#### Success Response (`200 OK`)
```json
{
  "status": 200,
  "message": "Database connection is successful"
}
```

#### Error Response (`503 Service Unavailable`)
```json
{
  "status": 503,
  "message": "Database connection is failed"
}
```

---

## 2. Authentication APIs

### 2.1 Register User

- **Method:** `POST`
- **Endpoint:** `/api/v1/auth/register`
- **Authentication:** None (Public)

#### Request Body
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secretpassword123"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `name` | string | Yes | None | User's full name |
| `email` | string | Yes | Valid email format | User's email address |
| `password` | string | Yes | None | User's password |

#### Success Response (`200 OK`)
```json
{
  "statuscode": 201,
  "message": "User registered successfully",
  "data": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-10-06T23:00:00Z",
    "updated_at": "2026-10-06T23:00:00Z"
  }
}
```

---

### 2.2 Login User

- **Method:** `POST`
- **Endpoint:** `/api/v1/auth/login`
- **Authentication:** None (Public)

#### Request Body
```json
{
  "email": "john@example.com",
  "password": "secretpassword123"
}
```

#### Success Response (`200 OK`)
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

---

### 2.3 Get Current User Profile

- **Method:** `GET`
- **Endpoint:** `/api/v1/auth/me`
- **Authentication:** Bearer JWT Access Token

#### Success Response (`200 OK`)
```json
{
  "status_code": 200,
  "message": "User fetched successfully",
  "data": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-10-06T23:00:00Z",
    "updated_at": "2026-10-06T23:00:00Z"
  }
}
```

---

### 2.4 Logout User

- **Method:** `POST`
- **Endpoint:** `/api/v1/auth/logout`
- **Authentication:** Bearer JWT Access Token

#### Success Response (`200 OK`)
```json
{
  "status_code": 200,
  "message": "User logged out successfully"
}
```

---

### 2.5 Refresh Access Token

- **Method:** `POST`
- **Endpoint:** `/api/v1/auth/refresh`
- **Authentication:** Bearer JWT Refresh Token

#### Success Response (`200 OK`)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 3. Trip APIs

### 3.1 Create Trip

- **Method:** `POST`
- **Endpoint:** `/api/v1/trips`
- **Authentication:** Bearer JWT Access Token

#### Request Body
```json
{
  "name": "Goa Vacation 2026",
  "description": "Annual beach trip",
  "location": "Goa, India",
  "start_date": "2026-10-10",
  "end_date": "2026-10-15"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Trip title |
| `description` | string / null | No | Optional trip description |
| `location` | string / null | No | Optional destination |
| `start_date` | string (ISO date) | Yes | Start date (`YYYY-MM-DD`) |
| `end_date` | string (ISO date) | Yes | End date (`YYYY-MM-DD`) |

#### Success Response (`200 OK`)
```json
{
  "status_code": 201,
  "message": "Trip created successfully",
  "data": {
    "id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
    "name": "Goa Vacation 2026",
    "description": "Annual beach trip",
    "location": "Goa, India",
    "start_date": "2026-10-10",
    "end_date": "2026-10-15",
    "is_completed": false,
    "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "owner_name": "John Doe",
    "created_at": "2026-10-10T10:00:00Z",
    "updated_at": "2026-10-10T10:00:00Z"
  }
}
```

---

### 3.2 Get Trip by ID

- **Method:** `GET`
- **Endpoint:** `/api/v1/trips/{trip_id}`
- **Authentication:** Bearer JWT Access Token

#### Success Response (`200 OK`)
```json
{
  "id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
  "name": "Goa Vacation 2026",
  "description": "Annual beach trip",
  "location": "Goa, India",
  "start_date": "2026-10-10",
  "end_date": "2026-10-15",
  "is_completed": false,
  "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "owner_name": "John Doe",
  "created_at": "2026-10-10T10:00:00Z",
  "updated_at": "2026-10-10T10:00:00Z"
}
```

---

### 3.3 Get All Trips Owned by User

- **Method:** `GET`
- **Endpoint:** `/api/v1/trips`
- **Authentication:** Bearer JWT Access Token

#### Success Response (`200 OK`)
```json
[
  {
    "id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
    "name": "Goa Vacation 2026",
    "description": "Annual beach trip",
    "location": "Goa, India",
    "start_date": "2026-10-10",
    "end_date": "2026-10-15",
    "is_completed": false,
    "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "owner_name": "John Doe",
    "created_at": "2026-10-10T10:00:00Z",
    "updated_at": "2026-10-10T10:00:00Z"
  }
]
```

---

### 3.4 Update Trip

- **Method:** `PATCH`
- **Endpoint:** `/api/v1/trips/{trip_id}`
- **Authentication:** Bearer JWT Access Token

#### Request Body
```json
{
  "name": "Goa Trip 2026",
  "is_completed": true
}
```

#### Success Response (`200 OK`)
```json
{
  "status_code": 201,
  "message": "Trip updated succesfully.",
  "data": {
    "id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
    "name": "Goa Trip 2026",
    "description": "Annual beach trip",
    "location": "Goa, India",
    "start_date": "2026-10-10",
    "end_date": "2026-10-15",
    "is_completed": true,
    "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "owner_name": "John Doe",
    "created_at": "2026-10-10T10:00:00Z",
    "updated_at": "2026-10-10T10:30:00Z"
  }
}
```

---

### 3.5 Delete Trip

- **Method:** `DELETE`
- **Endpoint:** `/api/v1/trips/{trip_id}`
- **Authentication:** Bearer JWT Access Token

#### Success Response (`200 OK`)
```json
{
  "status_code": 200,
  "message": "Trip deleted successfully"
}
```

---

## 4. Trip Membership APIs

### 4.1 Add Member to Trip (Registered User or Guest)

- **Method:** `POST`
- **Endpoint:** `/api/v1/trips/{trip_id}/members`
- **Authentication:** Bearer JWT Access Token

#### Request Body
```json
{
  "display_name": "Alice Smith"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `display_name` | string | Yes | `min_length=1`, `max_length=100` | Name of the trip member |

#### Success Response (`201 Created`)
```json
{
  "status_code": 201,
  "message": "Member added successfully",
  "data": {
    "id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
    "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
    "user_id": null,
    "user_name": "Alice Smith",
    "joined_at": "2026-10-10",
    "left_at": null,
    "status": "ACTIVE",
    "created_at": "2026-10-10T10:00:00Z",
    "updated_at": "2026-10-10T10:00:00Z"
  }
}
```

---

### 4.2 Get All Trip Members

- **Method:** `GET`
- **Endpoint:** `/api/v1/trips/{trip_id}/members`
- **Authentication:** Bearer JWT Access Token

#### Success Response (`200 OK`)
```json
{
  "members": [
    {
      "id": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
      "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
      "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "user_name": "John Doe",
      "joined_at": "2026-10-10",
      "left_at": null,
      "status": "ACTIVE",
      "created_at": "2026-10-10T10:00:00Z",
      "updated_at": "2026-10-10T10:00:00Z"
    },
    {
      "id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
      "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
      "user_id": null,
      "user_name": "Alice Smith",
      "joined_at": "2026-10-10",
      "left_at": null,
      "status": "ACTIVE",
      "created_at": "2026-10-10T10:05:00Z",
      "updated_at": "2026-10-10T10:05:00Z"
    }
  ]
}
```

---

### 4.3 Get Trip Member by ID

- **Method:** `GET`
- **Endpoint:** `/api/v1/trips/{trip_id}/members/{member_id}`
- **Authentication:** Bearer JWT Access Token
- **Path Parameter:** `member_id` is the **trip membership UUID** (`TripMembershipModel.id`).

#### Success Response (`200 OK`)
```json
{
  "id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
  "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
  "user_id": null,
  "user_name": "Alice Smith",
  "joined_at": "2026-10-10",
  "left_at": null,
  "status": "ACTIVE",
  "created_at": "2026-10-10T10:05:00Z",
  "updated_at": "2026-10-10T10:05:00Z"
}
```

---

### 4.4 Remove Member from Trip

- **Method:** `DELETE`
- **Endpoint:** `/api/v1/trips/{trip_id}/members/{member_id}`
- **Authentication:** Bearer JWT Access Token
- **Path Parameter:** `member_id` is the **trip membership UUID**.

#### Success Response (`200 OK`)
```json
{
  "id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
  "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
  "user_id": null,
  "user_name": "Alice Smith",
  "joined_at": "2026-10-10",
  "left_at": "2026-10-10",
  "status": "LEFT",
  "created_at": "2026-10-10T10:05:00Z",
  "updated_at": "2026-10-10T10:15:00Z"
}
```

---

## 5. Expense APIs

### 5.1 Create Expense

- **Method:** `POST`
- **Endpoint:** `/api/v1/trips/{trip_id}/expenses`
- **Authentication:** Bearer JWT Access Token

#### Request Body (Equal Split)
```json
{
  "name": "Seafood Dinner",
  "description": "Beach shack dinner",
  "amount": 1500.00,
  "split_type": "EQUAL",
  "category": "Food",
  "paid_by_member_id": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
  "participant_member_ids": [
    "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
    "f9e8d7c6-b5a4-3210-9876-543210fedcba"
  ],
  "expense_date": "2026-10-10"
}
```

#### Request Body (Custom Split)
```json
{
  "name": "Taxi Fare",
  "description": "Airport pickup",
  "amount": 1000.00,
  "split_type": "CUSTOM",
  "category": "Travel",
  "paid_by_member_id": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
  "participant_member_ids": [
    "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
    "f9e8d7c6-b5a4-3210-9876-543210fedcba"
  ],
  "custom_allocation": {
    "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d": 600.00,
    "f9e8d7c6-b5a4-3210-9876-543210fedcba": 400.00
  },
  "expense_date": "2026-10-10"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Title of expense |
| `description` | string / null | No | Optional notes |
| `amount` | number (gt=0) | Yes | Total cost |
| `split_type` | string | Yes | Must be `"EQUAL"` or `"CUSTOM"` |
| `category` | string / null | No | Category tag |
| `paid_by_member_id` | UUID | Yes | **Trip Membership UUID** of payer |
| `participant_member_ids` | list[UUID] | Yes | **Trip Membership UUIDs** sharing cost |
| `custom_allocation` | dict[UUID, Decimal] / null | No | Dict of `member_id -> amount` (Required if `"CUSTOM"`) |
| `expense_date` | string (ISO date) | Yes | Date of expense |

#### Success Response (`201 Created`)
```json
{
  "id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
  "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
  "name": "Seafood Dinner",
  "description": "Beach shack dinner",
  "amount": 1500.00,
  "split_type": "EQUAL",
  "category": "Food",
  "paid_by_member_id": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
  "paid_by_name": "John Doe",
  "expense_date": "2026-10-10",
  "created_at": "2026-10-10T10:10:00Z",
  "updated_at": "2026-10-10T10:10:00Z"
}
```

---

### 5.2 Get All Expenses for Trip

- **Method:** `GET`
- **Endpoint:** `/api/v1/trips/{trip_id}/expenses`
- **Authentication:** Bearer JWT Access Token

#### Success Response (`200 OK`)
```json
{
  "total_expenses": 1,
  "expenses": [
    {
      "id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
      "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
      "name": "Seafood Dinner",
      "description": "Beach shack dinner",
      "amount": 1500.00,
      "split_type": "EQUAL",
      "category": "Food",
      "paid_by_member_id": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
      "paid_by_name": "John Doe",
      "expense_date": "2026-10-10",
      "created_at": "2026-10-10T10:10:00Z",
      "updated_at": "2026-10-10T10:10:00Z"
    }
  ]
}
```

---

### 5.3 Get Expense by ID

- **Method:** `GET`
- **Endpoint:** `/api/v1/trips/{trip_id}/expenses/{expense_id}`
- **Authentication:** Bearer JWT Access Token

#### Success Response (`200 OK`)
```json
{
  "id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
  "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
  "name": "Seafood Dinner",
  "description": "Beach shack dinner",
  "amount": 1500.00,
  "split_type": "EQUAL",
  "category": "Food",
  "paid_by_member_id": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
  "paid_by_name": "John Doe",
  "expense_date": "2026-10-10",
  "created_at": "2026-10-10T10:10:00Z",
  "updated_at": "2026-10-10T10:10:00Z"
}
```

---

## 6. Balance APIs

### 6.1 List Trip Balances

- **Method:** `GET`
- **Endpoint:** `/trips/{trip_id}/balances/`
- **Authentication:** Bearer JWT Access Token

#### Success Response (`200 OK`)
```json
{
  "balances": [
    {
      "member_id": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
      "member_name": "John Doe",
      "balance": 750.00
    },
    {
      "member_id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
      "member_name": "Alice Smith",
      "balance": -750.00
    }
  ]
}
```

---

## 7. Settlement APIs

### 7.1 Get Settlement Suggestions

- **Method:** `GET`
- **Endpoint:** `/trips/{trip_id}/settlements/`
- **Authentication:** Bearer JWT Access Token

#### Success Response (`200 OK`)
```json
{
  "settlements": [
    {
      "payer": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
      "payer_name": "Alice Smith",
      "payee": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
      "payee_name": "John Doe",
      "amount": 750.00
    }
  ]
}
```

---

## 8. Report APIs

### 8.1 Get Trip Report

- **Method:** `GET`
- **Endpoint:** `/api/v1/trip/{trip_id}/reports/`
- **Authentication:** Bearer JWT Access Token

#### Success Response (`200 OK`)
```json
{
  "members": {
    "members": [
      {
        "id": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
        "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "user_name": "John Doe",
        "joined_at": "2026-10-10",
        "left_at": null,
        "status": "ACTIVE",
        "created_at": "2026-10-10T10:00:00Z",
        "updated_at": "2026-10-10T10:00:00Z"
      },
      {
        "id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
        "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
        "user_id": null,
        "user_name": "Alice Smith",
        "joined_at": "2026-10-10",
        "left_at": null,
        "status": "ACTIVE",
        "created_at": "2026-10-10T10:05:00Z",
        "updated_at": "2026-10-10T10:05:00Z"
      }
    ]
  },
  "expenses": {
    "total_expenses": 1,
    "expenses": [
      {
        "id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
        "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
        "name": "Seafood Dinner",
        "description": "Beach shack dinner",
        "amount": 1500.00,
        "split_type": "EQUAL",
        "category": "Food",
        "paid_by_member_id": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
        "paid_by_name": "John Doe",
        "expense_date": "2026-10-10",
        "allocations": [
          {
            "member_id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
            "member_name": "Alice Smith",
            "amount": 750.00
          }
        ]
      }
    ]
  },
  "balances": {
    "balances": [
      {
        "member_id": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
        "member_name": "John Doe",
        "balance": 750.00
      },
      {
        "member_id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
        "member_name": "Alice Smith",
        "balance": -750.00
      }
    ]
  },
  "settlements": {
    "settlements": [
      {
        "payer": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
        "payer_name": "Alice Smith",
        "payee": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
        "payee_name": "John Doe",
        "amount": 750.00
      }
    ]
  }
}
```

---

### 8.2 Download Trip Report PDF

- **Method:** `GET`
- **Endpoint:** `/api/v1/trip/{trip_id}/reports/pdf`
- **Authentication:** Bearer JWT Access Token
- **Media Type:** `application/pdf`
- **Header:** `Content-Disposition: attachment; filename="trip_report_{trip_id}.pdf"`
- **Response:** Binary PDF stream.
