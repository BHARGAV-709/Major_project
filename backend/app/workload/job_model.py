from pydantic import BaseModel, Field
from typing import Optional

class Job(BaseModel):
    job_id: str
    tenant_id: int = 1
    job_type: str = "Data Pipeline"  # Data Pipeline, BI Query, ML Training, Batch Analytics
    arrival_time: float  # In seconds or minutes
    cpu_cores: int  # Requested CPU cores
    memory_mb: float  # Requested Memory in MB
    gpu_units: int = 0  # Requested GPU units (0, 1, 2)
    runtime: float  # Required execution duration
    priority: int = 3  # Priority level (1=Lowest, 5=Highest)
    deadline: float  # SLA deadline timestamp (Arrival + Runtime + Slack)
    sla_class: str = "Standard"  # Critical, High, Standard, Low
    cost_budget: float = 50.0  # Max budget limit for execution
    status: str = "WAITING"  # WAITING, READY, ALLOCATED, RUNNING, COMPLETED, VIOLATED
    
    start_time: Optional[float] = None
    finish_time: Optional[float] = None
    assigned_server_id: Optional[int] = None
    waiting_time: Optional[float] = None
    sla_violated: bool = False
    actual_cost: float = 0.0

    def to_dict(self) -> dict:
        return self.model_dump()
