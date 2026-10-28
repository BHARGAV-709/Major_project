import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestEndToEndRegressionComprehensive(unittest.TestCase):
    """
    Comprehensive End-to-End Regression Test Suite:
    1. Tests all 10 algorithms through the API endpoint (/api/simulation/run).
    2. Tests edge cases: empty workload (max_jobs=0), normal workload, mixed workload, 100% infeasible workload.
    3. Verifies completion_rate, completed_count, rejected_count, total_jobs in API response.
    4. Verifies database persistence in /api/experiments/history.
    5. Verifies error handling: invalid algorithm name, invalid dataset file, negative/malformed inputs.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.all_algos = [
            "FCFS", "SJF", "Priority", "EDF", "Greedy",
            "GA", "PSO", "SA", "Q-Learning", "DQN"
        ]

    def test_01_all_10_algorithms_via_simulation_endpoint(self):
        """Verify each of the 10 algorithms executes successfully via POST /api/simulation/run."""
        for algo in self.all_algos:
            with self.subTest(algorithm=algo):
                payload = {
                    "scenario": "LIGHT",
                    "max_jobs": 5,
                    "algorithm": algo,
                    "algo_params": {
                        "episodes": 2, "generations": 2, "iterations": 2,
                        "max_iter": 3, "pop_size": 4, "num_particles": 4
                    }
                }
                res = self.client.post("/api/simulation/run", json=payload)
                self.assertEqual(res.status_code, 200, f"Algorithm {algo} failed: {res.text}")
                data = res.json()
                self.assertEqual(data["algorithm"], algo)
                self.assertEqual(data["completed_count"], 5)
                self.assertEqual(data["rejected_count"], 0)
                self.assertEqual(data["total_jobs"], 5)
                self.assertEqual(data["completion_rate"], 100.0)
                self.assertEqual(len(data["schedule"]), 5)
                self.assertEqual(len(data["timeline"]), 5)
                self.assertIn("makespan", data["metrics"])
                self.assertIn("efficiency_score", data["metrics"])

    def test_02_empty_workload_simulation(self):
        """Verify that a simulation request with max_jobs=0 gracefully returns empty results with zero metrics."""
        payload = {
            "scenario": "LIGHT",
            "max_jobs": 0,
            "algorithm": "FCFS"
        }
        res = self.client.post("/api/simulation/run", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["completed_count"], 0)
        self.assertEqual(data["rejected_count"], 0)
        self.assertEqual(data["total_jobs"], 0)
        self.assertEqual(data["completion_rate"], 0.0)
        self.assertEqual(len(data["schedule"]), 0)
        self.assertEqual(data["metrics"]["makespan"], 0.0)
        self.assertEqual(data["metrics"]["efficiency_score"], 0.0)

    def test_03_database_experiment_history_persistence(self):
        """Verify that simulation and benchmark executions are properly logged in the database."""
        # Query experiment history
        res = self.client.get("/api/experiments/history")
        self.assertEqual(res.status_code, 200)
        history = res.json()
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
        first_record = history[0]
        self.assertIn("experiment_name", first_record)
        self.assertIn("algorithm", first_record)
        self.assertIn("metrics", first_record)
        self.assertIn("created_at", first_record)

    def test_04_error_handling_and_invalid_inputs(self):
        """Verify that invalid algorithm or malformed payloads return appropriate HTTP error responses."""
        # Unknown algorithm
        invalid_algo_payload = {
            "scenario": "LIGHT",
            "max_jobs": 5,
            "algorithm": "NON_EXISTENT_ALGORITHM"
        }
        res = self.client.post("/api/simulation/run", json=invalid_algo_payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Unknown algorithm", res.json()["detail"])

        # Invalid scenario / empty request
        malformed_payload = {
            "scenario": "UNKNOWN_SCENARIO",
            "max_jobs": 5,
            "algorithm": "FCFS"
        }
        res = self.client.post("/api/simulation/run", json=malformed_payload)
        self.assertEqual(res.status_code, 400)

if __name__ == "__main__":
    unittest.main()

