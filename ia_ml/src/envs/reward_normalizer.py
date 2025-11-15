import gymnasium as gym
import numpy as np

class RunningMeanStd:
    def __init__(self, eps: float = 1e-4):
        self.mean = 0.0
        self.var = 1.0
        self.count = eps

    def update(self, x: np.ndarray):
        x = np.asarray(x, dtype=np.float64)
        if x.size == 0:
            return
        batch_mean = x.mean()
        batch_var = x.var()
        batch_count = x.size
        delta = batch_mean - self.mean
        tot_count = self.count + batch_count
        new_mean = self.mean + delta * (batch_count / tot_count)
        m_a = self.var * (self.count)
        m_b = batch_var * (batch_count)
        M2 = m_a + m_b + delta**2 * (self.count * batch_count / tot_count)
        self.mean = new_mean
        self.var = M2 / tot_count
        self.count = tot_count

class RewardNormalizer(gym.Wrapper):
    """
    Normaliza rewards usando estadísticas de retornos descontados (online).
    Configurable vía gamma, clip_range y scale.
    Compatible con step() que devuelve (obs, reward, done, info) o
    (obs, reward, done, truncated, info) (gymnasium).
    """
    def __init__(self, env, gamma: float = 0.99, clip_range: float = 10.0, eps: float = 1e-8, scale: float = 1.0):
        super().__init__(env)
        self.gamma = float(gamma)
        self.clip_range = float(clip_range)
        self.eps = float(eps)
        self.scale = float(scale)
        self.rms = RunningMeanStd(eps=1e-4)
        self.episode_ret = 0.0

    def reset(self, **kwargs):
        self.episode_ret = 0.0
        return self.env.reset(**kwargs)

    def step(self, action):
        result = self.env.step(action)
        # soportar gym (4-tuple) y gymnasium (5-tuple)
        if len(result) == 4:
            obs, reward, done, info = result
            truncated = False
        else:
            obs, reward, done, truncated, info = result

        # actualizar retorno descontado y estadísticas
        try:
            r = float(reward)
        except Exception:
            r = float(np.asarray(reward).item())
        self.episode_ret = self.episode_ret * self.gamma + r
        self.rms.update(np.array([self.episode_ret]))

        std = np.sqrt(self.rms.var) + self.eps
        norm_reward = (r / std) * self.scale
        norm_reward = float(np.clip(norm_reward, -self.clip_range, self.clip_range))

        if done or truncated:
            self.episode_ret = 0.0

        if len(result) == 4:
            return obs, norm_reward, done, info
        return obs, norm_reward, done, truncated, info