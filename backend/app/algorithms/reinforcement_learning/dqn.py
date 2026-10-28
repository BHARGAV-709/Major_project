import random
import copy
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Any, Tuple
from app.workload.job_model import Job
from app.simulation.resource_manager import ClusterResourceState
from app.algorithms.reinforcement_learning.environment import RLSchedulingEnv

class ReplayBuffer:
    def __init__(self, capacity: int = 5000):
        self.buffer = []
        self.capacity = capacity
        self.pos = 0

    def push(self, state, action, reward, next_state, done):
        if len(self.buffer) < self.capacity:
            self.buffer.append(None)
        self.buffer[self.pos] = (state, action, reward, next_state, done)
        self.pos = (self.pos + 1) % self.capacity

    def sample(self, batch_size: int):
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = zip(*batch)
        return (np.array(state, dtype=np.float32),
                np.array(action, dtype=np.int64),
                np.array(reward, dtype=np.float32),
                np.array(next_state, dtype=np.float32),
                np.array(done, dtype=np.float32))

    def __len__(self):
        return len(self.buffer)

class DQNNetwork(nn.Module):
    def __init__(self, state_dim: int = 6, action_dim: int = 6):
        super(DQNNetwork, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )

    def forward(self, x):
        return self.fc(x)

class DQNScheduler:
    """
    Deep Q-Network (DQN) Scheduler using PyTorch.
    Features state neural approximation, experience replay, target network updates, and MSE loss training.
    """

    def __init__(self, 
                 episodes: int = 100, 
                 batch_size: int = 32, 
                 gamma: float = 0.95, 
                 lr: float = 0.001, 
                 epsilon_start: float = 1.0, 
                 epsilon_min: float = 0.05, 
                 epsilon_decay: float = 0.96,
                 max_action_slots: int = 5):
        self.episodes = episodes
        self.batch_size = batch_size
        self.gamma = gamma
        self.lr = lr
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.max_action_slots = max_action_slots
        self.action_dim = max_action_slots + 1

        self.policy_net = DQNNetwork(state_dim=6, action_dim=self.action_dim)
        self.target_net = DQNNetwork(state_dim=6, action_dim=self.action_dim)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.lr)
        self.memory = ReplayBuffer(capacity=5000)

    def select_action(self, state: np.ndarray, evaluate: bool = False) -> int:
        if not evaluate and np.random.rand() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.policy_net(state_tensor)
            return int(torch.argmax(q_values).item())

    def evaluate_policy(self, jobs: List[Job], cluster_state: ClusterResourceState, max_steps: int = 500) -> Tuple[List[Job], float]:
        """
        Separate deterministic evaluation of the learned DQN policy (epsilon = 0).
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
            total_loss = 0.0
            losses_count = 0
            done = False
            step_count = 0

            while not done and step_count < 400:
                step_count += 1
                action = self.select_action(state, evaluate=False)
                next_state, reward, done, info = env.step(action)
                
                self.memory.push(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward

                # Perform Gradient Descent Step if sufficient samples in Replay Buffer
                if len(self.memory) >= self.batch_size:
                    b_state, b_action, b_reward, b_next_state, b_done = self.memory.sample(self.batch_size)
                    
                    t_state = torch.FloatTensor(b_state)
                    t_action = torch.LongTensor(b_action).unsqueeze(1)
                    t_reward = torch.FloatTensor(b_reward).unsqueeze(1)
                    t_next_state = torch.FloatTensor(b_next_state)
                    t_done = torch.FloatTensor(b_done).unsqueeze(1)

                    q_val = self.policy_net(t_state).gather(1, t_action)
                    with torch.no_grad():
                        max_next_q = self.target_net(t_next_state).max(1)[0].unsqueeze(1)
                        target_q = t_reward + (1 - t_done) * self.gamma * max_next_q

                    loss = nn.MSELoss()(q_val, target_q)
                    self.optimizer.zero_grad()
                    loss.backward()
                    self.optimizer.step()

                    total_loss += loss.item()
                    losses_count += 1

            # Update Target Network every 5 episodes
            if ep % 5 == 0:
                self.target_net.load_state_dict(self.policy_net.state_dict())

            # Epsilon decay
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

            completed = env.simulator.completed_jobs
            rejected = env.simulator.rejected_jobs
            resolved = len(completed) + len(rejected)
            if resolved >= len(jobs) and total_reward > best_train_reward:
                best_train_reward = total_reward
                best_train_schedule = copy.deepcopy(completed)

            avg_loss = (total_loss / losses_count) if losses_count > 0 else 0.0
            history.append({
                "episode": ep,
                "reward": round(total_reward, 2),
                "loss": round(avg_loss, 4),
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
            "eval_reward": round(final_reward, 2)
        }
