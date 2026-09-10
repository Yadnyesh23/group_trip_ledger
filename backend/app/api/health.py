from fastapi import APIRouter, Depends
from app.database.db import get_db

from app.services.health import HealthService
from app.schemas.health import HealthCheckResponse

router = APIRouter(prefix='/api/v1', tags=['Health'])

@router.get("/health", response_model=HealthCheckResponse)
def health_check(db=Depends(get_db)):
    health_status = HealthService.health_check(db)

    if health_status:
        return HealthCheckResponse(
            status = 200,
            message = "Database connection is successful"
        )
    else:
        return HealthCheckResponse(
            status = 503,
            message = "Database connection is failed"
        )
        

        
    