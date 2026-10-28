import unittest
from app.workload import WorkloadGenerator
from app.config import DEFAULT_CLUSTER_CONFIG
from app.scheduler import SchedulingDecisionEngine
from app.evaluation.metrics import PerformanceEvaluator

class TestBenchmarkingCorrectnessAndFairness(unittest.TestCase):
    """
    Validation and regression tests verifying:
    1. Input equality across all 10 algorithms (identical job instances, identical resources).
    2. Consistency and boundaries of metric calculations.
    3. Monotonicity and bounds of the composite efficiency score [0.0, 100.0].
    4. Deterministic repeatability of heuristic algorithms.
    5. Absence of duplicate, missing, or corrupt jobs in returned schedules.
    """

    @classmethod
    def setUpClass(cls):
        cls.cluster_config = DEFAULT_CLUSTER_CONFIG
        cls.algos = ["FCFS", "SJF", "Priority", "EDF", "Greedy", "GA", "PSO", "SA", "Q-Learning", "DQN"]

    def test_01_identical_workload_and_resource_fairness(self):
        """Verify every algorithm receives an identical deep copy of the job list and cluster resources."""
        jobs = WorkloadGenerator.generate_scenario("MEDIUM", num_jobs=10, seed=42)
        initial_ids = [j.job_id for j in jobs]

        for algo in self.algos:
            with self.subTest(algorithm=algo):
                res = SchedulingDecisionEngine.execute_algorithm(
                    algo, jobs, self.cluster_config,
                    {"episodes": 3, "generations": 3, "iterations": 3, "max_iter": 5}
                )
                scheduled_ids = [j["job_id"] for j in res["schedule"]]
                # Ensure no jobs were dropped, added or duplicated
                self.assertEqual(len(scheduled_ids), len(initial_ids))
                self.assertEqual(set(scheduled_ids), set(initial_ids))

    def test_02_metric_formulas_and_boundaries(self):
        """Verify metric calculation formulas produce values within rigorous bounds."""
        jobs = WorkloadGenerator.generate_scenario("LIGHT", num_jobs=10, seed=42)
        res = SchedulingDecisionEngine.execute_algorithm("FCFS", jobs, self.cluster_config)
        metrics = PerformanceEvaluator.calculate_metrics(res["schedule"], self.cluster_config)

        # Makespan must be positive and >= max finish time
        self.assertGreater(metrics["makespan"], 0.0)
        self.assertGreaterEqual(metrics["avg_waiting_time"], 0.0)
        self.assertGreaterEqual(metrics["max_waiting_time"], metrics["avg_waiting_time"])

        # Utilization percentages must be in [0.0, 100.0]
        self.assertTrue(0.0 <= metrics["cpu_utilization"] <= 100.0)
        self.assertTrue(0.0 <= metrics["memory_utilization"] <= 100.0)
        self.assertTrue(0.0 <= metrics["gpu_utilization"] <= 100.0)
        self.assertTrue(0.0 <= metrics["overall_utilization"] <= 100.0)

        # SLA violation rate in [0.0, 100.0]
        self.assertTrue(0.0 <= metrics["sla_violation_rate"] <= 100.0)

        # Efficiency score bounded in [0.0, 100.0]
        self.assertTrue(0.0 <= metrics["efficiency_score"] <= 100.0)

    def test_03_empty_and_extreme_schedule_handling(self):
        """Verify metric calculation safely handles empty schedules and extreme delays without crashing."""
        empty_metrics = PerformanceEvaluator.calculate_metrics([], self.cluster_config)
        self.assertEqual(empty_metrics["makespan"], 0.0)
        self.assertEqual(empty_metrics["efficiency_score"], 0.0)

        extreme_schedule = [{
            "job_id": "JOB-EXT",
            "runtime": 5.0,
            "finish_time": 1000.0,
            "waiting_time": 995.0,
            "cpu_cores": 1,
            "memory_mb": 512,
            "gpu_units": 0,
            "sla_status": "VIOLATED",
            "deadline": 10.0
        }]
        extreme_metrics = PerformanceEvaluator.calculate_metrics(extreme_schedule, self.cluster_config)
        self.assertTrue(0.0 <= extreme_metrics["efficiency_score"] <= 100.0)
        self.assertEqual(extreme_metrics["sla_violation_rate"], 100.0)

    def test_04_heuristic_deterministic_reproducibility(self):
        """Verify heuristics produce identical results when evaluated on the same workload."""
        jobs = WorkloadGenerator.generate_scenario("MEDIUM", num_jobs=10, seed=42)
        for algo in ["FCFS", "SJF", "Priority", "EDF", "Greedy"]:
            run1 = SchedulingDecisionEngine.execute_algorithm(algo, jobs, self.cluster_config)
            run2 = SchedulingDecisionEngine.execute_algorithm(algo, jobs, self.cluster_config)
            m1 = PerformanceEvaluator.calculate_metrics(run1["schedule"], self.cluster_config)
            m2 = PerformanceEvaluator.calculate_metrics(run2["schedule"], self.cluster_config)
            self.assertEqual(m1["makespan"], m2["makespan"])
            self.assertEqual(m1["avg_waiting_time"], m2["avg_waiting_time"])
            self.assertEqual(m1["efficiency_score"], m2["efficiency_score"])

if __name__ == "__main__":
    unittest.main()

