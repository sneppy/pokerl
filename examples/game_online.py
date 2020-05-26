import sys
import logging
from argparse import ArgumentParser
from pokerl.network import PokerGameServer, PokerGameClient
from pokerl.agents import RandomAgent

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

parser = ArgumentParser('pokerl')
parser.add_argument('host', nargs='?')
parser.add_argument('--bind', '-B', default='localhost')
parser.add_argument('--num-players', '-N', default=4, type=int)
parser.add_argument('--agent', '-A')
args = parser.parse_args()

def import_class(path: str):
	"""  """

	name = path.split('.')[-1]
	path = path[:-(len(name) + 1)]
	return getattr(__import__(path, fromlist=[name]), name)

if args.host:
	# Create agent
	if args.agent is not None: agent = import_class(args.agent)()
	else: agent = RandomAgent()

	# Run client
	client = PokerGameClient(agent=agent)
	client.connect(*args.host.split(':'))
else:
	# Create server
	server = PokerGameServer(num_players=args.num_players)
	server.setup(*args.bind.split(':'))
	server.run()
	server.close()