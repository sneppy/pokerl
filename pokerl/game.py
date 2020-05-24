import random
import logging
import numpy as np
from typing import Union
from pokerl.judger import compare_hands
from pokerl.cards import create_default_deck
from pokerl.enums import PokerMoves, PlayerState, HandRanking

class Game:
	"""  """

	def __init__(self, **config):
		"""  """
		
		# Different credits
		self.num_players: int= config.get('num_players', 4)
		self.start_credits: Union[np.ndarray, int, list] = config.get('start_credits', 100)
		self.big_blind: float= config.get('big_blind', 2)
		self.small_blind: float= config.get('small_blind', 1)
		self.logger: logging.Logger= config.get('logger', logging.getLogger())

		self.deck = create_default_deck()
		self.turn = 0
		self.big_blind_idx = 0
		self.small_blind_idx = 0
		self.active_player = 0
		self.player_states = np.full((self.num_players,), PlayerState.ACTIVE, dtype=np.uint8)
		self.credits = np.zeros((self.num_players,))
		self.bets = np.zeros((self.num_players,))
		self.pending_bets = np.zeros((self.num_players,))
		self.payoffs = np.zeros((self.num_players,))
	
	@property
	def shared_cards(self):
		"""  """

		return [] if self.turn == 0 else self.deck[:self.turn + 2]
	
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
	
	@property
	def blind_idx(self):
		"""  """

		return [self.big_blind_idx, self.small_blind_idx]
	
	@property
	def blind_value(self):
		"""  """

		return [self.big_blind, self.small_blind]
	
	def get_first_playing(self, idx):
		"""  """

		return (idx + np.argmax(np.roll(self.player_states, -idx) != PlayerState.BROKEN)) % self.num_players
	
	def get_cards_of(self, player):
		"""  """

		card_idx = 5 + player * 2
		return self.deck[card_idx:card_idx + 2]
	
	def get_hand_for(self, player):
		"""  """

		card_idx = 5 + player * 2
		return self.shared_cards + self.deck[card_idx:card_idx + 2]

	def reset(self):
		"""  """

		# Reset initial state
		self.active_player = 0
		self.big_blind_idx = self.num_players - 1
		self.small_blind_idx = self.big_blind_idx - 1
		self.credits[:] = self.start_credits if isinstance(self.start_credits, int) else self.start_credits[:]
		
		# Setup hand
		self.setup_hand()
	
	def setup_hand(self):
		"""  """

		# Shuffle deck
		random.shuffle(self.deck)
		self.logger.info('Dealing cards')
		for player in range(self.num_players):
			if self.player_states[player] != PlayerState.BROKEN:
				self.logger.info('Player %d has cards: %s', player, self.get_cards_of(player).__repr__())

		# Reset player states
		self.turn = 0
		self.player_states[self.player_states != PlayerState.BROKEN] = PlayerState.ACTIVE
		self.bets[:] = .0
		self.pending_bets[:] = .0
		self.payoffs[:] = .0
		
		# Blind bets
		self.logger.info('Player %d is big blind', self.big_blind_idx)
		self.logger.info('Big blind is $%.2f; small blind is $%.2f', self.big_blind, self.small_blind)
		self.pending_bets[self.blind_idx] += self.blind_value
		self.player_states[self.big_blind_idx] = PlayerState.CALLED

		# Update active player
		self.active_player = self.get_first_playing(self.big_blind_idx + 1)
		self.logger.info('Player %d starts the turn', self.active_player)

		# Update blinds for next hand
		self.small_blind_idx = self.big_blind_idx
		self.big_blind_idx = self.active_player

	def next_turn(self):
		"""  """
		
		# Commit pending bets
		self.bets += self.pending_bets
		self.credits -= self.pending_bets
		self.pending_bets[:] = .0

		# Check turn state:
		# -	if only one player can be active
		# 	game has handed
		num_contestant = np.sum(np.logical_or(self.player_states == PlayerState.CALLED, self.player_states == PlayerState.ALL_IN))

		if num_contestant == 0: raise AssertionError('Invalid state, all players folded')
		elif self.turn == 3:
			# Last turn, end game.
			# Build player hands
			hands = [self.get_hand_for(idx) if state in [PlayerState.CALLED, PlayerState.ALL_IN] else [] for idx, state in enumerate(self.player_states)]
			self.logger.debug('Final hands: %s', hands.__repr__())

			onehot, winners, rankings = compare_hands(hands)
			winning_hands = [rankings[winner] for winner in winners]
			self.logger.info('Player(s) %s wins the hand with a %s', winners.__repr__(), HandRanking.as_string[rankings[0][0]])
			# TODO: Handle all-ins
			self.payoffs = self.pot * np.array(onehot) / np.sum(onehot)
			self.credits += self.payoffs
			self.logger.info('Total pot is $%.2f', self.pot)
			self.logger.info('; '.join(['Player %d takes $%.2f' % (player, payoff) for player, payoff in enumerate(self.payoffs) if payoff > .0]))

			# Set broken state
			self.player_states[self.credits <= self.big_blind] = PlayerState.BROKEN
			self.logger.info('; '.join(['Player %d has $%.2f' % credit for credit in enumerate(self.credits)]))
			
			# Setup new hand
			self.setup_hand()
		else:
			self.logger.info('Shared cards: %s', self.deck[:self.turn + 3].__repr__())

			# Normal state, we have some
			# players that are playing
			# and we need to deal one card
			self.turn += 1

			# Reset active state
			self.player_states[self.player_states == PlayerState.CALLED] = PlayerState.ACTIVE
	
	def next(self):
		"""  """
		
		# Check if there is no active player
		current_player = self.active_player
		self.active_player = (current_player + 1) % self.num_players

		while self.player_states[self.active_player] != PlayerState.ACTIVE:
			if self.active_player == current_player: self.next_turn()
			self.active_player = (self.active_player + 1) % self.num_players

	def step(self, action: Union[int, float]):
		"""  """

		# TODO: Allow for both discrete actions
		# and continous bets

		if isinstance(action, int):
			# TODO: Compute valid actions
			#valid_actions = []
			#if not action in valid_actions: raise ValueError

			self.logger.info('High bet is %.2f', self.high_bet)
			self.logger.debug('Player %d played action: %s', self.active_player, PokerMoves.as_string[action])

			if action == PokerMoves.FOLD:
				self.player_states[self.active_player] = PlayerState.FOLDED
				self.logger.info('Player %d folds', self.active_player)
			else:
				# Call first
				bet_value = high_bet = self.high_bet
				credit = self.credits[self.active_player] + self.pending_bets[self.active_player] # Needed for small blind

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
					self.logger.info('Player %d goes all-in', self.active_player)
				else:
					if bet_value > high_bet:
						# We also raised
						self.player_states[self.player_states == PlayerState.CALLED] = PlayerState.ACTIVE
						self.logger.info('Player %d raises to $%.2f', self.active_player, bet_value)
					else:
						self.logger.info('Player %d called $%.2f', self.active_player, bet_value)
					
					# We called
					self.player_states[self.active_player] = PlayerState.CALLED
				
				# Update pending bets
				self.pending_bets[self.active_player] = bet_value
			
			# Next player
			self.next()
		else: raise NotImplementedError