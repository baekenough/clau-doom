---
name: python-best-practices
description: Python patterns for VizDoom game glue, statistical analytics with statsmodels ANOVA, and DuckDB data processing
user-invocable: false
---

# Python Best Practices for clau-doom Analytics and VizDoom

## statsmodels: ANOVA and Regression

### One-Way ANOVA

```python
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm

def run_one_way_anova(df: pd.DataFrame, response: str, factor: str) -> pd.DataFrame:
    """Run one-way ANOVA on experiment data.

    Args:
        df: DataFrame with columns for response variable and factor.
        response: Name of the response variable column (e.g., 'fitness_score').
        factor: Name of the factor column (e.g., 'rag_strategy').

    Returns:
        ANOVA table as DataFrame.
    """
    formula = f"{response} ~ C({factor})"
    model = ols(formula, data=df).fit()
    anova_table = anova_lm(model, typ=2)
    return anova_table
```

### Two-Way ANOVA with Interaction

```python
def run_two_way_anova(
    df: pd.DataFrame,
    response: str,
    factor_a: str,
    factor_b: str,
) -> pd.DataFrame:
    """Run two-way ANOVA with interaction term.

    Example: fitness_score ~ C(rag_strategy) * C(mutation_rate)
    """
    formula = f"{response} ~ C({factor_a}) * C({factor_b})"
    model = ols(formula, data=df).fit()
    anova_table = anova_lm(model, typ=2)
    return anova_table
```

### Regression Diagnostics

```python
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson

def check_assumptions(model) -> dict:
    """Check ANOVA/regression assumptions."""
    residuals = model.resid
    fitted = model.fittedvalues

    # Normality (Shapiro-Wilk)
    from scipy.stats import shapiro
    stat, p_normality = shapiro(residuals)

    # Homoscedasticity (Breusch-Pagan)
    bp_stat, bp_p, _, _ = het_breuschpagan(residuals, model.model.exog)

    # Independence (Durbin-Watson)
    dw_stat = durbin_watson(residuals)

    return {
        "normality_p": p_normality,
        "normality_ok": p_normality > 0.05,
        "homoscedasticity_p": bp_p,
        "homoscedasticity_ok": bp_p > 0.05,
        "durbin_watson": dw_stat,
        "independence_ok": 1.5 < dw_stat < 2.5,
    }
```

### Post-hoc Tukey HSD

```python
from statsmodels.stats.multicomp import pairwise_tukeyhsd

def run_tukey_hsd(df: pd.DataFrame, response: str, factor: str) -> pd.DataFrame:
    """Run Tukey HSD post-hoc test after significant ANOVA."""
    result = pairwise_tukeyhsd(
        endog=df[response],
        groups=df[factor],
        alpha=0.05,
    )
    return pd.DataFrame(
        data=result._results_table.data[1:],
        columns=result._results_table.data[0],
    )
```

## DuckDB: Data Processing

### Python API

```python
import duckdb

def create_experiment_db(db_path: str) -> duckdb.DuckDBPyConnection:
    """Initialize DuckDB for experiment data storage."""
    conn = duckdb.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS generations (
            experiment_id VARCHAR,
            generation_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            population_size INTEGER,
            avg_fitness DOUBLE,
            max_fitness DOUBLE,
            min_fitness DOUBLE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_scores (
            experiment_id VARCHAR,
            generation_id INTEGER,
            agent_id VARCHAR,
            kills INTEGER,
            deaths INTEGER,
            health_remaining DOUBLE,
            ammo_efficiency DOUBLE,
            exploration_coverage DOUBLE,
            fitness_score DOUBLE,
            rag_strategy VARCHAR,
            mutation_rate DOUBLE
        )
    """)
    return conn
```

### SQL Queries with DataFrame Integration

```python
def get_generation_summary(conn: duckdb.DuckDBPyConnection, experiment_id: str) -> pd.DataFrame:
    """Get per-generation summary statistics."""
    return conn.execute("""
        SELECT
            generation_id,
            COUNT(*) as n_agents,
            AVG(fitness_score) as mean_fitness,
            STDDEV(fitness_score) as std_fitness,
            MAX(fitness_score) as best_fitness,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fitness_score) as median_fitness
        FROM agent_scores
        WHERE experiment_id = ?
        GROUP BY generation_id
        ORDER BY generation_id
    """, [experiment_id]).fetchdf()


def get_anova_data(
    conn: duckdb.DuckDBPyConnection,
    experiment_id: str,
    factors: list[str],
) -> pd.DataFrame:
    """Extract data formatted for ANOVA analysis."""
    factor_cols = ", ".join(factors)
    return conn.execute(f"""
        SELECT {factor_cols}, fitness_score
        FROM agent_scores
        WHERE experiment_id = ?
        AND generation_id = (
            SELECT MAX(generation_id)
            FROM agent_scores
            WHERE experiment_id = ?
        )
    """, [experiment_id, experiment_id]).fetchdf()
```

### Bulk Insert from Game Results

```python
def insert_generation_results(
    conn: duckdb.DuckDBPyConnection,
    results: list[dict],
) -> None:
    """Bulk insert a generation's worth of agent scores."""
    df = pd.DataFrame(results)
    conn.execute("""
        INSERT INTO agent_scores
        SELECT * FROM df
    """)
```

## VizDoom: Game Setup and Control

### Game Configuration

```python
import vizdoom as vzd

def create_game(
    config_path: str,
    scenario_path: str,
    headless: bool = True,
    resolution: tuple[int, int] = (320, 240),
) -> vzd.DoomGame:
    """Create and configure a VizDoom game instance."""
    game = vzd.DoomGame()
    game.load_config(config_path)
    game.set_doom_scenario_path(scenario_path)

    # Display
    if headless:
        game.set_window_visible(False)
        game.set_screen_resolution(vzd.ScreenResolution.RES_320X240)
    else:
        game.set_window_visible(True)
        game.set_screen_resolution(vzd.ScreenResolution.RES_640X480)

    game.set_screen_format(vzd.ScreenFormat.RGB24)

    # Game variables to track
    game.add_available_game_variable(vzd.GameVariable.HEALTH)
    game.add_available_game_variable(vzd.GameVariable.AMMO2)
    game.add_available_game_variable(vzd.GameVariable.KILLCOUNT)
    game.add_available_game_variable(vzd.GameVariable.DEATHCOUNT)

    game.set_episode_timeout(2100)  # 60 seconds at 35 fps
    game.set_episode_start_time(10)

    return game
```

### Action Space

```python
from dataclasses import dataclass

@dataclass
class ActionSpace:
    """Define available actions for agents."""
    MOVE_FORWARD = [1, 0, 0, 0, 0, 0]
    MOVE_BACKWARD = [0, 1, 0, 0, 0, 0]
    TURN_LEFT = [0, 0, 1, 0, 0, 0]
    TURN_RIGHT = [0, 0, 0, 1, 0, 0]
    ATTACK = [0, 0, 0, 0, 1, 0]
    USE = [0, 0, 0, 0, 0, 1]
    MOVE_LEFT = [1, 0, 1, 0, 0, 0]
    MOVE_RIGHT = [1, 0, 0, 1, 0, 0]
    ATTACK_FORWARD = [1, 0, 0, 0, 1, 0]

    @classmethod
    def all_actions(cls) -> list[list[int]]:
        return [
            cls.MOVE_FORWARD, cls.MOVE_BACKWARD,
            cls.TURN_LEFT, cls.TURN_RIGHT,
            cls.ATTACK, cls.USE,
            cls.MOVE_LEFT, cls.MOVE_RIGHT,
            cls.ATTACK_FORWARD,
        ]
```

### Game Loop with Observation Extraction

```python
import numpy as np

def run_episode(
    game: vzd.DoomGame,
    agent_callback,
    max_steps: int = 2100,
) -> dict:
    """Run a single episode and collect metrics."""
    game.new_episode()
    step = 0
    total_reward = 0.0

    while not game.is_episode_finished() and step < max_steps:
        state = game.get_state()
        screen_buf = state.screen_buffer  # np.ndarray (H, W, 3)
        game_vars = state.game_variables  # [health, ammo, kills, deaths]

        observation = {
            "screen": screen_buf,
            "health": game_vars[0],
            "ammo": game_vars[1],
            "kills": game_vars[2],
            "deaths": game_vars[3],
            "step": step,
        }

        action = agent_callback(observation)
        reward = game.make_action(action)
        total_reward += reward
        step += 1

    return {
        "total_reward": total_reward,
        "steps": step,
        "kills": int(game.get_game_variable(vzd.GameVariable.KILLCOUNT)),
        "deaths": int(game.get_game_variable(vzd.GameVariable.DEATHCOUNT)),
        "health_remaining": max(0, game.get_game_variable(vzd.GameVariable.HEALTH)),
    }
```

### Headless Mode for Batch Evaluation

```python
def batch_evaluate(
    scenario_path: str,
    agents: list,
    episodes_per_agent: int = 5,
) -> list[dict]:
    """Evaluate multiple agents in headless mode."""
    game = create_game(
        config_path="scenarios/basic.cfg",
        scenario_path=scenario_path,
        headless=True,
    )
    game.init()

    results = []
    for agent in agents:
        agent_results = []
        for _ in range(episodes_per_agent):
            result = run_episode(game, agent.get_action)
            agent_results.append(result)

        avg_result = {
            "agent_id": agent.id,
            "avg_kills": np.mean([r["kills"] for r in agent_results]),
            "avg_deaths": np.mean([r["deaths"] for r in agent_results]),
            "avg_reward": np.mean([r["total_reward"] for r in agent_results]),
            "avg_health": np.mean([r["health_remaining"] for r in agent_results]),
        }
        results.append(avg_result)

    game.close()
    return results
```

## Visualization with matplotlib/seaborn

### ANOVA Results Plot

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_anova_results(df: pd.DataFrame, response: str, factor: str, output_path: str) -> None:
    """Create box plot with individual points for ANOVA visualization."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Box plot with swarm
    sns.boxplot(data=df, x=factor, y=response, ax=axes[0])
    sns.swarmplot(data=df, x=factor, y=response, color="0.25", size=3, ax=axes[0])
    axes[0].set_title(f"{response} by {factor}")

    # Means with CI
    sns.pointplot(data=df, x=factor, y=response, ci=95, join=True, ax=axes[1])
    axes[1].set_title(f"Mean {response} with 95% CI")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
```

### Residual Diagnostic Plot

```python
def plot_residuals(model, output_path: str) -> None:
    """Create residual diagnostic plots for ANOVA model."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    residuals = model.resid
    fitted = model.fittedvalues

    # Residuals vs Fitted
    axes[0, 0].scatter(fitted, residuals, alpha=0.5)
    axes[0, 0].axhline(y=0, color="r", linestyle="--")
    axes[0, 0].set_xlabel("Fitted values")
    axes[0, 0].set_ylabel("Residuals")
    axes[0, 0].set_title("Residuals vs Fitted")

    # Q-Q Plot
    from statsmodels.graphics.gofplots import qqplot
    qqplot(residuals, line="45", ax=axes[0, 1])
    axes[0, 1].set_title("Normal Q-Q")

    # Scale-Location
    axes[1, 0].scatter(fitted, np.sqrt(np.abs(residuals)), alpha=0.5)
    axes[1, 0].set_xlabel("Fitted values")
    axes[1, 0].set_ylabel("sqrt(|Residuals|)")
    axes[1, 0].set_title("Scale-Location")

    # Histogram of residuals
    axes[1, 1].hist(residuals, bins=30, edgecolor="black")
    axes[1, 1].set_title("Residual Distribution")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
```

### Fitness Evolution Plot

```python
def plot_fitness_evolution(gen_summary: pd.DataFrame, output_path: str) -> None:
    """Plot fitness trends across generations."""
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(gen_summary["generation_id"], gen_summary["mean_fitness"], label="Mean", linewidth=2)
    ax.fill_between(
        gen_summary["generation_id"],
        gen_summary["mean_fitness"] - gen_summary["std_fitness"],
        gen_summary["mean_fitness"] + gen_summary["std_fitness"],
        alpha=0.2,
        label="Mean +/- 1 SD",
    )
    ax.plot(gen_summary["generation_id"], gen_summary["best_fitness"],
            label="Best", linestyle="--", linewidth=1)
    ax.plot(gen_summary["generation_id"], gen_summary["median_fitness"],
            label="Median", linestyle=":", linewidth=1)

    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness Score")
    ax.set_title("Fitness Evolution Across Generations")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
```

## Type Hints

```python
from typing import Protocol, TypeVar
from collections.abc import Callable

class AgentProtocol(Protocol):
    """Protocol for agent implementations."""
    id: str

    def get_action(self, observation: dict) -> list[int]: ...
    def update(self, reward: float) -> None: ...

T = TypeVar("T")

def top_k_agents(agents: list[T], scores: dict[str, float], k: int) -> list[T]:
    """Select top-k agents by fitness score."""
    return sorted(agents, key=lambda a: scores.get(a.id, 0.0), reverse=True)[:k]
```

## Virtual Environments

```bash
# Create and activate
python -m venv .venv
source .venv/bin/activate

# Requirements
pip install -r requirements.txt
```

### requirements.txt Structure

```
# Core analytics
statsmodels>=0.14
duckdb>=1.1
pandas>=2.2
numpy>=2.0

# Visualization
matplotlib>=3.9
seaborn>=0.13

# VizDoom
vizdoom>=1.2

# Code quality
ruff>=0.8
mypy>=1.13
```

## Code Style

- Follow PEP 8
- Use ruff for linting and formatting
- Use mypy for type checking in strict mode
- Docstrings: Google style
- Line length: 100 characters
