import logging
import socket, pickle
from ..agents import PokerAgent, RandomAgent
from ..enums import PokerMoves

class PokerGameClient:
	"""  """

	def __init__(self, agent: PokerAgent=RandomAgent(), logger: logging.Logger=logging.getLogger()):
		"""  """

		assert agent is not None, 'Invalid agent'
		self.agent = agent
		self.logger = logger

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.player = -1
		self.state = None

	def connect(self, host: str='localhost', port: int=25560):
		"""  """

		# Wait for ready state
		port = int(port)
		self.sock.connect((host, port))
		msg = self.sock.recv(1024)
		msg: dict= pickle.loads(msg)

		assert msg.get('status') == 'ready', 'Invalid status'
		self.player = msg.get('player', 0)

		self.logger.info('Connected to %s:%d as player %d', host, port, self.player)

		while True:
			try:
				# Receive state from server
				msg = self.sock.recv(65536)
				msg: dict = pickle.loads(msg)
			except (socket.error, EOFError): break

			status = msg['status']
			
			if status == 'step':
				self.logger.info('Player %d played action: %s', msg['active_player'], PokerMoves.as_string[msg['action']])
			elif status == 'play':
				assert msg['player'] == self.player, 'Received message with wrong player id'

				# Send agent action
				active_state = msg.get('active_state')
				action = self.agent(active_state)
				action = pickle.dumps((self.player, action))
				self.sock.sendall(action)
			elif status == 'stats':
				self.logger.info('Payoffs: %s', list(msg['payoffs']))
				self.logger.info('Credits: %s', list(msg['credits']))