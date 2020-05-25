import numpy as np
from .agent import PokerAgent, Game

class RandomAgent(PokerAgent):
	""" Totally randomized agent

	Implements a poker agent that selects
	a random action from the list of valid
	actions using a uniform distribution
	"""

	def __call__(self, state: Game.StateView) -> int:
		"""  """
		
		# Return random valid action
		vu = state.valid_actions
		return np.random.choice(len(vu), p=vu / np.sum(vu))