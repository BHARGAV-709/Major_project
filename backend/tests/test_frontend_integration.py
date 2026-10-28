import unittest
import io
import os
from fastapi.testclient import TestClient
from app.main import app
from app.config import RAW_DATASET_PATH, CORS_ORIGINS

class TestFrontendBackendIntegration(unittest.TestCase):
    """
    Integration tests covering all API endpoints invoked by the React frontend:
    - Status check
    - Dataset preview and upload
    - Preprocessing pipeline execution
    - Workload generation
    - Single simulation execution (including timeline & schedule for Gantt)
    - Multi-algorithm benchmark comparison
    - Experiments history
    - CORS and Configurable Origins
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_api_status(self):
        """Frontend Header / Status indicator."""
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ONLINE")
        self.assertIn("dataset_found", data)
        self.assertIn("algorithms", data)

    def test_dataset_preview(self):
        """Frontend Dataset.jsx preview."""
        response = self.client.get("/api/dataset/preview?max_rows=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("columns", data)
        self.assertIn("preview_rows", data)
        self.assertLessEqual(len(data["preview_rows"]), 10)

    def test_dataset_upload(self):
        """Frontend Dataset.jsx CSV upload."""
        csv_content = b"job_id,cpu_cores,memory_mb,gpu_units,runtime,arrival_time,deadline,priority\nJOB-01,2,2048,0,10.0,0.0,20.0,3\n"
        files = {"file": ("test_upload.csv", io.BytesIO(csv_content), "text/csv")}
        response = self.client.post("/api/dataset/upload", files=files)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["rows"], 1)

    def test_preprocessing_run(self):
        """Frontend Preprocessing.jsx 8-step pipeline execution."""
        payload = {
            "missing_strategy": "impute_mean",
            "outlier_method": "iqr",
            "scale_method": "minmax"
        }
        response = self.client.post("/api/preprocessing/run", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("summary", data)
        self.assertIn("sample_cleaned_rows", data)

    def test_workload_generation(self):
        """Frontend WorkloadGenerator.jsx synthetic scenario generation."""
        response = self.client.post("/api/workload/generate?scenario=LIGHT&num_jobs=10&seed=42")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["scenario"], "LIGHT")
        self.assertEqual(data["count"], 10)
        self.assertEqual(len(data["jobs"]), 10)

    def test_simulation_run(self):
        """Frontend Simulation.jsx and GanttView.jsx execution with timeline and metrics."""
        payload = {
            "scenario": "LIGHT",
            "max_jobs": 5,
            "algorithm": "Q-Learning",
            "algo_params": {"episodes": 2}
        }
        response = self.client.post("/api/simulation/run", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("metrics", data)
        self.assertIn("schedule", data)
        self.assertIn("timeline", data)
        self.assertEqual(len(data["timeline"]), 5)
        # Verify Gantt timeline item schema
        first_item = data["timeline"][0]
        for key in ["job_id", "job_type", "server_id", "start_time", "finish_time", "cpu", "memory_mb", "gpu"]:
            self.assertIn(key, first_item)

    def test_benchmark_run(self):
        """Frontend Experiments.jsx, Dashboard.jsx, and Results.jsx multi-algorithm benchmark."""
        payload = {
            "scenario": "LIGHT",
            "max_jobs": 5,
            "algorithms": ["FCFS", "SJF", "Q-Learning"],
            "algo_params": {"episodes": 2}
        }
        response = self.client.post("/api/benchmark/run", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("benchmark_summary", data)
        self.assertIn("detailed_results", data)
        self.assertEqual(len(data["benchmark_summary"]), 3)
        # Check summary ranking properties
        self.assertEqual(data["benchmark_summary"][0]["rank"], 1)
        for res in data["benchmark_summary"]:
            self.assertIn("efficiency_score", res)
            self.assertIn("makespan", res)

    def test_experiment_history(self):
        """Frontend /experiments/history database query."""
        response = self.client.get("/api/experiments/history")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_cors_configuration(self):
        """Verify configurable CORS origins include standard frontend dev ports."""
        self.assertTrue(len(CORS_ORIGINS) > 0)
        self.assertTrue(any("3000" in o or "*" in o for o in CORS_ORIGINS))

if __name__ == "__main__":
    unittest.main()

