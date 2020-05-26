import sys
import logging
from argparse import ArgumentParser
from pokerl.network import PokerGameServer

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

parser = ArgumentParser('pokerl')
parser.add_argument('--bind', '-B', default='localhost')
parser.add_argument('--num-players', '-N', default=4, type=int)
parser.add_argument('--num-games', '-G', default=1, type=int)
args = parser.parse_args()

# Create and run server
server = PokerGameServer(num_players=args.num_players)
server.setup(*args.bind.split(':'))
server.run(num_games=args.num_games)
server.close()