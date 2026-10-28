import unittest
from app.workload.job_model import Job
from app.simulation.resource_manager import ClusterResourceState
from app.simulation.environment import DiscreteEventSimulator
from app.scheduler.decision_engine import SchedulingDecisionEngine
from app.evaluation.metrics import PerformanceEvaluator
from app.algorithms.heuristics import fcfs_scheduler

class TestInfeasibleJobHandlingFix(unittest.TestCase):
    """
    Validation tests for the fix handling permanently resource-infeasible jobs:
    1. Rejection across CPU, Memory, and GPU dimensions.
    2. Terminal status is explicitly 'REJECTED' (never silently left as 'WAITING' or 'COMPLETED').
    3. Feasible jobs complete normally; temporary waiting queues are unaffected.
    4. Purely infeasible workloads terminate cleanly with rejected_count equal to total jobs.
    5. API and DecisionEngine payload includes rejected_count and rejected_jobs metadata.
    6. Metrics remain robust and non-crashing.
    """

    @classmethod
    def setUpClass(cls):
        cls.cluster_cfg = {'cpu_cores': 4, 'memory_gb': 16, 'gpu_units': 2}
        cls.cluster_state = ClusterResourceState(total_cpu=4, total_memory_mb=16384.0, total_gpu=2)
        cls.algos = ['FCFS', 'SJF', 'Priority', 'EDF', 'Greedy', 'GA', 'PSO', 'SA', 'Q-Learning', 'DQN']

    def test_01_rejection_across_cpu_mem_gpu_dimensions(self):
        """Test that jobs exceeding cluster capacity in CPU, memory, or GPU are explicitly REJECTED."""
        infeas_cpu = Job(job_id='J_CPU', job_type='BATCH', arrival_time=0.0, runtime=5.0, cpu_cores=8, memory_mb=1024, gpu_units=0, priority=1, deadline=10.0)
        infeas_mem = Job(job_id='J_MEM', job_type='BATCH', arrival_time=0.0, runtime=5.0, cpu_cores=2, memory_mb=32768, gpu_units=0, priority=1, deadline=10.0)
        infeas_gpu = Job(job_id='J_GPU', job_type='BATCH', arrival_time=0.0, runtime=5.0, cpu_cores=2, memory_mb=1024, gpu_units=4, priority=1, deadline=10.0)
        feas = Job(job_id='J_OK', job_type='BATCH', arrival_time=0.0, runtime=5.0, cpu_cores=2, memory_mb=1024, gpu_units=1, priority=1, deadline=10.0)

        sim = DiscreteEventSimulator([infeas_cpu, infeas_mem, infeas_gpu, feas], self.cluster_state)
        completed = sim.run_simulation(fcfs_scheduler)

        # 1 feasible job completed
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].job_id, 'J_OK')
        self.assertEqual(completed[0].status, 'COMPLETED')

        # 3 infeasible jobs rejected
        self.assertEqual(len(sim.rejected_jobs), 3)
        rejected_ids = {j.job_id for j in sim.rejected_jobs}
        self.assertEqual(rejected_ids, {'J_CPU', 'J_MEM', 'J_GPU'})
        for rj in sim.rejected_jobs:
            self.assertEqual(rj.status, 'REJECTED')
            self.assertIsNone(rj.start_time)
            self.assertIsNone(rj.finish_time)

        # Waiting queue must be empty because all arrived jobs were either scheduled or rejected
        self.assertEqual(len(sim.waiting_queue), 0)

    def test_02_pure_infeasible_workload_across_all_algorithms(self):
        """Test a workload with only infeasible jobs across all 10 algorithms."""
        infeas_jobs = [
            Job(job_id='J_BIG1', job_type='BIG_DATA', arrival_time=0.0, runtime=10.0, cpu_cores=8, memory_mb=2048, gpu_units=0, priority=5, deadline=20.0),
            Job(job_id='J_BIG2', job_type='BIG_DATA', arrival_time=5.0, runtime=10.0, cpu_cores=16, memory_mb=2048, gpu_units=0, priority=5, deadline=20.0)
        ]
        for a in self.algos:
            with self.subTest(algorithm=a):
                res = SchedulingDecisionEngine.execute_algorithm(
                    a, infeas_jobs, self.cluster_cfg,
                    {'episodes': 2, 'generations': 2, 'iterations': 2, 'max_iter': 5}
                )
                self.assertEqual(res["completed_count"], 0)
                self.assertEqual(res["rejected_count"], 2)
                self.assertEqual(len(res["schedule"]), 0)
                self.assertEqual(len(res["rejected_jobs"]), 2)
                for rj in res["rejected_jobs"]:
                    self.assertEqual(rj["status"], "REJECTED")

    def test_03_mixed_workload_all_algorithms(self):
        """Test mixed workload across all 10 algorithms; verifies completed_count=2, rejected_count=1."""
        mixed_jobs = [
            Job(job_id='J_FEAS1', job_type='BATCH', arrival_time=0.0, runtime=10.0, cpu_cores=2, memory_mb=2048, gpu_units=0, priority=3, deadline=20.0),
            Job(job_id='J_INFEAS', job_type='BIG_DATA', arrival_time=0.0, runtime=10.0, cpu_cores=8, memory_mb=2048, gpu_units=0, priority=5, deadline=20.0),
            Job(job_id='J_FEAS2', job_type='BATCH', arrival_time=5.0, runtime=10.0, cpu_cores=2, memory_mb=2048, gpu_units=0, priority=2, deadline=30.0)
        ]
        for a in self.algos:
            with self.subTest(algorithm=a):
                res = SchedulingDecisionEngine.execute_algorithm(
                    a, mixed_jobs, self.cluster_cfg,
                    {'episodes': 2, 'generations': 2, 'iterations': 2, 'max_iter': 5}
                )
                self.assertEqual(res["completed_count"], 2)
                self.assertEqual(res["rejected_count"], 1)
                self.assertEqual(len(res["schedule"]), 2)
                self.assertEqual(res["rejected_jobs"][0]["job_id"], "J_INFEAS")
                self.assertEqual(res["rejected_jobs"][0]["status"], "REJECTED")

    def test_04_temporary_waiting_queue_preservation(self):
        """Verify that jobs temporarily waiting for resources are NOT marked as REJECTED."""
        # Cluster has 4 cores. J1 and J2 each need 3 cores. Both fit cluster individually!
        competing_jobs = [
            Job(job_id='J1', job_type='BATCH', arrival_time=0.0, runtime=10.0, cpu_cores=3, memory_mb=2048, gpu_units=0, priority=3, deadline=20.0),
            Job(job_id='J2', job_type='BATCH', arrival_time=0.0, runtime=10.0, cpu_cores=3, memory_mb=2048, gpu_units=0, priority=3, deadline=20.0)
        ]
        res = SchedulingDecisionEngine.execute_algorithm('FCFS', competing_jobs, self.cluster_cfg)
        self.assertEqual(res["completed_count"], 2)
        self.assertEqual(res["rejected_count"], 0)
        self.assertEqual(len(res["rejected_jobs"]), 0)
        # J1 finishes at 10.0, J2 finishes at 20.0
        sched = res["schedule"]
        self.assertEqual(sched[0]["finish_time"], 10.0)
        self.assertEqual(sched[1]["finish_time"], 20.0)

    def test_05_metric_semantics_across_three_workload_cases(self):
        """
        Explicitly verify metric semantics across all three workload categories:
        Case A: All jobs feasible (standard benchmark assumption)
        Case B: Mixed workload (some feasible, some permanently rejected)
        Case C: 100% rejected workload (all jobs permanently infeasible)
        """
        # Case A: All jobs feasible
        jobs_a = [
            Job(job_id='A1', job_type='BATCH', arrival_time=0.0, runtime=100.0, cpu_cores=4, memory_mb=8192, gpu_units=1, priority=1, deadline=200.0),
            Job(job_id='A2', job_type='BATCH', arrival_time=5.0, runtime=100.0, cpu_cores=4, memory_mb=8192, gpu_units=1, priority=1, deadline=250.0)
        ]
        res_a = SchedulingDecisionEngine.execute_algorithm('FCFS', jobs_a, self.cluster_cfg)
        metrics_a = PerformanceEvaluator.calculate_metrics(res_a["schedule"], self.cluster_cfg)
        self.assertEqual(res_a["completed_count"], 2)
        self.assertEqual(res_a["rejected_count"], 0)
        self.assertEqual(res_a["total_jobs"], 2)
        self.assertGreater(metrics_a["makespan"], 0.0)
        self.assertGreater(metrics_a["total_cost"], 0.0)
        self.assertIn("sla_violation_rate", metrics_a)

        # Case B: Mixed workload (1 feasible, 1 infeasible)
        jobs_b = [
            Job(job_id='B_FEAS', job_type='BATCH', arrival_time=0.0, runtime=100.0, cpu_cores=4, memory_mb=8192, gpu_units=1, priority=1, deadline=200.0),
            Job(job_id='B_REJECT', job_type='BIG_DATA', arrival_time=0.0, runtime=10.0, cpu_cores=8, memory_mb=2048, gpu_units=0, priority=1, deadline=15.0)
        ]
        res_b = SchedulingDecisionEngine.execute_algorithm('FCFS', jobs_b, self.cluster_cfg)
        metrics_b = PerformanceEvaluator.calculate_metrics(res_b["schedule"], self.cluster_cfg)
        self.assertEqual(res_b["completed_count"], 1)
        self.assertEqual(res_b["rejected_count"], 1)
        self.assertEqual(res_b["total_jobs"], 2)
        # Metrics evaluate admitted/executed schedule
        self.assertEqual(metrics_b["makespan"], 100.0)
        self.assertEqual(metrics_b["avg_waiting_time"], 0.0)
        # B_FEAS finished at t=100 <= deadline=200 -> 0 SLA violations
        self.assertEqual(metrics_b["sla_violation_count"], 0)
        self.assertEqual(metrics_b["sla_violation_rate"], 0.0)
        # Compute cost only incurred for executed B_FEAS
        self.assertGreater(metrics_b["total_cost"], 0.0)
        # Rejected jobs list explicitly captures B_REJECT with reason
        self.assertEqual(len(res_b["rejected_jobs"]), 1)
        self.assertEqual(res_b["rejected_jobs"][0]["job_id"], "B_REJECT")
        self.assertEqual(res_b["rejected_jobs"][0]["status"], "REJECTED")

        # Case C: 100% rejected workload
        jobs_c = [
            Job(job_id='C1', job_type='BIG_DATA', arrival_time=0.0, runtime=10.0, cpu_cores=8, memory_mb=2048, gpu_units=0, priority=1, deadline=15.0),
            Job(job_id='C2', job_type='GPU_BURST', arrival_time=0.0, runtime=10.0, cpu_cores=2, memory_mb=2048, gpu_units=5, priority=1, deadline=15.0)
        ]
        res_c = SchedulingDecisionEngine.execute_algorithm('FCFS', jobs_c, self.cluster_cfg)
        metrics_c = PerformanceEvaluator.calculate_metrics(res_c["schedule"], self.cluster_cfg)
        self.assertEqual(res_c["completed_count"], 0)
        self.assertEqual(res_c["rejected_count"], 2)
        self.assertEqual(res_c["total_jobs"], 2)
        self.assertEqual(len(res_c["schedule"]), 0)
        # Metrics must safely return 0.0 without divide-by-zero or crashes
        self.assertEqual(metrics_c["makespan"], 0.0)
        self.assertEqual(metrics_c["avg_waiting_time"], 0.0)
        self.assertEqual(metrics_c["cpu_utilization"], 0.0)
        self.assertEqual(metrics_c["memory_utilization"], 0.0)
        self.assertEqual(metrics_c["gpu_utilization"], 0.0)
        self.assertEqual(metrics_c["sla_violation_count"], 0)
        self.assertEqual(metrics_c["sla_violation_rate"], 0.0)
        self.assertEqual(metrics_c["total_cost"], 0.0)
        self.assertEqual(metrics_c["efficiency_score"], 0.0)

if __name__ == "__main__":
    unittest.main()
