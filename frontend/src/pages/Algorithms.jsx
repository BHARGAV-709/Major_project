import React, { useState } from 'react';
import { BrainCircuit, Cpu, Zap, Activity, Code, Layers, Info } from 'lucide-react';

const ALGO_DETAILS = [
  {
    name: 'FCFS (First-Come, First-Served)',
    category: 'Heuristic',
    complexity: 'O(N log N)',
    desc: 'Dispatches jobs strictly in the order of submission arrival timestamps. Simple, fair, and zero-overhead, but susceptible to the Convoy Effect where large computational tasks block smaller fast tasks.',
    formula: 'Dispatch_Priority = Arrival_Time (Ascending)'
  },
  {
    name: 'SJF (Shortest Job First)',
    category: 'Heuristic',
    complexity: 'O(N log N)',
    desc: 'Prioritizes queued jobs with the smallest execution duration. Provably minimizes average waiting time in single-resource systems, but can lead to starvation for resource-intensive, long-duration analytics jobs.',
    formula: 'Dispatch_Priority = Runtime (Ascending)'
  },
  {
    name: 'Priority Scheduling',
    category: 'Heuristic',
    complexity: 'O(N log N)',
    desc: 'Schedules jobs based on assigned tenant service tier (Class 1 to 5). Ensures high-tier business analytics execute ahead of standard batch jobs, breaking ties by arrival time.',
    formula: 'Dispatch_Priority = (-Priority_Class, Arrival_Time)'
  },
  {
    name: 'EDF (Earliest Deadline First)',
    category: 'Heuristic',
    complexity: 'O(N log N)',
    desc: 'Dynamic real-time scheduling algorithm that prioritizes jobs with the nearest committed SLA deadline. Optimal for minimizing deadline breaches under low-to-moderate utilization regimes.',
    formula: 'Dispatch_Priority = SLA_Deadline (Ascending)'
  },
  {
    name: 'Greedy Best-Fit',
    category: 'Heuristic',
    complexity: 'O(N)',
    desc: 'Dynamically selects candidate jobs at each decision tick that maximize instantaneous multi-resource packing efficiency across CPU cores, memory, and GPU accelerators.',
    formula: 'Fit = 0.45*(Req_CPU/Avail_CPU) + 0.45*(Req_Mem/Avail_Mem) + 0.10*(Req_GPU/Avail_GPU)'
  },
  {
    name: 'Genetic Algorithm (GA)',
    category: 'Metaheuristic',
    complexity: 'O(G * P * N)',
    desc: 'Evolutionary global optimization operating on permutation chromosomes. Utilizes Tournament Selection (k=3), Order Crossover (OX) to preserve permutation validity, and swap mutation to minimize multi-objective penalty.',
    formula: 'Fitness = W1*Makespan + W2*Avg_Wait + W3*SLA_Violations + W4*Cost - W5*Utilization'
  },
  {
    name: 'Particle Swarm Optimization (PSO)',
    category: 'Metaheuristic',
    complexity: 'O(I * P * N)',
    desc: 'Continuous swarm intelligence where particles navigate priority-weight space. Velocity and position updates steer particles toward their personal best (pbest) and the swarm global best (gbest).',
    formula: 'V_new = w*V + c1*r1*(pbest - X) + c2*r2*(gbest - X)'
  },
  {
    name: 'Simulated Annealing (SA)',
    category: 'Metaheuristic',
    complexity: 'O(K * N)',
    desc: 'Stochastic local search inspired by thermodynamic annealing. Explores neighboring permutations via pairwise job swaps and uses the Metropolis criterion P = exp(-delta/T) to accept uphill moves and avoid local traps.',
    formula: 'P_accept = min(1.0, exp(-(Fitness_new - Fitness_old) / T))'
  },
  {
    name: 'Tabular Q-Learning',
    category: 'Reinforcement Learning',
    complexity: 'O(E * S)',
    desc: 'Model-free reinforcement learning mapping a 6-dimensional discretized state vector (cluster utilization buckets, queue length, average priority/urgency) to dispatch actions, evaluated via deterministic greedy rollouts post-training.',
    formula: 'Q(s,a) <- Q(s,a) + alpha * [ r + gamma * max_a\' Q(s\',a\') - Q(s,a) ]'
  },
  {
    name: 'Deep Q-Network (DQN)',
    category: 'Reinforcement Learning',
    complexity: 'O(E * B)',
    desc: 'Deep RL agent using a PyTorch multi-layer perceptron (6 -> 64 -> 64 -> |A|), Experience Replay buffer, target network decoupling, and Huber/MSE loss minimization over temporal difference errors.',
    formula: 'Loss = E [ (r + gamma * max_a\' Q_target(s\',a\') - Q_online(s,a))^2 ]'
  }
];

export default function Algorithms() {
  const [selectedCategory, setSelectedCategory] = useState('ALL');

  const filtered = selectedCategory === 'ALL'
    ? ALGO_DETAILS
    : ALGO_DETAILS.filter(a => a.category === selectedCategory);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-6 rounded-xl shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Scheduling Algorithms Suite</h1>
          <p className="text-xs text-slate-500 mt-1">
            Comprehensive Suite of 10 Heuristic, Metaheuristic, and Reinforcement Learning Scheduling Strategies
          </p>
        </div>

        <div className="flex gap-2 text-xs">
          {['ALL', 'Heuristic', 'Metaheuristic', 'Reinforcement Learning'].map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                selectedCategory === cat
                  ? 'bg-brand-600 text-white shadow-xs'
                  : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filtered.map((item) => (
          <div key={item.name} className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-2">
              <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold uppercase border ${
                item.category === 'Heuristic' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                item.category === 'Metaheuristic' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' :
                'bg-emerald-50 text-emerald-700 border-emerald-200'
              }`}>
                {item.category}
              </span>
              <span className="text-xs font-mono text-slate-400">{item.complexity}</span>
            </div>

            <h3 className="text-sm font-bold text-slate-900 mt-1">{item.name}</h3>
            <p className="text-xs text-slate-600 mt-2 leading-relaxed">{item.desc}</p>

            <div className="mt-4 pt-3 border-t border-slate-100 bg-slate-50 p-2.5 rounded-lg font-mono text-[11px] text-slate-700">
              <span className="font-semibold text-slate-500 block mb-0.5 font-sans text-[10px]">Mathematical Formulation:</span>
              {item.formula}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
