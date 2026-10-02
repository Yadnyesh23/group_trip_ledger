from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.users import router as users_router
from app.api.trips import router as trips_router
from app.api.trip_membership import router as trip_membership_router

app = FastAPI()

app.include_router(health_router)
app.include_router(users_router)
app.include_router(trips_router)
app.include_router(trip_membership_router)

    
    