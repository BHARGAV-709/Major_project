from typing import Dict, Any, List, Optional
import copy
from app.workload.job_model import Job

class ClusterResourceState:
    """Tracks current cluster capacity and availability."""
    def __init__(self, total_cpu: int = 40, total_memory_mb: float = 262144.0, total_gpu: int = 8):
        self.total_cpu = total_cpu
        self.total_memory_mb = total_memory_mb  # 256 GB = 262,144 MB
        self.total_gpu = total_gpu
        
        self.allocated_cpu = 0
        self.allocated_memory_mb = 0.0
        self.allocated_gpu = 0

    @property
    def available_cpu(self) -> int:
        return self.total_cpu - self.allocated_cpu

    @property
    def available_memory_mb(self) -> float:
        return self.total_memory_mb - self.allocated_memory_mb

    @property
    def available_gpu(self) -> int:
        return self.total_gpu - self.allocated_gpu

    @property
    def cpu_utilization_pct(self) -> float:
        return round((self.allocated_cpu / self.total_cpu) * 100.0, 2) if self.total_cpu > 0 else 0.0

    @property
    def memory_utilization_pct(self) -> float:
        return round((self.allocated_memory_mb / self.total_memory_mb) * 100.0, 2) if self.total_memory_mb > 0 else 0.0

    @property
    def gpu_utilization_pct(self) -> float:
        return round((self.allocated_gpu / self.total_gpu) * 100.0, 2) if self.total_gpu > 0 else 0.0

    def is_feasible(self, job: Job) -> bool:
        """Check if job resource demands fit into available cluster capacity."""
        return (job.cpu_cores <= self.available_cpu and 
                job.memory_mb <= self.available_memory_mb and 
                job.gpu_units <= self.available_gpu)

    def fits_cluster_capacity(self, job: Job) -> bool:
        """Check if job resource demands fit within the cluster's total physical capacity."""
        return (job.cpu_cores <= self.total_cpu and 
                job.memory_mb <= self.total_memory_mb and 
                job.gpu_units <= self.total_gpu)

    def allocate(self, job: Job) -> bool:
        """Allocate resources for job."""
        if not self.is_feasible(job):
            return False
        self.allocated_cpu += job.cpu_cores
        self.allocated_memory_mb += job.memory_mb
        self.allocated_gpu += job.gpu_units
        return True

    def release(self, job: Job):
        """Release allocated resources when job finishes."""
        self.allocated_cpu = max(0, self.allocated_cpu - job.cpu_cores)
        self.allocated_memory_mb = max(0.0, self.allocated_memory_mb - job.memory_mb)
        self.allocated_gpu = max(0, self.allocated_gpu - job.gpu_units)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_cpu": self.total_cpu,
            "total_memory_gb": round(self.total_memory_mb / 1024.0, 2),
            "total_gpu": self.total_gpu,
            "available_cpu": self.available_cpu,
            "available_memory_gb": round(self.available_memory_mb / 1024.0, 2),
            "available_gpu": self.available_gpu,
            "cpu_utilization": self.cpu_utilization_pct,
            "memory_utilization": self.memory_utilization_pct,
            "gpu_utilization": self.gpu_utilization_pct
        }
