import heapq
import copy
from typing import List, Dict, Any, Callable, Optional
from app.workload.job_model import Job
from app.simulation.resource_manager import ClusterResourceState

class SimulationEvent:
    """Discrete simulation event (JOB_ARRIVAL, JOB_COMPLETION)."""
    def __init__(self, time: float, event_type: str, job: Job):
        self.time = time
        self.event_type = event_type  # 'JOB_ARRIVAL', 'JOB_COMPLETION'
        self.job = job

    def __lt__(self, other):
        return self.time < other.time

class DiscreteEventSimulator:
    """
    Core Discrete-Event Simulator Engine for Cluster Resource Allocation & Job Scheduling.
    Manages time progression, job arrivals, dynamic queues, resource allocation, and completion events.
    """
    
    def __init__(self, jobs: List[Job], cluster_state: Optional[ClusterResourceState] = None):
        self.original_jobs = [copy.deepcopy(j) for j in jobs]
        self.cluster = cluster_state or ClusterResourceState(total_cpu=40, total_memory_mb=262144.0, total_gpu=8)
        
        self.current_time: float = 0.0
        self.unarrived_jobs: List[Job] = sorted([copy.deepcopy(j) for j in jobs], key=lambda x: x.arrival_time)
        self.waiting_queue: List[Job] = []
        self.running_jobs: List[Job] = []
        self.completed_jobs: List[Job] = []
        self.rejected_jobs: List[Job] = []
        
        self.event_priority_queue: List[SimulationEvent] = []
        for j in self.unarrived_jobs:
            heapq.heappush(self.event_priority_queue, SimulationEvent(j.arrival_time, 'JOB_ARRIVAL', j))
            
        # Metrics and trajectory logs for visual rendering
        self.execution_timeline: List[Dict[str, Any]] = []
        self.resource_utilization_history: List[Dict[str, Any]] = []

    def reset(self):
        self.current_time = 0.0
        self.cluster.allocated_cpu = 0
        self.cluster.allocated_memory_mb = 0.0
        self.cluster.allocated_gpu = 0
        self.waiting_queue.clear()
        self.running_jobs.clear()
        self.completed_jobs.clear()
        self.rejected_jobs.clear()
        self.event_priority_queue.clear()
        
        for j in sorted([copy.deepcopy(j) for j in self.original_jobs], key=lambda x: x.arrival_time):
            heapq.heappush(self.event_priority_queue, SimulationEvent(j.arrival_time, 'JOB_ARRIVAL', j))
            
        self.execution_timeline.clear()
        self.resource_utilization_history.clear()

    def run_simulation(self, scheduler_func: Callable[['DiscreteEventSimulator'], Optional[Job]]) -> List[Job]:
        """
        Executes discrete-event loop using provided scheduling decision algorithm function.
        scheduler_func takes (simulator) -> returns next Job to schedule from waiting queue, or None.
        """
        self.reset()
        
        while self.event_priority_queue or self.waiting_queue or self.running_jobs:
            # 1. Process all pending completion/arrival events up to current event time
            if self.event_priority_queue:
                next_event = heapq.heappop(self.event_priority_queue)
                self.current_time = max(self.current_time, next_event.time)
                
                if next_event.event_type == 'JOB_ARRIVAL':
                    job = next_event.job
                    if not self.cluster.fits_cluster_capacity(job):
                        # Job demands exceed total cluster physical capacity -> Permanently Infeasible
                        job.status = "REJECTED"
                        self.rejected_jobs.append(job)
                    else:
                        job.status = "WAITING"
                        self.waiting_queue.append(job)
                elif next_event.event_type == 'JOB_COMPLETION':
                    job = next_event.job
                    job.status = "COMPLETED"
                    job.finish_time = self.current_time
                    job.sla_violated = (job.finish_time > job.deadline)
                    
                    self.cluster.release(job)
                    if job in self.running_jobs:
                        self.running_jobs.remove(job)
                    self.completed_jobs.append(job)

            # Record utilization sample
            self.resource_utilization_history.append({
                "time": self.current_time,
                **self.cluster.to_dict()
            })

            # 2. Invoke scheduler decision engine while feasible jobs exist in waiting queue
            scheduling = True
            while scheduling and self.waiting_queue:
                selected_job = scheduler_func(self)
                if selected_job and self.cluster.is_feasible(selected_job):
                    self.waiting_queue.remove(selected_job)
                    
                    selected_job.status = "RUNNING"
                    selected_job.start_time = self.current_time
                    selected_job.waiting_time = round(selected_job.start_time - selected_job.arrival_time, 2)
                    selected_job.assigned_server_id = int((hash(selected_job.job_id) % 10) + 1)
                    
                    self.cluster.allocate(selected_job)
                    self.running_jobs.append(selected_job)
                    
                    # Schedule JOB_COMPLETION event
                    finish_t = selected_job.start_time + selected_job.runtime
                    heapq.heappush(self.event_priority_queue, SimulationEvent(finish_t, 'JOB_COMPLETION', selected_job))
                    
                    # Timeline item for Gantt Chart
                    self.execution_timeline.append({
                        "job_id": selected_job.job_id,
                        "job_type": selected_job.job_type,
                        "server_id": selected_job.assigned_server_id,
                        "arrival_time": selected_job.arrival_time,
                        "start_time": selected_job.start_time,
                        "finish_time": finish_t,
                        "runtime": selected_job.runtime,
                        "waiting_time": selected_job.waiting_time,
                        "cpu": selected_job.cpu_cores,
                        "memory_mb": selected_job.memory_mb,
                        "gpu": selected_job.gpu_units,
                        "sla_violated": (finish_t > selected_job.deadline),
                        "priority": selected_job.priority
                    })
                else:
                    scheduling = False  # No feasible job found or queue empty

            # If no events remain in queue and running jobs exist, jump to next event
            if not self.event_priority_queue and not self.running_jobs and self.waiting_queue:
                # Deadlock guard: if waiting jobs exist but cannot fit cluster, break loop
                break

        return self.completed_jobs
