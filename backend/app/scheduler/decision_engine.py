import copy
from typing import List, Dict, Any
from app.workload.job_model import Job
from app.simulation.environment import DiscreteEventSimulator
from app.simulation.resource_manager import ClusterResourceState

from app.algorithms.heuristics import (
    fcfs_scheduler, 
    sjf_scheduler, 
    priority_scheduler, 
    edf_scheduler, 
    greedy_best_fit_scheduler
)
from app.algorithms.metaheuristics import (
    GeneticAlgorithmScheduler, 
    PSOScheduler, 
    SimulatedAnnealingScheduler
)
from app.algorithms.reinforcement_learning import (
    QLearningScheduler, 
    DQNScheduler
)

class SchedulingDecisionEngine:
    """
    Unified Orchestrator for all Scheduling Algorithms.
    Standardizes output format across FCFS, SJF, Priority, EDF, Greedy, GA, PSO, SA, Q-Learning, and DQN.
    """
    
    ALGORITHMS = [
        "FCFS", "SJF", "Priority", "EDF", "Greedy",
        "GA", "PSO", "SA", "Q-Learning", "DQN"
    ]

    @classmethod
    def execute_algorithm(cls, 
                          algorithm_name: str, 
                          jobs: List[Job], 
                          cluster_config: Dict[str, Any],
                          algo_params: Dict[str, Any] = None) -> Dict[str, Any]:
        
        algo_params = algo_params or {}
        cluster = ClusterResourceState(
            total_cpu=cluster_config.get("cpu_cores", 40),
            total_memory_mb=cluster_config.get("memory_gb", 256) * 1024.0,
            total_gpu=cluster_config.get("gpu_units", 8)
        )
        
        name = algorithm_name.upper().strip()
        sim = DiscreteEventSimulator(copy.deepcopy(jobs), cluster)
        completed_jobs: List[Job] = []
        extra_meta = {}

        import time
        t_start = time.time()

        if name == "FCFS":
            completed_jobs = sim.run_simulation(fcfs_scheduler)
        elif name == "SJF":
            completed_jobs = sim.run_simulation(sjf_scheduler)
        elif name == "PRIORITY":
            completed_jobs = sim.run_simulation(priority_scheduler)
        elif name == "EDF":
            completed_jobs = sim.run_simulation(edf_scheduler)
        elif name in ["GREEDY", "BEST_FIT"]:
            completed_jobs = sim.run_simulation(greedy_best_fit_scheduler)
        elif name == "GA":
            ga = GeneticAlgorithmScheduler(
                pop_size=algo_params.get("pop_size", 25),
                generations=algo_params.get("generations", 30)
            )
            res = ga.solve(jobs, cluster)
            completed_jobs = res["best_completed_jobs"]
            extra_meta["history"] = res["history"]
        elif name == "PSO":
            pso = PSOScheduler(
                num_particles=algo_params.get("num_particles", 20),
                iterations=algo_params.get("iterations", 25)
            )
            res = pso.solve(jobs, cluster)
            completed_jobs = res["best_completed_jobs"]
            extra_meta["history"] = res["history"]
        elif name == "SA":
            sa = SimulatedAnnealingScheduler(
                initial_temp=algo_params.get("initial_temp", 500.0),
                max_iter=algo_params.get("max_iter", 100)
            )
            res = sa.solve(jobs, cluster)
            completed_jobs = res["best_completed_jobs"]
            extra_meta["history"] = res["history"]
        elif name in ["Q-LEARNING", "Q_LEARNING", "QL"]:
            ql = QLearningScheduler(episodes=algo_params.get("episodes", 60))
            res = ql.train(jobs, cluster)
            completed_jobs = res["best_completed_jobs"]
            extra_meta["history"] = res["history"]
        elif name == "DQN":
            dqn = DQNScheduler(episodes=algo_params.get("episodes", 40))
            res = dqn.train(jobs, cluster)
            completed_jobs = res["best_completed_jobs"]
            extra_meta["history"] = res["history"]
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm_name}")

        exec_time = round(time.time() - t_start, 4)

        # Ensure timeline and resource history are populated for all algorithms
        execution_timeline = sim.execution_timeline
        resource_history = sim.resource_utilization_history

        if not execution_timeline and completed_jobs:
            timeline = []
            for j in completed_jobs:
                timeline.append({
                    "job_id": j.job_id,
                    "job_type": j.job_type,
                    "server_id": j.assigned_server_id or 1,
                    "arrival_time": j.arrival_time,
                    "start_time": j.start_time,
                    "finish_time": j.finish_time,
                    "runtime": j.runtime,
                    "waiting_time": j.waiting_time,
                    "cpu": j.cpu_cores,
                    "memory_mb": j.memory_mb,
                    "gpu": j.gpu_units,
                    "sla_violated": bool(j.finish_time > j.deadline if (j.finish_time is not None and j.deadline is not None) else False),
                    "priority": j.priority
                })
            timeline.sort(key=lambda t: t["start_time"] if t["start_time"] is not None else 0.0)
            execution_timeline = timeline

        if not resource_history and completed_jobs:
            timepoints = set()
            for j in completed_jobs:
                if j.arrival_time is not None:
                    timepoints.add(j.arrival_time)
                if j.start_time is not None:
                    timepoints.add(j.start_time)
                if j.finish_time is not None:
                    timepoints.add(j.finish_time)

            sorted_times = sorted(list(timepoints))
            built_history = []
            total_cpu = cluster.total_cpu
            total_mem = cluster.total_memory_mb
            total_gpu = cluster.total_gpu

            for t in sorted_times:
                running = [j for j in completed_jobs if j.start_time is not None and j.finish_time is not None and j.start_time <= t < j.finish_time]
                alloc_cpu = sum(j.cpu_cores for j in running)
                alloc_mem = sum(j.memory_mb for j in running)
                alloc_gpu = sum(j.gpu_units for j in running)

                cpu_u = min(100.0, round((alloc_cpu / total_cpu) * 100.0, 2)) if total_cpu > 0 else 0.0
                mem_u = min(100.0, round((alloc_mem / total_mem) * 100.0, 2)) if total_mem > 0 else 0.0
                gpu_u = min(100.0, round((alloc_gpu / total_gpu) * 100.0, 2)) if total_gpu > 0 else 0.0

                built_history.append({
                    "time": round(t, 2),
                    "total_cpu": total_cpu,
                    "total_memory_gb": round(total_mem / 1024.0, 2),
                    "total_gpu": total_gpu,
                    "available_cpu": max(0, total_cpu - alloc_cpu),
                    "available_memory_gb": round(max(0.0, total_mem - alloc_mem) / 1024.0, 2),
                    "available_gpu": max(0, total_gpu - alloc_gpu),
                    "cpu_utilization": cpu_u,
                    "memory_utilization": mem_u,
                    "gpu_utilization": gpu_u
                })
            resource_history = built_history

        # Build Standardized Output Schedule Array
        standardized_schedule = []
        for j in completed_jobs:
            standardized_schedule.append({
                "job_id": j.job_id,
                "tenant_id": j.tenant_id,
                "job_type": j.job_type,
                "resource_id": f"Server-{j.assigned_server_id or 1}",
                "arrival_time": j.arrival_time,
                "start_time": j.start_time,
                "finish_time": j.finish_time,
                "runtime": j.runtime,
                "waiting_time": j.waiting_time,
                "deadline": j.deadline,
                "sla_status": "VIOLATED" if j.sla_violated else "MET",
                "cpu_cores": j.cpu_cores,
                "memory_mb": j.memory_mb,
                "gpu_units": j.gpu_units,
                "cost_budget": j.cost_budget
            })

        # Identify rejected / permanently infeasible jobs
        completed_ids = {j.job_id for j in completed_jobs}
        rejected_jobs_list = []
        for j in jobs:
            if not cluster.fits_cluster_capacity(j):
                rejected_jobs_list.append({
                    "job_id": j.job_id,
                    "tenant_id": j.tenant_id,
                    "job_type": j.job_type,
                    "arrival_time": j.arrival_time,
                    "cpu_cores": j.cpu_cores,
                    "memory_mb": j.memory_mb,
                    "gpu_units": j.gpu_units,
                    "status": "REJECTED",
                    "reason": "Exceeds total cluster capacity (CPU, Memory, or GPU)"
                })

        return {
            "algorithm": name,
            "execution_time_sec": exec_time,
            "completed_count": len(completed_jobs),
            "rejected_count": len(rejected_jobs_list),
            "total_jobs": len(jobs),
            "schedule": standardized_schedule,
            "rejected_jobs": rejected_jobs_list,
            "timeline": execution_timeline,
            "resource_history": resource_history,
            "extra": extra_meta
        }
