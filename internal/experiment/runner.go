package experiment

import (
	"context"
	"fmt"
	"log"
	"time"
)

// Condition represents a DOE experimental condition.
type Condition struct {
	Name         string
	FactorLevels map[string]string
	Episodes     int
	Seeds        []int
}

// RunConfig holds experiment execution configuration.
type RunConfig struct {
	ExperimentID  string
	Conditions    []Condition
	ComposeFile   string
	GlueScriptDir string
}

// DOE001Config returns the standard DOE-001 configuration.
func DOE001Config() *RunConfig {
	seeds := DefaultDOE001Seeds()
	return &RunConfig{
		ExperimentID:  "DOE-001",
		ComposeFile:   "infra/docker-compose.yml",
		GlueScriptDir: "glue",
		Conditions: []Condition{
			{
				Name:     "random",
				Episodes: 70,
				Seeds:    seeds,
				FactorLevels: map[string]string{
					"DECISION_MODE": "random",
				},
			},
			{
				Name:     "rule_only",
				Episodes: 70,
				Seeds:    seeds,
				FactorLevels: map[string]string{
					"DECISION_MODE": "rule_only",
				},
			},
			{
				Name:     "full_agent",
				Episodes: 70,
				Seeds:    seeds,
				FactorLevels: map[string]string{
					"DECISION_MODE": "full_agent",
				},
			},
		},
	}
}

// RunResult holds results from a single condition run.
type RunResult struct {
	Condition        string
	EpisodesPlanned  int
	EpisodesComplete int
	StartTime        time.Time
	EndTime          time.Time
	Error            error
}

// ExperimentResult holds the full experiment outcome.
type ExperimentResult struct {
	ExperimentID string
	Runs         []RunResult
	TotalTime    time.Duration
}

// Runner executes DOE experiments.
type Runner struct {
	config *RunConfig
}

// NewRunner creates an experiment runner.
func NewRunner(config *RunConfig) *Runner {
	return &Runner{config: config}
}

// Run executes all conditions sequentially.
func (r *Runner) Run(ctx context.Context) (*ExperimentResult, error) {
	result := &ExperimentResult{
		ExperimentID: r.config.ExperimentID,
	}
	overallStart := time.Now()

	log.Printf("Starting experiment %s with %d conditions",
		r.config.ExperimentID, len(r.config.Conditions))

	for i, cond := range r.config.Conditions {
		select {
		case <-ctx.Done():
			return result, ctx.Err()
		default:
		}

		log.Printf("\n--- Condition %d/%d: %s (%d episodes) ---",
			i+1, len(r.config.Conditions), cond.Name, cond.Episodes)

		runResult := r.runCondition(ctx, cond)
		result.Runs = append(result.Runs, runResult)

		if runResult.Error != nil {
			log.Printf("ERROR in condition %s: %v", cond.Name, runResult.Error)
		} else {
			log.Printf("Condition %s complete: %d/%d episodes",
				cond.Name, runResult.EpisodesComplete, runResult.EpisodesPlanned)
		}
	}

	result.TotalTime = time.Since(overallStart)
	log.Printf("\nExperiment %s complete in %v", r.config.ExperimentID, result.TotalTime)
	return result, nil
}

// runCondition executes a single experimental condition.
func (r *Runner) runCondition(ctx context.Context, cond Condition) RunResult {
	start := time.Now()
	result := RunResult{
		Condition:       cond.Name,
		EpisodesPlanned: cond.Episodes,
		StartTime:       start,
	}

	// TODO: Implementation phases:
	// 1. Inject factor levels into agent MD template
	// 2. Start/restart VizDoom container with condition config
	// 3. Run episodes via gRPC (Python glue <-> Rust agent-core)
	// 4. Collect results from DuckDB
	// 5. Verify episode count and data integrity

	log.Printf("  Would inject factors: %v", cond.FactorLevels)
	log.Printf("  Would run %d episodes with seeds [%d, %d, ..., %d]",
		cond.Episodes, cond.Seeds[0], cond.Seeds[1], cond.Seeds[len(cond.Seeds)-1])

	result.EpisodesComplete = 0
	result.EndTime = time.Now()
	return result
}

// PrintSummary outputs experiment results.
func (r *ExperimentResult) PrintSummary() {
	fmt.Printf("\n=== Experiment %s Summary ===\n", r.ExperimentID)
	fmt.Printf("Total time: %v\n\n", r.TotalTime)
	fmt.Printf("%-15s %10s %10s %8s %s\n", "Condition", "Planned", "Complete", "Time", "Status")
	fmt.Printf("%-15s %10s %10s %8s %s\n", "─────────", "───────", "────────", "────", "──────")
	for _, run := range r.Runs {
		status := "OK"
		if run.Error != nil {
			status = "FAIL"
		}
		duration := run.EndTime.Sub(run.StartTime)
		fmt.Printf("%-15s %10d %10d %8v %s\n",
			run.Condition, run.EpisodesPlanned, run.EpisodesComplete, duration.Round(time.Second), status)
	}
}
