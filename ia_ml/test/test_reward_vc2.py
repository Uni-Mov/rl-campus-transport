import numpy as np
from src.envs.reward_normalizer import RunningMeanStd, VC2Normalizer


def test_running_mean_std():
    rms = RunningMeanStd(eps=1e-4)
    data = np.array([1.0, 2.0, 3.0])
    rms.update(data)
    mean, var, count = rms.as_numpy()
    assert abs(mean - data.mean()) < 1e-8
    assert abs(var - data.var()) < 1e-8
    assert count >= 3.0


class DummyEnv:
    def reset(self, **kwargs):
        return np.zeros(1), {}

    def step(self, action):
        # obs, reward, done, info
        return np.zeros(1), 1.0, False, {}


def test_vc2_normalize_denormalize():
    env = DummyEnv()
    norm = VC2Normalizer(env)

    # push some values and returns
    returns = np.array([10.0, 12.0, 9.0, 11.0])
    values = np.array([9.0, 11.0, 8.5, 10.0])

    # push value batch so value stats are updated
    norm.push_value_batch(values)

    Rn, Vn, adv = norm.normalize_returns_values(returns, values)
    # shapes
    assert Rn.shape == returns.shape
    assert Vn.shape == values.shape
    assert adv.shape == returns.shape

    # denormalize Vn should approximately equal original values
    Vrec = norm.denormalize_value(Vn)
    assert np.allclose(Vrec, values, atol=1e-6)
