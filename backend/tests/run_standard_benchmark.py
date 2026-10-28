import json
import copy
import numpy as np
from app.workload.job_model import Job
from app.scheduler.decision_engine import SchedulingDecisionEngine
from app.evaluation.metrics import PerformanceEvaluator

def run_standardized_benchmark():
    with open("benchmark_workloads_standard.json", "r") as f:
        data = json.load(f)

    cluster_config = data["cluster"]
    workloads_dict = data["workloads"]

    # All 10 supported algorithms
    deterministic_algos = ["FCFS", "SJF", "Priority", "EDF", "Greedy"]
    stochastic_algos = ["GA", "PSO", "SA", "Q-Learning", "DQN"]

    scenarios = ["LIGHT", "MEDIUM", "HEAVY"]
    benchmark_report = {}

    for scenario_name in scenarios:
        raw_jobs = [Job(**d) for d in workloads_dict[scenario_name]]
        print(f"\n=======================================================")
        print(f"BENCHMARK SCENARIO: {scenario_name} (25 jobs, identical workload)")
        print(f"=======================================================")
        
        scenario_results = {}

        # 1. Deterministic Heuristics (single exact run)
        for algo in deterministic_algos:
            res = SchedulingDecisionEngine.execute_algorithm(
                algo, copy.deepcopy(raw_jobs), cluster_config
            )
            m = PerformanceEvaluator.calculate_metrics(res["schedule"], cluster_config)
            scenario_results[algo] = {
                "type": "Deterministic",
                "makespan": (m["makespan"], 0.0),
                "avg_waiting": (m["avg_waiting_time"], 0.0),
                "utilization": (m["overall_utilization"], 0.0),
                "sla_rate": (m["sla_violation_rate"], 0.0),
                "cost": (m["total_cost"], 0.0),
                "score": (m["efficiency_score"], 0.0),
                "cpu_time": (res["execution_time_sec"], 0.0),
                "completed": res["completed_count"]
            }

        # 2. Stochastic Algorithms (5 repeated seeds for robust mean ± std)
        stochastic_seeds = [10, 20, 30, 40, 50]
        stochastic_params = {
            "GA": {"pop_size": 25, "generations": 25},
            "PSO": {"num_particles": 20, "iterations": 25},
            "SA": {"initial_temp": 500.0, "max_iter": 75},
            "Q-Learning": {"episodes": 30},
            "DQN": {"episodes": 25}
        }

        for algo in stochastic_algos:
            runs_m = []
            runs_t = []
            params = stochastic_params[algo]

            for s_seed in stochastic_seeds:
                np.random.seed(s_seed)
                res = SchedulingDecisionEngine.execute_algorithm(
                    algo, copy.deepcopy(raw_jobs), cluster_config, params
                )
                m = PerformanceEvaluator.calculate_metrics(res["schedule"], cluster_config)
                runs_m.append(m)
                runs_t.append(res["execution_time_sec"])

            mk_vals = [r["makespan"] for r in runs_m]
            wt_vals = [r["avg_waiting_time"] for r in runs_m]
            ut_vals = [r["overall_utilization"] for r in runs_m]
            sla_vals = [r["sla_violation_rate"] for r in runs_m]
            cost_vals = [r["total_cost"] for r in runs_m]
            score_vals = [r["efficiency_score"] for r in runs_m]

            scenario_results[algo] = {
                "type": "Stochastic (5 seeds)",
                "makespan": (round(float(np.mean(mk_vals)), 2), round(float(np.std(mk_vals)), 2)),
                "avg_waiting": (round(float(np.mean(wt_vals)), 2), round(float(np.std(wt_vals)), 2)),
                "utilization": (round(float(np.mean(ut_vals)), 2), round(float(np.std(ut_vals)), 2)),
                "sla_rate": (round(float(np.mean(sla_vals)), 2), round(float(np.std(sla_vals)), 2)),
                "cost": (round(float(np.mean(cost_vals)), 2), round(float(np.std(cost_vals)), 2)),
                "score": (round(float(np.mean(score_vals)), 2), round(float(np.std(score_vals)), 2)),
                "cpu_time": (round(float(np.mean(runs_t)), 4), round(float(np.std(runs_t)), 4)),
                "completed": len(res["schedule"])
            }

        benchmark_report[scenario_name] = scenario_results

        # Print formatted summary table
        print(f"{'Algorithm':12s} | {'Makespan (s)':17s} | {'Wait (s)':13s} | {'Util (%)':14s} | {'SLA Viol (%)':15s} | {'Total Cost ($)':17s} | {'Score':14s} | {'Compute Time'}")
        print("-" * 125)
        for a_name in deterministic_algos + stochastic_algos:
            d = scenario_results[a_name]
            mk_s = f"{d['makespan'][0]:.2f} ± {d['makespan'][1]:.2f}" if d['makespan'][1] > 0 else f"{d['makespan'][0]:.2f}"
            wt_s = f"{d['avg_waiting'][0]:.2f} ± {d['avg_waiting'][1]:.2f}" if d['avg_waiting'][1] > 0 else f"{d['avg_waiting'][0]:.2f}"
            ut_s = f"{d['utilization'][0]:.2f} ± {d['utilization'][1]:.2f}" if d['utilization'][1] > 0 else f"{d['utilization'][0]:.2f}"
            sla_s = f"{d['sla_rate'][0]:.1f} ± {d['sla_rate'][1]:.1f}" if d['sla_rate'][1] > 0 else f"{d['sla_rate'][0]:.1f}"
            cost_s = f"${d['cost'][0]:.2f} ± {d['cost'][1]:.2f}" if d['cost'][1] > 0 else f"${d['cost'][0]:.2f}"
            sc_s = f"{d['score'][0]:.2f} ± {d['score'][1]:.2f}" if d['score'][1] > 0 else f"{d['score'][0]:.2f}"
            t_s = f"{d['cpu_time'][0]:.3f}s"
            print(f"{a_name:12s} | {mk_s:17s} | {wt_s:13s} | {ut_s:14s} | {sla_s:15s} | {cost_s:17s} | {sc_s:14s} | {t_s}")

    with open("standardized_benchmark_results.json", "w") as f:
        json.dump(benchmark_report, f, indent=2)
    print("\nBenchmark completed and saved to standardized_benchmark_results.json")

if __name__ == "__main__":
    run_standardized_benchmark()
