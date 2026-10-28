from typing import Optional
from app.workload.job_model import Job
from app.simulation.environment import DiscreteEventSimulator

def sjf_scheduler(sim: DiscreteEventSimulator) -> Optional[Job]:
    """
    Shortest Job First (SJF) Heuristic:
    Selects the feasible job with the shortest execution runtime.
    """
    feasible_jobs = [j for j in sim.waiting_queue if sim.cluster.is_feasible(j)]
    if not feasible_jobs:
        return None
    feasible_jobs.sort(key=lambda j: j.runtime)
    return feasible_jobs[0]
