import logging
import socket, pickle
from ..game import Game

class PokerGameServer:
	"""  """

	def __init__(self, logger: logging.Logger=logging.getLogger(), **game_config):
		"""  """

		self.logger = logger

		self.game = Game(logger=self.logger, **game_config)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clients = []
	
	def setup(self, host: str='localhost', port: int=25560):
		"""  """
		
		# Waiting for players
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((host, int(port)))
		self.sock.listen()

		self.logger.info('server running on %s:%d' % (host, int(port)))

		while len(self.clients) < self.game.num_players:
			client, addr = self.sock.accept()
			self.logger.info('%s connecting as Player %d' % (addr, len(self.clients)))
			self.clients.append(client)
		
		# Start game
		self.game.reset()
		for player, client in enumerate(self.clients):
			# Send ready state
			data = pickle.dumps(dict(status='ready', player=player, num_players=self.game.num_players))
			client.sendall(data)
	
	def step(self):
		"""  """
		
		# Get active client
		player_client = self.clients[self.game.active_player]

		# Get active state and send to player
		active_state = self.game.active_state
		active_state = pickle.dumps(dict(status='play', player=self.game.active_player, active_state=active_state))
		player_client.sendall(active_state)

		# Wait for a response
		action = player_client.recv(1024)
		player, action = pickle.loads(action)
		assert player == self.game.active_player, 'Received action from wrong player'
		
		# Do action
		done, hand, _ = self.game.step(action)

		# Send update to other clients
		if False:
			log = dict(status='step', active_player=player, action=action)
			log = pickle.dumps(log)
			for client in self.clients:
				client.sendall(log)

		if False and hand:
			# Send hand stats
			stats = dict(status='stats', credits=self.game.credits, payoffs=self.game.payoffs)
			stats = pickle.dumps(stats)
			for client in self.clients: client.sendall(stats)
		
		return done
	
	def run(self, num_games: int=1):
		"""  """

		for game in range(num_games):
			self.game.reset()
			while not self.step(): pass
	
	def close(self):
		"""  """
		
		# Close all connections
		for _ in range(len(self.clients)):
			client = self.clients.pop()
			client.close()