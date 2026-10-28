# Resource Allocation and Scheduling Optimization for Enterprise Analytics

[![Backend Tests](https://img.shields.io/badge/pytest-27%2F27%20passed-brightgreen.svg)]()
[![Frontend Build](https://img.shields.io/badge/vite%20build-passing-brightgreen.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)]()
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg)]()
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C.svg)]()

An end-to-end discrete-event simulation, benchmarking, and visualization platform designed to evaluate multi-tenant enterprise scheduling algorithms across heterogeneous compute resources (CPU Cores, RAM Memory, and GPU Accelerators).

The framework implements, benchmarks, and analyzes **10 distinct scheduling algorithms** spanning classical heuristics, metaheuristic evolutionary strategies, and reinforcement learning methods under standardized multi-dimensional workload constraints.

---

## Table of Contents
1. [Architectural Overview](#architectural-overview)
2. [Technology Stack](#technology-stack)
3. [Implemented Scheduling Algorithms](#implemented-scheduling-algorithms)
4. [Evaluation Metrics & Formulations](#evaluation-metrics--formulations)
5. [Standardized Benchmark Results (25 Jobs)](#standardized-benchmark-results-25-jobs)
6. [Empirical Analysis & Academic Findings](#empirical-analysis--academic-findings)
7. [Installation & Setup](#installation--setup)
8. [Running Verification Suites](#running-verification-suites)
9. [Project Limitations & Known Boundaries](#project-limitations--known-boundaries)

---

## Architectural Overview

The platform uses a decoupled client-server architecture:
- **Backend (FastAPI + Python 3.10)**: Provides high-throughput asynchronous REST endpoints, SQLite persistence via SQLAlchemy, discrete-event simulation engines (`SimEngine`), algorithm implementations, policy evaluators, and benchmark runners.
- **Frontend (React 18 + Vite + TailwindCSS)**: Delivers a responsive dashboard with interactive Gantt timeline views, multi-metric comparison charts (Recharts), workload generators, dataset upload & preprocessing, and CSV export capabilities.

```
┌─────────────────────────────────────────────────────────────┐
│                    React 18 + Vite UI                       │
│  (Dashboard, Simulation, Workload Gen, Gantt, Comparison)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON REST APIs
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Backend Engine                   │
│                                                             │
│  ┌───────────────────────┐       ┌───────────────────────┐  │
│  │  Workload Generator   │       │ Discrete Event Engine │  │
│  │ (Light/Medium/Heavy)  │       │ (SimEngine Timeline)  │  │
│  └───────────┬───────────┘       └───────────┬───────────┘  │
│              │                               │              │
│  ┌───────────▼───────────────────────────────▼───────────┐  │
│  │             10 Scheduling Algorithms                  │  │
│  │  • Heuristics: FCFS, SJF, Priority, EDF, Greedy       │  │
│  │  • Metaheuristics: GA, PSO, SA                        │  │
│  │  • Reinforcement Learning: Tabular Q-Learning, DQN    │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│  ┌───────────────────────────▼───────────────────────────┐  │
│  │          Performance Evaluator & SQLite DB            │  │
│  │    (Makespan, Wait Time, Utilization, SLA, Cost)      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technologies & Libraries |
| :--- | :--- |
| **Backend Framework** | Python 3.10, FastAPI, Uvicorn, Starlette, Pydantic |
| **Data Processing & ML** | NumPy, PyTorch (DQN Neural Architecture), Pandas, Scikit-Learn |
| **Database & ORM** | SQLite (`resource_scheduler.db`), SQLAlchemy ORM |
| **Testing Harness** | Pytest 9.x, Starlette TestClient, AnyIO |
| **Frontend Framework** | React 18.3, Vite 6.x, React Router DOM 6.x |
| **UI Components & Styling**| TailwindCSS, Lucide-React icons, Recharts visualization library |
| **Networking & HTTP** | Axios client with configurable environment baseURL |

---

## Implemented Scheduling Algorithms

The platform benchmarks 10 algorithms categorized into three distinct algorithmic paradigms:

### 1. Heuristic Dispatchers
- **FCFS (First-Come, First-Served)**: Dispatches jobs strictly in order of arrival timestamps ($T_{\text{arrival}}$). Simple and predictable, but subject to the convoy effect when long-duration jobs monopolize cluster resources.
- **SJF (Shortest Job First)**: Prioritizes queued jobs with the smallest execution duration ($T_{\text{runtime}}$). Proven to minimize mean waiting time, though susceptible to long-job starvation under sustained load.
- **Priority Scheduling**: Sorts waiting queues by user tenant tier (Classes 1–5). Ensures business-critical analytics execute ahead of standard batch jobs.
- **EDF (Earliest Deadline First)**: Schedules jobs with the nearest SLA commitment timestamp ($T_{\text{deadline}}$). Dynamic optimal scheduling for avoiding deadline breaches under low utilization.
- **Greedy Best-Fit**: Evaluates candidate jobs dynamically at each scheduling tick using a multi-resource fit metric:
  $$\text{Fit} = 0.45 \cdot \left(\frac{\text{req\_cpu}}{\text{avail\_cpu}}\right) + 0.45 \cdot \left(\frac{\text{req\_mem}}{\text{avail\_mem}}\right) + 0.10 \cdot \left(\frac{\text{req\_gpu}}{\text{avail\_gpu}}\right)$$
  Prioritizes jobs that maximize instantaneous resource utilization without exceeding available capacities.

### 2. Metaheuristic Global Optimizers
- **Genetic Algorithm (GA)**: Evolutionary optimizer that encodes job sequence permutations as chromosomes. Employs:
  - **Selection**: Tournament selection ($k=3$).
  - **Crossover**: Order Crossover (OX) preserving permutation validity without duplicate job IDs.
  - **Mutation**: Swap mutation ($p_m = 0.1$).
  - **Fitness Function**: Multi-objective minimization of weighted makespan, waiting time, SLA violation penalties, and resource idle overhead.
- **Particle Swarm Optimization (PSO)**: Swarm intelligence operating on continuous position vectors mapped to job priority rankings. Particles update velocities towards personal best ($\mathbf{p}_{\text{best}}$) and global best ($\mathbf{g}_{\text{best}}$):
  $$\mathbf{v}_{i}^{(t+1)} = w \cdot \mathbf{v}_{i}^{(t)} + c_1 r_1 (\mathbf{p}_{\text{best},i} - \mathbf{x}_{i}^{(t)}) + c_2 r_2 (\mathbf{g}_{\text{best}} - \mathbf{x}_{i}^{(t)})$$
- **Simulated Annealing (SA)**: Probabilistic hill-climbing search inspired by metallurgical annealing. Explores neighboring job permutations via adjacent swap operations. Employs the Metropolis acceptance criterion:
  $$P(\text{accept}) = \exp\left(-\frac{\Delta F}{T}\right)$$
  allowing controlled uphill steps at high temperatures ($T$) to escape local minima.

### 3. Reinforcement Learning Agents
- **Tabular Q-Learning**: Model-free temporal difference control using a discretized 6-dimensional state vector (CPU utilization bucket, RAM utilization bucket, GPU utilization bucket, queue length bucket, average queue priority, and urgency index). Updates state-action values via the classic Bellman equation:
  $$Q(s, a) \leftarrow Q(s, a) + \alpha \left[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right]$$
- **Deep Q-Network (DQN)**: Deep RL agent utilizing a multi-layer perceptron (Linear $6 \to 64 \to 64 \to |\mathcal{A}|$) parameterized with PyTorch. Features an Experience Replay Buffer ($N = 2000$), target network decoupling ($\tau$-updates), and MSE loss minimization on temporal difference error:
  $$\mathcal{L}(\theta) = \mathbb{E}\left[ \left( r + \gamma \max_{a'} Q(s', a'; \theta^-) - Q(s, a; \theta) \right)^2 \right]$$

> **Evaluation Procedure**: Both Q-Learning and DQN are trained for 25–30 episodes under exploratory $\epsilon$-greedy policies. Post-training, the learned policy is evaluated deterministically ($\epsilon = 0$) across the identical evaluation workload to produce final schedules and metrics.

---

## Evaluation Metrics & Formulations

All 10 algorithms are evaluated through `PerformanceEvaluator` in `backend/app/evaluation/metrics.py` using identical, un-skewed mathematical formulas:

### 1. Makespan ($M$)
The total simulation timestamp when all queued jobs have finished execution:
$$M = \max_{j \in \mathcal{J}} (\text{finish\_time}_j)$$

### 2. Average Waiting Time ($\bar{W}$)
The average latency from job submission arrival to the start of processing:
$$\bar{W} = \frac{1}{|\mathcal{J}|} \sum_{j \in \mathcal{J}} (\text{start\_time}_j - \text{arrival\_time}_j)$$

### 3. Resource Utilization ($U$)
Dimension-specific occupancy computed as the ratio of active core-seconds, byte-seconds, and unit-seconds to total available cluster capacity over the makespan:
$$U_{\text{CPU}} = \frac{\sum_{j} \text{cpu}_j \cdot \text{runtime}_j}{C_{\text{CPU}} \cdot M} \times 100, \quad U_{\text{Mem}} = \frac{\sum_{j} \text{mem}_j \cdot \text{runtime}_j}{C_{\text{Mem}} \cdot M} \times 100, \quad U_{\text{GPU}} = \frac{\sum_{j} \text{gpu}_j \cdot \text{runtime}_j}{C_{\text{GPU}} \cdot M} \times 100$$
$$U_{\text{overall}} = 0.45 \cdot U_{\text{CPU}} + 0.45 \cdot U_{\text{Mem}} + 0.10 \cdot U_{\text{GPU}}$$

### 4. SLA Violation Rate ($R_{\text{SLA}}$)
Percentage of scheduled jobs whose execution finish time exceeds the negotiated SLA deadline:
$$R_{\text{SLA}} = \frac{\sum_{j} \mathbb{I}(\text{finish\_time}_j > \text{deadline}_j)}{|\mathcal{J}|} \times 100$$

### 5. Financial Cost Model
Calculates cloud compute consumption plus monetary penalties incurred from SLA breaches:
$$\text{Cost} = \sum (\text{cpu\_time} \cdot \text{Rate}_{\text{CPU}}) + \sum (\text{mem\_time} \cdot \text{Rate}_{\text{Mem}}) + \sum (\text{gpu\_time} \cdot \text{Rate}_{\text{GPU}}) + (N_{\text{violations}} \cdot \text{Penalty}_{\text{SLA}})$$
*Default rates: CPU = \$0.00005/sec, Memory = \$0.00001/GB-sec, GPU = \$0.0002/sec, SLA Penalty = \$25.00/breach.*

### 6. Composite Efficiency Score
A normalized metric (0 to 100) combining cluster utilization, SLA compliance, and waiting latency:
$$\text{Score} = \max\left(0, \min\left(100, 0.40 \cdot U_{\text{overall}} + 0.40 \cdot (100 - R_{\text{SLA}}) + 0.20 \cdot \max(0, 100 - \bar{W})\right)\right)$$

*Note on Waiting Time Saturation*: When average waiting time $\bar{W} \ge 100$ seconds under heavy queue saturation, the waiting penalty term $\max(0, 100 - \bar{W})$ evaluates to `0.0` (it saturates rather than becoming negative), leaving the score determined by utilization ($40\%$) and SLA compliance ($40\%$).

---

## Standardized Benchmark Results (25 Jobs)

All benchmarks were executed on an identical cluster environment:
- **Cluster Capacity**: 40 CPU Cores, 256 GB RAM, 8 GPU Accelerators.
- **Workload Scale**: Standardized at **$N = 25$ jobs per scenario**, generated with deterministic Master Seed `42` and serialized to `benchmark_workloads_standard.json`.
- **Fairness Guarantee**: All 10 algorithms receive identical deep-copied job instances within each scenario.
- **Reporting Methodology**:
  - **Deterministic Heuristics (FCFS, SJF, Priority, EDF, Greedy)**: Single exact execution run.
  - **Stochastic Optimizers (GA, PSO, SA, Q-Learning, DQN)**: Evaluated over **5 independent random seeds** ($S \in \{10, 20, 30, 40, 50\}$). Results report $\text{Mean} \pm \text{Standard Deviation}$.
- **Source of Truth Artifact**: Direct verification against `standardized_benchmark_results.json`.

### Benchmark Results Table

| Workload | Algorithm | Type | Makespan (s) | Avg Wait (s) | Utilization (%) | SLA Viol (%) | Total Cost (\$) | Efficiency Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **LIGHT** | **FCFS** | Deterministic | 255.53 | 0.00 | 6.22% | 0.0% | \$0.08 | 62.49 |
| | **SJF** | Deterministic | 255.53 | 0.00 | 6.22% | 0.0% | \$0.08 | 62.49 |
| | **Priority** | Deterministic | 255.53 | 0.00 | 6.22% | 0.0% | \$0.08 | 62.49 |
| | **EDF** | Deterministic | 255.53 | 0.00 | 6.22% | 0.0% | \$0.08 | 62.49 |
| | **Greedy** | Deterministic | 255.53 | 0.00 | 6.22% | 0.0% | \$0.08 | 62.49 |
| | **GA** | Stochastic (5 seeds) | 255.53 | 0.00 | 6.22% | 0.0% | \$0.08 | 62.49 |
| | **PSO** | Stochastic (5 seeds) | 255.53 | 0.00 | 6.22% | 0.0% | \$0.08 | 62.49 |
| | **SA** | Stochastic (5 seeds) | 255.53 | 0.00 | 6.22% | 0.0% | \$0.08 | 62.49 |
| | **Q-Learning**| Stochastic (5 seeds) | 255.53 | 4.16 ± 3.38 | 6.22% | 5.6% ± 5.4% | \$35.08 ± 33.91 | 59.42 ± 2.84 |
| | **DQN** | Stochastic (5 seeds) | 260.68 ± 7.96 | 3.02 ± 2.77 | 6.10% ± 0.18% | 3.2% ± 6.4% | \$20.08 ± 40.00 | 60.56 ± 2.84 |
| **MEDIUM** | **PSO** | Stochastic (5 seeds) | **176.45 ± 0.35** | **8.95 ± 0.44** | **44.21% ± 0.09%** | **9.6% ± 2.0%** | **\$60.43 ± 12.25** | **72.06 ± 0.71** |
| | **GA** | Stochastic (5 seeds) | 175.92 ± 0.35 | 8.57 ± 0.57 | 44.35% ± 0.09% | 11.2% ± 1.6% | \$70.43 ± 10.00 | 71.54 ± 0.55 |
| | **SJF** | Deterministic | 178.18 | 8.07 | 43.78% | 12.0% | \$75.43 | 71.10 |
| | **SA** | Stochastic (5 seeds) | 179.01 ± 3.78 | 8.68 ± 0.38 | 43.60% ± 0.90% | 13.6% ± 3.2% | \$85.43 ± 20.00 | 70.26 ± 1.15 |
| | **Priority** | Deterministic | 189.61 | 10.24 | 41.14% | 20.0% | \$125.43 | 66.41 |
| | **EDF** | Deterministic | 180.77 | 9.25 | 43.15% | 24.0% | \$150.43 | 65.81 |
| | **Greedy** | Deterministic | 176.62 | 9.87 | 44.17% | 28.0% | \$175.43 | 64.49 |
| | **FCFS** | Deterministic | 176.62 | 10.21 | 44.17% | 28.0% | \$175.43 | 64.43 |
| | **DQN** | Stochastic (5 seeds) | 207.66 ± 10.49 | 19.19 ± 2.33 | 37.66% ± 1.91% | 32.0% ± 5.1% | \$200.43 ± 31.62 | 58.43 ± 2.87 |
| | **Q-Learning**| Stochastic (5 seeds) | 202.59 ± 12.06| 20.17 ± 2.62 | 38.64% ± 2.28% | 33.6% ± 2.0% | \$210.43 ± 12.25 | 57.98 ± 0.74 |
| **HEAVY** | **PSO** | Stochastic (5 seeds) | **374.51 ± 4.64** | **84.63 ± 4.49** | **60.51% ± 0.75%** | **56.8% ± 1.6%** | **\$356.25 ± 10.00** | **44.56 ± 1.13** |
| | **GA** | Stochastic (5 seeds) | 377.56 ± 6.66 | 85.76 ± 4.11 | 60.03% ± 1.05% | 56.8% ± 1.6% | \$356.25 ± 10.00 | 44.14 ± 1.12 |
| | **SA** | Stochastic (5 seeds) | 391.92 ± 5.61 | 96.47 ± 7.10 | 57.83% ± 0.83% | 60.8% ± 1.6% | \$381.25 ± 10.00 | 39.80 ± 1.08 |
| | **FCFS** | Deterministic | 385.40 | 118.70 | 58.79% | 64.0% | \$401.25 | 37.92 |
| | **Priority** | Deterministic | 398.54 | 98.36 | 56.86% | 64.0% | \$401.25 | 37.47 |
| | **SJF** | Deterministic | 433.86 | 78.00 | 52.22% | 72.0% | \$451.25 | 36.49 |
| | **EDF** | Deterministic | 444.65 | 80.04 | 50.95% | 76.0% | \$476.25 | 33.97 |
| | **Greedy** | Deterministic | 410.64 | 106.00 | 55.18% | 72.0% | \$451.25 | 33.27 |
| | **Q-Learning**| Stochastic (5 seeds) | 557.41 ± 31.36| 158.53 ± 12.05| 40.78% ± 2.36% | 81.6% ± 6.5% | \$511.25 ± 40.62 | 23.67 ± 2.55 |
| | **DQN** | Stochastic (5 seeds) | 715.45 ± 164.52| 218.17 ± 77.49| 33.13% ± 6.45% | 80.8% ± 3.0% | \$506.25 ± 18.71 | 20.93 ± 3.19 |

---

## Empirical Analysis & Academic Findings

### 1. Low Load Invariance
In the **LIGHT** scenario (25 jobs arriving over 250s to a 40-core / 256GB / 8-GPU cluster), instantaneous resource availability is never constrained. All classical heuristics and metaheuristics run jobs immediately upon arrival ($\bar{W} = 0.00\text{s}$), producing identical makespans ($255.53\text{s}$). RL agents incur small occasional exploratory waiting times ($\sim 2–4$s). This verifies simulator consistency and establishes a valid zero-congestion baseline.

### 2. Metaheuristic Dominance Under Medium and Heavy Load
- **PSO** achieved the highest overall efficiency in both MEDIUM (**Score: 72.06 ± 0.71**, SLA Violation: 9.6% ± 2.0%) and HEAVY (**Score: 44.56 ± 1.13**, SLA Violation: 56.8% ± 1.6%) workloads.
- **GA** achieved near-identical top-tier performance (**71.54 ± 0.55** in Medium, **44.14 ± 1.12** in Heavy).
- **Explanation**: Evolutionary and particle swarm algorithms search across global sequence permutations, optimizing multi-job packing and avoiding myopic dispatch choices that bottleneck future multi-dimensional allocations.

### 3. Heuristic Baseline Behaviors
- **SJF** performed exceptionally well under MEDIUM load (Score: **71.10**, Makespan: 178.18s, SLA Violation: 12.0%), nearly matching GA by clearing short pipeline jobs quickly and freeing compute capacity.
- Under HEAVY load, standard heuristics degraded due to queue saturation; **FCFS** and **Priority** achieved moderate efficiency (Scores: ~37.5–37.9), outperforming EDF and Greedy Best-Fit which suffered from priority inversions and suboptimal packing fragmentation.

### 4. Reinforcement Learning Performance Reality
- **Empirical Observation**: Under current state-action abstractions and practical training budgets (25–30 episodes), Tabular Q-Learning and DQN did not surpass metaheuristics or classical heuristics (Scores: 57.98–58.43 in Medium, 20.93–23.67 in Heavy).
- **Root-Cause Analysis**:
  1. *Coarse State Representation*: The 6-dimensional aggregated state vector (`[cpu_u, mem_u, gpu_u, q_len, avg_prio, avg_urgency]`) compresses the individual requirements of all queued jobs into global averages, depriving the RL agent of fine-grained pairwise matching information.
  2. *Sample Inefficiency*: Modern RL requires tens of thousands of training rollouts to converge on combinatorial scheduling state spaces. A 30-episode budget provides initial policy shaping but insufficient convergence for complex multi-resource packing.
  3. *Action Masking Constraints*: The RL agent outputs discrete job indices. When selected jobs are infeasible due to capacity, fallback mechanisms must intervene, diluting policy gradient signals.

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm 9+

### 1. Backend Setup
```bash
# Clone the repository
cd "Major Project"

# Create and activate virtual environment (optional but recommended)
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Install backend dependencies
pip install fastapi uvicorn sqlalchemy pydantic numpy torch scikit-learn pandas pytest httpx anyio

# Set Python path to backend directory
# Windows PowerShell:
$env:PYTHONPATH="backend"
# Linux/macOS:
export PYTHONPATH="backend"

# Run FastAPI backend development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables (optional, defaults to http://127.0.0.1:8000/api)
cp .env.example .env

# Start development server
npm run dev
# Or build for production preview:
npm run build
npm run preview -- --port 3000
```

---

## Running Verification Suites

The repository contains an automated test harness validating end-to-end simulation pipelines, timeline generation, RL policy evaluations, and API integration:

```powershell
# Set PYTHONPATH and execute pytest suite
$env:PYTHONPATH="backend"
pytest backend
```

Expected output:
```
======================= 27 passed, 2 warnings in 13.59s =======================
```

### Frontend Production Build
```bash
cd frontend
npm run build
```

Expected output:
```
✓ built in 536ms
```

---

## Project Limitations & Known Boundaries

1. **Non-Preemptive Execution**: Once a job is allocated cluster resources, it runs uninterrupted until completion. Preemption and migration are not modeled in the current discrete-event engine.
2. **Homogeneous Flat Cluster**: Compute nodes are modeled as a unified aggregated pool of CPU, RAM, and GPU capacity rather than a distributed topology with network switch latency or NUMA domains.
3. **Training Sample Budgets**: RL agents are configured for rapid interactive web execution (25–30 episodes). For deep convergence matching metaheuristic performance, offline pre-training over $\ge 10,000$ episodes with per-job attention graph neural networks (GNNs) is recommended.
4. **Synchronous Simulation API**: The simulation benchmark runs synchronously per request. For very large batches ($N > 200$), requests may take several seconds, benefiting from future asynchronous Celery/Redis job queues.
