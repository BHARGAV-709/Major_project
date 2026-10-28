from app.database.db import Base, engine, get_db
from app.database.models import DatasetRecord, ExperimentRecord

# Create tables
Base.metadata.create_all(bind=engine)
