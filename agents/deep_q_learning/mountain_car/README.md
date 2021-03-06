# Mountain Car with Deep Q Learning

![Trained agent on MountainCar-v0](https://s7.gifyu.com/images/trained_agent.gif)

*Trained agent playing the game*

This module can be used to train a DQN agent to play the [MountainCar](https://gym.openai.com/envs/MountainCar-v0/) environment from [Gym](https://gym.openai.com/).

It also has tools to evaluate and visualize the agent performance.

### Training

For training a new agent use the `train_agent.py` scrip. 
Use `--help` for information on how to use it.

```
python train_agent.py -h

usage: train_agent.py [-h] --name NAME [--config_file CONFIG_FILE]
                      [--output_dir OUTPUT_DIR] [--debug] [--replace]

Q Learning agent that plays the MoveToGoal hard environment.

optional arguments:
  -h, --help            show this help message and exit
  --config_file CONFIG_FILE
                        Configuration file for the experiment. (default: C:\pr
                        ojects\reinforcement_learning_study\agents\deep_q_lear
                        ning\mountain_car\configurations\default.json)
  --output_dir OUTPUT_DIR
                        Where to save the experiments files (default:
                        C:\Users\Fico\rl_experiments\deep_q_learning)
  --debug               Activate to run Tensorflow in eager mode. (default:
                        False)
  --replace             Activate to replace old experiment in the output
                        folder. (default: False)

REQUIRED named arguments:
  --name NAME           The name of this experiment. The experiments files get
                        saved under this name. (default: None)
```

The configurations file is used to set all the hyperparameters for the experiment.
The values in `configurations/default.json` (used by default) worked good for me. 
You can copy this file and try your own hyperparameters.
With this configuration it took almost 2 hs to train on my MSI GeForce RTX 2060 SUPER.

The model is saved in `--output_dir` with the given `--name`.
All training information and the final model are saved here, so it can be easily revisited.

You can [download (3 MB)](https://drive.google.com/uc?export=download&id=1Uzr_S3QVeufs27FSnWARVy9C54mLZUS1)
the model I trained using the default configurations, and try it out yourself.  

### Testing

To test a trained agent use the `test_agent.py` script
Use `--help` for information on how to use it.

```
python test_agent.py -h

usage: test_agent.py [-h] --experiment_dir EXPERIMENT_DIR
                     [--episodes EPISODES] [--render_games]

Test Deep Q Learning agent that plays the MountainCar environment.

optional arguments:
  -h, --help            show this help message and exit
  --episodes EPISODES   The number of episodes to play during testing.
                        (default: 200)
  --render_games        Activate to render the agent playing each episode.
                        (default: False)

REQUIRED named arguments:
  --experiment_dir EXPERIMENT_DIR
                        The path to a trained agent directory. (default: None)
```

### Analysis

The `agent_analysis.py` script is still under development, but for now, 
it plots the Q values predicted by a trained agent for random states.
Use `--help` for information on how to use it.

```
python agent_analysis.py -h

usage: agent_analysis.py [-h] --experiment_dir EXPERIMENT_DIR

Analyse Deep Q Learning agent that plays the MountainCar environment.

optional arguments:
  -h, --help            show this help message and exit

REQUIRED named arguments:
  --experiment_dir EXPERIMENT_DIR
```

This is an example plot from a trained agent:

![q_values](https://i.ibb.co/8rv3QRQ/q-values.png)
![q_values_xy](https://i.ibb.co/tJfKDhz/q-values-xy.png)

If you show the plot using the script, you can rotate it interactively.

The plot shows the best q value for random states of the game.
The different colors indicate witch action has the highest Q value 
for that state (left = red, right = green, null = blue).
