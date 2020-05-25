import socket, pickle
from ..game import Game

class PokerGameServer:
	"""  """

	def __init__(self, **game_config):
		"""  """

		self.game = Game(**game_config)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clients = []
	
	def run(self, host: str='localhost', port: int=25560):
		"""  """
		
		# Waiting for players
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((host, int(port)))
		self.sock.listen()

		print('server running on %s:%d' % (host, int(port)))

		while len(self.clients) < self.game.num_players:
			client, addr = self.sock.accept()
			print('%s connecting as Player %d' % (addr, len(self.clients)))
			self.clients.append(client)
		
		# Start game
		self.game.reset()
		for player, client in enumerate(self.clients):
			# Send ready state
			data = pickle.dumps(dict(status='ready', player=player, num_players=self.game.num_players))
			client.sendall(data)
		
		game_over = False
		while not game_over:
			player_client = self.clients[self.game.active_player]

			# Get active state and send to player
			active_state = self.game.active_state
			active_state = pickle.dumps(dict(status='playing', player=self.game.active_player, active_state=active_state))
			player_client.sendall(active_state)

			# Wait for a response
			action = player_client.recv(1024)
			player, action = pickle.loads(action)
			assert player == self.game.active_player, 'Received action from wrong player'
			
			# Do action
			game_over, _, _ = self.game.step(action)
		
		print('game ended')