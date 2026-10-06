# GroupTrip Ledger API Documentation

> **Note:** This documentation is generated strictly from the active codebase of the FastAPI backend. It reflects actual implementation, route definitions, schemas, services, and dependencies.

---
    
## Complete API Summary Table

| # | Title | Method | Endpoint | Auth Required | Success Status |
|---|-------|--------|----------|---------------|----------------|
| 1 | Health Check | `GET` | `/api/v1/health` | No | 200 OK |
| 2 | Register User | `POST` | `/api/v1/auth/register` | No | 200 OK *(Field says 201)* |
| 3 | Login User | `POST` | `/api/v1/auth/login` | No | 200 OK |
| 4 | Get Current User Profile | `GET` | `/api/v1/auth/me` | Bearer JWT | 200 OK *(Inferred)* |
| 5 | Logout User | `POST` | `/api/v1/auth/logout` | Bearer JWT | 200 OK *(Inferred)* |
| 6 | Refresh Access Token | `POST` | `/api/v1/auth/refresh` | Refresh Token JWT | 200 OK *(Inferred)* |
| 7 | Create Trip | `POST` | `/api/v1/trips` | Bearer JWT | 200 OK *(Field says 201)* |
| 8 | Get Trip by ID | `GET` | `/api/v1/trips/{trip_id}` | Bearer JWT | 200 OK |
| 9 | Get All Trips Owned by User | `GET` | `/api/v1/trips` | Bearer JWT | 200 OK |
| 10 | Update Trip | `PATCH` | `/api/v1/trips/{trip_id}` | Bearer JWT | 200 OK *(Field says 201)* |
| 11 | Delete Trip | `DELETE` | `/api/v1/trips/{trip_id}` | Bearer JWT | 200 OK *(Inferred)* |
| 12 | Add Member to Trip | `POST` | `/api/v1/trips/{trip_id}/members` | Bearer JWT | 200 OK *(Field says 201)* |
| 13 | Get All Trip Members | `GET` | `/api/v1/trips/{trip_id}/members` | Bearer JWT | 200 OK |
| 14 | Get Trip Member by ID | `GET` | `/api/v1/trips/{trip_id}/members/{member_id}` | Bearer JWT | 200 OK |
| 15 | Remove Member from Trip | `DELETE` | `/api/v1/trips/{trip_id}/members/{member_id}` | Bearer JWT | 200 OK |
| 16 | Create Expense | `POST` | `/api/v1/trips/{trip_id}/expenses` | Bearer JWT | 201 Created |
| 17 | Get All Expenses for Trip | `GET` | `/api/v1/trips/{trip_id}/expenses` | Bearer JWT | 200 OK |
| 18 | Get Expense by ID | `GET` | `/api/v1/trips/{trip_id}/expenses/{expense_id}` | Bearer JWT | 200 OK |
| 19 | List Trip Balances | `GET` | `/trips/{trip_id}/balances/` | Bearer JWT | 200 OK *(Inferred)* |
| 20 | Get Settlement Suggestions | `GET` | `/trips/{trip_id}/settlements/` | Bearer JWT | 200 OK *(Inferred)* |

---

## 1. Health API

### 1.1 Health Check

- **METHOD:** `GET`
- **ENDPOINT:** `/api/v1/health`
- **Purpose:** Checks the database connection health status.
- **Authentication:** Not required
- **Authorization Rules:** None (Public)
- **Path Parameters:** None
- **Query Parameters:** None
- **Request Body:** None

#### Success Response
- **Status Code:** `200 OK`
- **Declared Response Model:** `HealthCheckResponse`

```json
{
  "status": 200,
  "message": "Database connection is successful"
}
```

**Field Definition:**
| Field | Type | Description |
|-------|------|-------------|
| `status` | integer | HTTP status code (200 or 503) |
| `message` | string | Health message (`Database connection is successful` or `Database connection is failed`) |

#### Error Responses
- **`503 Service Unavailable`** (Database check failed):
```json
{
  "status": 503,
  "message": "Database connection is failed"
}
```

---

## 2. Authentication APIs

### 2.1 Register User

- **METHOD:** `POST`
- **ENDPOINT:** `/api/v1/auth/register`
- **Purpose:** Register a new user with name, email, and password.
- **Authentication:** Not required
- **Authorization Rules:** None (Public)
- **Path Parameters:** None
- **Query Parameters:** None

#### Request Body
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secretpassword123"
}
```

**Request Schema (`RegisterRequest`):**
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `name` | string | Yes | None | Full name of the user |
| `email` | string | Yes | Valid email format (`EmailStr`) | Unique user email address |
| `password` | string | Yes | None | User password |

#### Success Response
- **Status Code:** `200 OK` *(Note: HTTP header status is 200 OK; body contains `statuscode: 201`)*
- **Declared Response Model:** `RegisterResponse`

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

**Response Schema (`RegisterResponse`):**
| Field | Type | Description |
|-------|------|-------------|
| `statuscode` | integer | Status code number (Note typo in field name: `statuscode` instead of `status_code`) |
| `message` | string | Status description |
| `data` | object (`UserResponse`) | Registered user object |
| `data.id` | UUID | Generated user ID |
| `data.name` | string | User full name |
| `data.email` | string | User email address |
| `data.created_at` | datetime | Timestamp of user creation |
| `data.updated_at` | datetime | Timestamp of user profile update |

#### Error Responses
- **`422 Unprocessable Entity`** (Validation error on email format or missing fields):
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```
- **`500 Internal Server Error`** *(Backend Implementation Issue)*: `AuthService.register_user` raises an unhandled `ValueError("User already exists")` when duplicate email is submitted.

---

### 2.2 Login User

- **METHOD:** `POST`
- **ENDPOINT:** `/api/v1/auth/login`
- **Purpose:** Authenticate user credentials and return access and refresh tokens.
- **Authentication:** Not required
- **Authorization Rules:** None (Public)
- **Path Parameters:** None
- **Query Parameters:** None

#### Request Body
```json
{
  "email": "john@example.com",
  "password": "secretpassword123"
}
```

**Request Schema (`LoginRequest`):**
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `email` | string | Yes | Valid email format (`EmailStr`) | User email address |
| `password` | string | Yes | None | User password |

#### Success Response
- **Status Code:** `200 OK`
- **Declared Response Model:** `LoginResponse`

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

**Response Schema (`LoginResponse`):**
| Field | Type | Description |
|-------|------|-------------|
| `statuscode` | integer | Status code (Note typo in field name: `statuscode`) |
| `message` | string | Response message |
| `tokens` | object (`TokenResponse`) | JWT token pair |
| `tokens.access_token` | string | JWT Access Token |
| `tokens.refresh_token` | string | JWT Refresh Token |
| `tokens.token_type` | string | Token type (Default: `"bearer"`) |

#### Error Responses
- **`422 Unprocessable Entity`** (Invalid email or missing fields)
- **`500 Internal Server Error`** *(Backend Implementation Issue)*: `AuthService.login_user` raises an unhandled `ValueError("Invalid email or password")` when credentials are invalid.

---

### 2.3 Get Current User Profile

- **METHOD:** `GET`
- **ENDPOINT:** `/api/v1/auth/me`
- **Purpose:** Fetch the profile details of the currently authenticated user.
- **Authentication:** Bearer JWT required (`get_current_user` dependency)
- **Authorization Rules:** User must present a valid, non-expired Bearer Access Token in `Authorization` header.
- **Path Parameters:** None
- **Query Parameters:** None
- **Request Body:** None

#### Success Response
- **Status Code:** `200 OK` *(Inferred)*
- **Declared Response Model:** None *(Inferred from `MeResponse` instantiation in route handler)*

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

**Inferred Response Schema (`MeResponse`):**
| Field | Type | Description |
|-------|------|-------------|
| `status_code` | integer | HTTP status code (200) |
| `message` | string | Response message |
| `data` | object (`UserResponse`) | User profile object |
| `data.id` | UUID | User ID |
| `data.name` | string | User name |
| `data.email` | string | User email address |
| `data.created_at` | datetime | Creation timestamp |
| `data.updated_at` | datetime | Update timestamp |

#### Error Responses
- **`401 Unauthorized`** (Invalid or missing JWT token):
```json
{
  "detail": "Invalid token"
}
```

---

### 2.4 Logout User

- **METHOD:** `POST`
- **ENDPOINT:** `/api/v1/auth/logout`
- **Purpose:** Revoke all refresh tokens associated with the current user.
- **Authentication:** Bearer JWT required (`get_current_user` dependency)
- **Authorization Rules:** User must present a valid Bearer Access Token.
- **Path Parameters:** None
- **Query Parameters:** None
- **Request Body:** None

#### Success Response
- **Status Code:** `200 OK` *(Inferred)*
- **Declared Response Model:** None *(Inferred from `LogoutResponse` instantiation)*

```json
{
  "status_code": 200,
  "message": "User logged out successfully"
}
```

**Inferred Response Schema (`LogoutResponse`):**
| Field | Type | Description |
|-------|------|-------------|
| `status_code` | integer | HTTP status code (200) |
| `message` | string | Confirmation message |

#### Error Responses
- **`401 Unauthorized`**:
```json
{
  "detail": "Invalid token"
}
```

---

### 2.5 Refresh Access Token

- **METHOD:** `POST`
- **ENDPOINT:** `/api/v1/auth/refresh`
- **Purpose:** Generate a new JWT access token using a valid, non-revoked refresh token.
- **Authentication:** Bearer JWT required (`get_user_from_refresh_token` dependency)
- **Authorization Rules:** Header must contain a valid refresh token (`type: "refresh"`) that is present in the database and not marked `revoked`.
- **Path Parameters:** None
- **Query Parameters:** None
- **Request Body:** None

#### Success Response
- **Status Code:** `200 OK` *(Inferred)*
- **Declared Response Model:** None *(Inferred from return dictionary in route)*

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Inferred Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | Newly generated access token |
| `token_type` | string | Token type (`bearer`) |

#### Error Responses
- **`401 Unauthorized`**:
```json
{
  "detail": "Invalid refresh token"
}
```
or
```json
{
  "detail": "Refresh token has been revoked"
}
```

---

## 3. Trip APIs

### 3.1 Create Trip

- **METHOD:** `POST`
- **ENDPOINT:** `/api/v1/trips`
- **Purpose:** Create a new group trip. Automatically adds the current user as the trip owner and active member.
- **Authentication:** Bearer JWT required (`get_current_user`)
- **Authorization Rules:** Authenticated user becomes the owner of the created trip.
- **Path Parameters:** None
- **Query Parameters:** None

#### Request Body
```json
{
  "name": "Goa Trip 2026",
  "description": "Annual vacation with friends",
  "location": "Goa, India",
  "start_date": "2026-10-10",
  "end_date": "2026-10-15"
}
```

**Request Schema (`CreateTripRequest`):**
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `name` | string | Yes | None | Name of the trip |
| `description` | string/null | No | Default: `null` | Optional description |
| `location` | string/null | No | Default: `null` | Optional location |
| `start_date` | string (date) | Yes | ISO date format (`YYYY-MM-DD`) | Trip start date |
| `end_date` | string (date) | Yes | ISO date format (`YYYY-MM-DD`) | Trip end date |

#### Success Response
- **Status Code:** `200 OK` *(Note: HTTP header status is 200; JSON body has `status_code: 201`)*
- **Declared Response Model:** `CreateTripResponse`

```json
{
  "status_code": 201,
  "message": "Trip created successfully",
  "data": {
    "id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
    "name": "Goa Trip 2026",
    "description": "Annual vacation with friends",
    "location": "Goa, India",
    "start_date": "2026-10-10",
    "end_date": "2026-10-15",
    "is_completed": false,
    "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "created_at": "2026-10-06T23:00:00Z",
    "updated_at": "2026-10-06T23:00:00Z"
  }
}
```

**Response Schema (`CreateTripResponse`):**
| Field | Type | Description |
|-------|------|-------------|
| `status_code` | integer | Status code (201) |
| `message` | string | Status message |
| `data` | object (`TripResponse`) | Created trip object |
| `data.id` | UUID | Unique trip ID |
| `data.name` | string | Trip name |
| `data.description` | string/null | Trip description |
| `data.location` | string/null | Trip location |
| `data.start_date` | string (date) | Trip start date |
| `data.end_date` | string (date) | Trip end date |
| `data.is_completed` | boolean | Completion status (default `false`) |
| `data.owner_id` | UUID | Owner user ID |
| `data.created_at` | datetime | Creation timestamp |
| `data.updated_at` | datetime | Last updated timestamp |

#### Error Responses
- **`400 Bad Request`** (Invalid date range):
```json
{
  "detail": "Start date cannot be after end date"
}
```
- **`401 Unauthorized`** (Invalid/missing token)
- **`422 Unprocessable Entity`** (Validation failure)

---

### 3.2 Get Trip by ID

- **METHOD:** `GET`
- **ENDPOINT:** `/api/v1/trips/{trip_id}`
- **Purpose:** Retrieve trip details by trip UUID.
- **Authentication:** Bearer JWT required (`get_current_user`)
- **Authorization Rules:** Currently, ONLY the trip owner (`trip.owner_id == current_user.id`) can fetch trip details. *(Note: Non-owner members get 403 Forbidden)*.
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `trip_id` | UUID | Yes | Target trip UUID |
- **Query Parameters:** None
- **Request Body:** None

#### Success Response
- **Status Code:** `200 OK`
- **Declared Response Model:** `TripResponse`

```json
{
  "id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
  "name": "Goa Trip 2026",
  "description": "Annual vacation with friends",
  "location": "Goa, India",
  "start_date": "2026-10-10",
  "end_date": "2026-10-15",
  "is_completed": false,
  "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "created_at": "2026-10-06T23:00:00Z",
  "updated_at": "2026-10-06T23:00:00Z"
}
```

**Response Schema (`TripResponse`):**
| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Trip ID |
| `name` | string | Trip name |
| `description` | string/null | Trip description |
| `location` | string/null | Trip location |
| `start_date` | date | Start date |
| `end_date` | date | End date |
| `is_completed` | boolean | Completion flag |
| `owner_id` | UUID | Owner user ID |
| `created_at` | datetime | Created timestamp |
| `updated_at` | datetime | Updated timestamp |

#### Error Responses
- **`403 Forbidden`** (Logged in user is not the trip owner):
```json
{
  "detail": "You do not have access to this trip"
}
```
- **`404 Not Found`** (Trip does not exist):
```json
{
  "detail": "Trip not found"
}
```
- **`401 Unauthorized`**

---

### 3.3 Get All Trips Owned by User

- **METHOD:** `GET`
- **ENDPOINT:** `/api/v1/trips`
- **Purpose:** Retrieve list of all trips where the authenticated user is the owner.
- **Authentication:** Bearer JWT required (`get_current_user`)
- **Authorization Rules:** Returns trips where `owner_id == current_user.id`.
- **Path Parameters:** None
- **Query Parameters:** None
- **Request Body:** None

#### Success Response
- **Status Code:** `200 OK`
- **Declared Response Model:** `list[TripResponse]`

```json
[
  {
    "id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
    "name": "Goa Trip 2026",
    "description": "Annual vacation with friends",
    "location": "Goa, India",
    "start_date": "2026-10-10",
    "end_date": "2026-10-15",
    "is_completed": false,
    "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "created_at": "2026-10-06T23:00:00Z",
    "updated_at": "2026-10-06T23:00:00Z"
  }
]
```

**Response Schema (`list[TripResponse]`):**
Array of `TripResponse` items.

#### Error Responses
- **`401 Unauthorized`**

---

### 3.4 Update Trip

- **METHOD:** `PATCH`
- **ENDPOINT:** `/api/v1/trips/{trip_id}`
- **Purpose:** Update specific fields of an existing trip.
- **Authentication:** Bearer JWT required (`get_current_user`)
- **Authorization Rules:** Only the trip owner (`trip.owner_id == current_user.id`) can update the trip.
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `trip_id` | UUID | Yes | Target trip UUID |
- **Query Parameters:** None

#### Request Body
```json
{
  "name": "Goa Trip 2026 (Updated)",
  "location": "North Goa",
  "is_completed": true
}
```

**Request Schema (`UpdateTripRequest`):**
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `name` | string/null | No | Optional | Updated name |
| `description` | string/null | No | Optional | Updated description |
| `location` | string/null | No | Optional | Updated location |
| `start_date` | string (date)/null | No | Optional | Updated start date |
| `end_date` | string (date)/null | No | Optional | Updated end date |
| `is_completed` | boolean/null | No | Optional | Trip completion flag |

#### Success Response
- **Status Code:** `200 OK` *(Note: HTTP status is 200 OK; JSON body has `status_code: 201`)*
- **Declared Response Model:** `UpdateTripResponse`

```json
{
  "status_code": 201,
  "message": "Trip updated succesfully.",
  "data": {
    "id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
    "name": "Goa Trip 2026 (Updated)",
    "description": "Annual vacation with friends",
    "location": "North Goa",
    "start_date": "2026-10-10",
    "end_date": "2026-10-15",
    "is_completed": true,
    "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "created_at": "2026-10-06T23:00:00Z",
    "updated_at": "2026-10-06T23:10:00Z"
  }
}
```

**Response Schema (`UpdateTripResponse`):**
| Field | Type | Description |
|-------|------|-------------|
| `status_code` | integer | Status code (201) |
| `message` | string | Status message (Note typo: `succesfully.`) |
| `data` | object (`TripResponse`) | Updated trip details |

#### Error Responses
- **`400 Bad Request`** (No fields supplied or invalid dates):
```json
{
  "detail": "No fields provided for update"
}
```
- **`403 Forbidden`** (Non-owner):
```json
{
  "detail": "Only the trip owner can update this trip"
}
```
- **`404 Not Found`** (Trip not found):
```json
{
  "detail": "Trip not found"
}
```
- **`401 Unauthorized`**

---

### 3.5 Delete Trip

- **METHOD:** `DELETE`
- **ENDPOINT:** `/api/v1/trips/{trip_id}`
- **Purpose:** Delete a trip by ID.
- **Authentication:** Bearer JWT required (`get_current_user`)
- **Authorization Rules:** Only the trip owner can delete the trip.
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `trip_id` | UUID | Yes | Target trip UUID |
- **Query Parameters:** None
- **Request Body:** None

#### Success Response
- **Status Code:** `200 OK` *(Inferred)*
- **Declared Response Model:** None *(Inferred from raw dict return)*

```json
{
  "status_code": 200,
  "message": "Trip deleted successfully"
}
```

**Inferred Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `status_code` | integer | Status code (200) |
| `message` | string | Confirmation message |

#### Error Responses
- **`403 Forbidden`** (Non-owner):
```json
{
  "detail": "Only the trip owner can delete this trip"
}
```
- **`404 Not Found`** (Trip not found):
```json
{
  "detail": "Trip not found"
}
```
- **`401 Unauthorized`**

---

## 4. Trip Member APIs

### 4.1 Add Member to Trip

- **METHOD:** `POST`
- **ENDPOINT:** `/api/v1/trips/{trip_id}/members`
- **Purpose:** Add a registered user as an active member of a trip.
- **Authentication:** Bearer JWT required (`get_current_user`)
- **Authorization Rules:** Only the trip owner (`trip.owner_id == current_user.id`) can add members.
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `trip_id` | UUID | Yes | Trip UUID |
- **Query Parameters:** None

#### Request Body
```json
{
  "user_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
}
```

**Request Schema (`AddMemberRequest`):**
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `user_id` | UUID | Yes | Valid UUID | UUID of user to add as member |

#### Success Response
- **Status Code:** `200 OK` *(Note: Header is 200 OK; JSON body `status_code` is 201)*
- **Declared Response Model:** `AddTripMemberResponse`

```json
{
  "status_code": 201,
  "message": "Member added successfully",
  "data": {
    "id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
    "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
    "user_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "joined_at": "2026-10-06",
    "left_at": null,
    "status": "ACTIVE",
    "created_at": "2026-10-06T23:00:00Z",
    "updated_at": "2026-10-06T23:00:00Z"
  }
}
```

**Response Schema (`AddTripMemberResponse`):**
| Field | Type | Description |
|-------|------|-------------|
| `status_code` | integer | Status code (201) |
| `message` | string | Status description |
| `data` | object (`TripMemberResponse`) | Member record details |
| `data.id` | UUID | Membership record ID |
| `data.trip_id` | UUID | Trip ID |
| `data.user_id` | UUID | User ID of member |
| `data.joined_at` | string (date) | Date member joined trip |
| `data.left_at` | string (date)/null | Date member left trip |
| `data.status` | string | Status (`ACTIVE`) |
| `data.created_at` | datetime | Creation timestamp |
| `data.updated_at` | datetime | Update timestamp |

#### Error Responses
- **`403 Forbidden`** (Not the trip owner):
```json
{
  "detail": "Only the trip owner can add members"
}
```
- **`404 Not Found`** (Trip or User not found):
```json
{
  "detail": "Trip not found"
}
```
or
```json
{
  "detail": "User not found"
}
```
- **`409 Conflict`** (User is already a trip member):
```json
{
  "detail": "User is already a member of this trip"
}
```
- **`401 Unauthorized`**

---

### 4.2 Get All Trip Members

- **METHOD:** `GET`
- **ENDPOINT:** `/api/v1/trips/{trip_id}/members`
- **Purpose:** Get a list of all members registered for a trip.
- **Authentication:** Bearer JWT required (`get_current_user`)
- **Authorization Rules:** User must be authenticated. *(Note: Code currently does not verify if user is owner or member of the trip)*.
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `trip_id` | UUID | Yes | Target trip UUID |
- **Query Parameters:** None
- **Request Body:** None

#### Success Response
- **Status Code:** `200 OK`
- **Declared Response Model:** `TripMemberListResponse`

```json
{
  "members": [
    {
      "id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
      "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
      "user_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "joined_at": "2026-10-06",
      "left_at": null,
      "status": "ACTIVE",
      "created_at": "2026-10-06T23:00:00Z",
      "updated_at": "2026-10-06T23:00:00Z"
    }
  ]
}
```

**Response Schema (`TripMemberListResponse`):**
| Field | Type | Description |
|-------|------|-------------|
| `members` | array | List of `TripMemberResponse` objects |

#### Error Responses
- **`404 Not Found`** (Trip does not exist):
```json
{
  "detail": "Trip not found"
}
```
- **`401 Unauthorized`**

---

### 4.3 Get Trip Member by ID

- **METHOD:** `GET`
- **ENDPOINT:** `/api/v1/trips/{trip_id}/members/{member_id}`
- **Purpose:** Get specific trip member details by member user ID.
- **Authentication:** Bearer JWT required (`get_current_user`)
- **Authorization Rules:** User must be authenticated.
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `trip_id` | UUID | Yes | Trip UUID |
  | `member_id` | UUID | Yes | Member user UUID |
- **Query Parameters:** None
- **Request Body:** None

#### Success Response
- **Status Code:** `200 OK`
- **Declared Response Model:** `TripMemberResponse`

```json
{
  "id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
  "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
  "user_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "joined_at": "2026-10-06",
  "left_at": null,
  "status": "ACTIVE",
  "created_at": "2026-10-06T23:00:00Z",
  "updated_at": "2026-10-06T23:00:00Z"
}
```

**Response Schema (`TripMemberResponse`):**
See schema table in Section 4.1.

#### Error Responses
- **`404 Not Found`** (Trip or Member not found):
```json
{
  "detail": "Member not found"
}
```
- **`401 Unauthorized`**

---

### 4.4 Remove Member from Trip

- **METHOD:** `DELETE`
- **ENDPOINT:** `/api/v1/trips/{trip_id}/members/{member_id}`
- **Purpose:** Remove a member from a trip.
- **Authentication:** Bearer JWT required (`get_current_user`)
- **Authorization Rules:** Only the trip owner can remove members. Trip owner cannot remove themselves.
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `trip_id` | UUID | Yes | Trip UUID |
  | `member_id` | UUID | Yes | Member user UUID to remove |
- **Query Parameters:** None
- **Request Body:** None

#### Success Response
- **Status Code:** `200 OK`
- **Declared Response Model:** `TripMemberResponse`

```json
{
  "id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
  "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
  "user_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "joined_at": "2026-10-06",
  "left_at": "2026-10-06",
  "status": "REMOVED",
  "created_at": "2026-10-06T23:00:00Z",
  "updated_at": "2026-10-06T23:05:00Z"
}
```

**Response Schema (`TripMemberResponse`):**
See Section 4.1.

#### Error Responses
- **`400 Bad Request`** (Attempting to remove trip owner):
```json
{
  "detail": "Trip owner cannot be removed"
}
```
- **`403 Forbidden`** (Non-owner user):
```json
{
  "detail": "Only the trip owner can remove members"
}
```
- **`404 Not Found`** (Trip or Member not found):
```json
{
  "detail": "Member not found"
}
```
- **`401 Unauthorized`**

---

## 5. Expense APIs

### 5.1 Create Expense

- **METHOD:** `POST`
- **ENDPOINT:** `/api/v1/trips/{trip_id}/expenses`
- **Purpose:** Create a new expense for a trip with equal or custom split among active trip participants.
- **Authentication:** Bearer JWT required (`get_current_user`)
- **Authorization Rules:**
  - Only the trip owner (`trip.owner_id == current_user.id`) can create expenses.
  - The payer (`paid_by_user_id`) must be an active member of the trip.
  - All participants (`participant_user_ids`) must be active members of the trip.
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `trip_id` | UUID | Yes | Trip UUID |
- **Query Parameters:** None

#### Request Body (Equal Split Example)
```json
{
  "name": "Dinner at Beach Shack",
  "description": "Seafood dinner",
  "amount": 1500.00,
  "split_type": "EQUAL",
  "category": "Food",
  "paid_by_user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "participant_user_ids": [
    "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
  ],
  "expense_date": "2026-10-06"
}
```

#### Request Body (Custom Split Example)
```json
{
  "name": "Taxi Fare",
  "description": "Airport to hotel",
  "amount": 1000.00,
  "split_type": "CUSTOM",
  "category": "Travel",
  "paid_by_user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "participant_user_ids": [
    "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
  ],
  "custom_allocation": {
    "3fa85f64-5717-4562-b3fc-2c963f66afa6": 600.00,
    "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d": 400.00
  },
  "expense_date": "2026-10-06"
}
```

**Request Schema (`ExpenseCreateRequest`):**
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `name` | string | Yes | `min_length=1`, `max_length=100` | Expense title |
| `description` | string/null | No | Default `null`, `max_length=500` | Optional description |
| `amount` | number (Decimal) | Yes | `gt=0` (greater than 0) | Total expense amount |
| `split_type` | string (Enum) | Yes | Must be `"EQUAL"` or `"CUSTOM"` | Method of splitting expense |
| `category` | string/null | No | Default `null`, `max_length=100` | Category (e.g. Food, Travel) |
| `paid_by_user_id` | UUID | Yes | Valid UUID | User ID who paid for expense |
| `participant_user_ids` | array[UUID] | Yes | `min_length=1`, no duplicates | List of user IDs sharing cost |
| `custom_allocation` | dict[UUID, Decimal]/null | No | Required if `split_type` is `"CUSTOM"` | Map of user_id -> allocated amount |
| `expense_date` | string (date) | Yes | ISO date format | Date of expense |

#### Success Response
- **Status Code:** `201 Created`
- **Declared Response Model:** `ExpenseResponse`

```json
{
  "id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
  "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
  "name": "Dinner at Beach Shack",
  "description": "Seafood dinner",
  "amount": 1500.00,
  "split_type": "EQUAL",
  "category": "Food",
  "paid_by_user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "expense_date": "2026-10-06",
  "created_at": "2026-10-06T23:00:00Z",
  "updated_at": "2026-10-06T23:00:00Z"
}
```

**Response Schema (`ExpenseResponse`):**
| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Expense ID |
| `trip_id` | UUID | Trip ID |
| `name` | string | Expense name |
| `description` | string/null | Expense description |
| `amount` | number (Decimal) | Total amount |
| `split_type` | string | `"EQUAL"` or `"CUSTOM"` |
| `category` | string/null | Category string |
| `paid_by_user_id` | UUID | Payer user ID |
| `expense_date` | date | Date of expense |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Update timestamp |

#### Error Responses
- **`400 Bad Request`** (Invalid payer/participants or custom allocation mismatch):
```json
{
  "detail": "The payer is not an active member of the trip"
}
```
or
```json
{
  "detail": "Custom allocation total must equal expense amount"
}
```
- **`403 Forbidden`** (User is not trip owner):
```json
{
  "detail": "Only the trip owner can add expenses"
}
```
- **`404 Not Found`** (Trip not found):
```json
{
  "detail": "Trip not found"
}
```
- **`401 Unauthorized`**

---

### 5.2 Get All Expenses for Trip

- **METHOD:** `GET`
- **ENDPOINT:** `/api/v1/trips/{trip_id}/expenses`
- **Purpose:** Retrieve all expenses recorded for a trip.
- **Authentication:** Bearer JWT required (`get_current_user`)
- **Authorization Rules:** Only trip owner (`trip.owner_id == current_user.id`) can view trip expenses.
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `trip_id` | UUID | Yes | Trip UUID |
- **Query Parameters:** None
- **Request Body:** None

#### Success Response
- **Status Code:** `200 OK`
- **Declared Response Model:** `ExpenseListResponse`

```json
{
  "total_expenses": 1,
  "expenses": [
    {
      "id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
      "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
      "name": "Dinner at Beach Shack",
      "description": "Seafood dinner",
      "amount": 1500.00,
      "split_type": "EQUAL",
      "category": "Food",
      "paid_by_user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "expense_date": "2026-10-06",
      "created_at": "2026-10-06T23:00:00Z",
      "updated_at": "2026-10-06T23:00:00Z"
    }
  ]
}
```

**Response Schema (`ExpenseListResponse`):**
| Field | Type | Description |
|-------|------|-------------|
| `total_expenses` | integer | Total count of expenses |
| `expenses` | array | List of `ExpenseResponse` items |

#### Error Responses
- **`403 Forbidden`**:
```json
{
  "detail": "Only owner can see expenses"
}
```
- **`404 Not Found`** *(Note: Backend raises 404 if expenses list is empty!)*:
```json
{
  "detail": "Expenses list is empty"
}
```
or
```json
{
  "detail": "Trip not found"
}
```
- **`401 Unauthorized`**

---

### 5.3 Get Expense by ID

- **METHOD:** `GET`
- **ENDPOINT:** `/api/v1/trips/{trip_id}/expenses/{expense_id}`
- **Purpose:** Retrieve detailed info of a single expense.
- **Authentication:** Bearer JWT required (`get_current_user`)
- **Authorization Rules:** Only trip owner can view expense.
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `trip_id` | UUID | Yes | Trip UUID |
  | `expense_id` | UUID | Yes | Expense UUID |
- **Query Parameters:** None
- **Request Body:** None

#### Success Response
- **Status Code:** `200 OK`
- **Declared Response Model:** `ExpenseResponse`

```json
{
  "id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
  "trip_id": "e0b1c2d3-e4f5-4a6b-8c9d-0e1f2a3b4c5d",
  "name": "Dinner at Beach Shack",
  "description": "Seafood dinner",
  "amount": 1500.00,
  "split_type": "EQUAL",
  "category": "Food",
  "paid_by_user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "expense_date": "2026-10-06",
  "created_at": "2026-10-06T23:00:00Z",
  "updated_at": "2026-10-06T23:00:00Z"
}
```

**Response Schema (`ExpenseResponse`):**
See Section 5.1.

#### Error Responses
- **`403 Forbidden`**:
```json
{
  "detail": "Only owner can see expenses"
}
```
- **`404 Not Found`**:
```json
{
  "detail": "Expense not found"
}
```
- **`401 Unauthorized`**

---

## 6. Balance APIs

### 6.1 List Trip Balances

- **METHOD:** `GET`
- **ENDPOINT:** `/trips/{trip_id}/balances/` *(Note: Missing `/api/v1` prefix and includes trailing slash)*
- **Purpose:** Calculate net balances for each member in a trip (paid amount minus allocated cost). Positive balance means user is owed money; negative balance means user owes money.
- **Authentication:** Bearer JWT required (`get_current_user`)
- **Authorization Rules:** User must be an active member of the trip (`is_member(trip_id, current_user_id)`).
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `trip_id` | UUID | Yes | Trip UUID |
- **Query Parameters:** None
- **Request Body:** None

#### Success Response
- **Status Code:** `200 OK` *(Inferred)*
- **Declared Response Model:** None *(Inferred from raw dict return)*

```json
{
  "balances": [
    {
      "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "balance": 750.00
    },
    {
      "user_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "balance": -750.00
    }
  ]
}
```

**Inferred Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `balances` | array | List of user balance objects |
| `balances[].user_id` | UUID | User ID |
| `balances[].balance` | number/Decimal | Net balance amount (+ is owed, - owes) |

#### Error Responses
- **`403 Forbidden`** (User is not a member of the trip):
```json
{
  "detail": "You are not a member of this trip"
}
```
- **`404 Not Found`** (Trip not found):
```json
{
  "detail": "Trip not found"
}
```
- **`401 Unauthorized`**

---

## 7. Settlement APIs

### 7.1 Get Settlement Suggestions

- **METHOD:** `GET`
- **ENDPOINT:** `/trips/{trip_id}/settlements/` *(Note: Missing `/api/v1` prefix and includes trailing slash)*
- **Purpose:** Calculate optimized debt settlement transaction paths (who pays whom how much) to clear all balances with minimal transactions.
- **Authentication:** Bearer JWT required (`get_current_user`)
- **Authorization Rules:** User must be a member of the trip.
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `trip_id` | UUID | Yes | Trip UUID |
- **Query Parameters:** None
- **Request Body:** None

#### Success Response
- **Status Code:** `200 OK` *(Inferred)*
- **Declared Response Model:** None *(Inferred from raw dict return)*

```json
{
  "settlements": [
    {
      "payer": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "payee": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "amount": 750.00
    }
  ]
}
```

**Inferred Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `settlements` | array | List of settlement transaction objects |
| `settlements[].payer` | UUID | User ID who should pay |
| `settlements[].payee` | UUID | User ID who should receive payment |
| `settlements[].amount` | number/Decimal | Transaction amount |

#### Error Responses
- **`403 Forbidden`**:
```json
{
  "detail": "You are not a member of this trip"
}
```
- **`404 Not Found`**:
```json
{
  "detail": "Trip not found"
}
```
- **`401 Unauthorized`**

---

## API Coverage Summary

- **Total Number of Endpoints:** `20`
- **Public Endpoints (No Auth):** `3` (`/api/v1/health`, `/api/v1/auth/register`, `/api/v1/auth/login`)
- **Authenticated Endpoints:** `17`
- **Endpoints by HTTP Method:**
  - `POST`: 7 (`/register`, `/login`, `/logout`, `/refresh`, `/trips`, `/members`, `/expenses`)
  - `GET`: 10 (`/health`, `/me`, `/trips/{trip_id}`, `/trips`, `/members`, `/members/{member_id}`, `/expenses`, `/expenses/{expense_id}`, `/balances/`, `/settlements/`)
  - `PATCH`: 1 (`/trips/{trip_id}`)
  - `DELETE`: 2 (`/trips/{trip_id}`, `/members/{member_id}`)
- **Endpoints Grouped by Module:**
  - Health: 1
  - Auth: 5
  - Trip: 5
  - Trip Membership: 4
  - Expenses: 3
  - Balances: 1
  - Settlements: 1
- **Incomplete / Schema Inferred Endpoints:** `6` (`/me`, `/logout`, `/refresh`, `DELETE /trips/{trip_id}`, `/balances/`, `/settlements/`)

---

## Backend API Issues Found

Below is a detailed list of inconsistencies and bugs found in the backend code that should be resolved before starting frontend React integration:

### 1. Inconsistent Endpoint URL Prefixes
- Most routers use `/api/v1` prefix (`/api/v1/auth`, `/api/v1/trips`, etc.).
- `balances.py` uses prefix `/trips/{trip_id}/balances` (lacks `/api/v1`).
- `settlements.py` uses prefix `/trips/{trip_id}/settlements` (lacks `/api/v1`).

### 2. Trailing Slash Inconsistencies
- `balances.py` defines `@router.get("/")`, exposing `/trips/{trip_id}/balances/` with a trailing slash.
- `settlements.py` defines `@router.get("/")`, exposing `/trips/{trip_id}/settlements/` with a trailing slash.
- All other routes do not use trailing slashes.

### 3. Unhandled Exceptions (HTTP 500 Internal Server Errors)
- `AuthService.register_user` raises `ValueError("User already exists")`. FastAPI does not catch `ValueError`, returning HTTP 500 instead of `409 Conflict` or `400 Bad Request`.
- `AuthService.login_user` raises `ValueError("Invalid email or password")`, returning HTTP 500 instead of `401 Unauthorized` or `400 Bad Request`.

### 4. HTTP Status Code Mismatches
- `POST /api/v1/auth/register` returns `200 OK` in HTTP headers, while the JSON body returns `"statuscode": 201`.
- `POST /api/v1/trips` returns `200 OK` in HTTP headers, while JSON body returns `"status_code": 201`.
- `PATCH /api/v1/trips/{trip_id}` returns `200 OK` in HTTP headers, while JSON body returns `"status_code": 201`.
- `POST /api/v1/trips/{trip_id}/members` returns `200 OK` in HTTP headers, while JSON body returns `"status_code": 201`.
*Fix requirement:* Add `status_code=status.HTTP_201_CREATED` to `@router.post(...)` or align JSON `status_code` values to match actual HTTP responses.

### 5. Naming Typos in Response Schemas
- In `app/schemas/auth.py`: `RegisterResponse` and `LoginResponse` use the key `statuscode` (lowercase 'c'), while `MeResponse`, `LogoutResponse`, `CreateTripResponse`, `UpdateTripResponse`, and `AddTripMemberResponse` use `status_code` (snake_case).

### 6. Missing `response_model` Definitions
The following routes lack `response_model` annotations on their `@router` decorators:
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/refresh`
- `DELETE /api/v1/trips/{trip_id}`
- `GET /trips/{trip_id}/balances/`
- `GET /trips/{trip_id}/settlements/`

### 7. Authorization & Access Control Inconsistencies
- `GET /api/v1/trips/{trip_id}`: Checks `if trip.owner_id != user_id: raise 403`. Active trip members cannot view basic trip details, only the creator can.
- `GET /api/v1/trips/{trip_id}/expenses` and `GET /api/v1/trips/{trip_id}/expenses/{expense_id}`: Only the trip owner can view expenses (`current_user_id != trip.owner_id -> 403`). Active members cannot view trip expenses.
- `GET /api/v1/trips/{trip_id}/members`: Does not verify if the requesting user is a member or owner of the trip at all. Any authenticated user with a `trip_id` can list members.

### 8. Bad 404 Behavior on Empty List
- `GET /api/v1/trips/{trip_id}/expenses`: In `ExpensesService.get_all_expense_of_trip`, if `len(expenses) == 0`, it raises `HTTPException(status_code=404, detail="Expenses list is empty")`. An empty expense list is a valid state and should return `200 OK` with an empty array `[]` and `total_expenses: 0`.
