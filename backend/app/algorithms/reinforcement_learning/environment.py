import numpy as np
import copy
from typing import List, Dict, Any, Tuple, Optional
from app.workload.job_model import Job
from app.simulation.environment import DiscreteEventSimulator, SimulationEvent
from app.simulation.resource_manager import ClusterResourceState

class RLSchedulingEnv:
    """
    MDP Scheduling Environment for Reinforcement Learning (Q-Learning / DQN).
    State: [CPU_Util, Mem_Util, GPU_Util, Queue_Size_Norm, Avg_Priority_Norm, SLA_Urgency_Norm]
    Action: Index in waiting queue (0 to max_actions-1) or WAIT (max_actions)
    Reward: Balances resource utilization (+), waiting time (-), SLA compliance (+/-)
    """

    def __init__(self, jobs: List[Job], cluster_state: Optional[ClusterResourceState] = None, max_action_slots: int = 5):
        self.original_jobs = [copy.deepcopy(j) for j in jobs]
        self.cluster_state = cluster_state or ClusterResourceState(total_cpu=40, total_memory_mb=262144.0, total_gpu=8)
        self.max_action_slots = max_action_slots
        self.simulator = DiscreteEventSimulator(self.original_jobs, copy.deepcopy(self.cluster_state))
        self.reset()

    def reset(self) -> np.ndarray:
        self.simulator.reset()
        # Fast-forward simulation to first arrival event
        if self.simulator.event_priority_queue and not self.simulator.waiting_queue:
            first_event = self.simulator.event_priority_queue[0]
            self.simulator.current_time = first_event.time
            while self.simulator.event_priority_queue and self.simulator.event_priority_queue[0].time <= self.simulator.current_time:
                evt = heapq_pop_event(self.simulator)
                if evt.event_type == 'JOB_ARRIVAL':
                    job = evt.job
                    if not self.simulator.cluster.fits_cluster_capacity(job):
                        job.status = "REJECTED"
                        self.simulator.rejected_jobs.append(job)
                    else:
                        job.status = "WAITING"
                        self.simulator.waiting_queue.append(job)
        return self._get_state()

    def _get_state(self) -> np.ndarray:
        cpu_u = self.simulator.cluster.cpu_utilization_pct / 100.0
        mem_u = self.simulator.cluster.memory_utilization_pct / 100.0
        gpu_u = self.simulator.cluster.gpu_utilization_pct / 100.0
        
        q_len = min(1.0, len(self.simulator.waiting_queue) / 50.0)
        
        if self.simulator.waiting_queue:
            avg_prio = sum(j.priority for j in self.simulator.waiting_queue) / (len(self.simulator.waiting_queue) * 5.0)
            avg_urgency = sum(max(0.1, j.deadline - self.simulator.current_time) for j in self.simulator.waiting_queue) / (len(self.simulator.waiting_queue) * 100.0)
        else:
            avg_prio = 0.5
            avg_urgency = 1.0

        return np.array([cpu_u, mem_u, gpu_u, q_len, avg_prio, min(1.0, avg_urgency)], dtype=np.float32)

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """
        Executes action:
        0 to max_action_slots - 1 -> Schedule corresponding job from waiting queue
        max_action_slots -> WAIT (advance simulation time)
        """
        reward = 0.0
        done = False

        if action < self.max_action_slots and action < len(self.simulator.waiting_queue):
            candidate_job = self.simulator.waiting_queue[action]
            if self.simulator.cluster.is_feasible(candidate_job):
                # Valid allocation
                self.simulator.waiting_queue.remove(candidate_job)
                candidate_job.status = "RUNNING"
                candidate_job.start_time = self.simulator.current_time
                candidate_job.waiting_time = round(candidate_job.start_time - candidate_job.arrival_time, 2)
                candidate_job.assigned_server_id = int((hash(candidate_job.job_id) % 10) + 1)
                
                self.simulator.cluster.allocate(candidate_job)
                self.simulator.running_jobs.append(candidate_job)
                
                finish_t = candidate_job.start_time + candidate_job.runtime
                import heapq
                heapq.heappush(self.simulator.event_priority_queue, 
                               type(self.simulator.event_priority_queue[0])(finish_t, 'JOB_COMPLETION', candidate_job) 
                               if self.simulator.event_priority_queue else 
                               SimulationEvent(finish_t, 'JOB_COMPLETION', candidate_job))

                # Track timeline event
                self.simulator.execution_timeline.append({
                    "job_id": candidate_job.job_id,
                    "job_type": candidate_job.job_type,
                    "server_id": candidate_job.assigned_server_id,
                    "arrival_time": candidate_job.arrival_time,
                    "start_time": candidate_job.start_time,
                    "finish_time": finish_t,
                    "runtime": candidate_job.runtime,
                    "waiting_time": candidate_job.waiting_time,
                    "cpu": candidate_job.cpu_cores,
                    "memory_mb": candidate_job.memory_mb,
                    "gpu": candidate_job.gpu_units,
                    "sla_violated": (finish_t > candidate_job.deadline),
                    "priority": candidate_job.priority
                })

                # Positive Reward
                util_bonus = (self.simulator.cluster.cpu_utilization_pct + self.simulator.cluster.memory_utilization_pct) / 100.0
                wait_penalty = candidate_job.waiting_time / 50.0
                sla_bonus = 2.0 if finish_t <= candidate_job.deadline else -5.0
                
                reward = 5.0 + (util_bonus * 3.0) - wait_penalty + sla_bonus
            else:
                # Infeasible allocation penalty
                reward = -5.0
        else:
            # WAIT Action: advance simulation time to next completion or arrival event
            if self.simulator.event_priority_queue:
                next_event = self.simulator.event_priority_queue[0]
                # Advance time
                self.simulator.current_time = max(self.simulator.current_time, next_event.time)
                
                # Process all events at current time
                while self.simulator.event_priority_queue and self.simulator.event_priority_queue[0].time <= self.simulator.current_time:
                    import heapq
                    evt = heapq.heappop(self.simulator.event_priority_queue)
                    if evt.event_type == 'JOB_ARRIVAL':
                        job = evt.job
                        if not self.simulator.cluster.fits_cluster_capacity(job):
                            job.status = "REJECTED"
                            self.simulator.rejected_jobs.append(job)
                        else:
                            job.status = "WAITING"
                            self.simulator.waiting_queue.append(job)
                    elif evt.event_type == 'JOB_COMPLETION':
                        job = evt.job
                        job.status = "COMPLETED"
                        job.finish_time = self.simulator.current_time
                        job.sla_violated = (job.finish_time > job.deadline)
                        self.simulator.cluster.release(job)
                        if job in self.simulator.running_jobs:
                            self.simulator.running_jobs.remove(job)
                        self.simulator.completed_jobs.append(job)

                # Record utilization sample
                self.simulator.resource_utilization_history.append({
                    "time": self.simulator.current_time,
                    **self.simulator.cluster.to_dict()
                })
                
                reward = -0.5  # Slight wait cost
            else:
                reward = -2.0

        # Check terminal condition
        if not self.simulator.event_priority_queue and not self.simulator.running_jobs and not self.simulator.waiting_queue:
            done = True
        elif (len(self.simulator.completed_jobs) + len(self.simulator.rejected_jobs)) >= len(self.original_jobs):
            done = True

        next_state = self._get_state()
        return next_state, reward, done, {"completed_count": len(self.simulator.completed_jobs)}

def heapq_pop_event(sim: DiscreteEventSimulator):
    import heapq
    return heapq.heappop(sim.event_priority_queue)
