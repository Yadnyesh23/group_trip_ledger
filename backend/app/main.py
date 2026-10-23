from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.users import router as users_router
from app.api.trips import router as trips_router
from app.api.trip_membership import router as trip_membership_router
from app.api.expenses import router as expenses_router
from app.api.balances import router as balance_router
from app.api.settlements import router as settlements_router
from app.api.reports import router as reports_router

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(users_router)
app.include_router(trips_router)
app.include_router(trip_membership_router)
app.include_router(expenses_router)
app.include_router(balance_router)
app.include_router(settlements_router)
app.include_router(reports_router)

    
    