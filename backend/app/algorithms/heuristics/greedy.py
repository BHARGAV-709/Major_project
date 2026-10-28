from typing import Optional
from app.workload.job_model import Job
from app.simulation.environment import DiscreteEventSimulator

def greedy_best_fit_scheduler(sim: DiscreteEventSimulator) -> Optional[Job]:
    """
    Greedy / Best-Fit Resource Allocator:
    Selects the feasible job that maximizes immediate resource utilization efficiency (best fit).
    """
    feasible_jobs = [j for j in sim.waiting_queue if sim.cluster.is_feasible(j)]
    if not feasible_jobs:
        return None
    
    # Calculate fit score: ratio of requested resources to available capacity
    def calc_fit_score(job: Job) -> float:
        cpu_ratio = job.cpu_cores / sim.cluster.available_cpu if sim.cluster.available_cpu > 0 else 0
        mem_ratio = job.memory_mb / sim.cluster.available_memory_mb if sim.cluster.available_memory_mb > 0 else 0
        gpu_ratio = (job.gpu_units / sim.cluster.available_gpu) if (sim.cluster.available_gpu > 0 and job.gpu_units > 0) else 0.0
        return (0.4 * cpu_ratio) + (0.4 * mem_ratio) + (0.2 * gpu_ratio)

    feasible_jobs.sort(key=calc_fit_score, reverse=True)
    return feasible_jobs[0]
