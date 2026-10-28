import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from app.database.db import Base

class DatasetRecord(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    filename = Column(String)
    row_count = Column(Integer)
    column_count = Column(Integer)
    status = Column(String, default="RAW")
    preprocessing_summary = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ExperimentRecord(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    experiment_name = Column(String)
    scenario_type = Column(String)
    algorithm_name = Column(String)
    num_jobs = Column(Integer)
    cluster_config = Column(JSON)
    metrics = Column(JSON)
    execution_time_sec = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
