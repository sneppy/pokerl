import socket, pickle
import numpy as np
from ..agents import PokerAgent, RandomAgent

class PokerGameClient:
	"""  """

	def __init__(self, agent: PokerAgent=RandomAgent()):
		"""  """

		assert agent is not None, 'Invalid agent'
		self.agent = agent

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.player = -1
		self.state = None

	def connect(self, host: str='localhost', port: int=25560):
		"""  """

		# Wait for ready state
		self.sock.connect((host, int(port)))
		ready_state = self.sock.recv(1024)
		ready_state: dict= pickle.loads(ready_state)

		assert ready_state.get('status') == 'ready', 'Invalid status'
		self.player = ready_state.get('player', 0)
		print('Connnected to %s:%d as player %d' % (host, port, self.player))

		while True:
			# Receive state from server
			state = self.sock.recv(4096)
			state: dict = pickle.loads(state)
			assert state.get('player') == self.player, 'Received state with wrong player id'

			status = state.get('status', 'playing')
			if status == 'over': break
			elif status == 'playing':
				# Send random action
				active_state = state.get('active_state')
				action = self.agent(active_state)
				action = pickle.dumps((self.player, action))
				self.sock.sendall(action)
			else: raise AssertionError('Invalid status')