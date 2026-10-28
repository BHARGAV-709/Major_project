import React from 'react';
import { BookOpen, CheckCircle2, FileText, Cpu, BrainCircuit, ShieldAlert, BarChart3, Scale, Layers } from 'lucide-react';

export default function Documentation() {
  return (
    <div className="space-y-6 max-w-5xl">
      {/* Title */}
      <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-xs">
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Academic Project Documentation & Viva Guide</h1>
        <p className="text-xs text-slate-500 mt-1">
          Project Title: Resource Allocation and Scheduling Optimization for Enterprise Analytics: Heuristic, Metaheuristic, and RL Methods
        </p>
      </div>

      {/* Section 1: Abstract & Problem Statement */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-3">
        <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
          <BookOpen className="w-5 h-5 text-brand-600" />
          <h2 className="text-base font-bold text-slate-900">1. Problem Statement & Research Objectives</h2>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">
          Modern enterprise analytics platforms run heterogeneous workloads (Data Pipeline ETL jobs, Business Intelligence queries, Machine Learning training tasks, and Batch Analytics) competing for multi-dimensional compute resources (CPU Cores, RAM Memory GB, and GPU Accelerators).
        </p>
        <p className="text-xs text-slate-600 leading-relaxed font-semibold text-slate-800">
          The core objective: Which job should execute first, on which resources, and at what time so that the overall system finishes quickly (Makespan), uses multi-dimensional resources efficiently (Utilization), minimizes waiting latency, avoids financial SLA penalties, and minimizes compute operational expenditure?
        </p>
      </div>

      {/* Section 2: Mathematical Formulations */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
          <Cpu className="w-5 h-5 text-indigo-600" />
          <h2 className="text-base font-bold text-slate-900">2. Evaluation Metrics & Implemented Formulations</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
            <h4 className="font-bold text-slate-900">Makespan (M)</h4>
            <p className="text-slate-600 mt-1 font-mono text-[11px]">Makespan = max_j ( FinishTime_j )</p>
            <p className="text-slate-500 mt-1">Total simulation time elapsed until all submitted enterprise jobs finish execution.</p>
          </div>

          <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
            <h4 className="font-bold text-slate-900">Average Waiting Time (W)</h4>
            <p className="text-slate-600 mt-1 font-mono text-[11px]">Avg_Wait = (1/N) * sum_j ( StartTime_j - ArrivalTime_j )</p>
            <p className="text-slate-500 mt-1">Mean queue latency between job arrival in the cluster and the start of allocation.</p>
          </div>

          <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
            <h4 className="font-bold text-slate-900">Multi-Resource Utilization (%)</h4>
            <p className="text-slate-600 mt-1 font-mono text-[11px]">U_overall = 0.45*U_CPU + 0.45*U_Mem + 0.10*U_GPU</p>
            <p className="text-slate-500 mt-1">U_dim = (Used Resource Time / (Cluster_Capacity * Makespan)) * 100.</p>
          </div>

          <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
            <h4 className="font-bold text-slate-900">SLA Violation Rate (%)</h4>
            <p className="text-slate-600 mt-1 font-mono text-[11px]">SLA_Viol_Rate = ( Count( FinishTime_j &gt; Deadline_j ) / N ) * 100</p>
            <p className="text-slate-500 mt-1">Percentage of scheduled analytics workloads exceeding negotiated tenant deadlines.</p>
          </div>

          <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
            <h4 className="font-bold text-slate-900">Total Financial Cost ($)</h4>
            <p className="text-slate-600 mt-1 font-mono text-[11px]">Cost = CPU_cost + Mem_cost + GPU_cost + (Violations * $25.00)</p>
            <p className="text-slate-500 mt-1">Hardware usage costs plus financial contractual penalties for SLA breaches.</p>
          </div>

          <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
            <h4 className="font-bold text-slate-900">Composite Efficiency Score (0-100)</h4>
            <p className="text-slate-600 mt-1 font-mono text-[11px]">Score = 0.40*U_overall + 0.40*(100 - SLA_Viol) + 0.20*max(0, 100 - Avg_Wait)</p>
            <p className="text-slate-500 mt-1">Balanced academic benchmark metric bounded between 0.0 and 100.0 (saturates when Wait &ge; 100s).</p>
          </div>
        </div>
      </div>

      {/* Section 3: Empirical Benchmarking Findings */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
          <BarChart3 className="w-5 h-5 text-amber-600" />
          <h2 className="text-base font-bold text-slate-900">3. Standardized 25-Job Benchmark Findings (Source of Truth)</h2>
        </div>

        <div className="space-y-3 text-xs text-slate-600">
          <p>
            Benchmarks conducted across standardized 25-job Light, Medium, and Heavy workloads on a 40 CPU / 256GB RAM / 8 GPU cluster revealed distinct operational regimes verified against <code>standardized_benchmark_results.json</code>:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
            <div className="border border-slate-200 p-3 rounded-lg bg-slate-50">
              <h5 className="font-bold text-slate-800">Light Workload (Low Load)</h5>
              <p className="mt-1 text-[11px]">
                Zero congestion across all heuristics and metaheuristics (Makespan: 255.53s, Avg Wait: 0.00s, SLA Violations: 0%, Score: 62.49). RL agents exhibit minor exploration delays (~2–4s).
              </p>
            </div>
            <div className="border border-slate-200 p-3 rounded-lg bg-slate-50">
              <h5 className="font-bold text-slate-800">Medium Workload (Moderate Load)</h5>
              <p className="mt-1 text-[11px]">
                <strong>PSO</strong> (Score: 72.06 ± 0.71, SLA: 9.6%) and <strong>GA</strong> (71.54 ± 0.55, SLA: 11.2%) lead. <strong>SJF</strong> is the top heuristic (Score: 71.10, SLA: 12.0%) by prioritizing short execution jobs.
              </p>
            </div>
            <div className="border border-slate-200 p-3 rounded-lg bg-slate-50">
              <h5 className="font-bold text-slate-800">Heavy Workload (Saturated Load)</h5>
              <p className="mt-1 text-[11px]">
                Metaheuristics strongly outperform heuristics. <strong>PSO</strong> (Score: 44.56 ± 1.13, Makespan: 374.51s, SLA: 56.8%) and <strong>GA</strong> (44.14 ± 1.12, Makespan: 377.56s) dominate due to global permutation optimization.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Section 4: Viva Questions & Answers */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
          <BrainCircuit className="w-5 h-5 text-emerald-600" />
          <h2 className="text-base font-bold text-slate-900">4. Project Viva & Evaluation Q&A</h2>
        </div>

        <div className="space-y-4 text-xs">
          <div className="border-b border-slate-100 pb-3">
            <h4 className="font-bold text-slate-900">Q1: Why compare Heuristics, Metaheuristics, and RL together?</h4>
            <p className="text-slate-600 mt-1">
              Heuristics (FCFS, SJF, Priority, EDF, Greedy) execute in O(N log N) time and serve as standard production baselines. Metaheuristics (GA, PSO, SA) search global permutation spaces to escape greedy local optima. Reinforcement Learning (Q-Learning, DQN) trains adaptive agents that learn state-to-dispatch mappings. Benchmarking all three under identical workloads exposes their exact trade-offs in computation time versus schedule quality.
            </p>
          </div>

          <div className="border-b border-slate-100 pb-3">
            <h4 className="font-bold text-slate-900">Q2: Why did Metaheuristics (PSO/GA) outperform RL (Q-Learning/DQN) in Heavy benchmarks?</h4>
            <p className="text-slate-600 mt-1">
              Metaheuristics directly optimize full job sequence permutations across thousands of fitness evaluations. In contrast, tabular Q-Learning and DQN use a 6-dimensional aggregate state vector (average utilization, queue length, average priority/urgency) and a compact 25-30 episode training budget suitable for interactive execution. Without job-level attention architectures and thousands of training rollouts, RL acts on coarse state averages while GA/PSO evaluate exact schedule structures.
            </p>
          </div>

          <div className="border-b border-slate-100 pb-3">
            <h4 className="font-bold text-slate-900">Q3: How does the discrete-event simulator prevent resource deadlock and race conditions?</h4>
            <p className="text-slate-600 mt-1">
              The discrete-event simulator maintains an event priority queue sorted by simulation timestamp. Active allocations track exact CPU, memory, and GPU usage. When a running job completes, allocated resources are released immediately, and the scheduler dispatches waiting jobs only when requested resources are fully within cluster limits. Non-preemptive execution prevents cyclic waiting.
            </p>
          </div>

          <div>
            <h4 className="font-bold text-slate-900">Q4: How was policy evaluation separated from training in Q-Learning and DQN?</h4>
            <p className="text-slate-600 mt-1">
              During training, RL agents balance exploration and exploitation using an epsilon-greedy decay schedule (epsilon = 1.0 down to 0.05). In earlier revisions, exploratory schedules were accidentally recorded. In the corrected design, training updates the Q-table or PyTorch DQN network across episodes, and a distinct deterministic rollout (epsilon = 0) is executed to produce the reported schedule and metrics.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
