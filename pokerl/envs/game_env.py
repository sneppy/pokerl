import numpy as np
from typing import Tuple, List
from .env import PokerEnv, Game
from ..enums import PlayerState

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
		
		reward = .0
		done, hand, _ = self.game.step(action)

		if done or self.game.player_states[self.player_agent] == PlayerState.BROKEN:
			# Game has ended or we are broken anyway
			return self.game.active_state, self.game.payoffs[self.player_agent], True, True
		else:
			while not hand and self.game.active_player != self.player_agent:
				# Step over opponents
				action = self.agents[self.game.active_player](self.game.active_state)
				done, hand, _ = self.game.step(action)
			
			# Set reward if hand has ended
			if hand: reward = self.game.payoffs[self.player_agent]

			while not done and self.game.active_player != self.player_agent:
				# Step over opponents
				action = self.agents[self.game.active_player](self.game.active_state)
				done, *_ = self.game.step(action)
		
			return self.game.active_state, reward, done, hand