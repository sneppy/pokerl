# PokeRL

**pokerl** is a poker Reinforcement Learning (RL) environment.

Currently the only game supported is _No Limit Texas Hold'em_.

Usage
-----

```console
agent@pokerl:~$ pip install pokerl
```

A game is created by creating a new instance of the `Game` class:

```python
from pokerl import Game
game = Game()
```

The constructor accepts various parameters, such as the number of players and the initial credits:

```python
game = Game(num_players=4, start_credits=100)
game.reset() # Init game state
```

At each step, there is an _active player_ and an _active state_, which captures the state of the game as seen by the active player.
The active player performs actions by passing a valid integer value to `game.step(action)`:

```python
from pokerl.enums import PokerMoves
game.step(PokerMoves.CALL)
game.step(PokerMoves.FOLD)
game.step(PokerMoves.ALL_IN)
```

> The type of `action` must be `int` or `np.integer`

The `game.active_state` property is an object of type `Game.StateView` that has various informations that can be used by the agent to make informed decisions.
In particular, `valid_actions` is a one-hot encoded `np.ndarray` of valid actions:

```python
# Choose random action
valids = game.active_state.valid_actions
action = np.random.choice(len(valids), p=valids / np.sum(valids))
game.step(action)
```

If an invalid action is passed to `game.step` (e.g. if you try to call a bet but you don't have enough credit) an `AssertionError` is thrown.

`game.step` also returns a 3-element tuple indicating whether the game is over, the hand is over and/or the round of bets is over:

```python
done, _, _ = game.step(action)
if done: print('game is over')
```

After each hand, the net profit of each player is saved in `game.payoffs`.

For more info see the [Wiki page](https://github.com/nondecidibile/pokerl/wiki).

### Environments

If you are familiar with OpenAI Gym, the `racerl.envs` environments expose an API similar to that of `gym.Env`.
The `PokerGameEnv` simulates an entire game and returns a non-zero reward after each hand, depending on the player's payoffs and bets.
To use the `PokerGameEnv` create a new instance by passing a list of opponents:

```python
from pokerl import Game
from pokerl.envs import PokerGameEnv

def random_agent(state: Game.StateView) -> int:

	actions = state.valid_action_indices
	return np.random.choice(list(actions))

env = PokerGameEnv([random_agent, random_agent, random_agent], num_players=4)
```

An opponent must be a callable object which receives the game state as seen by the agent and returns the action to perform.
The usual methods `env.reset()` and `env.step(action)` can be used to reset the state and perform actions on the environment:

```python
# Evaluate agent on one run

R = []
state = env.reset()
done = False
while not done:
	action = predict(state)
	state, rwd, done = env.step(action)
	R.append(rwd)

print('score', np.sum(R))
```

The reward is the sum of the payoffs.

### Network

The `network` branch is an experimental branch where it is possible to play online games.
Many functionalities, however, are also available in the main branch.

To create a server, create a new instance of the `pokerl.network.PokerGameServer` class:

```python
from pokerl.network import PokerGameServer
server = PokerGameServer(num_players=3)
```

The constructor accepts the same parameters of `Game`.
To start the server and play a game, use `server.setup(host, port)` followed by `server.run()`:

```python
server.setup('localhost', 25560)
#server.setup() Listen on default host and port
server.run()
```

A client is an instance of `pokerl.network.PokerGameClient`.
The contructor accepts a strategy policy `agent`, which ideally is a subclass of `pokerl.agents.PokerAgent`:

```python
from pokerl.agents import RandomAgent
client = PokerGameClient(agent=RandomAgent)
```

To connect to a server, use `client.connect(host, port)`:

```python
client.connect('localhost', 25560)
client.connect() # Use default host and port
```

Once all the players have connected, the game begins.

At the moment, it is not possible to follow the actions of other clients.

Contributors
------------

- Andrea Mecchia @ [sneppy](https://github.com/sneppy)
- Guglielmo Manneschi @ [nondecidibile](https://github.com/nondecidibile)