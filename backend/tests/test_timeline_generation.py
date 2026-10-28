import unittest
from app.workload import WorkloadGenerator
from app.config import DEFAULT_CLUSTER_CONFIG
from app.scheduler import SchedulingDecisionEngine

class TestTimelineAndGanttGeneration(unittest.TestCase):
    """
    Regression and validation tests for timeline generation and Gantt response data
    across all supported algorithms in single-simulation and comparison interfaces.
    """

    @classmethod
    def setUpClass(cls):
        cls.jobs = WorkloadGenerator.generate_scenario("LIGHT", num_jobs=10, seed=42)
        cls.cluster_config = DEFAULT_CLUSTER_CONFIG
        cls.expected_timeline_keys = {
            "job_id", "job_type", "server_id", "arrival_time", "start_time",
            "finish_time", "runtime", "waiting_time", "cpu", "memory_mb",
            "gpu", "sla_violated", "priority"
        }
        cls.all_algorithms = [
            "FCFS", "SJF", "Priority", "EDF", "Greedy",
            "GA", "PSO", "SA", "Q-Learning", "DQN"
        ]

    def test_all_algorithms_generate_non_empty_timeline(self):
        """Verify every supported algorithm generates non-empty timeline and resource history."""
        algo_params = {
            "episodes": 3,
            "generations": 3,
            "iterations": 3,
            "max_iter": 3,
            "pop_size": 5,
            "num_particles": 5
        }
        for algo in self.all_algorithms:
            with self.subTest(algorithm=algo):
                res = SchedulingDecisionEngine.execute_algorithm(
                    algorithm_name=algo,
                    jobs=self.jobs,
                    cluster_config=self.cluster_config,
                    algo_params=algo_params
                )
                self.assertIn("timeline", res)
                self.assertIn("resource_history", res)
                self.assertGreater(len(res["timeline"]), 0, f"Algorithm {algo} returned empty timeline")
                self.assertEqual(len(res["timeline"]), len(res["schedule"]),
                                 f"Algorithm {algo} timeline count does not match schedule count")
                self.assertGreater(len(res["resource_history"]), 0,
                                   f"Algorithm {algo} returned empty resource_history")

    def test_timeline_schema_and_frontend_compatibility(self):
        """Verify all timeline items adhere to the schema expected by GanttChartComponent.jsx."""
        algo_params = {"episodes": 2, "generations": 2, "iterations": 2, "max_iter": 2}
        for algo in ["GA", "PSO", "SA", "Q-Learning", "DQN"]:
            with self.subTest(algorithm=algo):
                res = SchedulingDecisionEngine.execute_algorithm(
                    algorithm_name=algo,
                    jobs=self.jobs,
                    cluster_config=self.cluster_config,
                    algo_params=algo_params
                )
                for item in res["timeline"]:
                    for key in self.expected_timeline_keys:
                        self.assertIn(key, item, f"Key '{key}' missing from {algo} timeline item: {item}")
                    # Type and value checks
                    self.assertIsInstance(item["job_id"], str)
                    self.assertIsInstance(item["server_id"], int)
                    self.assertGreaterEqual(item["server_id"], 1)
                    self.assertIsInstance(item["start_time"], (int, float))
                    self.assertIsInstance(item["finish_time"], (int, float))

    def test_timeline_invariants_and_capacity_constraints(self):
        """Verify start time precedes finish time, jobs do not start before arrival, and no duplicate job entries."""
        algo_params = {"episodes": 2, "generations": 2, "iterations": 2, "max_iter": 2}
        for algo in self.all_algorithms:
            with self.subTest(algorithm=algo):
                res = SchedulingDecisionEngine.execute_algorithm(
                    algorithm_name=algo,
                    jobs=self.jobs,
                    cluster_config=self.cluster_config,
                    algo_params=algo_params
                )
                timeline = res["timeline"]
                seen_jobs = set()

                for item in timeline:
                    # No duplicate jobs
                    self.assertNotIn(item["job_id"], seen_jobs, f"Duplicate job in {algo} timeline: {item['job_id']}")
                    seen_jobs.add(item["job_id"])

                    # Temporal consistency
                    self.assertGreaterEqual(
                        item["start_time"], item["arrival_time"],
                        f"Job {item['job_id']} started at {item['start_time']} before arrival {item['arrival_time']} in {algo}"
                    )
                    self.assertGreaterEqual(
                        item["finish_time"], item["start_time"],
                        f"Job {item['job_id']} finish time {item['finish_time']} is before start time {item['start_time']} in {algo}"
                    )

                # Check aggregate resource capacity constraints at all distinct times
                total_cpu = self.cluster_config["cpu_cores"]
                total_gpu = self.cluster_config["gpu_units"]
                timepoints = {t["start_time"] for t in timeline} | {t["finish_time"] for t in timeline}

                for t in timepoints:
                    active = [j for j in timeline if j["start_time"] <= t < j["finish_time"]]
                    used_cpu = sum(j["cpu"] for j in active)
                    used_gpu = sum(j["gpu"] for j in active)
                    self.assertLessEqual(used_cpu, total_cpu, f"CPU capacity exceeded at time {t} in {algo}: {used_cpu} > {total_cpu}")
                    self.assertLessEqual(used_gpu, total_gpu, f"GPU capacity exceeded at time {t} in {algo}: {used_gpu} > {total_gpu}")

if __name__ == "__main__":
    unittest.main()

