from pydantic import BaseModel

class HealthCheckResponse(BaseModel):
    status : int
    message : str