from sqlalchemy import text

class HealthService:
    def __init__(self, session):
        self.session = session
    
    def health_check(db_session):
        try:
            db_session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            raise Exception(f"Database connection error : {str(e)}")  