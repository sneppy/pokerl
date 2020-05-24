from typing import Union
from pokerl.enums import CardRank, CardSuit

class Card:
	"""  """

	@property
	def rank(self) -> int:
		"""  """

		return (self.value & 0xf) or 13 # Make ace highest rank
	
	@property
	def suit(self) -> int:
		"""  """

		return self.value >> 4
	
	def __init__(self, value: Union[int, tuple]):
		"""  """
		
		if isinstance(value, tuple): value = (value[1] << 4) | value[0]
		assert (value & 0xf) < CardRank.NUM_RANKS, 'Invalid card rank'
		assert (value >> 4) < CardSuit.NUM_SUITS, 'Invalid card suit'

		# Set value
		self.value = value
	
	def __repr__(self) -> str:
		"""  """
		
		return chr(0x1f0a1 + self.value)

def create_default_deck():
	"""  """

	return [Card((rank, suit)) for rank in range(CardRank.NUM_RANKS) for suit in range(CardSuit.NUM_SUITS)]