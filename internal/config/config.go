package config

// Config holds global clau-doom configuration.
type Config struct {
	ComposeFile    string
	DataDir        string
	AgentTemplates string
	OpenSearchURL  string
	DuckDBPath     string
}

// DefaultConfig returns the standard configuration.
func DefaultConfig() *Config {
	return &Config{
		ComposeFile:    "infra/docker-compose.yml",
		DataDir:        "volumes/data",
		AgentTemplates: "volumes/agents/templates",
		OpenSearchURL:  "http://localhost:9200",
		DuckDBPath:     "volumes/data/clau-doom.duckdb",
	}
}
