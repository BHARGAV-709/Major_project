import numpy as np
import copy
import math
from typing import List, Dict, Any, Tuple
from app.workload.job_model import Job
from app.simulation.environment import DiscreteEventSimulator
from app.simulation.resource_manager import ClusterResourceState

class SimulatedAnnealingScheduler:
    """
    Simulated Annealing (SA) for Job Scheduling Optimization.
    Gradually decreases temperature while allowing probabilistic acceptance of worse schedules
    using Metropolis criterion: P = exp(-delta / T).
    """
    
    def __init__(self, initial_temp: float = 1000.0, cooling_rate: float = 0.92, min_temp: float = 1.0, max_iter: int = 150):
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.max_iter = max_iter

    def solve(self, jobs: List[Job], cluster_state: ClusterResourceState) -> Dict[str, Any]:
        num_jobs = len(jobs)
        if num_jobs == 0:
            return {
                "best_chromosome": [],
                "best_order": [],
                "best_fitness": 0.0,
                "best_completed_jobs": [],
                "history": []
            }
        if num_jobs == 1:
            def eval_single(order):
                job_map = {idx: j for idx, j in enumerate(jobs)}
                ordered_jobs = [job_map[idx] for idx in order]
                sim = DiscreteEventSimulator(ordered_jobs, copy.deepcopy(cluster_state))
                completed = sim.run_simulation(lambda s: s.waiting_queue[0] if s.waiting_queue and s.cluster.is_feasible(s.waiting_queue[0]) else None)
                makespan = max(j.finish_time for j in completed) if completed else 1000.0
                return makespan, completed
            fit, comp = eval_single([0])
            return {
                "best_chromosome": [0],
                "best_order": [0],
                "best_fitness": round(fit, 2),
                "best_completed_jobs": comp,
                "history": [{"step": 1, "temperature": self.initial_temp, "best_fitness": round(fit, 2)}]
            }

        def evaluate_schedule(order: List[int]) -> Tuple[float, List[Job]]:
            job_map = {idx: j for idx, j in enumerate(jobs)}
            ordered_jobs = [job_map[idx] for idx in order]
            
            sim = DiscreteEventSimulator(ordered_jobs, copy.deepcopy(cluster_state))
            order_index_map = {j.job_id: i for i, j in enumerate(ordered_jobs)}

            def sa_dynamic_scheduler(s: DiscreteEventSimulator):
                feasible = [j for j in s.waiting_queue if s.cluster.is_feasible(j)]
                if not feasible:
                    return None
                feasible.sort(key=lambda j: order_index_map[j.job_id])
                return feasible[0]

            completed = sim.run_simulation(sa_dynamic_scheduler)
            if not completed:
                return 999999.0, []

            makespan = max(j.finish_time for j in completed) if completed else 1000.0
            avg_waiting = sum(j.waiting_time for j in completed) / len(completed) if completed else 500.0
            sla_violations = sum(1 for j in completed if j.sla_violated)
            
            fitness = (0.35 * makespan) + (0.3 * avg_waiting) + (0.35 * (sla_violations * 25.0))
            return fitness, completed

        current_solution = list(np.random.permutation(num_jobs))
        current_fitness, current_completed = evaluate_schedule(current_solution)
        
        best_solution = current_solution.copy()
        best_fitness = current_fitness
        best_completed_jobs = current_completed
        
        temp = self.initial_temp
        history = []
        step = 0

        while temp > self.min_temp and step < self.max_iter:
            step += 1
            # Generate neighbor solution by swapping two random indices
            neighbor = current_solution.copy()
            i, j = np.random.choice(num_jobs, 2, replace=False)
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
            
            neighbor_fitness, neighbor_completed = evaluate_schedule(neighbor)
            delta = neighbor_fitness - current_fitness

            # Accept if better or probabilistically via Metropolis criterion
            if delta < 0 or np.random.rand() < math.exp(-delta / temp):
                current_solution = neighbor
                current_fitness = neighbor_fitness
                current_completed = neighbor_completed
                
                if current_fitness < best_fitness:
                    best_solution = current_solution.copy()
                    best_fitness = current_fitness
                    best_completed_jobs = current_completed

            temp *= self.cooling_rate
            history.append({"step": step, "temperature": round(temp, 2), "best_fitness": round(best_fitness, 2)})

        return {
            "best_chromosome": best_solution,
            "best_fitness": round(best_fitness, 2),
            "best_completed_jobs": best_completed_jobs,
            "history": history
        }
