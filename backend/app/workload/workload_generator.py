import numpy as np
from typing import List, Dict, Any
from app.workload.job_model import Job

class WorkloadGenerator:
    """Generates synthetic enterprise workloads for controlled experiment scenarios."""
    
    SCENARIO_CONFIGS: Dict[str, Dict[str, Any]] = {
        "LIGHT": {
            "arrival_interval_mean": 10.0,
            "cpu_range": (1, 4),
            "memory_range": (1024, 8192),
            "gpu_prob": 0.1,
            "runtime_mean": 15.0,
            "slack_mult": (2.0, 3.5)
        },
        "MEDIUM": {
            "arrival_interval_mean": 5.0,
            "cpu_range": (2, 8),
            "memory_range": (2048, 16384),
            "gpu_prob": 0.25,
            "runtime_mean": 30.0,
            "slack_mult": (1.5, 2.5)
        },
        "HEAVY": {
            "arrival_interval_mean": 2.0,
            "cpu_range": (4, 16),
            "memory_range": (4096, 32768),
            "gpu_prob": 0.4,
            "runtime_mean": 45.0,
            "slack_mult": (1.2, 1.8)
        },
        "BURSTY": {
            "arrival_interval_mean": 1.0,
            "cpu_range": (2, 12),
            "memory_range": (2048, 24576),
            "gpu_prob": 0.3,
            "runtime_mean": 25.0,
            "slack_mult": (1.3, 2.0)
        },
        "OVERLOADED": {
            "arrival_interval_mean": 0.5,
            "cpu_range": (8, 24),
            "memory_range": (8192, 49152),
            "gpu_prob": 0.5,
            "runtime_mean": 60.0,
            "slack_mult": (1.1, 1.4)
        }
    }

    @classmethod
    def generate_scenario(cls, scenario: str = "MEDIUM", num_jobs: int = 100, seed: int = 42) -> List[Job]:
        np.random.seed(seed)
        cfg = cls.SCENARIO_CONFIGS.get(scenario.upper(), cls.SCENARIO_CONFIGS["MEDIUM"])
        
        jobs: List[Job] = []
        current_time = 0.0

        for i in range(1, num_jobs + 1):
            if scenario.upper() == "BURSTY" and (i % 20 < 10):
                # Sudden arrival burst
                interval = np.random.exponential(scale=cfg["arrival_interval_mean"] * 0.2)
            else:
                interval = np.random.exponential(scale=cfg["arrival_interval_mean"])
            
            current_time += interval
            arrival_time = round(current_time, 2)
            
            cpu = int(np.random.randint(cfg["cpu_range"][0], cfg["cpu_range"][1] + 1))
            memory = float(np.random.randint(cfg["memory_range"][0], cfg["memory_range"][1] + 1))
            has_gpu = np.random.rand() < cfg["gpu_prob"]
            gpu_units = int(np.random.choice([1, 2])) if has_gpu else 0
            
            runtime = round(float(np.random.exponential(scale=cfg["runtime_mean"])) + 5.0, 2)
            priority = int(np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.2, 0.4, 0.2, 0.1]))
            
            # SLA & Job type categorization
            if gpu_units > 0 or cpu >= 12:
                job_type = "ML Training"
                sla_class = "Critical" if priority >= 4 else "High"
            elif memory >= 16384:
                job_type = "Data Pipeline"
                sla_class = "High"
            elif runtime <= 20.0:
                job_type = "BI Query"
                sla_class = "Standard"
            else:
                job_type = "Batch Analytics"
                sla_class = "Low"

            slack = np.random.uniform(cfg["slack_mult"][0], cfg["slack_mult"][1])
            deadline = round(arrival_time + (runtime * slack), 2)
            
            cost_budget = round(cpu * 0.05 * runtime + (memory / 1024.0) * 0.02 * runtime + gpu_units * 0.2 * runtime, 2)

            job = Job(
                job_id=f"SYN-{scenario[:3]}-{str(i).zfill(4)}",
                tenant_id=int(np.random.randint(1, 20)),
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

        jobs.sort(key=lambda j: j.arrival_time)
        return jobs
