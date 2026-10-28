from typing import List, Dict, Any
from app.workload.job_model import Job
from app.scheduler.decision_engine import SchedulingDecisionEngine
from app.evaluation.metrics import PerformanceEvaluator

class BenchmarkRunner:
    """Runs fair side-by-side benchmark comparison across multiple scheduling algorithms under identical workload conditions."""

    @classmethod
    def run_benchmark(cls, 
                      jobs: List[Job], 
                      cluster_config: Dict[str, Any], 
                      algorithms: List[str] = None,
                      algo_params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        
        target_algos = algorithms or ["FCFS", "SJF", "Priority", "EDF", "Greedy", "GA", "PSO", "SA", "Q-Learning", "DQN"]
        results = []

        for algo_name in target_algos:
            exec_res = SchedulingDecisionEngine.execute_algorithm(
                algorithm_name=algo_name,
                jobs=jobs,
                cluster_config=cluster_config,
                algo_params=algo_params
            )
            
            metrics = PerformanceEvaluator.calculate_metrics(
                schedule=exec_res["schedule"],
                cluster_config=cluster_config
            )
            
            results.append({
                "algorithm": algo_name,
                "execution_time_sec": exec_res["execution_time_sec"],
                "completed_count": exec_res["completed_count"],
                "rejected_count": exec_res.get("rejected_count", 0),
                "total_jobs": exec_res["total_jobs"],
                "metrics": metrics,
                "schedule": exec_res["schedule"],
                "rejected_jobs": exec_res.get("rejected_jobs", []),
                "timeline": exec_res["timeline"],
                "resource_history": exec_res["resource_history"],
                "extra": exec_res.get("extra", {})
            })

        # Rank algorithms by composite efficiency score
        results.sort(key=lambda r: r["metrics"]["efficiency_score"], reverse=True)
        for idx, res in enumerate(results):
            res["rank"] = idx + 1

        return results
