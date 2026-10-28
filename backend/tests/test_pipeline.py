import unittest
from app.preprocessing import PreprocessingPipeline
from app.workload import WorkloadLoader, WorkloadGenerator
from app.scheduler import SchedulingDecisionEngine
from app.evaluation import PerformanceEvaluator, BenchmarkRunner
from app.config import RAW_DATASET_PATH, DEFAULT_CLUSTER_CONFIG

class TestResourceSchedulingSystem(unittest.TestCase):

    def test_01_data_preprocessing(self):
        pipeline = PreprocessingPipeline()
        res = pipeline.run_full_pipeline(RAW_DATASET_PATH)
        self.assertTrue(res["validation"]["valid"])
        self.assertEqual(res["validation"]["remaining_missing_values"], 0)
        self.assertEqual(res["validation"]["remaining_duplicates"], 0)

    def test_02_workload_loading(self):
        jobs = WorkloadLoader.load_from_csv(RAW_DATASET_PATH, max_jobs=20)
        self.assertEqual(len(jobs), 20)
        self.assertTrue(all(j.cpu_cores > 0 for j in jobs))

    def test_03_heuristics_execution(self):
        jobs = WorkloadGenerator.generate_scenario("MEDIUM", num_jobs=15, seed=42)
        for algo in ["FCFS", "SJF", "Priority", "EDF", "Greedy"]:
            res = SchedulingDecisionEngine.execute_algorithm(algo, jobs, DEFAULT_CLUSTER_CONFIG)
            self.assertGreater(len(res["schedule"]), 0)

    def test_04_metaheuristics_execution(self):
        jobs = WorkloadGenerator.generate_scenario("LIGHT", num_jobs=10, seed=42)
        for algo in ["GA", "PSO", "SA"]:
            res = SchedulingDecisionEngine.execute_algorithm(algo, jobs, DEFAULT_CLUSTER_CONFIG)
            self.assertGreater(len(res["schedule"]), 0)

    def test_05_reinforcement_learning(self):
        jobs = WorkloadGenerator.generate_scenario("LIGHT", num_jobs=10, seed=42)
        for algo in ["Q-Learning", "DQN"]:
            res = SchedulingDecisionEngine.execute_algorithm(algo, jobs, DEFAULT_CLUSTER_CONFIG, {"episodes": 5})
            self.assertGreater(len(res["schedule"]), 0)

if __name__ == "__main__":
    unittest.main()
