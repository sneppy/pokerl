# PokeRL

**pokerl** is a poker Reinforcement Learning (RL) environment.

Currently the only game supported is _No Limit Texas Hold'em_.

Usage
-----

```bash
$ pip install pokerl
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
The active player performs actions using `game.step(action)`:

```python
from pokerl.enums import PokerMoves

game.step(PokerMoves.CALL) # or 2
```

The `game.active_state` property is an object of type `Game.StateView` that has various informations that can be used by the agent to perform informed decisions.
In particular, `Game.StateView.valid_actions` is a one-hot encoded `np.ndarray` of valid actions:

```python
# Choose random action
valids = game.active_state.valid_actions
action = np.random.choice(len(valids), p=valids / np.sum(valids))
game.step(action)
```

If an invalid action is passed to `game.step` (e.g. if you try to call a bet but you don't have enough credit) an `AssertionError` is thrown.

`game.step` also returns a 3-element tuple indicating whether the game is over, the hand is over and/or the turn is over:

```python
done, _, _ = game.step(action)
if done: print('game is over')
```

After each hand, the net profit of each player is saved in `game.payoffs`.

For more info see the [Wiki page](https://github.com/nondecidibile/pokerl/wiki).

Contributors
------------

- Andrea Mecchia @ [sneppy](https://github.com/sneppy)
- Guglielmo Manneschi @ [nondecidibile](https://github.com/nondecidibile)