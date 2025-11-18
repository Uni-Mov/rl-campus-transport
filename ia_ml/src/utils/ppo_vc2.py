"""Basic PPO implementation that integrates VC2 normalization.

This module provides a minimal, well-documented PPO trainer showing how
to integrate the `VC2Normalizer` implemented in the envs module. The
implementation focuses on the normalization and update steps; it is not
an optimized production implementation but is correct and suitable for
experimentation and debugging.
"""

from typing import Optional, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# NOTE: import the normalizer relative to package layout
from ia_ml.src.envs.reward_normalizer import VC2Normalizer


class PPOAgent:
    """Minimal PPO agent integrated with VC2 normalization.

    Usage:
    - Create env and wrap with `VC2Normalizer`.
    - Pass the same normalizer instance to PPOAgent.
    - During rollouts, push critic values to normalizer via
      `normalizer.push_value_batch(values)` so value statistics are kept up
      to date.
    - Before updates, call `normalizer.normalize_returns_values(returns, values)`
      and use the returned normalized advantages/targets for optimization.
    """

    def __init__(
        self,
        policy: nn.Module,
        value_net: nn.Module,
        optimizer: optim.Optimizer,
        normalizer: Optional[VC2Normalizer] = None,
        clip_epsilon: float = 0.2,
        value_coef: float = 0.5,
        entropy_coef: float = 0.01,
    ):
        self.policy = policy
        self.value_net = value_net
        self.optimizer = optimizer
        self.normalizer = normalizer
        self.clip_epsilon = clip_epsilon
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef

    @staticmethod
    def compute_gae(rewards: np.ndarray, values: np.ndarray, dones: np.ndarray, gamma: float, lam: float) -> np.ndarray:
        """Compute GAE-lambda returns (targets) from collected rewards and values.

        Returns an array of shape (T,) with the estimated discounted returns (targets).
        """
        T = len(rewards)
        advantages = np.zeros(T, dtype=np.float64)
        lastgaelam = 0.0
        for t in reversed(range(T)):
            if t == T - 1:
                nextnonterminal = 1.0 - float(dones[t])
                nextvalues = values[t]
            else:
                nextnonterminal = 1.0 - float(dones[t + 1])
                nextvalues = values[t + 1]
            delta = rewards[t] + gamma * nextvalues * nextnonterminal - values[t]
            lastgaelam = delta + gamma * lam * nextnonterminal * lastgaelam
            advantages[t] = lastgaelam
        returns = advantages + values
        return returns

    def update(self, batch: dict, epochs: int = 4, minibatch_size: int = 64):
        """Perform PPO update using a single collected batch.

        batch must contain numpy arrays: obs, actions, log_probs, returns (raw), values (raw), dones, rewards
        The normalizer will be used to normalize returns and values and compute
        normalized advantages used in policy loss.
        """
        obs = batch["obs"]
        actions = batch["actions"]
        old_log_probs = batch["log_probs"]
        returns_raw = batch["returns"]
        values_raw = batch["values"]
        dones = batch.get("dones", np.zeros_like(returns_raw, dtype=np.bool_))

        # Ensure normalizer has seen the value batch (update its stats)
        if self.normalizer is not None:
            self.normalizer.push_value_batch(values_raw)

        # Obtain normalized returns, values and advantages
        if self.normalizer is not None:
            returns_norm, values_norm, advantages = self.normalizer.normalize_returns_values(returns_raw, values_raw)
        else:
            # fallback: standardize advantages with batch std
            advantages = returns_raw - values_raw
            adv_std = np.std(advantages) + 1e-8
            advantages = (advantages - np.mean(advantages)) / adv_std
            returns_norm = returns_raw
            values_norm = values_raw

        # Convert everything to torch
        obs_t = torch.as_tensor(obs, dtype=torch.float32)
        actions_t = torch.as_tensor(actions, dtype=torch.float32)
        old_log_probs_t = torch.as_tensor(old_log_probs, dtype=torch.float32)
        returns_t = torch.as_tensor(returns_norm, dtype=torch.float32)
        values_t = torch.as_tensor(values_norm, dtype=torch.float32)
        advantages_t = torch.as_tensor(advantages, dtype=torch.float32)

        N = len(advantages)
        inds = np.arange(N)

        for _ in range(epochs):
            np.random.shuffle(inds)
            for start in range(0, N, minibatch_size):
                mb_inds = inds[start : start + minibatch_size]
                mb_obs = obs_t[mb_inds]
                mb_actions = actions_t[mb_inds]
                mb_old_logp = old_log_probs_t[mb_inds]
                mb_returns = returns_t[mb_inds]
                mb_values = values_t[mb_inds]
                mb_adv = advantages_t[mb_inds]

                # policy forward
                dist = self.policy(mb_obs)
                # assume policy returns a torch.distributions.Distribution
                new_logp = dist.log_prob(mb_actions).sum(-1)
                entropy = dist.entropy().sum(-1).mean()

                ratio = torch.exp(new_logp - mb_old_logp)
                surr1 = ratio * mb_adv
                surr2 = torch.clamp(ratio, 1.0 - self.clip_epsilon, 1.0 + self.clip_epsilon) * mb_adv
                policy_loss = -torch.min(surr1, surr2).mean()

                # value loss on the normalized scale
                value_preds = self.value_net(mb_obs).squeeze(-1)
                value_loss = nn.functional.mse_loss(value_preds, mb_returns)

                loss = policy_loss + self.value_coef * value_loss - self.entropy_coef * entropy

                self.optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(list(self.policy.parameters()) + list(self.value_net.parameters()), max_norm=0.5)
                self.optimizer.step()

        # Return some scalars for logging
        return {
            "policy_loss": float(policy_loss.detach().cpu().numpy()),
            "value_loss": float(value_loss.detach().cpu().numpy()),
            "entropy": float(entropy.detach().cpu().numpy()),
        }
