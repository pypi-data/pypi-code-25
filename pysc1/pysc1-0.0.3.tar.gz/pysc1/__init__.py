print('''
============================================
pysc1 : The StarCraft I Learning Environment
============================================

This package is currently in enthusiastic development. Just wait a sec.
Meanwhile, refer to https://github.com/bboyseiok/pysc1-gym for now.

Thank you.

# Pysc1-gym

Installing and managing Starcraft I learning environment can be tedious and full of errors. Here, I present to you packaged way of running a nice Starcraft I gym simulation in your laptop or some clusters.

I was using Windows 10 while making this work, so the instructions are made in reference to the Windows system. 

### "OpenAI Gym" like code for Starcraft I

After the Environment is set, you can access the features of Starcraft I just like in OpenAI Gym:
```python
env = sc.SingleBattleEnv(args.ip, args.port)
env.seed(777)
agent = RandomAgent(env.action_space)

episodes = 0
while episodes < 100:
    obs = env._reset()
    done = False
    while not done:
        action = agent.act()
        obs, reward, done, info = env._step(action)
    episodes += 1

env.close()
```

## prerequisites

* OpenAI Gym
* Starcraft 1.1.16
* BWAPI 4.1.2
* TorchCraft 1.0.2
* TorchCraft-py
* Gym-TorchCraft

Because of the dependencies here, Python 2.7 is used. In the future, support for Python 3.6+ would be added.

* Python 2.7
I recommend using `conda create -n "pysc1-gym" python=2.7` to manage separate packages.

Get the TorchCraft 1.0-2 from [here](https://github.com/TorchCraft/TorchCraft/releases)

check to prerequisites again. For start, `git clone https://github.com/openai/gym` and `cd gym` and `pip install -e .` for minimal install of gym.

## Installation (Windows 10 with Anaconda)
The installation process is long, but it should be lot shorter than doing this from scratch. So relax and slowly follow the steps. Take a deep breath...

0. `activate pysc1-gym` to activate the environment.

1. Check your Starcraft Installation. The directory is called `$STARCRAFT`.

2. run `pysc1-gym/bwapi/BWAPI_412_Setup.exe` and install on `$BWAPI` directory and run `$BWAPI/Chaoslauncher/Chaoslauncher.exe` that is inside the BWAPI installation location.

3. From Settings in `Chaoslauncher`, choose the path to the Starcraft installation directory `$STARCRAFT`.

3.1. Full Installation

3.2. The Abyss (ICCUP) and Games Podolsk are optional

4. copy files in `pysc1-gym/torchcraft/*.dll` to `$STARCRAFT` directory.

5. copy files in `pysc1-gym/config/*.ini` to `$STARCRAFT/bwapi-data` directory

6. run `pysc1-gym/install.bat` (while still inside the `pysc1-gym` environment). This will install custom dependencies `torchcraft-py` and `gym-starcraft`. (Check if no existing installations are there in the pysc1-gym env.) This will take some time installing the dependencies. *wait patiently... have a coffee.*

7. copy contents of `pysc1-gym/maps/` to `$STARCRAFT/maps/`.

8. run Chaoslauncher with `BWAPI 4.1.2 injector [RELEASE]` and `W-mode 1.02` checked. The Starcraft window will open in waiting mode.

*Don't panic if the window is not responsive. It's supposed to be that way!*

9. cd `pysc1-gym/examples` (while still inside the `pysc1-gym` environment) and run `python random_agent.py --ip=localhost --port=11111`

10. The agent will run

## Custom Maps for Reinforcement Learning

Custom maps I created for diverse RL environments.

### BroodWar/Micros

* bc12v12_c_far.scx 12 Battlecruisers against each other

* m24v24_c_far_mod.scx 24 Marines against each other

* zt12v12_j_far.scm 11 Zealots and a High Templar against each other

## TODO

* support python 3.6+
* more easy installation.

============================================
pysc1 : The StarCraft I Learning Environment
============================================

This package is currently in enthusiastic development. Just wait a sec.
Meanwhile, refer to https://github.com/bboyseiok/pysc1-gym for now.

Thank you.

''')