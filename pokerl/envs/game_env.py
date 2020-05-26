import numpy as np
from typing import Tuple, List
from .env import PokerEnv, Game

class PokerGameEnv(PokerEnv):
	""" RL environment that simualates an entire poker game
	
	However, the episode is considered done
	after each hand.
	"""

	def __init__(self, agents: list=None, **game_config):
		"""  """

		self.game = Game(**game_config)
		self.agents = [None, *agents]
		self.player_agent = 0

	def reset(self) -> Game.StateView:
		"""  """
		
		self.game.reset()
		while self.game.active_player != self.player_agent:
			action = self.agents[self.game.active_player](self.game.active_state)
			done, *_ = self.game.step(action)
			if done: self.game.reset()
		
		return self.game.active_state

	def step(self, action: int) -> Tuple[Game.StateView, float, bool]:
		"""  """
		
		done, hand, _ = self.game.step(action)
		if hand: reward = self.game.payoffs[self.player_agent]
		else: reward = .0

		return self.game.active_state, reward, done