# Examples

This page contains various examples of how to use `pokerl`.

> Before running the examples, make sure to set the project root directory in `PYTHONPATH`.

`examples/game_online.py`
-------------------------

This example shows out to play an online game with multiple agents.
To start the server, run `python examples/game_online --num-players 3`.
You can change the interface and the port to which to bind with the argument `--bind <host>[:<port>]`.

To start the client, specify the address and port of the server, which defaults to 25560.
You also need to specify an agent that will decide which action to take at each step:

```console
agent@pokerl:~$ python examples/game_online localhost:25560 --agent pokerl.agents.RandomAgent
```

To play as a human, use `pokerl.agents.CLIAgent`.
If you want to test one of your agents, either create a class which overrides `__call__(self, state: Game.StateView) -> int` or define a function which returns a similar function or an instance of that class.
The agent constructor and the function may accept any number of parameters passed using `--agent-args <argument>`:

```console
agent@pokerl:~$ python examples/game_online localhost --agent your.agent.keras --agent-args .models/2020-05-23
```

`examples/eval_online.py`
-------------------------

The server in this example may be used in place of the server in `examples/game_online.py` to evaluate the performance of multiple agents.
The arguments accepted are `--num-players -N`, `--num-games -G` and `--bind -B <host>[:<port>]`:

```console
agent@pokerl:~$ python examples/eval_online.py --num-players 4 --num-games 5000 --bind 0.0.0.0:8080
```

At the end of the evaluation the stats of the games are returned.
