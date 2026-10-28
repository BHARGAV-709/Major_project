import pandas as pd
import numpy as np
from typing import List
from pathlib import Path
from app.workload.job_model import Job

JOB_TYPES = ["Data Pipeline", "BI Query", "ML Training", "Batch Analytics"]
SLA_CLASSES = ["Critical", "High", "Standard", "Low"]

class WorkloadLoader:
    """Loads workload dataset (e.g., container_scheduling_dataset_10000.csv) and converts into Job objects."""
    
    @staticmethod
    def load_from_csv(filepath: str, max_jobs: int = 1000, seed: int = 42) -> List[Job]:
        np.random.seed(seed)
        df = pd.read_csv(filepath)
        
        if max_jobs and max_jobs < len(df):
            df = df.iloc[:max_jobs].copy()
            
        jobs: List[Job] = []
        
        for idx, row in df.iterrows():
            cid = str(int(row.get('Container_ID', idx + 1)))
            tenant_id = int(row.get('Tenant_ID', 1))
            
            # Map raw fields or derive standard units
            cpu = max(1, int(row.get('Requested_CPU_Cores', 2)))
            memory = max(256.0, float(row.get('Requested_Memory_MB', 4096.0)))
            
            # Derived fields for enterprise analytics workload
            # Arrival time in seconds (scaling down ms to human-readable simulation time)
            arr_raw = float(row.get('Execution_Start_Time_ms', idx * 5000))
            arrival_time = round(arr_raw / 1000.0, 2)
            
            # Runtime (Makespan / duration)
            make_raw = float(row.get('Makespan_ms', 30000))
            runtime = max(5.0, round(make_raw / 1000.0, 2))
            
            # Priority (1 to 5)
            priority = int((tenant_id % 5) + 1)
            
            # Job Type assignment based on resource demand
            if cpu >= 8 or memory >= 16384:
                job_type = "ML Training"
                gpu_units = np.random.choice([1, 2], p=[0.7, 0.3])
                sla_class = "Critical"
            elif memory >= 8192:
                job_type = "Data Pipeline"
                gpu_units = 0
                sla_class = "High"
            elif runtime < 20.0:
                job_type = "BI Query"
                gpu_units = 0
                sla_class = "Standard"
            else:
                job_type = "Batch Analytics"
                gpu_units = 0
                sla_class = "Low"

            # SLA Deadline: Arrival + Runtime + Slack Factor (1.2 to 2.5)
            slack_factor = {
                "Critical": 1.2,
                "High": 1.5,
                "Standard": 2.0,
                "Low": 2.5
            }[sla_class]
            
            deadline = round(arrival_time + (runtime * slack_factor), 2)
            
            # Cost budget estimation
            cost_budget = round(cpu * 0.05 * runtime + (memory / 1024.0) * 0.02 * runtime + gpu_units * 0.2 * runtime, 2)
            
            job = Job(
                job_id=f"J{cid.zfill(4)}",
                tenant_id=tenant_id,
                job_type=job_type,
                arrival_time=arrival_time,
                cpu_cores=cpu,
                memory_mb=memory,
                gpu_units=gpu_units,
                runtime=runtime,
                priority=priority,
                deadline=deadline,
                sla_class=sla_class,
                cost_budget=cost_budget
            )
            jobs.append(job)

        # Sort by arrival time
        jobs.sort(key=lambda j: j.arrival_time)
        return jobs
