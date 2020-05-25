from ..game import Game

class PokerAgent:
	""" Interface for poker agents
	
	The minimum requirement is that
	it implements `__call__` to
	predict the next action
	"""

	def __call__(self, state: Game.StateView) -> int:
		""" Takes state view """

		raise NotImplementedError