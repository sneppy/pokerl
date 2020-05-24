import random
import logging
import numpy as np
from typing import Union, List, Tuple, Generator
from .judger import compare_hands, compare_rankings, eval_hand
from .cards import Card, create_default_deck
from .enums import PokerMoves, PlayerState, HandRanking

class Game:
	""" A Texas Hold'em game
	
	Usage
	-----

	```python
	import sys
	import logging
	import numpy as np
	from pokerl import Game

	# Enable logging
	logging.basicConfig(stream=sys.stdout, level=logging.INFO)

	# Create game
	game = Game(num_players=4, start_credits=100)

	for g in range(10):
		game.reset()
		game_over = False
		while not game_over:
			# Get random action from valid actions
			v, _ = game.get_valid_actions()
			u = np.random.choice(len(v), p=v / np.sum(v))

			game_over, *_ = game.step(u)
	```
	"""

	def __init__(self, **config):
		""" TODO """
		
		# Different credits
		self.num_players: int= config.get('num_players', 4)
		self.start_credits: Union[np.ndarray, int, list] = config.get('start_credits', 100)
		self.big_blind: float= config.get('big_blind', 2)
		self.small_blind: float= config.get('small_blind', 1)
		self.logger: logging.Logger= config.get('logger', logging.getLogger())

		self.deck = create_default_deck()
		self.turn = 0
		self.hand = 0
		self.big_blind_idx = 0
		self.small_blind_idx = 0
		self.active_player = 0
		self.player_states = np.full((self.num_players,), PlayerState.ACTIVE, dtype=np.uint8)
		self.credits = np.zeros((self.num_players,))
		self.bets = np.zeros((self.num_players,))
		self.pending_bets = np.zeros((self.num_players,))
		self.minimum_raise_value = .0
		self.payoffs = np.zeros((self.num_players,))
	
	@property
	def community_cards(self) -> List[Card]:
		""" The list of shared cards
		
		Depending on the current turn
		of the hand, zero, three, four
		or five cards are returned"""

		# In Texas Hold'em, cards are burnt
		# but the probability of 5 drawing
		# a set of 5 cards is actually the
		# same thus we don't care
		return [] if self.turn == 0 else self.deck[:self.turn + 2]
	
	@property
	def pot(self) -> float:
		""" The sum of all the bets """

		return np.sum(self.bets)
	
	@property
	def high_bet(self) -> float:
		""" The current highest bet """
		
		return np.max(self.pending_bets)
	
	@property
	def high_bidders(self) -> np.ndarray:
		""" List of bidders that match the high bet """

		return self.bets == self.high_bet
	
	@property
	def pending_credits(self) -> np.ndarray:
		""" The estimated number of credits """

		return self.credits - self.pending_bets
	
	@property
	def blind_idx(self) -> List[int]:
		""" A 2-elements list with the index of the big blind and the index of the small blind """

		return [self.big_blind_idx, self.small_blind_idx]
	
	@property
	def blind_value(self) -> List[float]:
		""" A 2-elements list with the value of big and small blinds """

		return [self.big_blind, self.small_blind]
	
	@property
	def game_over(self) -> bool:
		""" Returns true if all players but one are broken """

		return np.sum(self.player_states != PlayerState.BROKEN) == 1
	
	@property
	def active_state(self) -> dict:
		""" The state of the game as perceived by the active player
		
		Returns
		-------
		dict
			A python dictionary with the
			following items:
			- `player_cards`: a 2-element
				list with the cards in the
				hand of the active player;
			- `community_cards`: the list
				of community cards;
			- `credits`: the credits of all
				players as a numpy array;
			- `bets`: the bets of previous
				turns by all players;
			- `pending_bets`: the bets of
				this turn;
			- `minimum_raise_value`: the
				minimum value required to
				raise the bet;
			- `valid_actions`: a tuple where
				the first element encodes
				the valid actions with ones
				and the second element has
				the indices of the valid
				actions.
		"""

		return dict(
			player_cards=self.get_cards_of(self.active_player),
			community_cards=self.community_cards,
			credits=self.credits,
			bets=self.bets,
			pending_bets=self.pending_bets,
			minimum_raise_value=self.minimum_raise_value,
			valid_actions=self.get_valid_actions(self.active_player)
		)
	
	def get_first_playing(self, idx: int) -> int:
		""" Returns the index of the first non-broken player, starting from player `idx` """

		return (idx + np.argmax(np.roll(self.player_states, -idx) != PlayerState.BROKEN)) % self.num_players
	
	def get_valid_actions(self, player: int=None) -> Tuple[np.ndarray, Generator[int, None, None]]:
		""" List of valid actions
		
		Returns the actions that `player`
		could take in the current game
		state
		
		Params
		------
		player : int
			index of the player. If `None`,
			`self.active_player` is used
			isntead.
		
		Returns
		-------
		tuple
			A tuple where the first element
			is a one-hot encoded array of
			valid actions, and the second
			element is a generator of indices
			of valid actions
		"""

		if player is None: player = self.active_player

		high_bet = self.high_bet
		credit = self.credits[player]
		onehot = np.ones((PokerMoves.NUM_MOVES))
		
		# Compute minimum raise value
		raise_values = np.array([0.1, 0.25, 0.5]) * (credit - high_bet)
		raise_values = np.logical_and(raise_values > self.minimum_raise_value, (high_bet + raise_values) < credit)
		onehot[PokerMoves.RAISE_ANY:PokerMoves.RAISE_ANY + PokerMoves.NUM_RAISE_MOVES] = raise_values

		# Compute call and check validity
		onehot[PokerMoves.CHECK] = high_bet == .0 # Check only if no hight bet
		onehot[PokerMoves.CALL] = high_bet < credit # Call only if enough credits
		
		# Generate action indices using
		# a generator, so that we don't
		# iterate unless requested
		valids = (action for action, valid in enumerate(onehot) if valid)

		return onehot, valids
	
	def get_cards_of(self, player: int) -> List[Card]:
		""" Returns the cards in the hands of `player` """

		card_idx = 5 + player * 2
		return self.deck[card_idx:card_idx + 2]
	
	def get_hand_for(self, player) -> List[Card]:
		""" Returns the final hand for `player` """

		card_idx = 5 + player * 2
		return self.deck[:5] + self.deck[card_idx:card_idx + 2]

	def reset(self, **config):
		"""Reset game to its initial state
		
		Accepts the same parameters of `__init__`
		"""

		# Reset initial state
		self.hand = 0
		self.active_player = 0
		self.big_blind_idx = self.num_players - 1
		self.small_blind_idx = self.big_blind_idx - 1
		self.credits[:] = self.start_credits if isinstance(self.start_credits, int) else self.start_credits[:]
		self.player_states[:] = PlayerState.ACTIVE
		
		# Setup hand
		self.setup_hand()
	
	def setup_hand(self):
		""" Setup a new hand """

		self.hand += 1

		# Reset player states
		self.turn = 0
		self.player_states[self.credits <= self.big_blind] = PlayerState.BROKEN
		self.player_states[self.player_states != PlayerState.BROKEN] = PlayerState.ACTIVE
		self.bets[:] = .0
		self.pending_bets[:] = .0

		# Shuffle deck
		random.shuffle(self.deck)
		self.logger.info('Dealing cards')
		for player in range(self.num_players):
			if self.player_states[player] != PlayerState.BROKEN:
				self.logger.info('Player %d has cards: %s', player, self.get_cards_of(player))

		# Update blinds and active player
		self.small_blind_idx = self.get_first_playing(self.small_blind_idx + 1)
		self.big_blind_idx = self.get_first_playing(self.small_blind_idx + 1)
		self.active_player = self.get_first_playing(self.big_blind_idx + 1)
		
		# Blind bets
		self.pending_bets[self.blind_idx] += self.blind_value
		self.player_states[self.big_blind_idx] = PlayerState.CALLED
		self.minimum_raise_value = self.big_blind

		self.logger.info('; '.join(['Player %d is %s with $%.2f' % (player, PlayerState.as_string[state], self.credits[player]) for player, state in enumerate(self.player_states)]))
		self.logger.info('Player %d is big blind', self.big_blind_idx)
		self.logger.info('Big blind is $%.2f; small blind is $%.2f', self.big_blind, self.small_blind)
		self.logger.info('Player %d starts the turn', self.active_player)
	
	def end_hand(self):
		""" Called to end the current hand and compute winners """

		# Commit pending bets
		self.bets += self.pending_bets
		self.credits -= self.pending_bets

		self.pending_bets[:] = .0
		self.minimum_raise_value = .0
		
		self.logger.info('Pot value is $%.2f', self.pot)

		# Reset payoffs; we only reset them
		# here so that they are available after
		# hand has ended
		self.payoffs[:] = .0

		# Get number of potential winners
		potential_winners = np.logical_and(self.player_states != PlayerState.BROKEN, self.player_states != PlayerState.FOLDED)
		num_potential_winners = np.sum(potential_winners)
		assert num_potential_winners > 0, 'Invalid state: no potential winner'
		
		if num_potential_winners == 1:
			# Winner takes all
			winner = np.argmax(potential_winners)

			self.payoffs[winner] = self.pot
			self.credits[winner] += self.pot

			self.logger.info('Player %d wins by last stand', winner)
		else:
			# Make working copy of bets
			bets = np.copy(self.bets)

			# First compute hand rankings
			hands = (self.get_hand_for(player) if state == PlayerState.CALLED or state == PlayerState.ALL_IN else [] for player, state in enumerate(self.player_states))
			hand_rankings = list(map(eval_hand, hands))
			none_ranking = (HandRanking.NONE, [])

			self.logger.debug('Final hands: %s', hands)

			# Sort players by lowest bets and generate allins iterator
			sorted_players = np.argsort(self.bets)
			showdown = (player for player in sorted_players if self.player_states[player] == PlayerState.CALLED or self.player_states[player] == PlayerState.ALL_IN)
			
			for player in showdown:
				if bets[player] == .0: break # Nothing left to split
				if num_potential_winners == 1:
					# Player must be potential winner
					self.payoffs[player] += np.sum(bets)
					self.logger.info('Player %d wins by last stand', player)

					break

				# Get max bet for this player
				max_bet = bets[player]
				max_bets = np.clip(bets, .0, max_bet)
				
				# Get hand winners and distribute wins
				onehot, winners = compare_rankings(hand_rankings)
				winning_hands = (hand_rankings[winner] for winner in winners)

				if len(winners) == 1: self.payoffs[winners] += np.sum(max_bets)
				else: self.payoffs += np.sum(max_bets) * np.array(onehot) / np.sum(onehot)

				self.logger.debug('Hand rankings: %s', hand_rankings)
				self.logger.info('Player(s) %s wins with %s', winners, ', '.join([HandRanking.as_string[ranking] for ranking, kickers in winning_hands]))

				# Reset player hand and subtract max bets
				hand_rankings[player] = none_ranking
				bets -= max_bets

				num_potential_winners -= 1

			# Distribute wins
			self.credits += self.payoffs
		
		# Compute player hand's net value
		self.payoffs -= self.bets

		self.logger.info('Players\'s net profits: %s', self.payoffs)
		
		# Next hand
		self.setup_hand()

	def next_turn(self) -> Tuple[bool, bool, bool]:
		""" Advances to next turn
		
		Returns
		-------
		tuple
			A tuple indicating whether:
			- the game has ended
			- the hand has ended
			- the turn has ended
		"""

		# Commit pending bets
		self.bets += self.pending_bets
		self.credits -= self.pending_bets

		self.pending_bets[:] = .0
		self.minimum_raise_value = .0
		
		# Next turn
		self.turn += 1

		if self.turn == 4:
			self.end_hand()
			return self.game_over, True, True
		else:
			next_turn_players = self.player_states == PlayerState.CALLED
			num_next_turn_players = np.sum(next_turn_players)

			if num_next_turn_players > 1:
				# Reset states
				self.player_states[next_turn_players] = PlayerState.ACTIVE

			self.logger.info('Community cards: %s', self.deck[:self.turn + 2].__repr__())
			self.active_player = (self.active_player + 1) % self.num_players
			return False, False, True
	
	def next_player(self) -> Tuple[bool, bool, bool]:
		""" Find next player
		
		Depending on the game state,
		this function may cause the
		end of the hand or game.
		At the end of the function,
		`self.active_player` points
		to the right player
		
		Returns
		-------
		tuple
			A tuple indicating whether:
			- the game has ended
			- the hand has ended
			- the turn has ended
		"""

		# Get number of playing players
		playing_players = np.logical_and(self.player_states != PlayerState.BROKEN, self.player_states != PlayerState.FOLDED)
		num_playing_players = np.sum(playing_players)

		if num_playing_players > 1:
			# Proceed normally
			done = False, False, False
			current_player = self.active_player
			self.active_player = (self.active_player + 1) % self.num_players

			while self.player_states[self.active_player] != PlayerState.ACTIVE:
				if current_player == self.active_player:
					done = self.next_turn()
					if done[0]: return done # Game is over
				else: self.active_player = (self.active_player + 1) % self.num_players

			self.logger.info('It\'s Player %d\'s turn', self.active_player)
			
			return done
		else:
			# One winner takes all
			self.end_hand()
			return False, True, False

	def step(self, action: Union[int, float]) -> Tuple[bool, bool, bool]:
		""" Perform a step of the game
		
		Make the current active player
		perform `action` and advance
		game state
		
		Params
		------
		action
			Index of a valid action, as in
			`PokerMoves`
		
		Returns
		-------
		tuple
			A tuple indicating whether:
			- the game has ended
			- the hand has ended
			- the turn has ended
		"""

		# TODO: Allow for both discrete actions
		# and continous bets

		if isinstance(action, int):
			# TODO: Compute valid actions
			_, valid_actions = self.get_valid_actions()
			if not action in valid_actions:
				self.logger.error('Player %d invalid move: `%s`', self.active_player, PokerMoves.as_string[action])
				raise ValueError('Player %d invalid move: `%s`' % (self.active_player, PokerMoves.as_string[action]))

			self.logger.info('High bet is $%.2f', self.high_bet)
			self.logger.debug('Player %d played action: %s', self.active_player, PokerMoves.as_string[action])

			if action == PokerMoves.FOLD:
				self.player_states[self.active_player] = PlayerState.FOLDED
				self.logger.info('Player %d folds', self.active_player)
			elif action == PokerMoves.CHECK:
				self.player_states[self.active_player] = PlayerState.CALLED
				self.logger.info('Player %d checks', self.active_player)
			else:
				# Call first, always bet something
				high_bet = self.high_bet
				bet_value = max(high_bet, self.big_blind)
				credit = self.credits[self.active_player]
				self.player_states[self.active_player] = PlayerState.CALLED

				if action == PokerMoves.ALL_IN:
					bet_value = credit
					self.player_states[self.active_player] = PlayerState.ALL_IN
					self.logger.info('Player %d goes all-in with $%.2f', self.active_player, bet_value)
				elif action >= PokerMoves.RAISE_ANY:
					# Add raise value
					future_credit = credit - bet_value
					raise_factor = [0.1, 0.25, 0.5][action - PokerMoves.RAISE_ANY]
					raise_value = future_credit * raise_factor
					bet_value += raise_value
				
				if bet_value > high_bet:
					# We raised the high bet, reset all aclled states to active
					current_state = self.player_states[self.active_player]
					self.player_states[self.player_states == PlayerState.CALLED] = PlayerState.ACTIVE
					self.player_states[self.active_player] = current_state

					# Set minimum raise value
					self.minimum_raise_value = bet_value - high_bet

					self.logger.info('Player %d raises to $%.2f', self.active_player, bet_value)
					self.logger.info('Minimum raise value is $%.2f', self.minimum_raise_value)
				else:
					# We called the high bet
					self.logger.info('Player %d called $%.2f', self.active_player, bet_value)
				
				# Update pending bets
				self.pending_bets[self.active_player] = bet_value
			
			# Next player
			return self.next_player()
		else: raise NotImplementedError