import numpy as np
from typing import Tuple
from ..game import Game

class PokerEnv:
	""" Base class for all poker environments
	
	`PokerEnv` exposes an api similar to that of
	`gym.Env`. Reset the state of the env with
	`env.reset()`, which returns the state of the
	agent. Take actions with `end.step(action)`
	and observe a tuple `(next state, reward, done)`.
	"""

	def reset(self) -> Game.StateView:
		"""  """

		raise NotImplementedError

	def step(self, action: int) -> Tuple[Game.StateView, float, bool]:
		"""  """

		raise NotImplementedError