from .agent import PokerAgent, Game

class CLIAgent(PokerAgent):
	""" Human console agent
	
	Implements an agent that receives commands
	from the CLI and prints the state to the
	CLI
	"""

	def __call__(self, state: Game.StateView) -> int:
		"""  """

		# Print state to console and return input
		return int(input(str(state) + '\naction> '))