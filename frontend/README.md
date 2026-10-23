# GroupTrip Ledger – Frontend

React + JavaScript + Vite + React Router + Tailwind CSS + Lucide React + Axios + React Hook Form + Zod,
wired to the existing GroupTrip Ledger FastAPI backend.

## 1. Prerequisites
- Node.js 18 or newer (20 LTS recommended) and npm
- The FastAPI backend running (default `http://127.0.0.1:8000`)

## 2. Install (Windows, PowerShell or Command Prompt)
```
cd frontend
npm install
```
`npm install` also creates `package-lock.json` (it could not be generated offline when this project was written).

## 3. Configure the backend URL
```
copy .env.example .env
```
Edit `.env` if your backend is not on port 8000:
```
VITE_API_BASE_URL=http://127.0.0.1:8000
```
Restart the dev server after changing `.env`.

## 4. Run
```
npm run dev
```
Open http://localhost:5173

## 5. Build for production / lint
```
npm run build      # output in dist/
npm run preview    # serve the build locally
npm run lint
```

## 6. Required FastAPI CORS configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # lets the browser read the PDF filename
)
```

## 7. Routes
| Route | Page | Access |
|---|---|---|
| `/` | Landing | public |
| `/login`, `/register` | Auth | public |
| `/dashboard`, `/trips` | My Trips + Create Trip | protected |
| `/trips/:tripId` | Trip details (Overview, Edit, Delete) | protected |
| `/trips/:tripId/members` | Members | protected |
| `/trips/:tripId/expenses` | Expenses + Add Expense modal | protected |
| `/trips/:tripId/balances` | Balances & suggested settlements | protected |
| `/trips/:tripId/report` | Trip report + PDF download | protected |
| `/profile`, `/settings` | Profile & Settings | protected |

## 8. How it talks to the API
- `src/api/client.js` – one Axios instance, Bearer-token request interceptor, and a 401 interceptor that
  calls `POST /api/v1/auth/refresh` (with the refresh token) once, retries the failed request once,
  and logs out if the refresh fails. The refresh call bypasses the interceptor, so no refresh loops.
- `src/api/*.js` – one module per feature, using only the endpoints in `API_DOCUMENTATION.md`.
  Note the documented quirks: balances/settlements have no `/api/v1` prefix and end with `/`;
  reports use `/api/v1/trip/` (singular).
- Money: all financial identifiers are **member IDs**, never user IDs. Amounts are validated in integer paise
  (no floating-point drift). Balances and settlements are shown exactly as the backend returns them;
  the frontend has no settlement algorithm. The equal-split amounts in the Add Expense modal are a preview only.
- Tokens: stored in `localStorage` ("Remember me" checked) or `sessionStorage` (unchecked). Trade-off: any
  XSS bug could read them. The backend uses bearer tokens, so cookies are not an option without backend changes.

## 9. Known limitations
- **Not yet verified:** the build, ESLint run, and live calls against your backend were not run in the
  environment where this was written (no network access). Source files were only syntax-checked. Run
  `npm install`, `npm run build`, `npm run lint`, then try register → login → trip → members → expense →
  balances → report PDF.
- Photos in the designs are replaced by gradient placeholders (no photo assets were available).
- The API only supports adding members by `display_name`, so the Members page has no email column and
  members added here are guests. Members with an account are shown as "Registered".
- No expense edit/delete, payment-record, profile-update, change-password, or forgot-password endpoints
  exist, so those controls are omitted or shown as unavailable. The designs' "Settle" buttons are omitted
  because there is no payment endpoint; suggestions are display-only.
- The Expenses table shows split type and category instead of "Participants", since the list endpoint
  does not return allocations (the Report page does).
- `GET /api/v1/trips` returns only trips you own, so the dashboard shows only those.
- Currency is shown as ₹ (the API does not specify a currency). Registration requires 8+ characters in the
  UI only; the backend documents no password rule.
