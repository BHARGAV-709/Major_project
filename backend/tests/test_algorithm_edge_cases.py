import unittest
from app.workload.job_model import Job
from app.simulation.resource_manager import ClusterResourceState
from app.scheduler.decision_engine import SchedulingDecisionEngine
from app.evaluation.metrics import PerformanceEvaluator

class TestAlgorithmEdgeCasesAndCapacity(unittest.TestCase):
    """
    Focused unit tests covering edge cases and capacity constraints across all 10 algorithms:
    - Empty workloads (0 jobs)
    - Single-job workloads (1 job)
    - Simultaneous job arrivals (identical arrival timestamps)
    - Multi-dimensional capacity constraints (CPU, RAM, GPU)
    - Unscheduled handling for resource-infeasible jobs
    """

    @classmethod
    def setUpClass(cls):
        cls.cluster_cfg = {'cpu_cores': 4, 'memory_gb': 16, 'gpu_units': 2}
        cls.algos = ['FCFS', 'SJF', 'Priority', 'EDF', 'Greedy', 'GA', 'PSO', 'SA', 'Q-Learning', 'DQN']

    def test_01_empty_workload_all_algorithms(self):
        """Verify that passing an empty job list returns an empty schedule with 0.0 metrics."""
        for a in self.algos:
            with self.subTest(algorithm=a):
                res = SchedulingDecisionEngine.execute_algorithm(
                    a, [], self.cluster_cfg,
                    {'episodes': 1, 'generations': 1, 'iterations': 1, 'max_iter': 1}
                )
                self.assertEqual(len(res["schedule"]), 0)
                m = PerformanceEvaluator.calculate_metrics(res["schedule"], self.cluster_cfg)
                self.assertEqual(m["makespan"], 0.0)
                self.assertEqual(m["efficiency_score"], 0.0)

    def test_02_single_job_workload_all_algorithms(self):
        """Verify that all 10 algorithms schedule a single valid job correctly."""
        single_job = [Job(
            job_id='J_SOLO', job_type='ML_TRAIN', arrival_time=0.0, runtime=10.0,
            cpu_cores=2, memory_mb=4096, gpu_units=1, priority=5, deadline=20.0
        )]
        for a in self.algos:
            with self.subTest(algorithm=a):
                res = SchedulingDecisionEngine.execute_algorithm(
                    a, single_job, self.cluster_cfg,
                    {'episodes': 1, 'generations': 1, 'iterations': 1, 'max_iter': 1}
                )
                self.assertEqual(len(res["schedule"]), 1)
                scheduled_job = res["schedule"][0]
                self.assertEqual(scheduled_job["job_id"], "J_SOLO")
                self.assertEqual(scheduled_job["start_time"], 0.0)
                self.assertEqual(scheduled_job["finish_time"], 10.0)
                self.assertEqual(scheduled_job["waiting_time"], 0.0)

    def test_03_simultaneous_arrivals_all_algorithms(self):
        """Verify that multiple jobs arriving at t=0.0 are queued and scheduled without deadlock or starvation."""
        simul_jobs = [
            Job(job_id=f'J{i}', job_type='BATCH', arrival_time=0.0, runtime=5.0*(i+1),
                cpu_cores=2, memory_mb=2048, gpu_units=0, priority=i+1, deadline=50.0)
            for i in range(5)
        ]
        for a in self.algos:
            with self.subTest(algorithm=a):
                res = SchedulingDecisionEngine.execute_algorithm(
                    a, simul_jobs, self.cluster_cfg,
                    {'episodes': 2, 'generations': 2, 'iterations': 2, 'max_iter': 5}
                )
                self.assertEqual(len(res["schedule"]), 5)
                # Verify non-overlapping capacity: cluster has 4 cores, each job takes 2 cores -> at most 2 jobs run concurrently
                timeline = res["timeline"]
                for t_point in [0.0, 5.0, 10.0, 15.0, 20.0]:
                    concurrent_cores = sum(
                        item["cpu"] for item in timeline
                        if item["start_time"] <= t_point < item["finish_time"]
                    )
                    self.assertLessEqual(concurrent_cores, self.cluster_cfg["cpu_cores"])

    def test_04_resource_infeasible_job_never_scheduled(self):
        """Verify that a job requiring more resources than total cluster capacity is never allocated."""
        infeas_jobs = [
            Job(job_id='J_OK', job_type='BATCH', arrival_time=0.0, runtime=10.0, cpu_cores=2, memory_mb=2048, gpu_units=0, priority=3, deadline=20.0),
            Job(job_id='J_BIG', job_type='BIG_DATA', arrival_time=0.0, runtime=10.0, cpu_cores=8, memory_mb=2048, gpu_units=0, priority=5, deadline=20.0)
        ]
        for a in self.algos:
            with self.subTest(algorithm=a):
                res = SchedulingDecisionEngine.execute_algorithm(
                    a, infeas_jobs, self.cluster_cfg,
                    {'episodes': 2, 'generations': 2, 'iterations': 2, 'max_iter': 5}
                )
                scheduled_ids = [j["job_id"] for j in res["schedule"]]
                self.assertNotIn("J_BIG", scheduled_ids, f"{a} scheduled an infeasible job!")

if __name__ == "__main__":
    unittest.main()
