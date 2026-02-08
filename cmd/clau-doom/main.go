package main

import (
	"fmt"
	"os"

	"github.com/sangyi/clau-doom/internal/experiment"
	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "clau-doom",
	Short: "clau-doom: Multi-agent DOOM research orchestrator",
}

var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Print version",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("clau-doom v0.1.0")
	},
}

var statusCmd = &cobra.Command{
	Use:   "status",
	Short: "Show system status",
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Println("clau-doom status")
		fmt.Println("  Version: v0.1.0")
		fmt.Println("  Commands: init, spawn, stop, doe, status, version")
		return nil
	},
}

var initCmd = &cobra.Command{
	Use:   "init",
	Short: "Initialize clau-doom environment",
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Println("Initializing clau-doom environment...")
		dirs := []string{
			"volumes/data",
			"volumes/agents/active",
			"volumes/agents/templates",
			"volumes/opensearch",
		}
		for _, d := range dirs {
			if err := os.MkdirAll(d, 0o755); err != nil {
				return fmt.Errorf("failed to create %s: %w", d, err)
			}
		}
		fmt.Println("Environment initialized.")
		return nil
	},
}

func init() {
	rootCmd.AddCommand(versionCmd, statusCmd, initCmd)
	rootCmd.AddCommand(experiment.NewDOECommand())
}

func main() {
	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}
