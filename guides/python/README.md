# Python Reference Guide

Reference documentation for Python development in clau-doom analytics and VizDoom glue.

## Key Resources

- [VizDoom Python API](https://vizdoom.cs.put.edu.pl/api/python/)
- [DuckDB Python API](https://duckdb.org/docs/api/python/overview.html)
- [statsmodels Documentation](https://www.statsmodels.org/stable/)
- [matplotlib](https://matplotlib.org/stable/contents.html)
- [seaborn Statistical Visualization](https://seaborn.pydata.org/)

## clau-doom Context

Python serves two roles in clau-doom:
1. **VizDoom glue** (`glue/vizdoom_bridge.py`): Thin bridge between VizDoom API and Rust agent via shared memory or pipes. Minimal logic.
2. **Analytics** (`analytics/`): Statistical analysis run by research-analyst agent. ANOVA, residual diagnostics, SPC charts, capability analysis.

## statsmodels

### ANOVA with OLS + anova_lm

Two-way ANOVA with interaction effects for DOE factorial analysis.

```python
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm

# Load DOE results from DuckDB
df = pd.read_sql("""
    SELECT r.run_id, r.retreat_threshold, r.ammo_conservation,
           r.exploration_priority, d.kill_rate, d.survival_time
    FROM doe_runs r
    JOIN doe_results d ON r.run_id = d.run_id
    WHERE r.experiment_id = 'EXP-021'
""", conn)

# Fit OLS model with main effects and interactions
model = ols(
    'kill_rate ~ C(retreat_threshold) * C(ammo_conservation) * C(exploration_priority)',
    data=df
).fit()

# Type II ANOVA table (marginal sums of squares)
anova_table = anova_lm(model, typ=2)
print(anova_table)
# Output: Source | sum_sq | df | F | PR(>F)
```

### Regression for RSM (Response Surface)

```python
from statsmodels.formula.api import ols

# Fit second-order response surface model
model = ols(
    'kill_rate ~ retreat + ammo + retreat:ammo + I(retreat**2) + I(ammo**2)',
    data=rsm_data
).fit()

print(model.summary())  # R-squared, coefficients, p-values

# Predict optimal point
import numpy as np
from scipy.optimize import minimize

def neg_response(x):
    return -model.predict(pd.DataFrame({
        'retreat': [x[0]], 'ammo': [x[1]]
    }))[0]

result = minimize(neg_response, x0=[0.35, 0.5], bounds=[(0.2, 0.5), (0.0, 1.0)])
print(f"Optimal: retreat={result.x[0]:.3f}, ammo={result.x[1]:.3f}")
```

### Residual Diagnostics

```python
import matplotlib.pyplot as plt
import scipy.stats as stats
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson

residuals = model.resid
fitted = model.fittedvalues

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# 1. Normal probability plot
stats.probplot(residuals, dist="norm", plot=axes[0, 0])
axes[0, 0].set_title("Normal Probability Plot")

# 2. Residuals vs fitted values (check constant variance)
axes[0, 1].scatter(fitted, residuals, alpha=0.6)
axes[0, 1].axhline(y=0, color='r', linestyle='--')
axes[0, 1].set_xlabel("Fitted Values")
axes[0, 1].set_ylabel("Residuals")
axes[0, 1].set_title("Residuals vs Fitted")

# 3. Histogram of residuals
axes[1, 0].hist(residuals, bins=20, edgecolor='black')
axes[1, 0].set_title("Histogram of Residuals")

# 4. Residuals vs run order (check independence)
axes[1, 1].plot(range(len(residuals)), residuals, marker='o', linestyle='-')
axes[1, 1].axhline(y=0, color='r', linestyle='--')
axes[1, 1].set_xlabel("Run Order")
axes[1, 1].set_ylabel("Residuals")
axes[1, 1].set_title("Residuals vs Run Order")

plt.tight_layout()
plt.savefig("residual_diagnostics.png", dpi=150)

# Anderson-Darling normality test
ad_stat, ad_crit, ad_sig = stats.anderson(residuals, dist='norm')
print(f"Anderson-Darling: stat={ad_stat:.4f}")

# Levene test for equal variance
from scipy.stats import levene
groups = [group['kill_rate'].values for _, group in df.groupby('retreat_threshold')]
lev_stat, lev_p = levene(*groups)
print(f"Levene: stat={lev_stat:.4f}, p={lev_p:.4f}")

# Durbin-Watson for independence
dw = durbin_watson(residuals)
print(f"Durbin-Watson: {dw:.4f}")  # ~2.0 = no autocorrelation
```

## DuckDB Python API

### Connect and Query

```python
import duckdb

# Connect to agent-specific DuckDB file
conn = duckdb.connect("volumes/data/player-007/game.duckdb")

# Direct query returning pandas DataFrame
df = conn.execute("""
    SELECT
        episode_id,
        AVG(kills) as avg_kills,
        AVG(survival_time) as avg_survival,
        STDDEV(kills) as std_kills
    FROM experiments
    WHERE experiment_id = 'EXP-021'
    GROUP BY episode_id
    ORDER BY episode_id
""").fetchdf()

# Insert DOE results
conn.execute("""
    INSERT INTO doe_results (run_id, episode_id, kill_rate, survival_time, damage_taken)
    VALUES (?, ?, ?, ?, ?)
""", [run_id, episode_id, kills, survival, damage])

# Bulk insert from DataFrame
conn.execute("INSERT INTO spc_observations SELECT * FROM df_observations")
```

### Aggregate for SPC

```python
# Compute X-bar and R for control chart
spc_data = conn.execute("""
    SELECT
        generation,
        AVG(kill_rate) as x_bar,
        MAX(kill_rate) - MIN(kill_rate) as r_value,
        COUNT(*) as n
    FROM episode_metrics
    GROUP BY generation
    ORDER BY generation
""").fetchdf()
```

## VizDoom API

### Game Initialization

```python
import vizdoom as vzd

def create_game(config_path: str, seed: int, visible: bool = False) -> vzd.DoomGame:
    game = vzd.DoomGame()
    game.load_config(config_path)
    game.set_seed(seed)

    if not visible:
        game.set_window_visible(False)
        game.set_screen_resolution(vzd.ScreenResolution.RES_320X240)

    game.set_mode(vzd.Mode.PLAYER)
    game.init()
    return game
```

### Action and Observation Space

```python
# Available actions (binary vector)
# [MOVE_FORWARD, MOVE_BACKWARD, MOVE_LEFT, MOVE_RIGHT,
#  TURN_LEFT, TURN_RIGHT, ATTACK, USE]
action = [1, 0, 0, 0, 0, 0, 1, 0]  # Move forward + attack

# Execute action, get reward
reward = game.make_action(action, tics=4)

# Observation
state = game.get_state()
screen_buffer = state.screen_buffer    # numpy array (H, W, C)
depth_buffer = state.depth_buffer      # numpy array (H, W) if enabled
labels_buffer = state.labels_buffer    # numpy array (H, W) semantic labels
game_variables = state.game_variables  # [health, ammo, armor, ...]
```

## matplotlib / seaborn

### SPC Control Chart

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_xbar_r_chart(data, metric_name="kill_rate"):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    generations = data['generation']
    x_bar = data['x_bar']
    r_values = data['r_value']

    x_bar_mean = x_bar.mean()
    r_bar = r_values.mean()
    A2 = 0.577  # for n=5 subgroup size (from control chart constants table)

    ucl_xbar = x_bar_mean + A2 * r_bar
    lcl_xbar = x_bar_mean - A2 * r_bar

    # X-bar chart
    ax1.plot(generations, x_bar, 'b-o', markersize=4)
    ax1.axhline(x_bar_mean, color='green', linestyle='-', label='CL')
    ax1.axhline(ucl_xbar, color='red', linestyle='--', label='UCL')
    ax1.axhline(lcl_xbar, color='red', linestyle='--', label='LCL')
    ax1.set_ylabel(f"X-bar ({metric_name})")
    ax1.set_title(f"X-bar Chart: {metric_name}")
    ax1.legend()

    # R chart
    D3, D4 = 0, 2.114  # for n=5
    ax2.plot(generations, r_values, 'b-o', markersize=4)
    ax2.axhline(r_bar, color='green', linestyle='-', label='CL')
    ax2.axhline(D4 * r_bar, color='red', linestyle='--', label='UCL')
    ax2.axhline(D3 * r_bar, color='red', linestyle='--', label='LCL')
    ax2.set_xlabel("Generation")
    ax2.set_ylabel("Range")
    ax2.set_title("R Chart")
    ax2.legend()

    plt.tight_layout()
    plt.savefig(f"spc_{metric_name}.png", dpi=150)
```

### Effect Plots with seaborn

```python
import seaborn as sns

# Main effect plot
def plot_main_effects(df, factors, response='kill_rate'):
    fig, axes = plt.subplots(1, len(factors), figsize=(5*len(factors), 4))
    for i, factor in enumerate(factors):
        means = df.groupby(factor)[response].mean()
        axes[i].plot(means.index, means.values, 'bo-', markersize=8)
        axes[i].axhline(df[response].mean(), color='gray', linestyle='--')
        axes[i].set_xlabel(factor)
        axes[i].set_ylabel(f"Mean {response}")
        axes[i].set_title(f"Main Effect: {factor}")
    plt.tight_layout()
    plt.savefig("main_effects.png", dpi=150)

# Interaction plot
def plot_interaction(df, factor1, factor2, response='kill_rate'):
    fig, ax = plt.subplots(figsize=(8, 5))
    for level, group in df.groupby(factor2):
        means = group.groupby(factor1)[response].mean()
        ax.plot(means.index, means.values, 'o-', label=f"{factor2}={level}")
    ax.set_xlabel(factor1)
    ax.set_ylabel(f"Mean {response}")
    ax.set_title(f"Interaction: {factor1} x {factor2}")
    ax.legend()
    plt.savefig(f"interaction_{factor1}_{factor2}.png", dpi=150)
```

## Package Dependencies

| Package | Purpose |
|---------|---------|
| `vizdoom` | VizDoom game API |
| `duckdb` | Local database access |
| `statsmodels` | ANOVA, regression, diagnostics |
| `scipy` | Statistical tests (Anderson-Darling, Levene, etc.) |
| `pandas` | Data manipulation |
| `numpy` | Numerical computation |
| `matplotlib` | Plotting |
| `seaborn` | Statistical visualization |
