# VizDoom Reference Guide

Reference documentation for VizDoom integration in clau-doom.

## Key Resources

- [VizDoom GitHub](https://github.com/Farama-Foundation/ViZDoom)
- [VizDoom Python API](https://vizdoom.cs.put.edu.pl/api/python/)
- [VizDoom Scenarios](https://vizdoom.cs.put.edu.pl/scenarios/)
- [Doom Wiki](https://doomwiki.org/)

## clau-doom Context

VizDoom provides the game environment where AI agents compete. The game runs inside Docker containers with Xvfb (virtual framebuffer) for headless operation and noVNC for real-time spectation via browser. Python serves only as a thin glue layer between VizDoom and the Rust agent.

## Game Initialization

### DoomGame Class

```python
import vizdoom as vzd

game = vzd.DoomGame()

# Load scenario configuration
game.load_config("scenarios/basic.cfg")

# Core settings
game.set_doom_scenario_path("scenarios/basic.wad")
game.set_doom_map("map01")
game.set_seed(42)  # Fixed seed for reproducibility (CRITICAL for DOE)

# Display settings
game.set_window_visible(True)         # True for noVNC, False for headless
game.set_screen_resolution(vzd.ScreenResolution.RES_640X480)
game.set_screen_format(vzd.ScreenFormat.RGB24)

# Rendering
game.set_render_hud(True)
game.set_render_weapon(True)
game.set_render_crosshair(True)

# Enable buffers
game.set_depth_buffer_enabled(True)
game.set_labels_buffer_enabled(True)
game.set_automap_buffer_enabled(False)

# Game variables to track
game.add_available_game_variable(vzd.GameVariable.HEALTH)
game.add_available_game_variable(vzd.GameVariable.AMMO2)  # Pistol ammo
game.add_available_game_variable(vzd.GameVariable.AMMO3)  # Shotgun ammo
game.add_available_game_variable(vzd.GameVariable.AMMO4)  # Chaingun ammo
game.add_available_game_variable(vzd.GameVariable.ARMOR)
game.add_available_game_variable(vzd.GameVariable.KILLCOUNT)
game.add_available_game_variable(vzd.GameVariable.DEATHCOUNT)
game.add_available_game_variable(vzd.GameVariable.POSITION_X)
game.add_available_game_variable(vzd.GameVariable.POSITION_Y)
game.add_available_game_variable(vzd.GameVariable.ANGLE)

# Initialize
game.init()
```

## Action Space

### Binary Actions

Each action is a binary flag. Multiple actions can be combined.

```python
# Define available actions
game.add_available_button(vzd.Button.MOVE_FORWARD)    # 0
game.add_available_button(vzd.Button.MOVE_BACKWARD)   # 1
game.add_available_button(vzd.Button.MOVE_LEFT)       # 2
game.add_available_button(vzd.Button.MOVE_RIGHT)      # 3
game.add_available_button(vzd.Button.TURN_LEFT)       # 4
game.add_available_button(vzd.Button.TURN_RIGHT)      # 5
game.add_available_button(vzd.Button.ATTACK)           # 6
game.add_available_button(vzd.Button.USE)              # 7
game.add_available_button(vzd.Button.SELECT_NEXT_WEAPON)  # 8
game.add_available_button(vzd.Button.SELECT_PREV_WEAPON)  # 9

# Execute action: binary vector matching button order
action = [1, 0, 0, 0, 0, 0, 1, 0, 0, 0]  # MOVE_FORWARD + ATTACK

# tics = number of game tics to repeat the action
reward = game.make_action(action, tics=4)
```

### Delta Actions

Continuous-valued actions for fine-grained control (used for mouse-like turning).

```python
game.add_available_button(vzd.Button.TURN_LEFT_RIGHT_DELTA)

# Positive = turn right, negative = turn left
action = [0] * len(buttons)
action[turn_delta_index] = 15.0  # Turn right 15 degrees
```

### Common Action Combinations

```python
# Move forward while strafing left
STRAFE_LEFT_FORWARD = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0]

# Attack while retreating
RETREAT_ATTACK = [0, 1, 0, 0, 0, 0, 1, 0, 0, 0]

# Circle strafe right (move right + turn left)
CIRCLE_STRAFE = [0, 0, 0, 1, 1, 0, 1, 0, 0, 0]

# No action (wait/idle)
IDLE = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

## Observation Space

### Screen Buffer

```python
state = game.get_state()

# RGB pixel buffer: numpy array shape (H, W, 3)
screen = state.screen_buffer  # dtype: uint8, range [0, 255]

# Access as image for processing
# screen[y, x, channel] where channel: 0=R, 1=G, 2=B
```

### Depth Buffer

```python
# Distance from camera to each pixel (float32)
depth = state.depth_buffer  # shape (H, W), dtype: float32

# Useful for: enemy distance estimation, obstacle detection
# Values represent distance in game units
```

### Labels Buffer

```python
# Semantic segmentation: each pixel labeled with object ID
labels = state.labels_buffer  # shape (H, W), dtype: uint8

# Object labels available
for label in state.labels:
    print(f"ID={label.object_id}, Name={label.object_name}, "
          f"Value={label.value}, "
          f"X={label.object_position_x}, Y={label.object_position_y}, "
          f"Width={label.width}, Height={label.height}")

# Label values correspond to DoomFixedToFloat IDs:
# Common: 0=nothing, 255=wall, specific IDs for monsters/items
```

### Game Variables

```python
# Numeric game state variables (defined during setup)
variables = state.game_variables

health = variables[0]      # HEALTH
ammo_pistol = variables[1] # AMMO2
ammo_shotgun = variables[2] # AMMO3
ammo_chain = variables[3]  # AMMO4
armor = variables[4]       # ARMOR
kills = variables[5]       # KILLCOUNT
deaths = variables[6]      # DEATHCOUNT
pos_x = variables[7]       # POSITION_X
pos_y = variables[8]       # POSITION_Y
angle = variables[9]       # ANGLE
```

## Scenario Configuration (.cfg Files)

### Basic Configuration

```ini
# scenarios/clau-doom-basic.cfg

# Doom engine settings
doom_scenario_path = basic.wad
doom_map = map01

# Episode settings
episode_timeout = 2100        # 60 seconds at 35 tics/sec
episode_start_time = 14       # Skip initial tics

# Reward shaping
living_reward = -0.001        # Small penalty per tic (encourages action)
death_penalty = 1.0

# Render settings
screen_resolution = RES_640X480
screen_format = RGB24
render_hud = true
render_weapon = true

# Available buttons
available_buttons = {
    MOVE_FORWARD MOVE_BACKWARD MOVE_LEFT MOVE_RIGHT
    TURN_LEFT TURN_RIGHT ATTACK USE
    SELECT_NEXT_WEAPON SELECT_PREV_WEAPON
}

# Available game variables
available_game_variables = {
    HEALTH AMMO2 AMMO3 AMMO4 ARMOR
    KILLCOUNT DEATHCOUNT
    POSITION_X POSITION_Y ANGLE
}

# Mode
mode = PLAYER
```

### Custom Scenarios

```ini
# scenarios/multi-enemy-corridor.cfg
doom_scenario_path = multi_enemy.wad
doom_map = map01
episode_timeout = 4200        # 120 seconds
living_reward = -0.0005
death_penalty = 2.0

# Custom reward via game variable tracking
# (actual reward shaping done in Python/Rust glue)
```

## Headless Mode with Xvfb

For running inside Docker containers without a physical display.

```bash
# Start virtual framebuffer
Xvfb :99 -screen 0 640x480x24 &
export DISPLAY=:99

# Run VizDoom with window visible (rendered to virtual display)
python vizdoom_bridge.py --visible
```

### Docker Entrypoint

```bash
#!/bin/bash
# entrypoint.sh for doom-player container

# Start Xvfb
Xvfb :99 -screen 0 ${RESOLUTION:-640x480}x24 -ac &
export DISPLAY=:99

# Start x11vnc for noVNC access
x11vnc -display :99 -nopw -listen 0.0.0.0 -xkb -ncache 10 -forever &

# Start noVNC (WebSocket proxy)
/opt/noVNC/utils/novnc_proxy --vnc localhost:5900 --listen ${NOVNC_PORT:-6901} &

# Start the agent (Rust binary communicates with VizDoom via glue)
exec /app/agent-core --config /agent/config.md
```

## noVNC Streaming Setup

### Architecture

```
VizDoom (renders to Xvfb :99)
    |
    v
x11vnc (captures Xvfb, serves VNC on :5900)
    |
    v
noVNC proxy (WebSocket bridge: ws://container:6901/websockify)
    |
    v
Browser (noVNC JavaScript client connects via WebSocket)
```

### Container Port Mapping

```yaml
# docker-compose.yml
doom-player-001:
  ports:
    - "6901:6901"   # noVNC WebSocket
  environment:
    - DISPLAY=:99
    - NOVNC_PORT=6901
```

### Multiple Players

Each player container gets a unique noVNC port:

```
Player_001: ws://localhost:6901/websockify
Player_002: ws://localhost:6902/websockify
Player_003: ws://localhost:6903/websockify
...
```

Dashboard embeds multiple noVNC clients in a grid layout.

## Reward Shaping

### Default Rewards

```python
# VizDoom built-in rewards
reward = game.make_action(action)
# Includes: living_reward (per tic) + death_penalty + kill_reward
```

### Custom Reward Function

```python
def compute_reward(prev_vars, curr_vars, killed):
    reward = 0.0

    # Kill reward
    kill_diff = curr_vars['kills'] - prev_vars['kills']
    reward += kill_diff * 10.0

    # Health management
    health_diff = curr_vars['health'] - prev_vars['health']
    if health_diff < 0:
        reward += health_diff * 0.1  # Penalty for taking damage

    # Ammo efficiency
    ammo_diff = curr_vars['total_ammo'] - prev_vars['total_ammo']
    if ammo_diff < 0 and kill_diff == 0:
        reward -= 0.5  # Penalty for wasting ammo

    # Exploration (position change)
    dist = distance(prev_vars['pos'], curr_vars['pos'])
    reward += dist * 0.01  # Small reward for movement

    return reward
```

## Python API Examples

### Game Loop

```python
def run_episode(game, agent, seed):
    game.set_seed(seed)
    game.new_episode()

    total_reward = 0
    step = 0

    while not game.is_episode_finished():
        state = game.get_state()

        # Extract features for Rust agent
        features = extract_features(state)

        # Get action from Rust agent (via shared memory or pipe)
        action = agent.decide(features)

        # Execute
        reward = game.make_action(action, tics=4)
        total_reward += reward
        step += 1

    # Episode summary
    return {
        'total_reward': total_reward,
        'kills': game.get_game_variable(vzd.GameVariable.KILLCOUNT),
        'survival_time': step * 4,  # tics
        'seed': seed,
    }
```

### Batch Episodes for DOE Run

```python
def run_doe_episodes(game, agent, seeds, episodes_per_seed):
    results = []
    for seed in seeds:
        for rep in range(episodes_per_seed):
            result = run_episode(game, agent, seed)
            result['replicate'] = rep
            results.append(result)
    return results
```

## Feature Extraction for Rust Agent

The Python glue extracts compact features from VizDoom state and passes them to the Rust decision engine.

```python
import numpy as np

def extract_features(state):
    """Extract compact feature vector for Rust agent decision engine."""
    vars = state.game_variables
    labels = state.labels

    # Basic state
    health = vars[0] / 100.0  # Normalize to [0, 1]
    total_ammo = (vars[1] + vars[2] + vars[3]) / 200.0

    # Enemy detection from labels
    enemies = [l for l in labels if l.object_name in ENEMY_NAMES]
    enemy_count = len(enemies)
    nearest_enemy_dist = min((e.object_position_x for e in enemies), default=float('inf'))

    # Area classification
    depth = state.depth_buffer
    avg_depth = np.mean(depth)
    depth_std = np.std(depth)
    is_corridor = depth_std > CORRIDOR_THRESHOLD

    return {
        'health': health,
        'ammo': total_ammo,
        'enemy_count': enemy_count,
        'nearest_enemy_dist': nearest_enemy_dist,
        'is_corridor': is_corridor,
        'position': (vars[7], vars[8]),
        'angle': vars[9],
    }
```

## Performance Considerations

| Operation | Budget | Notes |
|-----------|--------|-------|
| VizDoom frame render | ~5ms | Screen + depth + labels |
| Feature extraction | ~2ms | Python numpy ops |
| Rust decision | ~5ms | Level 0 rule matching |
| OpenSearch kNN | ~20ms | Level 2 fallback |
| Total per tick | < 35ms | Must fit in one game tic (28.6ms at 35fps) |

For 35 fps gameplay, the total decision pipeline must complete within one game tic. Use `tics=4` skip to allow ~114ms budget when needed.
