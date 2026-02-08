package experiment

import (
	"context"
	"fmt"
	"log"

	"github.com/spf13/cobra"
)

var episodesPerCondition int

// NewDOECommand creates the 'doe' command group.
func NewDOECommand() *cobra.Command {
	doeCmd := &cobra.Command{
		Use:   "doe",
		Short: "DOE experiment management",
	}

	runCmd := &cobra.Command{
		Use:   "run [experiment-id]",
		Short: "Run a DOE experiment",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			expID := args[0]
			return runDOE(expID)
		},
	}
	runCmd.Flags().IntVar(&episodesPerCondition, "episodes-per-condition", 70,
		"Number of episodes per condition")

	statusCmd := &cobra.Command{
		Use:   "status [experiment-id]",
		Short: "Check experiment status",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Printf("Experiment %s: status check not yet implemented\n", args[0])
			return nil
		},
	}

	listCmd := &cobra.Command{
		Use:   "list",
		Short: "List available experiments",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Println("Available experiments:")
			fmt.Println("  DOE-001  OFAT Baseline Comparison (Random vs Rule-Only vs Full RAG)")
			return nil
		},
	}

	doeCmd.AddCommand(runCmd, statusCmd, listCmd)
	return doeCmd
}

func runDOE(expID string) error {
	switch expID {
	case "DOE-001":
		return runDOE001()
	default:
		return fmt.Errorf("unknown experiment: %s", expID)
	}
}

func runDOE001() error {
	log.Println("=== DOE-001: OFAT Baseline Comparison ===")
	log.Println("Conditions: Random, Rule-Only, Full RAG")
	log.Printf("Episodes per condition: %d\n", episodesPerCondition)
	log.Printf("Total episodes: %d\n", episodesPerCondition*3)

	config := DOE001Config()
	if episodesPerCondition != 70 {
		for i := range config.Conditions {
			config.Conditions[i].Episodes = episodesPerCondition
			config.Conditions[i].Seeds = GenerateSeedSet(42, 31, episodesPerCondition)
		}
	}

	seeds := config.Conditions[0].Seeds
	log.Printf("Seed set (n=%d): [%d, %d, ..., %d]",
		len(seeds), seeds[0], seeds[1], seeds[len(seeds)-1])
	log.Printf("Formula: seed_i = 42 + i * 31")

	runner := NewRunner(config)
	result, err := runner.Run(context.Background())
	if err != nil {
		return fmt.Errorf("experiment failed: %w", err)
	}

	result.PrintSummary()
	return nil
}
