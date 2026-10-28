from typing import Optional
from app.workload.job_model import Job
from app.simulation.environment import DiscreteEventSimulator

def fcfs_scheduler(sim: DiscreteEventSimulator) -> Optional[Job]:
    """
    First-Come, First-Served (FCFS) Heuristic:
    Selects the feasible job with the earliest arrival time.
    """
    feasible_jobs = [j for j in sim.waiting_queue if sim.cluster.is_feasible(j)]
    if not feasible_jobs:
        return None
    # Sort by arrival time ascending
    feasible_jobs.sort(key=lambda j: j.arrival_time)
    return feasible_jobs[0]
