from typing import Optional
from app.workload.job_model import Job
from app.simulation.environment import DiscreteEventSimulator

def priority_scheduler(sim: DiscreteEventSimulator) -> Optional[Job]:
    """
    Priority-Based Heuristic:
    Selects the feasible job with highest priority (5 = Highest, 1 = Lowest).
    Breaks ties with arrival time.
    """
    feasible_jobs = [j for j in sim.waiting_queue if sim.cluster.is_feasible(j)]
    if not feasible_jobs:
        return None
    feasible_jobs.sort(key=lambda j: (-j.priority, j.arrival_time))
    return feasible_jobs[0]
