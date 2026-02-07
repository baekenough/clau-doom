# MongoDB Reference Guide

Reference documentation for MongoDB usage in the clau-doom knowledge catalog and experimental data storage.

## Key Resources

- [MongoDB Manual](https://www.mongodb.com/docs/manual/)
- [Go mongo-driver Documentation](https://pkg.go.dev/go.mongodb.org/mongo-driver/mongo)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Aggregation Pipeline](https://www.mongodb.com/docs/manual/core/aggregation-pipeline/)
- [BSON Specification](https://bsonspec.org/)

## clau-doom Context

MongoDB serves as the knowledge catalog and experimental data store. Key components:

- **Knowledge Catalog**: Strategy documents with embeddings, trust scores, and metadata
- **Agent Configurations**: Versioned agent genomes across generations
- **Experiment Results**: DOE run data, ANOVA results, and meta-analysis findings
- **Evolution Tracking**: Generation-by-generation performance metrics and Pareto fronts

Access patterns:
```
orchestrator/ (Go)       → strategy_documents, agent_configs, experiment_results
research-analyst (Python) → experiment_results, doe_metadata
research-rag-curator (Python) → strategy_documents, trust_scores
```

Project layout:
```
orchestrator/internal/mongo/
├── client.go           # Connection management, pooling
├── strategy.go         # Strategy document CRUD
├── agent.go            # Agent config versioning
└── experiment.go       # Experiment result operations

research/scripts/
├── query_knowledge.py  # pymongo for analytics
└── update_trust.py     # Trust score batch updates
```

## Go mongo-driver Patterns

### Connection Management

```go
import (
    "context"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
)

func NewMongoClient(ctx context.Context, uri string) (*mongo.Client, error) {
    clientOpts := options.Client().
        ApplyURI(uri).
        SetMaxPoolSize(50).
        SetMinPoolSize(10).
        SetMaxConnIdleTime(30 * time.Second).
        SetAppName("clau-doom-orchestrator")

    client, err := mongo.Connect(ctx, clientOpts)
    if err != nil {
        return nil, fmt.Errorf("connecting to MongoDB: %w", err)
    }

    // Verify connection
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    if err := client.Ping(ctx, nil); err != nil {
        return nil, fmt.Errorf("pinging MongoDB: %w", err)
    }

    return client, nil
}

// Graceful shutdown
func (m *MongoStore) Close(ctx context.Context) error {
    return m.client.Disconnect(ctx)
}
```

### BSON Marshaling

```go
import (
    "go.mongodb.org/mongo-driver/bson"
    "go.mongodb.org/mongo-driver/bson/primitive"
)

type StrategyDocument struct {
    ID          primitive.ObjectID `bson:"_id,omitempty"`
    DocID       string             `bson:"doc_id"`
    Title       string             `bson:"title"`
    Content     string             `bson:"content"`
    Embedding   []float32          `bson:"embedding"`
    Tags        []string           `bson:"tags"`
    TrustScore  float64            `bson:"trust_score"`
    Generation  int                `bson:"generation"`
    Status      string             `bson:"status"` // "active", "archived", "deprecated"
    CreatedAt   time.Time          `bson:"created_at"`
    UpdatedAt   time.Time          `bson:"updated_at"`
}

// BSON marshaling is automatic via struct tags
```

### CRUD Operations

#### Insert

```go
func (s *StrategyStore) Insert(ctx context.Context, doc *StrategyDocument) error {
    doc.ID = primitive.NewObjectID()
    doc.CreatedAt = time.Now()
    doc.UpdatedAt = doc.CreatedAt

    coll := s.client.Database("clau_doom").Collection("strategy_documents")
    _, err := coll.InsertOne(ctx, doc)
    if err != nil {
        return fmt.Errorf("inserting strategy document: %w", err)
    }
    return nil
}

// Bulk insert
func (s *StrategyStore) InsertMany(ctx context.Context, docs []*StrategyDocument) error {
    if len(docs) == 0 {
        return nil
    }

    now := time.Now()
    documents := make([]interface{}, len(docs))
    for i, doc := range docs {
        doc.ID = primitive.NewObjectID()
        doc.CreatedAt = now
        doc.UpdatedAt = now
        documents[i] = doc
    }

    coll := s.client.Database("clau_doom").Collection("strategy_documents")
    opts := options.InsertMany().SetOrdered(false) // Continue on error
    _, err := coll.InsertMany(ctx, documents, opts)
    if err != nil {
        return fmt.Errorf("bulk inserting %d documents: %w", len(docs), err)
    }
    return nil
}
```

#### Find

```go
func (s *StrategyStore) FindByID(ctx context.Context, docID string) (*StrategyDocument, error) {
    coll := s.client.Database("clau_doom").Collection("strategy_documents")

    filter := bson.M{"doc_id": docID}
    var doc StrategyDocument

    err := coll.FindOne(ctx, filter).Decode(&doc)
    if err == mongo.ErrNoDocuments {
        return nil, fmt.Errorf("strategy document %s: %w", docID, ErrNotFound)
    }
    if err != nil {
        return nil, fmt.Errorf("finding document %s: %w", docID, err)
    }

    return &doc, nil
}

// Find many with filter
func (s *StrategyStore) FindActiveByTags(ctx context.Context, tags []string, minTrust float64) ([]*StrategyDocument, error) {
    coll := s.client.Database("clau_doom").Collection("strategy_documents")

    filter := bson.M{
        "status":      "active",
        "trust_score": bson.M{"$gte": minTrust},
        "tags":        bson.M{"$in": tags},
    }

    opts := options.Find().
        SetSort(bson.D{{Key: "trust_score", Value: -1}}).
        SetLimit(100)

    cursor, err := coll.Find(ctx, filter, opts)
    if err != nil {
        return nil, fmt.Errorf("finding active documents: %w", err)
    }
    defer cursor.Close(ctx)

    var docs []*StrategyDocument
    if err := cursor.All(ctx, &docs); err != nil {
        return nil, fmt.Errorf("decoding documents: %w", err)
    }

    return docs, nil
}
```

#### Update

```go
func (s *StrategyStore) UpdateTrustScore(ctx context.Context, docID string, newScore float64) error {
    coll := s.client.Database("clau_doom").Collection("strategy_documents")

    filter := bson.M{"doc_id": docID}
    update := bson.M{
        "$set": bson.M{
            "trust_score": newScore,
            "updated_at":  time.Now(),
        },
    }

    result, err := coll.UpdateOne(ctx, filter, update)
    if err != nil {
        return fmt.Errorf("updating trust score for %s: %w", docID, err)
    }

    if result.MatchedCount == 0 {
        return fmt.Errorf("document %s not found", docID)
    }

    return nil
}

// Increment operation
func (s *StrategyStore) IncrementUsageCount(ctx context.Context, docID string) error {
    coll := s.client.Database("clau_doom").Collection("strategy_documents")

    filter := bson.M{"doc_id": docID}
    update := bson.M{
        "$inc": bson.M{"usage_count": 1},
        "$set": bson.M{"updated_at": time.Now()},
    }

    _, err := coll.UpdateOne(ctx, filter, update)
    return err
}
```

#### Delete

```go
func (s *StrategyStore) Archive(ctx context.Context, docID string) error {
    coll := s.client.Database("clau_doom").Collection("strategy_documents")

    filter := bson.M{"doc_id": docID, "status": "active"}
    update := bson.M{
        "$set": bson.M{
            "status":     "archived",
            "updated_at": time.Now(),
        },
    }

    result, err := coll.UpdateOne(ctx, filter, update)
    if err != nil {
        return fmt.Errorf("archiving document %s: %w", docID, err)
    }

    if result.MatchedCount == 0 {
        return fmt.Errorf("active document %s not found", docID)
    }

    return nil
}

// Hard delete (rare, use with caution)
func (s *StrategyStore) Delete(ctx context.Context, docID string) error {
    coll := s.client.Database("clau_doom").Collection("strategy_documents")

    filter := bson.M{"doc_id": docID}
    result, err := coll.DeleteOne(ctx, filter)
    if err != nil {
        return fmt.Errorf("deleting document %s: %w", docID, err)
    }

    if result.DeletedCount == 0 {
        return fmt.Errorf("document %s not found", docID)
    }

    return nil
}
```

### Aggregation Pipelines

```go
// Average trust score by tag
func (s *StrategyStore) AverageTrustByTag(ctx context.Context) (map[string]float64, error) {
    coll := s.client.Database("clau_doom").Collection("strategy_documents")

    pipeline := bson.A{
        bson.M{"$match": bson.M{"status": "active"}},
        bson.M{"$unwind": "$tags"},
        bson.M{"$group": bson.M{
            "_id":        "$tags",
            "avg_trust":  bson.M{"$avg": "$trust_score"},
            "doc_count":  bson.M{"$sum": 1},
        }},
        bson.M{"$sort": bson.M{"avg_trust": -1}},
    }

    cursor, err := coll.Aggregate(ctx, pipeline)
    if err != nil {
        return nil, fmt.Errorf("aggregating trust by tag: %w", err)
    }
    defer cursor.Close(ctx)

    type Result struct {
        Tag      string  `bson:"_id"`
        AvgTrust float64 `bson:"avg_trust"`
        DocCount int     `bson:"doc_count"`
    }

    results := make(map[string]float64)
    for cursor.Next(ctx) {
        var r Result
        if err := cursor.Decode(&r); err != nil {
            return nil, err
        }
        results[r.Tag] = r.AvgTrust
    }

    return results, cursor.Err()
}

// Top N documents by trust within each generation
func (s *StrategyStore) TopDocsByGeneration(ctx context.Context, topN int) (map[int][]*StrategyDocument, error) {
    coll := s.client.Database("clau_doom").Collection("strategy_documents")

    pipeline := bson.A{
        bson.M{"$match": bson.M{"status": "active"}},
        bson.M{"$sort": bson.M{"trust_score": -1}},
        bson.M{"$group": bson.M{
            "_id": "$generation",
            "docs": bson.M{"$push": "$$ROOT"},
        }},
        bson.M{"$project": bson.M{
            "_id":  1,
            "docs": bson.M{"$slice": []interface{}{"$docs", topN}},
        }},
    }

    cursor, err := coll.Aggregate(ctx, pipeline)
    if err != nil {
        return nil, fmt.Errorf("aggregating top docs by generation: %w", err)
    }
    defer cursor.Close(ctx)

    type GenGroup struct {
        Generation int                   `bson:"_id"`
        Docs       []*StrategyDocument   `bson:"docs"`
    }

    results := make(map[int][]*StrategyDocument)
    for cursor.Next(ctx) {
        var g GenGroup
        if err := cursor.Decode(&g); err != nil {
            return nil, err
        }
        results[g.Generation] = g.Docs
    }

    return results, cursor.Err()
}

// Lookup (join) experiment results with agent configs
func (s *ExperimentStore) ResultsWithAgentConfigs(ctx context.Context, experimentID string) ([]*ExperimentResultWithConfig, error) {
    coll := s.client.Database("clau_doom").Collection("experiment_results")

    pipeline := bson.A{
        bson.M{"$match": bson.M{"experiment_id": experimentID}},
        bson.M{"$lookup": bson.M{
            "from":         "agent_configs",
            "localField":   "agent_id",
            "foreignField": "agent_id",
            "as":           "agent_config",
        }},
        bson.M{"$unwind": "$agent_config"},
        bson.M{"$project": bson.M{
            "run_id":       1,
            "score":        1,
            "kills":        1,
            "survival_sec": 1,
            "agent_config": 1,
        }},
    }

    cursor, err := coll.Aggregate(ctx, pipeline)
    if err != nil {
        return nil, fmt.Errorf("joining experiment results with configs: %w", err)
    }
    defer cursor.Close(ctx)

    var results []*ExperimentResultWithConfig
    if err := cursor.All(ctx, &results); err != nil {
        return nil, err
    }

    return results, nil
}
```

### Compound Indexing

```go
func (s *StrategyStore) EnsureIndexes(ctx context.Context) error {
    coll := s.client.Database("clau_doom").Collection("strategy_documents")

    indexes := []mongo.IndexModel{
        {
            Keys: bson.D{
                {Key: "status", Value: 1},
                {Key: "trust_score", Value: -1},
            },
            Options: options.Index().SetName("status_trust_idx"),
        },
        {
            Keys: bson.D{
                {Key: "tags", Value: 1},
                {Key: "trust_score", Value: -1},
            },
            Options: options.Index().SetName("tags_trust_idx"),
        },
        {
            Keys: bson.D{
                {Key: "generation", Value: 1},
                {Key: "trust_score", Value: -1},
            },
            Options: options.Index().SetName("generation_trust_idx"),
        },
        {
            Keys:    bson.D{{Key: "doc_id", Value: 1}},
            Options: options.Index().SetName("doc_id_unique").SetUnique(true),
        },
        {
            Keys:    bson.D{{Key: "content", Value: "text"}},
            Options: options.Index().SetName("content_text_idx"),
        },
    }

    _, err := coll.Indexes().CreateMany(ctx, indexes)
    if err != nil {
        return fmt.Errorf("creating indexes: %w", err)
    }

    return nil
}
```

### Error Handling

```go
import (
    "errors"
    "go.mongodb.org/mongo-driver/mongo"
)

var (
    ErrNotFound      = errors.New("document not found")
    ErrDuplicateKey  = errors.New("duplicate key")
)

func handleMongoError(err error) error {
    if err == nil {
        return nil
    }

    if errors.Is(err, mongo.ErrNoDocuments) {
        return ErrNotFound
    }

    if mongo.IsDuplicateKeyError(err) {
        return ErrDuplicateKey
    }

    return err
}

// Usage
doc, err := s.FindByID(ctx, docID)
if errors.Is(err, ErrNotFound) {
    // Handle missing document
}
```

### Context Propagation

```go
func (s *StrategyStore) BatchUpdate(ctx context.Context, updates []Update) error {
    coll := s.client.Database("clau_doom").Collection("strategy_documents")

    // Respect context deadline
    deadline, ok := ctx.Deadline()
    if ok {
        timeout := time.Until(deadline)
        if timeout < 0 {
            return fmt.Errorf("context already exceeded deadline")
        }
    }

    models := make([]mongo.WriteModel, len(updates))
    for i, u := range updates {
        models[i] = mongo.NewUpdateOneModel().
            SetFilter(bson.M{"doc_id": u.DocID}).
            SetUpdate(bson.M{"$set": u.Fields})
    }

    opts := options.BulkWrite().SetOrdered(false)
    _, err := coll.BulkWrite(ctx, models, opts)
    return err
}
```

## Python pymongo Patterns

### Connection

```python
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError

def get_mongo_client(uri: str) -> MongoClient:
    """Create MongoDB client with connection pooling."""
    client = MongoClient(
        uri,
        maxPoolSize=50,
        minPoolSize=10,
        maxIdleTimeMS=30000,
        appname="clau-doom-research"
    )

    # Verify connection
    try:
        client.admin.command('ping')
    except ConnectionFailure as e:
        raise RuntimeError(f"MongoDB connection failed: {e}")

    return client

# Usage
client = get_mongo_client("mongodb://localhost:27017")
db = client["clau_doom"]
collection = db["strategy_documents"]
```

### Collection Operations

```python
from datetime import datetime
from typing import List, Dict, Optional

def insert_strategy_document(
    collection,
    doc_id: str,
    title: str,
    content: str,
    embedding: List[float],
    tags: List[str],
    trust_score: float,
    generation: int
) -> str:
    """Insert a strategy document and return ObjectId."""
    document = {
        "doc_id": doc_id,
        "title": title,
        "content": content,
        "embedding": embedding,
        "tags": tags,
        "trust_score": trust_score,
        "generation": generation,
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    try:
        result = collection.insert_one(document)
        return str(result.inserted_id)
    except DuplicateKeyError:
        raise ValueError(f"Document with doc_id={doc_id} already exists")

def find_high_trust_docs(
    collection,
    min_trust: float = 0.7,
    tags: Optional[List[str]] = None,
    limit: int = 100
) -> List[Dict]:
    """Find active documents above trust threshold."""
    query = {
        "status": "active",
        "trust_score": {"$gte": min_trust}
    }

    if tags:
        query["tags"] = {"$in": tags}

    cursor = collection.find(query).sort("trust_score", -1).limit(limit)
    return list(cursor)

def update_trust_scores(
    collection,
    updates: Dict[str, float]
) -> int:
    """Batch update trust scores for multiple documents."""
    from pymongo import UpdateOne

    operations = [
        UpdateOne(
            {"doc_id": doc_id},
            {
                "$set": {
                    "trust_score": score,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        for doc_id, score in updates.items()
    ]

    result = collection.bulk_write(operations, ordered=False)
    return result.modified_count
```

### Aggregation from Python

```python
def average_trust_by_tag(collection) -> Dict[str, float]:
    """Compute average trust score per tag."""
    pipeline = [
        {"$match": {"status": "active"}},
        {"$unwind": "$tags"},
        {"$group": {
            "_id": "$tags",
            "avg_trust": {"$avg": "$trust_score"},
            "doc_count": {"$sum": 1}
        }},
        {"$sort": {"avg_trust": -1}}
    ]

    results = {}
    for doc in collection.aggregate(pipeline):
        results[doc["_id"]] = doc["avg_trust"]

    return results

def trust_score_distribution(collection, bin_size: float = 0.1) -> Dict[str, int]:
    """Compute trust score distribution histogram."""
    pipeline = [
        {"$match": {"status": "active"}},
        {"$bucket": {
            "groupBy": "$trust_score",
            "boundaries": [i * bin_size for i in range(int(1.0 / bin_size) + 1)],
            "default": "other",
            "output": {
                "count": {"$sum": 1}
            }
        }}
    ]

    results = {}
    for doc in collection.aggregate(pipeline):
        bucket_name = f"{doc['_id']:.1f}-{doc['_id'] + bin_size:.1f}"
        results[bucket_name] = doc["count"]

    return results
```

### DataFrame Integration

```python
import pandas as pd
from pymongo import MongoClient

def load_experiment_results_to_df(
    collection,
    experiment_id: str
) -> pd.DataFrame:
    """Load experiment results into pandas DataFrame."""
    query = {"experiment_id": experiment_id}
    cursor = collection.find(query)

    df = pd.DataFrame(list(cursor))

    # Convert ObjectId to string if needed
    if "_id" in df.columns:
        df["_id"] = df["_id"].astype(str)

    return df

def save_anova_results(
    collection,
    experiment_id: str,
    anova_table: pd.DataFrame,
    metadata: Dict
):
    """Save ANOVA results with experiment metadata."""
    document = {
        "experiment_id": experiment_id,
        "anova_table": anova_table.to_dict(orient="records"),
        "metadata": metadata,
        "created_at": datetime.utcnow()
    }

    collection.insert_one(document)
```

## Knowledge Catalog Schema

### strategy_documents Collection

```javascript
{
  "_id": ObjectId("..."),
  "doc_id": "strat-gen5-combat-012",
  "title": "Aggressive Close-Quarter Combat Strategy",
  "content": "When enemy at range < 5m and health > 50%, select shotgun...",
  "embedding": [0.123, -0.456, 0.789, ...], // 384-dim vector for kNN
  "tags": ["combat", "shotgun", "close-range", "high-health"],
  "trust_score": 0.87,
  "generation": 5,
  "status": "active", // "active" | "archived" | "deprecated"
  "usage_count": 142,
  "win_rate": 0.72,
  "created_at": ISODate("2026-02-07T10:00:00Z"),
  "updated_at": ISODate("2026-02-07T15:30:00Z")
}
```

### agent_configs Collection

```javascript
{
  "_id": ObjectId("..."),
  "agent_id": "agent-gen5-042",
  "generation": 5,
  "genome": {
    "memory": 0.75,
    "strength": 0.82,
    "curiosity": 0.45,
    "aggression": 0.68
  },
  "parent_ids": ["agent-gen4-021", "agent-gen4-035"],
  "mutation_rate": 0.1,
  "fitness_score": 0.85,
  "status": "active", // "active" | "archived" | "failed"
  "created_at": ISODate("2026-02-07T10:00:00Z")
}
```

### experiment_results Collection

```javascript
{
  "_id": ObjectId("..."),
  "experiment_id": "DOE-042",
  "run_id": "DOE-042-run-3",
  "agent_id": "agent-gen5-042",
  "factors": {
    "memory": 0.7,
    "strength": 0.5
  },
  "response": {
    "kills": 42,
    "deaths": 3,
    "survival_sec": 540.2,
    "damage_dealt": 8240,
    "damage_taken": 1250
  },
  "seed": 9999,
  "map": "E1M1",
  "difficulty": "medium",
  "created_at": ISODate("2026-02-07T12:00:00Z")
}
```

### Index Definitions

```javascript
// Compound indexes for common queries
db.strategy_documents.createIndex(
  { status: 1, trust_score: -1 },
  { name: "status_trust_idx" }
);

db.strategy_documents.createIndex(
  { tags: 1, trust_score: -1 },
  { name: "tags_trust_idx" }
);

db.strategy_documents.createIndex(
  { generation: 1, trust_score: -1 },
  { name: "generation_trust_idx" }
);

// Unique constraint on doc_id
db.strategy_documents.createIndex(
  { doc_id: 1 },
  { unique: true, name: "doc_id_unique" }
);

// Text index for content search
db.strategy_documents.createIndex(
  { content: "text" },
  { name: "content_text_idx" }
);

// Experiment results indexes
db.experiment_results.createIndex(
  { experiment_id: 1, run_id: 1 },
  { unique: true, name: "experiment_run_unique" }
);

db.experiment_results.createIndex(
  { agent_id: 1, created_at: -1 },
  { name: "agent_time_idx" }
);
```

## Trust Score Queries

### Find Active Documents Above Threshold

```go
func (s *StrategyStore) FindHighTrust(ctx context.Context, threshold float64) ([]*StrategyDocument, error) {
    coll := s.client.Database("clau_doom").Collection("strategy_documents")

    filter := bson.M{
        "status":      "active",
        "trust_score": bson.M{"$gte": threshold},
    }

    opts := options.Find().SetSort(bson.M{"trust_score": -1})
    cursor, err := coll.Find(ctx, filter, opts)
    if err != nil {
        return nil, err
    }
    defer cursor.Close(ctx)

    var docs []*StrategyDocument
    if err := cursor.All(ctx, &docs); err != nil {
        return nil, err
    }

    return docs, nil
}
```

### Aggregation for Average Trust by Tag

```python
def average_trust_by_tag_filtered(collection, min_docs: int = 5) -> Dict[str, float]:
    """Average trust per tag, filtering tags with < min_docs."""
    pipeline = [
        {"$match": {"status": "active"}},
        {"$unwind": "$tags"},
        {"$group": {
            "_id": "$tags",
            "avg_trust": {"$avg": "$trust_score"},
            "doc_count": {"$sum": 1}
        }},
        {"$match": {"doc_count": {"$gte": min_docs}}},
        {"$sort": {"avg_trust": -1}}
    ]

    results = {}
    for doc in collection.aggregate(pipeline):
        results[doc["_id"]] = {
            "avg_trust": doc["avg_trust"],
            "doc_count": doc["doc_count"]
        }

    return results
```

### Update Trust Scores After Generation

```go
func (s *StrategyStore) UpdateTrustScoresForGeneration(
    ctx context.Context,
    generation int,
    scoreUpdates map[string]float64,
) error {
    coll := s.client.Database("clau_doom").Collection("strategy_documents")

    models := make([]mongo.WriteModel, 0, len(scoreUpdates))
    now := time.Now()

    for docID, newScore := range scoreUpdates {
        model := mongo.NewUpdateOneModel().
            SetFilter(bson.M{
                "doc_id":     docID,
                "generation": generation,
            }).
            SetUpdate(bson.M{
                "$set": bson.M{
                    "trust_score": newScore,
                    "updated_at":  now,
                },
            })
        models = append(models, model)
    }

    opts := options.BulkWrite().SetOrdered(false)
    result, err := coll.BulkWrite(ctx, models, opts)
    if err != nil {
        return fmt.Errorf("bulk updating trust scores: %w", err)
    }

    if result.ModifiedCount != int64(len(scoreUpdates)) {
        return fmt.Errorf("expected %d updates, got %d", len(scoreUpdates), result.ModifiedCount)
    }

    return nil
}
```

## Performance Patterns

### Connection Pooling

```go
// Configure connection pool for high-throughput workloads
clientOpts := options.Client().
    ApplyURI("mongodb://localhost:27017").
    SetMaxPoolSize(100).        // Max concurrent connections
    SetMinPoolSize(20).          // Keep warm connections
    SetMaxConnIdleTime(60 * time.Second). // Close idle after 60s
    SetMaxConnecting(10)         // Max concurrent connection establishment
```

### Projection to Limit Returned Fields

```go
// Only fetch needed fields to reduce network I/O
opts := options.Find().SetProjection(bson.M{
    "doc_id":      1,
    "title":       1,
    "trust_score": 1,
    "tags":        1,
    "_id":         0, // Exclude _id
})

cursor, err := coll.Find(ctx, filter, opts)
```

### Batch Operations

```go
// Use BulkWrite for batch inserts/updates
func (s *StrategyStore) BulkUpsert(ctx context.Context, docs []*StrategyDocument) error {
    coll := s.client.Database("clau_doom").Collection("strategy_documents")

    models := make([]mongo.WriteModel, len(docs))
    for i, doc := range docs {
        models[i] = mongo.NewReplaceOneModel().
            SetFilter(bson.M{"doc_id": doc.DocID}).
            SetReplacement(doc).
            SetUpsert(true)
    }

    opts := options.BulkWrite().SetOrdered(false)
    _, err := coll.BulkWrite(ctx, models, opts)
    return err
}
```

### Read Concern / Write Concern

```go
// For critical writes (experiment results)
wcMajority := writeconcern.New(writeconcern.WMajority(), writeconcern.J(true))
opts := options.Collection().SetWriteConcern(wcMajority)
coll := db.Collection("experiment_results", opts)

// For read-heavy analytics queries
rcLocal := readconcern.Local()
opts := options.Collection().SetReadConcern(rcLocal)
coll := db.Collection("strategy_documents", opts)
```

## Monitoring

### Database Stats

```go
func (s *MongoStore) DatabaseStats(ctx context.Context) (*DBStats, error) {
    var result bson.M
    err := s.client.Database("clau_doom").RunCommand(ctx, bson.D{{Key: "dbStats", Value: 1}}).Decode(&result)
    if err != nil {
        return nil, err
    }

    return &DBStats{
        Collections:  result["collections"].(int32),
        DataSize:     result["dataSize"].(int64),
        IndexSize:    result["indexSize"].(int64),
        StorageSize:  result["storageSize"].(int64),
    }, nil
}
```

### Index Usage Stats

```go
func (s *StrategyStore) IndexStats(ctx context.Context) ([]bson.M, error) {
    coll := s.client.Database("clau_doom").Collection("strategy_documents")

    pipeline := bson.A{
        bson.M{"$indexStats": bson.M{}},
    }

    cursor, err := coll.Aggregate(ctx, pipeline)
    if err != nil {
        return nil, err
    }
    defer cursor.Close(ctx)

    var stats []bson.M
    if err := cursor.All(ctx, &stats); err != nil {
        return nil, err
    }

    return stats, nil
}
```

### Slow Query Profiling

```javascript
// Enable profiling for queries > 100ms
db.setProfilingLevel(1, { slowms: 100 });

// View slow queries
db.system.profile.find({
  ns: "clau_doom.strategy_documents",
  millis: { $gt: 100 }
}).sort({ ts: -1 }).limit(10);
```

```go
// Programmatic profiling check
func (s *MongoStore) GetSlowQueries(ctx context.Context, minMs int) ([]bson.M, error) {
    coll := s.client.Database("clau_doom").Collection("system.profile")

    filter := bson.M{
        "ns":     "clau_doom.strategy_documents",
        "millis": bson.M{"$gt": minMs},
    }

    opts := options.Find().SetSort(bson.M{"ts": -1}).SetLimit(10)
    cursor, err := coll.Find(ctx, filter, opts)
    if err != nil {
        return nil, err
    }
    defer cursor.Close(ctx)

    var queries []bson.M
    if err := cursor.All(ctx, &queries); err != nil {
        return nil, err
    }

    return queries, nil
}
```
