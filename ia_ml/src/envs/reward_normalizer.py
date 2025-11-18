"""VC2 normalization for Gym/Gymnasium environments.

This module implements a Variance-Controlled Value Normalization (VC2)
style wrapper and the associated RunningMeanStd utility.

Design choices implemented here (VC2-inspired):
- Maintain two RunningMeanStd statistics: one for discounted returns and
  one for critic value predictions.
- Provide API for agents to push value predictions so the wrapper can
  maintain a running estimate of value distribution.
- Normalize returns and values separately and compute advantages in the
  normalized space as (R_norm - V_norm). This keeps advantages with
  controlled variance and consistent scaling for PPO updates.

The wrapper supports Gymnasium (reset->(obs,info) and step->5-tuple)
and standard Gym (4-tuple). It also supports vectorized environments
where rewards/values are arrays.
"""

from typing import Tuple, Union
import gymnasium as gym
import numpy as np


class RunningMeanStd:
    """Online mean and variance estimator (Welford-style, batched updates).

    Attributes:
        mean: running mean
        var: running variance (population variance)
        count: running sample count (float)
    """

    def __init__(self, eps: float = 1e-4):
        # `eps` is numerical-stability epsilon, not an initial sample count.
        # Start `count` at 0.0 to avoid biasing the running mean when the
        # first update arrives. Keep `eps` for downstream stability use.
        self.mean = 0.0
        self.var = 1.0
        self.count = 0.0
        self.eps = float(eps)

    def as_numpy(self) -> Tuple[float, float, float]:
        return float(self.mean), float(self.var), float(self.count)

    def update(self, x: np.ndarray) -> None:
        """Update statistics with a batch of samples.

        x: array-like of shape (n,)
        """
        x = np.asarray(x, dtype=np.float64).ravel()
        if x.size == 0:
            return
        batch_mean = float(x.mean())
        batch_var = float(x.var())
        batch_count = float(x.size)

        delta = batch_mean - self.mean
        tot_count = self.count + batch_count

        new_mean = self.mean + delta * (batch_count / tot_count)
        m_a = self.var * (self.count)
        m_b = batch_var * (batch_count)
        M2 = m_a + m_b + delta * delta * (self.count * batch_count / tot_count)

        self.mean = new_mean
        self.var = M2 / tot_count
        self.count = tot_count


class VC2Normalizer(gym.Wrapper):
    """Gym wrapper that implements VC2-style normalization.

    API / expectations:
    - The agent collects values (critic predictions) during rollouts and
      must call `push_value_batch(values)` to allow the wrapper to
      track value statistics.
    - After computing returns and predicted values, the agent should
      call `normalize_returns_values(returns, values)` to obtain the
      normalized versions and normalized advantages ready for PPO.

    The normalization is reversible via `denormalize_value`.
    """

    def __init__(
        self,
        env: gym.Env,
        gamma: float = 0.99,
        clip_range: float = 10.0,
        eps: float = 1e-8,
        scale: float = 1.0,
    ):
        # gym.Wrapper asserts env is a gymnasium.Env. For unit tests we
        # sometimes pass lightweight dummy envs that aren't full gym.Env
        # instances. Try the normal Wrapper init, but fall back to a
        # permissive assignment for testing if the assert is raised.
        try:
            super().__init__(env)
        except AssertionError:
            # Fallback for non-gym envs used in unit tests: assign env
            # directly so the wrapper methods still operate on `self.env`.
            self.env = env
        self.gamma = float(gamma)
        self.clip_range = float(clip_range)
        self.eps = float(eps)
        self.scale = float(scale)

        # Two independent running statistics: one for discounted returns,
        # one for value predictions (V(s)).
        self.rms_return = RunningMeanStd(eps=1e-4)
        self.rms_value = RunningMeanStd(eps=1e-4)

        # track discounted-return accumulator per environment instance
        # Support both scalar envs and vectorized envs
        self._is_vector_env = getattr(self.env, "num_envs", None) is not None
        if self._is_vector_env:
            n = int(getattr(self.env, "num_envs"))
            self.episode_ret = np.zeros(n, dtype=np.float64)
        else:
            self.episode_ret = 0.0

    # ---- Gym API passthrough with discounted-return tracking ----
    def reset(self, **kwargs):
        # Reset episode return accumulators and return env reset
        if self._is_vector_env:
            self.episode_ret = np.zeros_like(self.episode_ret, dtype=np.float64)
        else:
            self.episode_ret = 0.0
        return self.env.reset(**kwargs)

    def step(self, action):
        """Step through the env and return normalized reward together with step output.

        Important: This wrapper normalizes per-step rewards using the running
        statistics of discounted returns (RMS of the discounted-return signal).
        For full VC2 training we recommend using the buffer + normalization
        helpers provided below and call `push_value_batch` from the agent.
        """
        result = self.env.step(action)
        # Support both classic gym 4-tuple and gymnasium 5-tuple
        if len(result) == 4:
            obs, reward, done, info = result
            truncated = False
        else:
            obs, reward, done, truncated, info = result

        # handle array or scalar reward
        r = reward
        try:
            r_arr = np.asarray(r, dtype=np.float64)
        except Exception:
            r_arr = np.array([float(r)], dtype=np.float64)

        # update discounted-return running accumulator(s)
        if self._is_vector_env:
            # elementwise gamma update
            self.episode_ret = self.episode_ret * self.gamma + r_arr
            self.rms_return.update(self.episode_ret)
            std = np.sqrt(self.rms_return.var) + self.eps
            norm_r = (r_arr / std) * self.scale
            norm_r = np.clip(norm_r, -self.clip_range, self.clip_range)
            norm_r = norm_r.astype(float)
        else:
            try:
                r_scalar = float(r_arr.item())
            except Exception:
                r_scalar = float(np.asarray(r_arr).item())
            self.episode_ret = self.episode_ret * self.gamma + r_scalar
            self.rms_return.update(np.array([self.episode_ret]))
            std = np.sqrt(self.rms_return.var) + self.eps
            norm_r = float(np.clip((r_scalar / std) * self.scale, -self.clip_range, self.clip_range))

        if done or truncated:
            # reset accumulator for environments that finished
            if self._is_vector_env:
                # if done is array-like, reset per-env where True
                try:
                    mask = np.asarray(done, dtype=bool)
                    # also handle truncated
                    if np.any(mask):
                        self.episode_ret[mask] = 0.0
                except Exception:
                    self.episode_ret = np.zeros_like(self.episode_ret)
            else:
                self.episode_ret = 0.0

        if len(result) == 4:
            return obs, norm_r, done, info
        return obs, norm_r, done, truncated, info

    # ---- VC2 API for agents/trainers ----
    def push_value_batch(self, values: Union[np.ndarray, list, float]) -> None:
        """Push a batch of critic predictions so value statistics can be updated.

        Values should be raw scalar predictions (not normalized).
        """
        v = np.asarray(values, dtype=np.float64).ravel()
        if v.size == 0:
            return
        self.rms_value.update(v)

    def normalize_returns_values(self, returns: np.ndarray, values: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Normalize returns and values and compute normalized advantages.

        Args:
            returns: array-like of shape (batch,)
            values: array-like of shape (batch,)

        Returns:
            returns_norm, values_norm, advantages_norm
        """
        R = np.asarray(returns, dtype=np.float64).ravel()
        V = np.asarray(values, dtype=np.float64).ravel()

        # Update running stats with this batch (important to include new data)
        if R.size > 0:
            self.rms_return.update(R)
        if V.size > 0:
            self.rms_value.update(V)

        r_std = np.sqrt(self.rms_return.var) + self.eps
        v_std = np.sqrt(self.rms_value.var) + self.eps

        Rn = (R - self.rms_return.mean) / r_std
        Vn = (V - self.rms_value.mean) / v_std

        advantages = Rn - Vn

        return Rn, Vn, advantages

    def denormalize_value(self, norm_value: Union[float, np.ndarray]) -> np.ndarray:
        """Inverse transform for normalized value(s).

        Useful for logging/analysis: given a normalized value (Vn), return V
        on the original reward scale using value running statistics.
        """
        nv = np.asarray(norm_value, dtype=np.float64)
        v = nv * (np.sqrt(self.rms_value.var) + self.eps) + self.rms_value.mean
        return v

    # Convenience helpers
    def get_return_stats(self) -> Tuple[float, float]:
        return float(self.rms_return.mean), float(self.rms_return.var)

    def get_value_stats(self) -> Tuple[float, float]:
        return float(self.rms_value.mean), float(self.rms_value.var)
