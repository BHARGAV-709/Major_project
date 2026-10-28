import numpy as np
from typing import List, Dict, Any
from app.config import COST_RATES

class PerformanceEvaluator:
    """
    Evaluates enterprise scheduling metrics across 5 dimensions:
    1. Makespan (Max finish time)
    2. Average Waiting Time (Mean delay before execution start)
    3. Resource Utilization (CPU, Memory, GPU active occupancy)
    4. SLA Violation Rate (% of jobs exceeding deadline)
    5. Total Cost ($ usage cost + SLA violation penalties)
    """

    @staticmethod
    def calculate_metrics(schedule: List[Dict[str, Any]], cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        if not schedule:
            return {
                "makespan": 0.0,
                "avg_waiting_time": 0.0,
                "max_waiting_time": 0.0,
                "cpu_utilization": 0.0,
                "memory_utilization": 0.0,
                "gpu_utilization": 0.0,
                "overall_utilization": 0.0,
                "sla_violation_count": 0,
                "sla_violation_rate": 0.0,
                "total_cost": 0.0,
                "efficiency_score": 0.0
            }

        total_jobs = len(schedule)
        
        # 1. Makespan
        finish_times = [j["finish_time"] for j in schedule if j.get("finish_time") is not None]
        makespan = max(finish_times) if finish_times else 1.0
        
        # 2. Waiting Time
        waiting_times = [j["waiting_time"] for j in schedule if j.get("waiting_time") is not None]
        avg_waiting = float(np.mean(waiting_times)) if waiting_times else 0.0
        max_waiting = float(np.max(waiting_times)) if waiting_times else 0.0
        
        # 3. Resource Utilization
        total_cpu = cluster_config.get("cpu_cores", 40)
        total_mem = cluster_config.get("memory_gb", 256) * 1024.0  # MB
        total_gpu = cluster_config.get("gpu_units", 8)
        
        cpu_time_used = sum(j["cpu_cores"] * j["runtime"] for j in schedule)
        mem_time_used = sum(j["memory_mb"] * j["runtime"] for j in schedule)
        gpu_time_used = sum(j["gpu_units"] * j["runtime"] for j in schedule)

        cpu_util = min(100.0, round((cpu_time_used / (total_cpu * makespan)) * 100.0, 2)) if (total_cpu * makespan) > 0 else 0.0
        mem_util = min(100.0, round((mem_time_used / (total_mem * makespan)) * 100.0, 2)) if (total_mem * makespan) > 0 else 0.0
        gpu_util = min(100.0, round((gpu_time_used / (total_gpu * makespan)) * 100.0, 2)) if (total_gpu * makespan) > 0 and total_gpu > 0 else 0.0
        
        overall_util = round((cpu_util * 0.45) + (mem_util * 0.45) + (gpu_util * 0.1), 2)

        # 4. SLA Violations
        sla_violations = sum(1 for j in schedule if j.get("sla_status") == "VIOLATED" or j.get("finish_time", 0) > j.get("deadline", 0))
        sla_violation_rate = round((sla_violations / total_jobs) * 100.0, 2)

        # 5. Cost Model Calculation
        cpu_cost = cpu_time_used * COST_RATES["cpu_core_per_sec"]
        mem_cost = (mem_time_used / 1024.0) * COST_RATES["memory_gb_per_sec"]
        gpu_cost = gpu_time_used * COST_RATES["gpu_unit_per_sec"]
        sla_penalty = sla_violations * COST_RATES["sla_violation_penalty"]
        
        total_cost = round(cpu_cost + mem_cost + gpu_cost + sla_penalty, 2)

        # Academic composite efficiency score (0 to 100)
        score = max(0.0, min(100.0, (overall_util * 0.4) + ((100.0 - sla_violation_rate) * 0.4) + (max(0, 100 - avg_waiting) * 0.2)))

        return {
            "makespan": round(makespan, 2),
            "avg_waiting_time": round(avg_waiting, 2),
            "max_waiting_time": round(max_waiting, 2),
            "cpu_utilization": cpu_util,
            "memory_utilization": mem_util,
            "gpu_utilization": gpu_util,
            "overall_utilization": overall_util,
            "sla_violation_count": sla_violations,
            "sla_violation_rate": sla_violation_rate,
            "total_cost": total_cost,
            "efficiency_score": round(score, 2)
        }
