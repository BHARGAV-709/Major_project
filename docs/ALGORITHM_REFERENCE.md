# Algorithm Reference Manual

This document details the mathematical theory, algorithmic mechanisms, parameters, and time complexities of all 10 scheduling algorithms implemented in the project.

---

## 1. Algorithmic Overview & Taxonomy

| # | Algorithm Name | Paradigm | Determinism | Decision Scope | Optimization Objective | Time Complexity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **FCFS** | Heuristic | Deterministic | Arrival Order | FIFO Queue Processing | $O(N \log N)$ |
| **2** | **SJF** | Heuristic | Deterministic | Runtime Greedy | Minimizing Average Wait Time | $O(N \log N)$ |
| **3** | **Priority** | Heuristic | Deterministic | Static Priority | Critical Job Accelerated Dispatch | $O(N \log N)$ |
| **4** | **EDF** | Heuristic | Deterministic | Dynamic Deadline | SLA Breach Minimization | $O(N \log N)$ |
| **5** | **Greedy Best-Fit** | Heuristic | Deterministic | Resource Matching | Multi-dimensional Residual Capacity | $O(N \cdot M)$ |
| **6** | **Genetic Algorithm** | Metaheuristic | Stochastic | Global Permutation | Composite Efficiency Fitness | $O(G \cdot P \cdot N \log N)$ |
| **7** | **PSO** | Metaheuristic | Stochastic | Global Swarm Permutation | Swarm Velocity & Position Mapping | $O(I \cdot S \cdot N \log N)$ |
| **8** | **Simulated Annealing**| Metaheuristic | Stochastic | Local Neighborhood | Metropolis Criterion Exploration | $O(K \cdot N \log N)$ |
| **9** | **Tabular Q-Learning**| Reinforcement Learning| Stochastic Policy / Deterministic Eval | State-Action Value | Temporal Difference Cumulative Reward| $O(E \cdot N \cdot |\mathcal{A}|)$ |
| **10**| **Deep Q-Network** | Reinforcement Learning| Stochastic Policy / Deterministic Eval | Deep Approximator | Bellman Error Replay Buffer Loss | $O(E \cdot N \cdot B \cdot W)$ |

*Notation: $N$ = Job count, $M$ = Server count, $G$ = Generations, $P$ = Population size, $I$ = Swarm iterations, $S$ = Particle count, $K$ = Annealing steps, $E$ = RL episodes, $|\mathcal{A}|$ = Action space size, $B$ = Mini-batch size, $W$ = Neural network weights count.*

---

## 2. Classical Deterministic Heuristics

### 2.1 First-Come, First-Served (FCFS)
- **Concept**: Jobs are admitted strictly in order of their submission timestamp ($t_{\text{arrival}}$). When resources become available, the head of the arrival queue is evaluated.
- **Dispatch Rule**:
  $$\text{Sort key}: \kappa_j = (t_{\text{arrival}, j}, \text{job\_id}_j)$$
- **Characteristics**: Simple and predictable. Susceptible to the *convoy effect*, where long-running batch jobs block shorter interactive jobs, inflating waiting times.

### 2.2 Shortest Job First (SJF)
- **Concept**: Prioritizes jobs with the smallest processing duration ($t_{\text{runtime}}$) among currently queued, arrived jobs.
- **Dispatch Rule**:
  $$\text{Sort key}: \kappa_j = (t_{\text{runtime}, j}, t_{\text{arrival}, j})$$
- **Characteristics**: Provably minimizes average waiting time in single-server environments. Highly effective under moderate contention, but long jobs can face starvation under continuous short-job arrivals.

### 2.3 Priority Scheduling
- **Concept**: Jobs are assigned an integer priority $\pi_j \in [1, 5]$ (where higher numerical value indicates higher scheduling urgency, e.g., Tier-1 production analytics).
- **Dispatch Rule**:
  $$\text{Sort key}: \kappa_j = (-\pi_j, t_{\text{arrival}, j})$$
- **Characteristics**: Protects mission-critical workloads at the cost of lower-priority background jobs.

### 2.4 Earliest Deadline First (EDF)
- **Concept**: Dynamic priority heuristic that inspects negotiated SLA deadlines ($d_j$). Jobs closest to expiring their SLA are scheduled first.
- **Dispatch Rule**:
  $$\text{Sort key}: \kappa_j = (d_j, t_{\text{arrival}, j})$$
- **Characteristics**: Optimal for preemptive uniprocessor real-time systems. In non-preemptive multi-resource environments, EDF can cause domino-effect violations under heavy overload when expired jobs consume scarce resources.

### 2.5 Greedy Best-Fit
- **Concept**: Evaluates cluster residual resources across CPU, memory, and GPU dimensions. Selects the job that minimizes unallocated residual capacity without exceeding limits.
- **Scoring Function**:
  $$\Delta(j) = (C_{\text{avail, CPU}} - \text{cpu}_j) + \frac{C_{\text{avail, Mem}} - \text{mem}_j}{1024} + 10 \cdot (C_{\text{avail, GPU}} - \text{gpu}_j)$$
- **Characteristics**: Maximizes instantaneous packing density, but lacks foresight into upcoming high-priority arrivals.

---

## 3. Stochastic Metaheuristic Optimizers

### 3.1 Genetic Algorithm (GA)
- **Chromosome Representation**: An integer permutation vector of length $N$ representing global dispatch sequence: $C = (\sigma_1, \sigma_2, \dots, \sigma_N)$.
- **Fitness Function**:
  $$F(C) = \text{PerformanceEvaluator.calculate\_metrics}(\text{Simulate}(C))[\text{"efficiency\_score"}]$$
- **Genetic Operators**:
  - *Selection*: Tournament Selection ($k=3$) choosing highest-fitness parents.
  - *Crossover*: Order Crossover (OX1) preserving relative ordering without creating duplicate job IDs.
  - *Mutation*: Swap Mutation (probability $p_m = 0.15$) swapping two random job indices.
- **Elitism**: Top 10% elite chromosomes directly transferred to the subsequent generation.

### 3.2 Particle Swarm Optimization (PSO)
- **Continuous Mapping (SPV Rule)**: Particles maintain continuous position vectors $X_i \in \mathbb{R}^N$ and velocity vectors $V_i \in \mathbb{R}^N$. Job permutation is derived via the Smallest Position Value (SPV) ranking of vector components:
  $$\sigma = \text{argsort}(X_i)$$
- **Kinetic Update Equations**:
  $$V_i(t+1) = w \cdot V_i(t) + c_1 r_1 \left( P_{\text{best}, i} - X_i(t) \right) + c_2 r_2 \left( G_{\text{best}} - X_i(t) \right)$$
  $$X_i(t+1) = X_i(t) + V_i(t+1)$$
- **Parameters**: Inertia weight $w = 0.7$, cognitive coefficient $c_1 = 1.5$, social coefficient $c_2 = 1.5$.

### 3.3 Simulated Annealing (SA)
- **Search Process**: Starts with initial temperature $T_0 = 500.0$ and cooling schedule $T_{k+1} = \alpha T_k$ ($\alpha = 0.95$).
- **Neighborhood Operator**: Generates candidate permutation $C'$ via 2-opt index swap.
- **Metropolis Acceptance Probability**:
  $$P(\text{accept}) = \begin{cases} 1.0 & \text{if } \Delta F \ge 0 \\ \exp\left(\frac{\Delta F}{T}\right) & \text{if } \Delta F < 0 \end{cases}$$
  where $\Delta F = F(C') - F(C)$. Allows controlled uphill transitions at high temperatures to escape local optima.

---

## 4. Reinforcement Learning Agents

### 4.1 Environment Formulation (`ResourceSchedulingEnv`)
- **State Space ($\mathcal{S} \in \mathbb{R}^6$)**:
  1. $s_1$: Cluster CPU utilization ratio $[0.0, 1.0]$.
  2. $s_2$: Cluster Memory utilization ratio $[0.0, 1.0]$.
  3. $s_3$: Cluster GPU utilization ratio $[0.0, 1.0]$.
  4. $s_4$: Queue length bucket $\min(10, \text{waiting count}) / 10.0$.
  5. $s_5$: Average normalized priority of queued jobs.
  6. $s_6$: Urgency index $\min_{j} (d_j - t) / 100.0$.
- **Action Space ($\mathcal{A}$)**: Discrete integer choice selecting among candidate waiting jobs in the queue.
- **Reward Function**:
  $$R_t = +1.0 \cdot \text{success} - 0.5 \cdot \text{infeasible} - 2.0 \cdot \mathbb{I}(\text{SLA Violated}) + 0.1 \cdot U_{\text{overall}}$$

### 4.2 Tabular Q-Learning
- **Discretization**: Each continuous state dimension is discretized into 4 discrete bins, forming a compact state hash table.
- **Bellman TD Update**:
  $$Q(s, a) \leftarrow Q(s, a) + \alpha \left[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right]$$
- **Hyperparameters**: Learning rate $\alpha = 0.1$, discount factor $\gamma = 0.95$, exploration decay $\epsilon_0 = 1.0 \to \epsilon_{\min} = 0.05$.

### 4.3 Deep Q-Network (DQN)
- **Neural Network Architecture**:
  - Input Layer: 6 continuous state features.
  - Hidden Layer 1: 64 neurons with ReLU activation.
  - Hidden Layer 2: 64 neurons with ReLU activation.
  - Output Layer: $|\mathcal{A}|$ linear outputs representing $Q(s, a; \theta)$.
- **Target Network & Experience Replay**:
  - Replay memory capacity $N_{\text{buffer}} = 2000$ transitions $(s, a, r, s', \text{done})$.
  - Mini-batch sampling size $B = 32$.
  - Target network weights $\theta^-$ synchronized every $\tau = 5$ episodes.
- **Loss Function**: Mean Squared Error on Temporal Difference target:
  $$\mathcal{L}(\theta) = \frac{1}{B} \sum_{i=1}^B \left( r_i + \gamma \max_{a'} Q(s'_i, a'; \theta^-) - Q(s_i, a_i; \theta) \right)^2$$
- **Policy Evaluation**:
  Following training, exploration is disabled ($\epsilon = 0.0$). The agent acts purely greedily to produce deterministic, reproducible schedules for evaluation.

