import numpy as np
import copy
from typing import List, Dict, Any, Tuple, Optional
from app.workload.job_model import Job
from app.simulation.environment import DiscreteEventSimulator
from app.simulation.resource_manager import ClusterResourceState

class GeneticAlgorithmScheduler:
    """
    Genetic Algorithm (GA) for Job Scheduling Optimization.
    Uses chromosome permutation representation, order crossover (OX), swap mutation,
    and a multi-objective weighted fitness function.
    """
    
    def __init__(self, 
                 pop_size: int = 30, 
                 generations: int = 40, 
                 crossover_rate: float = 0.8, 
                 mutation_rate: float = 0.15,
                 w1_makespan: float = 0.3,
                 w2_waiting: float = 0.25,
                 w3_sla: float = 0.25,
                 w4_cost: float = 0.1,
                 w5_utilization: float = 0.1):
        self.pop_size = pop_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        self.w1 = w1_makespan
        self.w2 = w2_waiting
        self.w3 = w3_sla
        self.w4 = w4_cost
        self.w5 = w5_utilization

    def evaluate_chromosome(self, chromosome: List[int], jobs: List[Job], cluster_state: ClusterResourceState) -> Tuple[float, List[Job]]:
        """Simulates execution order defined by chromosome and returns (fitness, completed_jobs)."""
        job_map = {idx: j for idx, j in enumerate(jobs)}
        ordered_jobs = [job_map[idx] for idx in chromosome]
        
        sim = DiscreteEventSimulator(ordered_jobs, copy.deepcopy(cluster_state))
        
        # Priority mapping scheduler using chromosome order
        order_index_map = {job.job_id: i for i, job in enumerate(ordered_jobs)}
        
        def ga_dynamic_scheduler(s: DiscreteEventSimulator) -> Optional[Job]:
            feasible = [j for j in s.waiting_queue if s.cluster.is_feasible(j)]
            if not feasible:
                return None
            feasible.sort(key=lambda j: order_index_map[j.job_id])
            return feasible[0]

        completed = sim.run_simulation(ga_dynamic_scheduler)
        
        if not completed:
            return 999999.0, []

        makespan = max(j.finish_time for j in completed) if completed else 1000.0
        avg_waiting = sum(j.waiting_time for j in completed) / len(completed) if completed else 500.0
        sla_violations = sum(1 for j in completed if j.sla_violated)
        total_cost = sum(j.cost_budget for j in completed)
        
        # Estimate utilization
        total_cap_time = cluster_state.total_cpu * makespan
        used_cpu_time = sum(j.cpu_cores * j.runtime for j in completed)
        utilization = (used_cpu_time / total_cap_time * 100.0) if total_cap_time > 0 else 50.0

        fitness = (self.w1 * makespan) + (self.w2 * avg_waiting) + (self.w3 * (sla_violations * 20.0)) + (self.w4 * total_cost) - (self.w5 * utilization)
        return fitness, completed

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
            fit, comp = self.evaluate_chromosome([0], jobs, cluster_state)
            return {
                "best_chromosome": [0],
                "best_order": [0],
                "best_fitness": round(fit, 2),
                "best_completed_jobs": comp,
                "history": [{"generation": 1, "best_fitness": round(fit, 2)}]
            }

        # Initialize Population (random permutations of job indices)
        population = [list(np.random.permutation(num_jobs)) for _ in range(self.pop_size)]
        
        best_chrom = None
        best_fitness = float('inf')
        best_completed_jobs = []
        history = []

        for gen in range(self.generations):
            fitness_scores = []
            evaluated_jobs = []
            
            for chrom in population:
                fit, comp = self.evaluate_chromosome(chrom, jobs, cluster_state)
                fitness_scores.append(fit)
                evaluated_jobs.append(comp)
                
                if fit < best_fitness:
                    best_fitness = fit
                    best_chrom = chrom.copy()
                    best_completed_jobs = comp

            history.append({"generation": gen + 1, "best_fitness": round(best_fitness, 2)})

            # Selection (Tournament Selection)
            new_pop = []
            for _ in range(self.pop_size):
                idx1, idx2 = np.random.choice(self.pop_size, 2, replace=False)
                winner = population[idx1] if fitness_scores[idx1] < fitness_scores[idx2] else population[idx2]
                new_pop.append(winner.copy())

            # Crossover (Order Crossover OX)
            for i in range(0, self.pop_size - 1, 2):
                if np.random.rand() < self.crossover_rate:
                    p1, p2 = new_pop[i], new_pop[i+1]
                    c1, c2 = self._order_crossover(p1, p2), self._order_crossover(p2, p1)
                    new_pop[i], new_pop[i+1] = c1, c2

            # Mutation (Swap Mutation)
            for i in range(self.pop_size):
                if np.random.rand() < self.mutation_rate:
                    a, b = np.random.choice(num_jobs, 2, replace=False)
                    new_pop[i][a], new_pop[i][b] = new_pop[i][b], new_pop[i][a]

            population = new_pop

        return {
            "best_chromosome": best_chrom,
            "best_fitness": round(best_fitness, 2),
            "best_completed_jobs": best_completed_jobs,
            "history": history
        }

    def _order_crossover(self, p1: List[int], p2: List[int]) -> List[int]:
        size = len(p1)
        start, end = sorted(np.random.choice(size, 2, replace=False))
        child = [-1] * size
        child[start:end+1] = p1[start:end+1]
        
        p2_idx = 0
        for i in range(size):
            if child[i] == -1:
                while p2[p2_idx] in child:
                    p2_idx += 1
                child[i] = p2[p2_idx]
        return child
