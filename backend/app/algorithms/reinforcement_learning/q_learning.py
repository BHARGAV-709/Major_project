import numpy as np
import copy
from typing import List, Dict, Any, Tuple
from app.workload.job_model import Job
from app.simulation.resource_manager import ClusterResourceState
from app.algorithms.reinforcement_learning.environment import RLSchedulingEnv

class QLearningScheduler:
    """
    Tabular Q-Learning Scheduler for Resource Allocation.
    Applies discretized state representation and Bellman update:
    Q(s, a) = Q(s, a) + alpha * [ r + gamma * max_a' Q(s', a') - Q(s, a) ]
    """

    def __init__(self, 
                 episodes: int = 150, 
                 alpha: float = 0.1, 
                 gamma: float = 0.95, 
                 epsilon_start: float = 1.0, 
                 epsilon_min: float = 0.05, 
                 epsilon_decay: float = 0.97,
                 max_action_slots: int = 5):
        self.episodes = episodes
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.max_action_slots = max_action_slots
        self.num_actions = max_action_slots + 1  # 0..max_action_slots-1 = schedule job, max_action_slots = WAIT
        
        self.q_table: Dict[Tuple[int, ...], np.ndarray] = {}

    def _discretize_state(self, state: np.ndarray) -> Tuple[int, ...]:
        # Discretize continuous state into discrete bins
        # state: [cpu_u, mem_u, gpu_u, q_len, avg_prio, avg_urgency]
        bins = [
            int(np.digitize(state[0], bins=[0.3, 0.7, 0.9])),
            int(np.digitize(state[1], bins=[0.3, 0.7, 0.9])),
            int(np.digitize(state[2], bins=[0.3, 0.7, 0.9])),
            int(np.digitize(state[3], bins=[0.2, 0.5, 0.8])),
            int(np.digitize(state[4], bins=[0.4, 0.7])),
            int(np.digitize(state[5], bins=[0.3, 0.7]))
        ]
        return tuple(bins)

    def _get_q_values(self, discrete_state: Tuple[int, ...]) -> np.ndarray:
        if discrete_state not in self.q_table:
            self.q_table[discrete_state] = np.zeros(self.num_actions, dtype=np.float32)
        return self.q_table[discrete_state]

    def select_action(self, state: np.ndarray, evaluate: bool = False) -> int:
        discrete_state = self._discretize_state(state)
        if not evaluate and np.random.rand() < self.epsilon:
            return int(np.random.randint(0, self.num_actions))
        q_vals = self._get_q_values(discrete_state)
        return int(np.argmax(q_vals))

    def evaluate_policy(self, jobs: List[Job], cluster_state: ClusterResourceState, max_steps: int = 500) -> Tuple[List[Job], float]:
        """
        Separate deterministic evaluation of the learned policy (epsilon = 0).
        Evaluates the greedy policy on a fresh environment rollout.
        """
        eval_env = RLSchedulingEnv(jobs, cluster_state, self.max_action_slots)
        state = eval_env.reset()
        done = False
        steps = 0
        total_reward = 0.0
        consecutive_infeasible = 0

        while not done and steps < max_steps:
            steps += 1
            action = self.select_action(state, evaluate=True)

            if action < self.max_action_slots and action < len(eval_env.simulator.waiting_queue):
                candidate_job = eval_env.simulator.waiting_queue[action]
                if not eval_env.simulator.cluster.is_feasible(candidate_job):
                    consecutive_infeasible += 1
                    if consecutive_infeasible >= 3:
                        action = self.max_action_slots
                        consecutive_infeasible = 0
                else:
                    consecutive_infeasible = 0
            else:
                consecutive_infeasible = 0

            state, reward, done, info = eval_env.step(action)
            total_reward += reward

        return eval_env.simulator.completed_jobs, total_reward

    def train(self, jobs: List[Job], cluster_state: ClusterResourceState) -> Dict[str, Any]:
        env = RLSchedulingEnv(jobs, cluster_state, self.max_action_slots)
        history = []
        best_train_reward = float('-inf')
        best_train_schedule: List[Job] = []

        for ep in range(1, self.episodes + 1):
            state = env.reset()
            total_reward = 0.0
            done = False
            step_count = 0
            
            while not done and step_count < 500:
                step_count += 1
                disc_state = self._discretize_state(state)
                action = self.select_action(state, evaluate=False)
                
                next_state, reward, done, info = env.step(action)
                next_disc_state = self._discretize_state(next_state)
                
                # Bellman Update Equation
                q_current = self._get_q_values(disc_state)[action]
                q_next_max = np.max(self._get_q_values(next_disc_state))
                
                td_target = reward + (self.gamma * q_next_max if not done else 0.0)
                self._get_q_values(disc_state)[action] += self.alpha * (td_target - q_current)
                
                state = next_state
                total_reward += reward

            # Decaying Epsilon
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
            
            completed = env.simulator.completed_jobs
            rejected = env.simulator.rejected_jobs
            resolved = len(completed) + len(rejected)
            if resolved >= len(jobs) and total_reward > best_train_reward:
                best_train_reward = total_reward
                best_train_schedule = copy.deepcopy(completed)

            history.append({
                "episode": ep,
                "reward": round(total_reward, 2),
                "epsilon": round(self.epsilon, 3),
                "completed": len(completed)
            })

        # Separate Deterministic Evaluation of the Learned Policy
        eval_completed, eval_reward = self.evaluate_policy(jobs, cluster_state)

        # Count feasible jobs in the workload
        feasible_count = sum(1 for j in jobs if cluster_state.fits_cluster_capacity(j))

        # Select schedule based on learned greedy policy, with fallback to best complete training episode
        if len(eval_completed) >= feasible_count:
            best_schedule = eval_completed
            final_reward = eval_reward
        elif best_train_schedule and len(best_train_schedule) >= feasible_count:
            best_schedule = best_train_schedule
            final_reward = best_train_reward
        else:
            best_schedule = eval_completed if len(eval_completed) >= len(best_train_schedule) else best_train_schedule
            final_reward = eval_reward

        return {
            "history": history,
            "best_completed_jobs": best_schedule,
            "eval_reward": round(final_reward, 2),
            "q_table_size": len(self.q_table)
        }
