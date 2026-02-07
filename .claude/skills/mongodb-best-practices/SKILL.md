---
name: mongodb-best-practices
description: Go and Python MongoDB driver patterns for knowledge catalog schema, aggregation pipelines, trust score indexing, and document lifecycle management
user-invocable: false
---

# MongoDB Best Practices for clau-doom Knowledge Store

## Knowledge Catalog Schema Design

### Core Collections

```javascript
// strategy_documents collection
{
  _id: ObjectId("..."),
  document_id: "strat-001",  // unique identifier
  agent_id: "agent-A",
  generation: 42,
  experiment_id: "DOE-042",

  // Content
  title: "High-aggression corridor navigation",
  content: "When entering narrow corridors with health > 70%...",
  tags: ["combat", "navigation", "aggressive"],
  category: "tactical",

  // Quality metrics
  trust_score: 0.85,  // 0.0-1.0, based on validation runs
  run_count: 120,     // number of episodes using this strategy
  win_rate: 0.78,     // success rate when applied
  avg_score: 245.6,   // average score achieved
  variance: 12.3,     // consistency metric

  // Lifecycle
  status: "ACTIVE",   // DRAFT | ACTIVE | DEPRECATED | RETIRED
  created_at: ISODate("2024-12-15T10:30:00Z"),
  updated_at: ISODate("2024-12-20T14:22:00Z"),
  deprecated_at: null,
  retired_at: null,

  // Versioning
  version: 3,
  parent_id: "strat-001-v2",  // previous version

  // RAG metadata
  embedding: [0.123, -0.456, ...],  // 768-dim vector for kNN
  embedding_model: "ollama/all-minilm",

  // Attribution
  discovered_by: "evolution-gen-42",
  refined_count: 2,
  contributors: ["research-pi", "research-analyst"]
}
```

```javascript
// agent_configs collection
{
  _id: ObjectId("..."),
  agent_id: "agent-A",
  generation: 42,
  experiment_id: "DOE-042",

  // Genome parameters (from AGENT.md)
  genome: {
    memory: 0.82,
    strength: 0.68,
    curiosity: 0.45,
    aggression: 0.71,
    health_threshold: 0.60,
    weapon_preference: "shotgun",
    retreat_distance: 150.0
  },

  // Performance
  fitness: 0.87,
  total_kills: 342,
  total_deaths: 45,
  avg_survival_time: 180.5,
  episodes_played: 150,

  // Strategy usage
  loaded_strategies: ["strat-001", "strat-023", "strat-045"],
  strategy_hit_rate: 0.65,  // % of decisions using RAG

  // Lifecycle
  status: "ACTIVE",
  created_at: ISODate("2024-12-15T10:00:00Z"),
  promoted_to_next_gen: true,

  // Metadata
  parent_genome_ids: ["agent-A-gen41", "agent-B-gen41"],  // crossover
  mutation_applied: true
}
```

```javascript
// experiment_results collection
{
  _id: ObjectId("..."),
  experiment_id: "DOE-042",
  run_id: 5,
  agent_id: "agent-A",

  // Experimental factors (from DOE design)
  factors: {
    memory: 0.7,
    strength: 0.5
  },

  // Response variables
  responses: {
    kill_efficiency: 42.3,
    survival_time: 180.5,
    damage_dealt: 1234.5,
    damage_taken: 234.5,
    ammo_efficiency: 0.78
  },

  // Episode-level data reference
  duckdb_table: "experiment_042_episodes",
  episode_count: 30,

  // Seed integrity
  seed_set: [42, 1337, 2023, 7890, 9999, ...],
  seed_hash: "sha256:abc123...",

  // Quality
  data_complete: true,
  outliers_removed: 3,
  diagnostics_passed: true,

  // Timestamps
  started_at: ISODate("2024-12-15T10:00:00Z"),
  completed_at: ISODate("2024-12-15T10:45:00Z")
}
```

### Schema Versioning

```javascript
// schema_versions collection
{
  _id: ObjectId("..."),
  collection_name: "strategy_documents",
  version: 3,
  schema: {
    // JSON Schema definition
    bsonType: "object",
    required: ["document_id", "agent_id", "trust_score", "status"],
    properties: {
      document_id: { bsonType: "string" },
      trust_score: { bsonType: "double", minimum: 0.0, maximum: 1.0 },
      status: { enum: ["DRAFT", "ACTIVE", "DEPRECATED", "RETIRED"] }
    }
  },
  applied_at: ISODate("2024-12-15T09:00:00Z"),
  migration_script: "migrations/003_add_embedding_model.js"
}
```

## Go mongo-driver Patterns

### Connection & Client Management

```go
package mongodb

import (
    "context"
    "fmt"
    "sync"
    "time"

    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
    "go.mongodb.org/mongo-driver/mongo/readpref"
)

var (
    client     *mongo.Client
    clientOnce sync.Once
    clientErr  error
)

// GetClient returns a singleton MongoDB client
func GetClient(ctx context.Context, uri string) (*mongo.Client, error) {
    clientOnce.Do(func() {
        clientOpts := options.Client().
            ApplyURI(uri).
            SetMaxPoolSize(50).
            SetMinPoolSize(10).
            SetMaxConnIdleTime(30 * time.Second).
            SetRetryWrites(true).
            SetWriteConcern(writeconcern.New(writeconcern.WMajority())).
            SetReadPreference(readpref.Primary())

        ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
        defer cancel()

        client, clientErr = mongo.Connect(ctx, clientOpts)
        if clientErr != nil {
            return
        }

        // Verify connection
        clientErr = client.Ping(ctx, readpref.Primary())
    })

    return client, clientErr
}

// Disconnect gracefully closes the MongoDB client
func Disconnect(ctx context.Context) error {
    if client == nil {
        return nil
    }
    return client.Disconnect(ctx)
}
```

### Repository Pattern

```go
package repository

import (
    "context"
    "fmt"
    "time"

    "go.mongodb.org/mongo-driver/bson"
    "go.mongodb.org/mongo-driver/bson/primitive"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
)

type StrategyDocumentRepository interface {
    Create(ctx context.Context, doc *StrategyDocument) error
    GetByID(ctx context.Context, id string) (*StrategyDocument, error)
    FindByAgent(ctx context.Context, agentID string, limit int) ([]*StrategyDocument, error)
    UpdateTrustScore(ctx context.Context, id string, newScore float64) error
    Deprecate(ctx context.Context, id string) error
    ListActive(ctx context.Context, offset, limit int) ([]*StrategyDocument, error)
}

type strategyDocRepo struct {
    collection *mongo.Collection
}

func NewStrategyDocumentRepository(db *mongo.Database) StrategyDocumentRepository {
    return &strategyDocRepo{
        collection: db.Collection("strategy_documents"),
    }
}

type StrategyDocument struct {
    ID          primitive.ObjectID `bson:"_id,omitempty"`
    DocumentID  string             `bson:"document_id"`
    AgentID     string             `bson:"agent_id"`
    Generation  int                `bson:"generation"`
    Title       string             `bson:"title"`
    Content     string             `bson:"content"`
    Tags        []string           `bson:"tags"`
    Category    string             `bson:"category"`
    TrustScore  float64            `bson:"trust_score"`
    RunCount    int                `bson:"run_count"`
    WinRate     float64            `bson:"win_rate"`
    Status      string             `bson:"status"`
    CreatedAt   time.Time          `bson:"created_at"`
    UpdatedAt   time.Time          `bson:"updated_at"`
    Embedding   []float32          `bson:"embedding,omitempty"`
}

func (r *strategyDocRepo) Create(ctx context.Context, doc *StrategyDocument) error {
    doc.ID = primitive.NewObjectID()
    doc.CreatedAt = time.Now()
    doc.UpdatedAt = time.Now()

    _, err := r.collection.InsertOne(ctx, doc)
    if err != nil {
        return fmt.Errorf("inserting strategy document: %w", err)
    }
    return nil
}

func (r *strategyDocRepo) GetByID(ctx context.Context, id string) (*StrategyDocument, error) {
    filter := bson.M{"document_id": id}

    var doc StrategyDocument
    err := r.collection.FindOne(ctx, filter).Decode(&doc)
    if err == mongo.ErrNoDocuments {
        return nil, fmt.Errorf("strategy document %s not found", id)
    }
    if err != nil {
        return nil, fmt.Errorf("finding strategy document: %w", err)
    }

    return &doc, nil
}

func (r *strategyDocRepo) FindByAgent(ctx context.Context, agentID string, limit int) ([]*StrategyDocument, error) {
    filter := bson.M{
        "agent_id": agentID,
        "status":   "ACTIVE",
    }
    opts := options.Find().
        SetSort(bson.D{{Key: "trust_score", Value: -1}}).
        SetLimit(int64(limit))

    cursor, err := r.collection.Find(ctx, filter, opts)
    if err != nil {
        return nil, fmt.Errorf("finding agent strategies: %w", err)
    }
    defer cursor.Close(ctx)

    var docs []*StrategyDocument
    if err := cursor.All(ctx, &docs); err != nil {
        return nil, fmt.Errorf("decoding strategies: %w", err)
    }

    return docs, nil
}

func (r *strategyDocRepo) UpdateTrustScore(ctx context.Context, id string, newScore float64) error {
    filter := bson.M{"document_id": id}
    update := bson.M{
        "$set": bson.M{
            "trust_score": newScore,
            "updated_at":  time.Now(),
        },
    }

    result, err := r.collection.UpdateOne(ctx, filter, update)
    if err != nil {
        return fmt.Errorf("updating trust score: %w", err)
    }
    if result.MatchedCount == 0 {
        return fmt.Errorf("strategy document %s not found", id)
    }

    return nil
}

func (r *strategyDocRepo) ListActive(ctx context.Context, offset, limit int) ([]*StrategyDocument, error) {
    filter := bson.M{"status": "ACTIVE"}
    opts := options.Find().
        SetSkip(int64(offset)).
        SetLimit(int64(limit)).
        SetSort(bson.D{{Key: "trust_score", Value: -1}})

    cursor, err := r.collection.Find(ctx, filter, opts)
    if err != nil {
        return nil, fmt.Errorf("listing active strategies: %w", err)
    }
    defer cursor.Close(ctx)

    var docs []*StrategyDocument
    if err := cursor.All(ctx, &docs); err != nil {
        return nil, fmt.Errorf("decoding strategies: %w", err)
    }

    return docs, nil
}
```

### Aggregation Pipelines

```go
package aggregation

import (
    "context"
    "fmt"

    "go.mongodb.org/mongo-driver/bson"
    "go.mongodb.org/mongo-driver/mongo"
)

type TrustScoreSummary struct {
    Tag        string  `bson:"_id"`
    AvgScore   float64 `bson:"avg_score"`
    MaxScore   float64 `bson:"max_score"`
    DocCount   int     `bson:"doc_count"`
}

// GetTrustScoreByTag returns aggregated trust scores grouped by tag
func GetTrustScoreByTag(ctx context.Context, coll *mongo.Collection) ([]TrustScoreSummary, error) {
    pipeline := mongo.Pipeline{
        // Stage 1: Unwind tags array
        {{Key: "$unwind", Value: "$tags"}},

        // Stage 2: Match only active documents
        {{Key: "$match", Value: bson.M{"status": "ACTIVE"}}},

        // Stage 3: Group by tag and compute stats
        {{Key: "$group", Value: bson.M{
            "_id":       "$tags",
            "avg_score": bson.M{"$avg": "$trust_score"},
            "max_score": bson.M{"$max": "$trust_score"},
            "doc_count": bson.M{"$sum": 1},
        }}},

        // Stage 4: Sort by average score descending
        {{Key: "$sort", Value: bson.M{"avg_score": -1}}},
    }

    cursor, err := coll.Aggregate(ctx, pipeline)
    if err != nil {
        return nil, fmt.Errorf("executing aggregation: %w", err)
    }
    defer cursor.Close(ctx)

    var results []TrustScoreSummary
    if err := cursor.All(ctx, &results); err != nil {
        return nil, fmt.Errorf("decoding aggregation results: %w", err)
    }

    return results, nil
}

type TopStrategy struct {
    DocumentID string  `bson:"document_id"`
    Title      string  `bson:"title"`
    TrustScore float64 `bson:"trust_score"`
    WinRate    float64 `bson:"win_rate"`
}

// GetTopNStrategies returns the N highest-scoring strategies
func GetTopNStrategies(ctx context.Context, coll *mongo.Collection, n int) ([]TopStrategy, error) {
    pipeline := mongo.Pipeline{
        // Stage 1: Match active documents
        {{Key: "$match", Value: bson.M{"status": "ACTIVE"}}},

        // Stage 2: Sort by trust score
        {{Key: "$sort", Value: bson.M{"trust_score": -1}}},

        // Stage 3: Limit to top N
        {{Key: "$limit", Value: n}},

        // Stage 4: Project only needed fields
        {{Key: "$project", Value: bson.M{
            "_id":         0,
            "document_id": 1,
            "title":       1,
            "trust_score": 1,
            "win_rate":    1,
        }}},
    }

    cursor, err := coll.Aggregate(ctx, pipeline)
    if err != nil {
        return nil, fmt.Errorf("executing aggregation: %w", err)
    }
    defer cursor.Close(ctx)

    var results []TopStrategy
    if err := cursor.All(ctx, &results); err != nil {
        return nil, fmt.Errorf("decoding aggregation results: %w", err)
    }

    return results, nil
}

type GenerationPerformance struct {
    Generation  int     `bson:"_id"`
    AvgFitness  float64 `bson:"avg_fitness"`
    MaxFitness  float64 `bson:"max_fitness"`
    AgentCount  int     `bson:"agent_count"`
}

// GetGenerationPerformance returns performance summary by generation
func GetGenerationPerformance(ctx context.Context, coll *mongo.Collection) ([]GenerationPerformance, error) {
    pipeline := mongo.Pipeline{
        // Stage 1: Match active agents
        {{Key: "$match", Value: bson.M{"status": "ACTIVE"}}},

        // Stage 2: Group by generation
        {{Key: "$group", Value: bson.M{
            "_id":         "$generation",
            "avg_fitness": bson.M{"$avg": "$fitness"},
            "max_fitness": bson.M{"$max": "$fitness"},
            "agent_count": bson.M{"$sum": 1},
        }}},

        // Stage 3: Sort by generation ascending
        {{Key: "$sort", Value: bson.M{"_id": 1}}},
    }

    cursor, err := coll.Aggregate(ctx, pipeline)
    if err != nil {
        return nil, fmt.Errorf("executing aggregation: %w", err)
    }
    defer cursor.Close(ctx)

    var results []GenerationPerformance
    if err := cursor.All(ctx, &results); err != nil {
        return nil, fmt.Errorf("decoding aggregation results: %w", err)
    }

    return results, nil
}
```

### Indexing Strategy

```go
package indexing

import (
    "context"
    "fmt"
    "time"

    "go.mongodb.org/mongo-driver/bson"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
)

// EnsureIndexes creates all required indexes on startup
func EnsureIndexes(ctx context.Context, db *mongo.Database) error {
    // Strategy documents indexes
    stratColl := db.Collection("strategy_documents")
    stratIndexes := []mongo.IndexModel{
        // Compound index for active document queries
        {
            Keys: bson.D{
                {Key: "status", Value: 1},
                {Key: "trust_score", Value: -1},
            },
            Options: options.Index().SetName("status_trust_idx"),
        },
        // Agent lookup
        {
            Keys:    bson.D{{Key: "agent_id", Value: 1}},
            Options: options.Index().SetName("agent_id_idx"),
        },
        // Unique document ID
        {
            Keys:    bson.D{{Key: "document_id", Value: 1}},
            Options: options.Index().SetUnique(true).SetName("document_id_unique"),
        },
        // Text search on content and title
        {
            Keys: bson.D{
                {Key: "title", Value: "text"},
                {Key: "content", Value: "text"},
            },
            Options: options.Index().SetName("text_search_idx"),
        },
        // TTL index for auto-cleanup of retired documents
        {
            Keys: bson.D{{Key: "retired_at", Value: 1}},
            Options: options.Index().
                SetExpireAfterSeconds(30 * 24 * 60 * 60). // 30 days
                SetName("retired_ttl_idx").
                SetPartialFilterExpression(bson.M{
                    "retired_at": bson.M{"$ne": nil},
                }),
        },
    }

    if _, err := stratColl.Indexes().CreateMany(ctx, stratIndexes); err != nil {
        return fmt.Errorf("creating strategy_documents indexes: %w", err)
    }

    // Agent configs indexes
    agentColl := db.Collection("agent_configs")
    agentIndexes := []mongo.IndexModel{
        // Generation + fitness for evolution queries
        {
            Keys: bson.D{
                {Key: "generation", Value: 1},
                {Key: "fitness", Value: -1},
            },
            Options: options.Index().SetName("generation_fitness_idx"),
        },
        // Unique agent ID per generation
        {
            Keys: bson.D{
                {Key: "agent_id", Value: 1},
                {Key: "generation", Value: 1},
            },
            Options: options.Index().SetUnique(true).SetName("agent_gen_unique"),
        },
    }

    if _, err := agentColl.Indexes().CreateMany(ctx, agentIndexes); err != nil {
        return fmt.Errorf("creating agent_configs indexes: %w", err)
    }

    // Experiment results indexes
    expColl := db.Collection("experiment_results")
    expIndexes := []mongo.IndexModel{
        // Experiment ID lookup
        {
            Keys:    bson.D{{Key: "experiment_id", Value: 1}},
            Options: options.Index().SetName("experiment_id_idx"),
        },
        // Unique run per experiment
        {
            Keys: bson.D{
                {Key: "experiment_id", Value: 1},
                {Key: "run_id", Value: 1},
            },
            Options: options.Index().SetUnique(true).SetName("exp_run_unique"),
        },
    }

    if _, err := expColl.Indexes().CreateMany(ctx, expIndexes); err != nil {
        return fmt.Errorf("creating experiment_results indexes: %w", err)
    }

    return nil
}

// DropIndex removes a specific index
func DropIndex(ctx context.Context, coll *mongo.Collection, indexName string) error {
    _, err := coll.Indexes().DropOne(ctx, indexName)
    return err
}

// ListIndexes returns all indexes for a collection
func ListIndexes(ctx context.Context, coll *mongo.Collection) ([]bson.M, error) {
    cursor, err := coll.Indexes().List(ctx)
    if err != nil {
        return nil, fmt.Errorf("listing indexes: %w", err)
    }
    defer cursor.Close(ctx)

    var indexes []bson.M
    if err := cursor.All(ctx, &indexes); err != nil {
        return nil, fmt.Errorf("decoding indexes: %w", err)
    }

    return indexes, nil
}
```

### Transaction Patterns

```go
package transaction

import (
    "context"
    "fmt"

    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
)

// AtomicStrategyPromotion promotes a draft strategy to active and deprecates old versions
func AtomicStrategyPromotion(ctx context.Context, client *mongo.Client, newDocID, oldDocID string) error {
    session, err := client.StartSession()
    if err != nil {
        return fmt.Errorf("starting session: %w", err)
    }
    defer session.EndSession(ctx)

    // Define transaction callback
    callback := func(sessCtx mongo.SessionContext) (interface{}, error) {
        coll := client.Database("clau-doom").Collection("strategy_documents")

        // Step 1: Promote new document to ACTIVE
        if err := promoteDocument(sessCtx, coll, newDocID); err != nil {
            return nil, err
        }

        // Step 2: Deprecate old document
        if err := deprecateDocument(sessCtx, coll, oldDocID); err != nil {
            return nil, err
        }

        return nil, nil
    }

    // Execute transaction with retry
    _, err = session.WithTransaction(ctx, callback, options.Transaction().
        SetReadPreference(readpref.Primary()).
        SetWriteConcern(writeconcern.New(writeconcern.WMajority())))

    return err
}

func promoteDocument(ctx context.Context, coll *mongo.Collection, docID string) error {
    filter := bson.M{"document_id": docID}
    update := bson.M{
        "$set": bson.M{
            "status":     "ACTIVE",
            "updated_at": time.Now(),
        },
    }

    result, err := coll.UpdateOne(ctx, filter, update)
    if err != nil {
        return fmt.Errorf("promoting document: %w", err)
    }
    if result.MatchedCount == 0 {
        return fmt.Errorf("document %s not found", docID)
    }

    return nil
}

func deprecateDocument(ctx context.Context, coll *mongo.Collection, docID string) error {
    filter := bson.M{"document_id": docID}
    update := bson.M{
        "$set": bson.M{
            "status":        "DEPRECATED",
            "deprecated_at": time.Now(),
            "updated_at":    time.Now(),
        },
    }

    _, err := coll.UpdateOne(ctx, filter, update)
    return err
}

// RetryableOperation executes an operation with exponential backoff retry
func RetryableOperation(ctx context.Context, maxRetries int, op func() error) error {
    var err error
    backoff := 100 * time.Millisecond

    for i := 0; i < maxRetries; i++ {
        err = op()
        if err == nil {
            return nil
        }

        // Check if error is retryable (transient network error, etc.)
        if !isRetryable(err) {
            return err
        }

        // Wait with exponential backoff
        select {
        case <-ctx.Done():
            return ctx.Err()
        case <-time.After(backoff):
            backoff *= 2
        }
    }

    return fmt.Errorf("max retries exceeded: %w", err)
}

func isRetryable(err error) bool {
    // Check for MongoDB transient errors
    // e.g., network errors, replica set reconfigurations
    return mongo.IsNetworkError(err) || mongo.IsTimeout(err)
}
```

### Testing with testcontainers

```go
package repository_test

import (
    "context"
    "testing"
    "time"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/wait"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
)

func setupTestMongo(t *testing.T) (*mongo.Client, func()) {
    ctx := context.Background()

    req := testcontainers.ContainerRequest{
        Image:        "mongo:7",
        ExposedPorts: []string{"27017/tcp"},
        WaitingFor:   wait.ForLog("Waiting for connections"),
    }

    mongoC, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: req,
        Started:          true,
    })
    require.NoError(t, err)

    host, err := mongoC.Host(ctx)
    require.NoError(t, err)

    port, err := mongoC.MappedPort(ctx, "27017")
    require.NoError(t, err)

    uri := fmt.Sprintf("mongodb://%s:%s", host, port.Port())
    client, err := mongo.Connect(ctx, options.Client().ApplyURI(uri))
    require.NoError(t, err)

    cleanup := func() {
        client.Disconnect(ctx)
        mongoC.Terminate(ctx)
    }

    return client, cleanup
}

func TestStrategyDocumentRepository(t *testing.T) {
    client, cleanup := setupTestMongo(t)
    defer cleanup()

    db := client.Database("test_clau_doom")
    repo := NewStrategyDocumentRepository(db)

    t.Run("Create and Get", func(t *testing.T) {
        doc := &StrategyDocument{
            DocumentID: "test-001",
            AgentID:    "agent-A",
            Generation: 1,
            Title:      "Test Strategy",
            Content:    "Test content",
            TrustScore: 0.75,
            Status:     "ACTIVE",
        }

        err := repo.Create(context.Background(), doc)
        require.NoError(t, err)

        retrieved, err := repo.GetByID(context.Background(), "test-001")
        require.NoError(t, err)
        assert.Equal(t, "Test Strategy", retrieved.Title)
        assert.Equal(t, 0.75, retrieved.TrustScore)
    })

    t.Run("Update Trust Score", func(t *testing.T) {
        err := repo.UpdateTrustScore(context.Background(), "test-001", 0.85)
        require.NoError(t, err)

        doc, err := repo.GetByID(context.Background(), "test-001")
        require.NoError(t, err)
        assert.Equal(t, 0.85, doc.TrustScore)
    })
}
```

## Python pymongo Patterns

### Connection Management

```python
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os

class MongoDBClient:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            self._client = MongoClient(
                uri,
                maxPoolSize=50,
                minPoolSize=10,
                serverSelectionTimeoutMS=5000,
                retryWrites=True
            )
            # Verify connection
            try:
                self._client.admin.command('ping')
                print("MongoDB connection successful")
            except ConnectionFailure:
                print("MongoDB connection failed")
                raise

    @property
    def client(self):
        return self._client

    @property
    def db(self):
        return self._client['clau-doom']

    def close(self):
        if self._client:
            self._client.close()
```

### DataFrame Integration

```python
import pandas as pd
from pymongo import MongoClient
from typing import List, Dict

class StrategyAnalytics:
    def __init__(self, client: MongoClient):
        self.db = client['clau-doom']
        self.strategies = self.db['strategy_documents']

    def cursor_to_dataframe(self, cursor) -> pd.DataFrame:
        """Convert MongoDB cursor to pandas DataFrame"""
        data = list(cursor)
        if not data:
            return pd.DataFrame()

        # Convert ObjectId to string for compatibility
        for doc in data:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])

        return pd.DataFrame(data)

    def get_active_strategies_df(self) -> pd.DataFrame:
        """Fetch all active strategies as DataFrame"""
        cursor = self.strategies.find(
            {"status": "ACTIVE"},
            projection={"_id": 0, "document_id": 1, "trust_score": 1,
                       "win_rate": 1, "run_count": 1, "tags": 1}
        )
        return self.cursor_to_dataframe(cursor)

    def bulk_dataframe_to_mongo(self, df: pd.DataFrame, collection_name: str):
        """Insert DataFrame rows as MongoDB documents"""
        collection = self.db[collection_name]

        # Convert DataFrame to list of dicts
        records = df.to_dict('records')

        # Bulk insert
        if records:
            result = collection.insert_many(records, ordered=False)
            return len(result.inserted_ids)
        return 0

    def trust_score_distribution(self) -> pd.DataFrame:
        """Analyze trust score distribution"""
        pipeline = [
            {"$match": {"status": "ACTIVE"}},
            {"$group": {
                "_id": None,
                "avg_score": {"$avg": "$trust_score"},
                "std_score": {"$stdDevPop": "$trust_score"},
                "min_score": {"$min": "$trust_score"},
                "max_score": {"$max": "$trust_score"},
                "count": {"$sum": 1}
            }}
        ]

        cursor = self.strategies.aggregate(pipeline)
        return self.cursor_to_dataframe(cursor)

    def strategy_quality_metrics(self) -> pd.DataFrame:
        """Compute quality metrics by category"""
        pipeline = [
            {"$match": {"status": "ACTIVE"}},
            {"$group": {
                "_id": "$category",
                "avg_trust": {"$avg": "$trust_score"},
                "avg_win_rate": {"$avg": "$win_rate"},
                "total_runs": {"$sum": "$run_count"},
                "doc_count": {"$sum": 1}
            }},
            {"$sort": {"avg_trust": -1}}
        ]

        cursor = self.strategies.aggregate(pipeline)
        df = self.cursor_to_dataframe(cursor)

        # Rename _id to category for clarity
        if not df.empty:
            df = df.rename(columns={"_id": "category"})

        return df

    def generation_comparison(self, gen1: int, gen2: int) -> pd.DataFrame:
        """Compare two generations side by side"""
        agents = self.db['agent_configs']

        pipeline = [
            {"$match": {"generation": {"$in": [gen1, gen2]}}},
            {"$group": {
                "_id": "$generation",
                "avg_fitness": {"$avg": "$fitness"},
                "max_fitness": {"$max": "$fitness"},
                "avg_kills": {"$avg": "$total_kills"},
                "agent_count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]

        cursor = agents.aggregate(pipeline)
        df = self.cursor_to_dataframe(cursor)

        if not df.empty:
            df = df.rename(columns={"_id": "generation"})

        return df
```

## Document Lifecycle Management

### State Machine

```python
from enum import Enum
from datetime import datetime
from typing import Optional

class DocumentStatus(Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"

class StrategyLifecycle:
    VALID_TRANSITIONS = {
        DocumentStatus.DRAFT: [DocumentStatus.ACTIVE],
        DocumentStatus.ACTIVE: [DocumentStatus.DEPRECATED],
        DocumentStatus.DEPRECATED: [DocumentStatus.RETIRED],
        DocumentStatus.RETIRED: []  # Terminal state
    }

    def __init__(self, db):
        self.collection = db['strategy_documents']

    def transition(self, document_id: str, target_status: DocumentStatus) -> bool:
        """Execute state transition with validation"""
        doc = self.collection.find_one({"document_id": document_id})
        if not doc:
            raise ValueError(f"Document {document_id} not found")

        current_status = DocumentStatus(doc['status'])

        # Validate transition
        if target_status not in self.VALID_TRANSITIONS[current_status]:
            raise ValueError(
                f"Invalid transition: {current_status} -> {target_status}"
            )

        # Execute transition
        update = {
            "$set": {
                "status": target_status.value,
                "updated_at": datetime.utcnow()
            }
        }

        # Add timestamp for specific transitions
        if target_status == DocumentStatus.DEPRECATED:
            update["$set"]["deprecated_at"] = datetime.utcnow()
        elif target_status == DocumentStatus.RETIRED:
            update["$set"]["retired_at"] = datetime.utcnow()

        result = self.collection.update_one(
            {"document_id": document_id},
            update
        )

        return result.modified_count > 0

    def archive_to_duckdb(self, document_id: str) -> bool:
        """Archive retired document to DuckDB before deletion"""
        import duckdb

        doc = self.collection.find_one({"document_id": document_id})
        if not doc or doc['status'] != DocumentStatus.RETIRED.value:
            raise ValueError(f"Only RETIRED documents can be archived")

        # Connect to DuckDB archive
        conn = duckdb.connect('data/archives/strategy_archive.duckdb')

        # Flatten document for SQL storage
        flat_doc = {
            'document_id': doc['document_id'],
            'agent_id': doc['agent_id'],
            'generation': doc['generation'],
            'title': doc['title'],
            'content': doc['content'],
            'trust_score': doc['trust_score'],
            'run_count': doc['run_count'],
            'created_at': doc['created_at'],
            'retired_at': doc['retired_at']
        }

        conn.execute("""
            INSERT INTO archived_strategies VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, list(flat_doc.values()))

        conn.close()

        # Delete from MongoDB after successful archive
        self.collection.delete_one({"document_id": document_id})

        return True

    def apply_quality_decay(self, generations_passed: int):
        """Reduce trust scores of old strategies"""
        decay_rate = 0.05  # 5% per generation

        pipeline = [
            {"$match": {"status": "ACTIVE"}},
            {"$set": {
                "trust_score": {
                    "$max": [
                        0.0,
                        {"$subtract": [
                            "$trust_score",
                            {"$multiply": [decay_rate, generations_passed]}
                        ]}
                    ]
                },
                "updated_at": datetime.utcnow()
            }}
        ]

        self.collection.update_many({}, pipeline)
```

## Monitoring & Operations

### Collection Stats

```go
package monitoring

import (
    "context"
    "fmt"

    "go.mongodb.org/mongo-driver/bson"
    "go.mongodb.org/mongo-driver/mongo"
)

type CollectionStats struct {
    Count      int64   `bson:"count"`
    Size       int64   `bson:"size"`
    AvgObjSize float64 `bson:"avgObjSize"`
    IndexSizes map[string]int64 `bson:"indexSizes"`
}

func GetCollectionStats(ctx context.Context, coll *mongo.Collection) (*CollectionStats, error) {
    var stats CollectionStats

    err := coll.Database().RunCommand(
        ctx,
        bson.D{{Key: "collStats", Value: coll.Name()}},
    ).Decode(&stats)

    if err != nil {
        return nil, fmt.Errorf("getting collection stats: %w", err)
    }

    return &stats, nil
}

func MonitorSlowQueries(ctx context.Context, db *mongo.Database, thresholdMs int) error {
    // Enable profiling for slow queries
    err := db.RunCommand(ctx, bson.D{
        {Key: "profile", Value: 1},
        {Key: "slowms", Value: thresholdMs},
    }).Err()

    return err
}
```

## Anti-Patterns to Avoid

### 1. Unbounded Queries

```go
// WRONG: No limit on results
func getAllStrategies(ctx context.Context, coll *mongo.Collection) ([]*StrategyDocument, error) {
    cursor, err := coll.Find(ctx, bson.M{})  // Can return millions of docs
    // ...
}

// CORRECT: Use pagination
func getStrategies(ctx context.Context, coll *mongo.Collection, page, limit int) ([]*StrategyDocument, error) {
    opts := options.Find().
        SetSkip(int64(page * limit)).
        SetLimit(int64(limit))
    cursor, err := coll.Find(ctx, bson.M{}, opts)
    // ...
}
```

### 2. Missing Indexes

```go
// WRONG: Query on unindexed field
filter := bson.M{"tags": "combat"}  // tags not indexed, full collection scan

// CORRECT: Ensure index exists
// Create index: db.strategy_documents.createIndex({tags: 1})
```

### 3. Large Documents

```go
// WRONG: Embedding huge arrays
type StrategyDocument struct {
    // ...
    AllEpisodeData []Episode  // Could be thousands of items, exceeds 16MB
}

// CORRECT: Store episode data separately or use GridFS
type StrategyDocument struct {
    // ...
    DuckDBReference string  // "experiment_042_episodes"
}
```

### 4. Not Using Projection

```go
// WRONG: Fetch entire document when only need few fields
cursor, _ := coll.Find(ctx, filter)  // Returns all fields including embeddings

// CORRECT: Project only needed fields
opts := options.Find().SetProjection(bson.M{
    "document_id": 1,
    "title": 1,
    "trust_score": 1,
})
cursor, _ := coll.Find(ctx, filter, opts)
```
