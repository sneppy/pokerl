import numpy as np
from typing import Union
from pokerl.enums import PokerMoves, PlayerState

class Game:
	"""  """

	def __init__(self, start_credits: Union[np.ndarray, list, float], num_players: int=4, debug: bool=False):
		"""  """

		if isinstance(start_credits, (float, int)):
			# Same amount for every player
			self.num_players = num_players
			self.start_credits = np.full((num_players,), start_credits)
		else:
			# Different credits
			self.num_players = len(start_credits)
			self.start_credits = np.array(start_credits)
		self.debug = debug

		self.turn = 0
		self.active_player = 0
		self.player_states = np.full((self.num_players,), PlayerState.ACTIVE, dtype=np.uint8)
		self.credits = np.zeros((self.num_players,))
		self.bets = np.zeros((self.num_players,))
		self.pending_bets = np.zeros((self.num_players,))
	
	@property
	def pot(self):
		"""  """

		return np.sum(self.bets)
	
	@property
	def high_bet(self):
		"""  """
		
		return np.max(self.pending_bets)
	
	@property
	def high_bidders(self):
		"""  """

		return self.bets == self.high_bet

	def reset(self):
		"""  """

		# Reset initial state
		self.turn = 0
		self.active_player = 0
		self.player_states[:] = PlayerState.ACTIVE
		self.credits[:] = self.start_credits[:]
		self.bets[:] = .0
		self.pending_bets[:] = .0
	
	def commit(self):
		"""  """
		
		# Commit pending bets
		self.bets += self.pending_bets
		self.pending_bets[:] = .0

		# Check turn state:
		# -	if only one player can be active
		# 	game has handed
		# TODO:

		# Reset active state
		self.player_states[self.player_states == PlayerState.CALLED] = PlayerState.ACTIVE
	
	def next(self):
		"""  """
		
		# Check if there is no active player
		current_player = self.active_player
		self.active_player = (current_player + 1) % self.num_players

		while self.player_states[self.active_player] != PlayerState.ACTIVE:
			if self.active_player == current_player: self.commit()
			self.active_player = (self.active_player + 1) % self.num_players

	def step(self, action: Union[int, float]):
		"""  """

		# TODO: Allow for both discrete actions
		# and continous bets

		if isinstance(action, int):
			# TODO: Compute valid actions
			#valid_actions = []
			#if not action in valid_actions: raise ValueError

			if action == PokerMoves.FOLD:
				self.player_states[self.active_player] = PlayerState.FOLDED
			else:
				# Call first
				bet_value = high_bet = self.high_bet
				credit = self.credits[self.active_player]

				if action >= PokerMoves.RAISE_ANY:
					future_credit = credit - bet_value
					raise_factor = [0.1, 0.25, 0.5, 1.0][action - PokerMoves.RAISE_ANY]
					raise_value = future_credit * raise_factor

					# Add raise value
					bet_value += raise_value
				
				if bet_value > credit:
					# We are all in
					bet_value = credit
					self.player_states[self.active_player] = PlayerState.ALL_IN
				else:
					if bet_value > high_bet:
						# We also raised
						self.player_states[self.player_states == PlayerState.CALLED] = PlayerState.ACTIVE
					
					# We called
					self.player_states[self.active_player] = PlayerState.CALLED
				
				# Update pending bets
				self.pending_bets[self.active_player] = bet_value
			
			print(self.player_states)
			
			# Next player
			self.next()
		else: raise NotImplementedError