import numpy as np
import copy
from typing import List, Dict, Any, Tuple
from app.workload.job_model import Job
from app.simulation.environment import DiscreteEventSimulator
from app.simulation.resource_manager import ClusterResourceState

class PSOScheduler:
    """
    Particle Swarm Optimization (PSO) for Job Scheduling.
    Particles represent continuous priority weights mapped to job indices.
    Tracks Personal Best (pbest) and Swarm Global Best (gbest).
    """
    
    def __init__(self, num_particles: int = 25, iterations: int = 30, w: float = 0.5, c1: float = 1.5, c2: float = 1.5):
        self.num_particles = num_particles
        self.iterations = iterations
        self.w = w    # Inertia weight
        self.c1 = c1  # Cognitive coefficient
        self.c2 = c2  # Social coefficient

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

        # Particle positions (priority weights) and velocities
        positions = np.random.rand(self.num_particles, num_jobs)
        velocities = np.random.uniform(-0.5, 0.5, (self.num_particles, num_jobs))
        
        pbest_pos = positions.copy()
        pbest_fitness = np.full(self.num_particles, float('inf'))
        
        gbest_pos = None
        gbest_fitness = float('inf')
        gbest_completed_jobs = []
        
        history = []

        def eval_particle(pos: np.ndarray) -> Tuple[float, List[Job]]:
            # Sort job indices by particle continuous values
            ordered_indices = list(np.argsort(pos))
            job_map = {idx: j for idx, j in enumerate(jobs)}
            ordered_jobs = [job_map[idx] for idx in ordered_indices]
            
            sim = DiscreteEventSimulator(ordered_jobs, copy.deepcopy(cluster_state))
            order_index_map = {j.job_id: i for i, j in enumerate(ordered_jobs)}

            def pso_dynamic_scheduler(s: DiscreteEventSimulator):
                feasible = [j for j in s.waiting_queue if s.cluster.is_feasible(j)]
                if not feasible:
                    return None
                feasible.sort(key=lambda j: order_index_map[j.job_id])
                return feasible[0]

            completed = sim.run_simulation(pso_dynamic_scheduler)
            if not completed:
                return 999999.0, []

            makespan = max(j.finish_time for j in completed) if completed else 1000.0
            avg_waiting = sum(j.waiting_time for j in completed) / len(completed) if completed else 500.0
            sla_violations = sum(1 for j in completed if j.sla_violated)
            
            fitness = (0.35 * makespan) + (0.3 * avg_waiting) + (0.35 * (sla_violations * 25.0))
            return fitness, completed

        for it in range(self.iterations):
            for i in range(self.num_particles):
                fit, comp = eval_particle(positions[i])
                
                if fit < pbest_fitness[i]:
                    pbest_fitness[i] = fit
                    pbest_pos[i] = positions[i].copy()
                    
                if fit < gbest_fitness:
                    gbest_fitness = fit
                    gbest_pos = positions[i].copy()
                    gbest_completed_jobs = comp

            # Velocity and Position update
            r1 = np.random.rand(self.num_particles, num_jobs)
            r2 = np.random.rand(self.num_particles, num_jobs)
            
            velocities = (self.w * velocities) + (self.c1 * r1 * (pbest_pos - positions)) + (self.c2 * r2 * (gbest_pos - positions))
            positions += velocities
            
            history.append({"iteration": it + 1, "gbest_fitness": round(gbest_fitness, 2)})

        best_chromosome = list(np.argsort(gbest_pos)) if gbest_pos is not None else list(range(num_jobs))
        return {
            "best_chromosome": best_chromosome,
            "best_fitness": round(gbest_fitness, 2),
            "best_completed_jobs": gbest_completed_jobs,
            "history": history
        }
