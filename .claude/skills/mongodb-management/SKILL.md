---
name: mongodb-management
description: MongoDB index management for knowledge store, document lifecycle operations, backup procedures, monitoring, and schema migrations
user-invocable: false
---

# MongoDB Management for clau-doom Knowledge Store

## Index Management

### Index Strategy

The clau-doom knowledge store uses MongoDB to manage strategy documents retrieved by RAG. Proper indexing is critical for query performance.

```javascript
// Core indexes for strategy_documents collection
db.strategy_documents.createIndex(
    { status: 1, trust_score: -1 },
    { name: "status_trust_idx", background: true }
)

db.strategy_documents.createIndex(
    { tags: 1, generation: -1 },
    { name: "tags_generation_idx", background: true }
)

db.strategy_documents.createIndex(
    { content: "text", title: "text" },
    { name: "fulltext_idx", weights: { title: 10, content: 1 } }
)

db.strategy_documents.createIndex(
    { deprecated_at: 1 },
    { name: "ttl_idx", expireAfterSeconds: 604800 }  // 7 days
)

db.strategy_documents.createIndex(
    { doc_id: 1 },
    { name: "doc_id_unique_idx", unique: true }
)
```

**Index Rationale**:
- `status_trust_idx`: Most queries filter by status (ACTIVE) and sort by trust_score
- `tags_generation_idx`: Tag-based retrieval with recency filtering
- `fulltext_idx`: Full-text search with title weighted higher
- `ttl_idx`: Auto-delete deprecated documents after grace period
- `doc_id_unique_idx`: Prevent duplicate document insertion

### Index Creation Patterns

```python
# Python (pymongo) - Application startup
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT

def initialize_indexes(db):
    """Create all required indexes on application startup."""
    collection = db.strategy_documents

    # Drop existing indexes (except _id)
    collection.drop_indexes()

    # Create indexes
    collection.create_index(
        [("status", ASCENDING), ("trust_score", DESCENDING)],
        name="status_trust_idx",
        background=True
    )

    collection.create_index(
        [("tags", ASCENDING), ("generation", DESCENDING)],
        name="tags_generation_idx",
        background=True
    )

    collection.create_index(
        [("content", TEXT), ("title", TEXT)],
        name="fulltext_idx",
        weights={"title": 10, "content": 1}
    )

    collection.create_index(
        [("deprecated_at", ASCENDING)],
        name="ttl_idx",
        expireAfterSeconds=604800
    )

    collection.create_index(
        [("doc_id", ASCENDING)],
        name="doc_id_unique_idx",
        unique=True
    )
```

```bash
# Background index creation for large collections
mongosh mongodb://localhost:27017/clau_doom --eval '
db.strategy_documents.createIndex(
    { status: 1, trust_score: -1 },
    { background: true }
)
'
```

### Index Performance

```python
# Query plan analysis
def analyze_query_performance(collection, query, sort=None):
    """Analyze query execution plan."""
    cursor = collection.find(query)
    if sort:
        cursor = cursor.sort(sort)

    explain = cursor.explain()

    print(f"Query stages: {explain['executionStats']['executionStages']['stage']}")
    print(f"Docs examined: {explain['executionStats']['totalDocsExamined']}")
    print(f"Docs returned: {explain['executionStats']['nReturned']}")
    print(f"Execution time: {explain['executionStats']['executionTimeMillis']} ms")

    # Check if index was used
    if "inputStage" in explain["executionStats"]["executionStages"]:
        input_stage = explain["executionStats"]["executionStages"]["inputStage"]
        if input_stage.get("stage") == "IXSCAN":
            print(f"Index used: {input_stage['indexName']}")
        else:
            print("WARNING: No index used (COLLSCAN)")

# Example usage
analyze_query_performance(
    db.strategy_documents,
    {"status": "ACTIVE"},
    [("trust_score", -1)]
)
```

```javascript
// Index usage statistics (mongo shell)
db.strategy_documents.aggregate([
    { $indexStats: {} },
    { $project: { name: 1, "accesses.ops": 1 } },
    { $sort: { "accesses.ops": -1 } }
])
```

**Identifying Unused Indexes**:

```python
from datetime import datetime, timedelta

def find_unused_indexes(db, days=30):
    """Find indexes not used in the last N days."""
    pipeline = [
        {"$indexStats": {}},
        {
            "$project": {
                "name": 1,
                "accesses": 1,
                "unused_days": {
                    "$divide": [
                        {"$subtract": [datetime.now(), "$accesses.since"]},
                        1000 * 60 * 60 * 24
                    ]
                }
            }
        },
        {"$match": {"unused_days": {"$gte": days}}}
    ]

    unused = list(db.strategy_documents.aggregate(pipeline))
    for idx in unused:
        print(f"Unused index: {idx['name']} (last used {idx['unused_days']:.0f} days ago)")
```

**Identifying Missing Indexes**:

```python
# Check slow query log
def analyze_slow_queries(db, threshold_ms=100):
    """Parse slow query log to identify missing indexes."""
    # Enable profiling
    db.set_profiling_level(1, slow_ms=threshold_ms)

    # After some time, analyze
    slow_queries = db.system.profile.find({
        "ns": "clau_doom.strategy_documents",
        "millis": {"$gte": threshold_ms}
    })

    for query in slow_queries:
        if query.get("planSummary") == "COLLSCAN":
            print(f"COLLSCAN detected: {query['command']}")
            print(f"Execution time: {query['millis']} ms")
            print(f"Consider adding index on: {list(query['command'].get('filter', {}).keys())}")
```

### Index Maintenance

```bash
# Reindex after major data changes
mongosh mongodb://localhost:27017/clau_doom --eval '
db.strategy_documents.reIndex()
'

# Drop unused indexes
mongosh mongodb://localhost:27017/clau_doom --eval '
db.strategy_documents.dropIndex("unused_index_name")
'

# Compact collection after bulk deletes
mongosh mongodb://localhost:27017/clau_doom --eval '
db.runCommand({ compact: "strategy_documents", force: true })
'
```

## Document Lifecycle Management

### State Machine

```
DRAFT → ACTIVE → DEPRECATED → RETIRED
```

**State Transition Rules**:

| Transition | Condition |
|------------|-----------|
| DRAFT → ACTIVE | quality_score >= 0.5 AND content validated |
| ACTIVE → DEPRECATED | quality_score < 0.3 for 3 consecutive generations |
| DEPRECATED → RETIRED | deprecated_at + 7 days grace period elapsed |
| Any → DRAFT | Manual review requested |

### Transition Operations

```python
from datetime import datetime, timezone

def activate_document(collection, doc_id: str):
    """Transition document from DRAFT to ACTIVE."""
    result = collection.update_one(
        {
            "doc_id": doc_id,
            "status": "DRAFT",
            "quality_score": {"$gte": 0.5}
        },
        {
            "$set": {
                "status": "ACTIVE",
                "activated_at": datetime.now(timezone.utc)
            }
        }
    )

    if result.modified_count == 0:
        raise ValueError(f"Cannot activate {doc_id}: not DRAFT or quality_score < 0.5")


def deprecate_document(collection, doc_id: str, reason: str):
    """Transition document from ACTIVE to DEPRECATED."""
    result = collection.update_one(
        {"doc_id": doc_id, "status": "ACTIVE"},
        {
            "$set": {
                "status": "DEPRECATED",
                "deprecated_at": datetime.now(timezone.utc),
                "deprecation_reason": reason
            }
        }
    )

    if result.modified_count == 0:
        raise ValueError(f"Cannot deprecate {doc_id}: not ACTIVE")


def retire_document(collection, doc_id: str, duckdb_conn):
    """Transition document from DEPRECATED to RETIRED (archive and delete)."""
    doc = collection.find_one({"doc_id": doc_id, "status": "DEPRECATED"})

    if not doc:
        raise ValueError(f"Cannot retire {doc_id}: not DEPRECATED")

    # Check grace period
    deprecated_at = doc["deprecated_at"]
    grace_days = 7
    if (datetime.now(timezone.utc) - deprecated_at).days < grace_days:
        raise ValueError(f"Grace period not elapsed ({grace_days} days required)")

    # Archive to DuckDB
    archive_to_duckdb(duckdb_conn, doc)

    # Delete from MongoDB
    collection.delete_one({"doc_id": doc_id})


def bulk_transition_after_generation(collection, generation_id: int):
    """Batch transition documents after generation evaluation."""
    # Activate high-quality drafts
    activated = collection.update_many(
        {
            "status": "DRAFT",
            "generation": generation_id,
            "quality_score": {"$gte": 0.5}
        },
        {
            "$set": {
                "status": "ACTIVE",
                "activated_at": datetime.now(timezone.utc)
            }
        }
    )

    # Deprecate low-quality active docs
    deprecated = collection.update_many(
        {
            "status": "ACTIVE",
            "low_quality_streak": {"$gte": 3}
        },
        {
            "$set": {
                "status": "DEPRECATED",
                "deprecated_at": datetime.now(timezone.utc),
                "deprecation_reason": "3 consecutive low-quality generations"
            }
        }
    )

    return {
        "activated": activated.modified_count,
        "deprecated": deprecated.modified_count
    }
```

### Quality Score Updates

```python
def compute_quality_score(
    retrieval_success_rate: float,
    author_performance: float,
    recency: float
) -> float:
    """Compute document quality score (0.0-1.0)."""
    return (
        retrieval_success_rate * 0.4 +
        author_performance * 0.3 +
        recency * 0.3
    )


def batch_update_quality_scores(collection, generation_id: int):
    """Update quality scores for all documents after generation."""
    pipeline = [
        {"$match": {"status": {"$in": ["DRAFT", "ACTIVE"]}}},
        {
            "$addFields": {
                "quality_score": {
                    "$add": [
                        {"$multiply": ["$retrieval_success_rate", 0.4]},
                        {"$multiply": ["$author_performance", 0.3]},
                        {"$multiply": ["$recency", 0.3]}
                    ]
                }
            }
        }
    ]

    # Compute scores
    docs = list(collection.aggregate(pipeline))

    # Bulk write
    bulk_ops = [
        {
            "updateOne": {
                "filter": {"_id": doc["_id"]},
                "update": {
                    "$set": {"quality_score": doc["quality_score"]},
                    "$push": {
                        "score_history": {
                            "generation": generation_id,
                            "score": doc["quality_score"],
                            "timestamp": datetime.now(timezone.utc)
                        }
                    }
                }
            }
        }
        for doc in docs
    ]

    if bulk_ops:
        collection.bulk_write(bulk_ops)


def apply_score_decay(collection, decay_rate=0.95):
    """Apply decay formula to aging documents."""
    collection.update_many(
        {"status": "ACTIVE"},
        [
            {
                "$set": {
                    "recency": {"$multiply": ["$recency", decay_rate]}
                }
            }
        ]
    )
```

## Archival to DuckDB

```python
import duckdb
import json

def archive_to_duckdb(duckdb_conn: duckdb.DuckDBPyConnection, doc: dict):
    """Export retired document to DuckDB archive."""
    # Convert MongoDB document to Parquet-compatible format
    archive_record = {
        "doc_id": doc["doc_id"],
        "title": doc["title"],
        "content": doc["content"],
        "tags": json.dumps(doc.get("tags", [])),
        "status": doc["status"],
        "quality_score": doc.get("quality_score", 0.0),
        "trust_score": doc.get("trust_score", 0.0),
        "generation": doc.get("generation", 0),
        "created_at": doc["created_at"].isoformat(),
        "deprecated_at": doc.get("deprecated_at", datetime.now(timezone.utc)).isoformat(),
        "archived_at": datetime.now(timezone.utc).isoformat(),
        "metadata": json.dumps(doc.get("metadata", {}))
    }

    duckdb_conn.execute("""
        INSERT INTO archived_documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, list(archive_record.values()))


def create_archive_table(duckdb_conn: duckdb.DuckDBPyConnection):
    """Create DuckDB archive table schema."""
    duckdb_conn.execute("""
        CREATE TABLE IF NOT EXISTS archived_documents (
            doc_id VARCHAR PRIMARY KEY,
            title VARCHAR,
            content VARCHAR,
            tags VARCHAR,
            status VARCHAR,
            quality_score DOUBLE,
            trust_score DOUBLE,
            generation INTEGER,
            created_at TIMESTAMP,
            deprecated_at TIMESTAMP,
            archived_at TIMESTAMP,
            metadata VARCHAR
        )
    """)


def batch_export_to_parquet(collection, output_path: str):
    """Batch export retired documents to Parquet file."""
    docs = list(collection.find({"status": "RETIRED"}))

    if not docs:
        return

    # Convert to records
    records = [
        {
            "doc_id": doc["doc_id"],
            "title": doc["title"],
            "content": doc["content"],
            "tags": json.dumps(doc.get("tags", [])),
            "quality_score": doc.get("quality_score", 0.0),
            "archived_at": datetime.now(timezone.utc).isoformat()
        }
        for doc in docs
    ]

    # Write to Parquet
    import pandas as pd
    df = pd.DataFrame(records)
    df.to_parquet(output_path, index=False)


def verify_archive(mongo_collection, duckdb_conn):
    """Verify archive integrity (count check)."""
    mongo_retired_count = mongo_collection.count_documents({"status": "RETIRED"})

    duckdb_archived_count = duckdb_conn.execute("""
        SELECT COUNT(*) FROM archived_documents
    """).fetchone()[0]

    if mongo_retired_count != duckdb_archived_count:
        raise ValueError(
            f"Archive mismatch: {mongo_retired_count} in MongoDB, "
            f"{duckdb_archived_count} in DuckDB"
        )
```

## Backup Procedures

### mongodump / mongorestore

```bash
# Full database backup
mongodump \
    --uri="mongodb://localhost:27017/clau_doom" \
    --archive="/backups/clau_doom_$(date +%Y%m%d).archive" \
    --gzip

# Collection-level backup
mongodump \
    --uri="mongodb://localhost:27017/clau_doom" \
    --collection=strategy_documents \
    --archive="/backups/strategy_docs_$(date +%Y%m%d).archive" \
    --gzip

# Point-in-time restore with oplog
mongodump \
    --uri="mongodb://localhost:27017/clau_doom" \
    --oplog \
    --archive="/backups/clau_doom_pit_$(date +%Y%m%d_%H%M).archive" \
    --gzip

# Restore
mongorestore \
    --uri="mongodb://localhost:27017/clau_doom" \
    --archive="/backups/clau_doom_20260207.archive" \
    --gzip \
    --drop
```

### Automated Backup Script

```python
#!/usr/bin/env python3
import subprocess
from datetime import datetime, timedelta
import os
import glob

BACKUP_DIR = "/backups/mongodb"
RETENTION_DAYS = 7
RETENTION_WEEKS = 4
RETENTION_MONTHS = 12

def create_backup():
    """Create date-stamped MongoDB backup."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    archive_path = f"{BACKUP_DIR}/daily/clau_doom_{timestamp}.archive"

    os.makedirs(os.path.dirname(archive_path), exist_ok=True)

    cmd = [
        "mongodump",
        "--uri=mongodb://localhost:27017/clau_doom",
        f"--archive={archive_path}",
        "--gzip"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Backup failed: {result.stderr}")

    print(f"Backup created: {archive_path}")
    return archive_path


def verify_backup(archive_path: str):
    """Verify backup by restoring to temp database."""
    temp_db = "clau_doom_verify_temp"

    cmd = [
        "mongorestore",
        f"--uri=mongodb://localhost:27017/{temp_db}",
        f"--archive={archive_path}",
        "--gzip",
        "--drop"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Verification failed: {result.stderr}")

    # Count documents
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    count = client[temp_db].strategy_documents.count_documents({})

    # Drop temp database
    client.drop_database(temp_db)

    print(f"Backup verified: {count} documents")


def rotate_backups():
    """Apply retention policy (7 daily, 4 weekly, 12 monthly)."""
    now = datetime.now()

    # Daily backups (keep last 7)
    daily_backups = sorted(glob.glob(f"{BACKUP_DIR}/daily/*.archive"))
    for backup in daily_backups[:-RETENTION_DAYS]:
        os.remove(backup)

    # Weekly backups (keep last 4)
    if now.weekday() == 0:  # Monday
        latest_daily = daily_backups[-1]
        weekly_path = f"{BACKUP_DIR}/weekly/clau_doom_week_{now.strftime('%Y%W')}.archive"
        os.makedirs(os.path.dirname(weekly_path), exist_ok=True)
        subprocess.run(["cp", latest_daily, weekly_path])

    weekly_backups = sorted(glob.glob(f"{BACKUP_DIR}/weekly/*.archive"))
    for backup in weekly_backups[:-RETENTION_WEEKS]:
        os.remove(backup)

    # Monthly backups (keep last 12)
    if now.day == 1:  # First day of month
        latest_daily = daily_backups[-1]
        monthly_path = f"{BACKUP_DIR}/monthly/clau_doom_month_{now.strftime('%Y%m')}.archive"
        os.makedirs(os.path.dirname(monthly_path), exist_ok=True)
        subprocess.run(["cp", latest_daily, monthly_path])

    monthly_backups = sorted(glob.glob(f"{BACKUP_DIR}/monthly/*.archive"))
    for backup in monthly_backups[:-RETENTION_MONTHS]:
        os.remove(backup)


if __name__ == "__main__":
    archive = create_backup()
    verify_backup(archive)
    rotate_backups()
```

**Cron schedule** (daily at 2 AM):

```cron
0 2 * * * /usr/bin/python3 /scripts/mongodb_backup.py >> /var/log/mongodb_backup.log 2>&1
```

### Docker Volume Backup

```bash
# Snapshot MongoDB data volume
docker run --rm \
    -v clau_doom_mongodb_data:/source:ro \
    -v /backups/volumes:/backup \
    alpine tar czf /backup/mongodb_data_$(date +%Y%m%d).tar.gz -C /source .

# Cross-host backup with rsync
rsync -avz --delete \
    /var/lib/docker/volumes/clau_doom_mongodb_data/ \
    backup-server:/backups/mongodb/clau_doom/
```

## Monitoring

### Collection Stats

```python
def get_collection_stats(db):
    """Get strategy_documents collection statistics."""
    stats = db.command("collStats", "strategy_documents")

    return {
        "document_count": stats["count"],
        "avg_document_size_bytes": stats.get("avgObjSize", 0),
        "total_storage_size_mb": stats["storageSize"] / (1024 * 1024),
        "total_index_size_mb": stats["totalIndexSize"] / (1024 * 1024),
        "indexes": [
            {
                "name": idx["name"],
                "size_mb": idx["size"] / (1024 * 1024)
            }
            for idx in stats.get("indexSizes", {}).items()
        ]
    }
```

```javascript
// mongo shell interpretation
var stats = db.strategy_documents.stats();
print("Documents: " + stats.count);
print("Avg doc size: " + stats.avgObjSize + " bytes");
print("Storage size: " + (stats.storageSize / 1024 / 1024).toFixed(2) + " MB");
print("Index size: " + (stats.totalIndexSize / 1024 / 1024).toFixed(2) + " MB");
```

### Query Performance Monitoring

```python
def enable_profiling(db, slow_ms=100):
    """Enable query profiling for slow queries."""
    db.set_profiling_level(1, slow_ms=slow_ms)


def analyze_slow_queries(db):
    """Analyze slow query patterns."""
    slow_queries = db.system.profile.find({
        "ns": "clau_doom.strategy_documents",
        "millis": {"$gte": 100}
    }).sort("ts", -1).limit(10)

    for query in slow_queries:
        print(f"\nQuery: {query['command']}")
        print(f"Duration: {query['millis']} ms")
        print(f"Plan: {query.get('planSummary', 'N/A')}")
        print(f"Docs examined: {query.get('docsExamined', 'N/A')}")


def get_query_patterns(db):
    """Aggregate common query patterns."""
    pipeline = [
        {"$match": {"ns": "clau_doom.strategy_documents"}},
        {
            "$group": {
                "_id": "$command.filter",
                "count": {"$sum": 1},
                "avg_millis": {"$avg": "$millis"}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]

    return list(db.system.profile.aggregate(pipeline))
```

### Connection Monitoring

```python
def monitor_connections(db):
    """Monitor MongoDB connection pool."""
    status = db.command("serverStatus")

    connections = status["connections"]
    return {
        "current": connections["current"],
        "available": connections["available"],
        "total_created": connections["totalCreated"],
        "active": connections.get("active", 0),
        "utilization_pct": (connections["current"] /
                           (connections["current"] + connections["available"]) * 100)
    }


def monitor_active_operations(db):
    """Monitor currently executing operations."""
    ops = db.current_op({"active": True})

    long_running = [
        {
            "opid": op["opid"],
            "op": op["op"],
            "ns": op.get("ns", "N/A"),
            "duration_secs": op.get("secs_running", 0)
        }
        for op in ops.get("inprog", [])
        if op.get("secs_running", 0) > 10
    ]

    return long_running
```

### Alerting Thresholds

```python
from dataclasses import dataclass

@dataclass
class MonitoringThresholds:
    collection_size_mb: float = 1024.0
    slow_query_ms: int = 100
    connection_utilization_pct: float = 80.0
    replication_lag_secs: int = 10

def check_alerts(db, thresholds: MonitoringThresholds):
    """Check monitoring thresholds and generate alerts."""
    alerts = []

    # Collection size
    stats = db.command("collStats", "strategy_documents")
    size_mb = stats["storageSize"] / (1024 * 1024)
    if size_mb > thresholds.collection_size_mb:
        alerts.append(f"ALERT: Collection size {size_mb:.1f} MB exceeds threshold")

    # Slow queries
    slow_count = db.system.profile.count_documents({"millis": {"$gte": thresholds.slow_query_ms}})
    if slow_count > 10:
        alerts.append(f"ALERT: {slow_count} slow queries detected")

    # Connection utilization
    conn_status = monitor_connections(db)
    if conn_status["utilization_pct"] > thresholds.connection_utilization_pct:
        alerts.append(
            f"ALERT: Connection pool {conn_status['utilization_pct']:.1f}% utilized"
        )

    return alerts
```

## Schema Migrations

### Migration Pattern

```python
class Migration:
    """Base migration class."""
    version: int
    description: str

    def forward(self, db):
        """Apply migration."""
        raise NotImplementedError

    def verify(self, db):
        """Verify migration succeeded."""
        raise NotImplementedError


class Migration001AddTrustScore(Migration):
    version = 1
    description = "Add trust_score field with default value"

    def forward(self, db):
        result = db.strategy_documents.update_many(
            {"trust_score": {"$exists": False}},
            {"$set": {"trust_score": 0.5}}
        )
        print(f"Updated {result.modified_count} documents")

    def verify(self, db):
        count_without = db.strategy_documents.count_documents(
            {"trust_score": {"$exists": False}}
        )
        if count_without > 0:
            raise ValueError(f"{count_without} documents still missing trust_score")


class Migration002AddSchemaVersion(Migration):
    version = 2
    description = "Add schema_version field"

    def forward(self, db):
        result = db.strategy_documents.update_many(
            {},
            {"$set": {"schema_version": 2}}
        )
        print(f"Updated {result.modified_count} documents")

    def verify(self, db):
        count = db.strategy_documents.count_documents({"schema_version": 2})
        total = db.strategy_documents.count_documents({})
        if count != total:
            raise ValueError(f"Only {count}/{total} documents migrated")


def run_migrations(db):
    """Run pending migrations on application startup."""
    # Get current schema version
    current_version = db.metadata.find_one({"_id": "schema_version"})
    current = current_version["version"] if current_version else 0

    migrations = [
        Migration001AddTrustScore(),
        Migration002AddSchemaVersion(),
    ]

    pending = [m for m in migrations if m.version > current]

    if not pending:
        print("No pending migrations")
        return

    for migration in pending:
        print(f"Running migration {migration.version}: {migration.description}")
        migration.forward(db)
        migration.verify(db)

        # Update schema version
        db.metadata.update_one(
            {"_id": "schema_version"},
            {"$set": {"version": migration.version}},
            upsert=True
        )
```

### Common Migration Examples

```python
# Rename field
db.strategy_documents.update_many(
    {},
    {"$rename": {"old_field_name": "new_field_name"}}
)

# Change field type (string to integer)
db.strategy_documents.find({"generation": {"$type": "string"}}).forEach(function(doc) {
    db.strategy_documents.update(
        {"_id": doc._id},
        {"$set": {"generation": parseInt(doc.generation)}}
    );
});

# Add new index
db.strategy_documents.createIndex(
    {"new_field": 1},
    {"background": true}
)

# Split collection (archive old documents)
db.strategy_documents.find({"status": "RETIRED"}).forEach(function(doc) {
    db.archived_documents.insert(doc);
    db.strategy_documents.remove({"_id": doc._id});
});
```

## Aggregation Pipelines for RAG

### Top Documents by Trust Score

```python
def get_top_documents(collection, n=10):
    """Retrieve top N active documents by trust score."""
    pipeline = [
        {"$match": {"status": "ACTIVE"}},
        {"$sort": {"trust_score": -1}},
        {"$limit": n},
        {
            "$project": {
                "doc_id": 1,
                "title": 1,
                "content": 1,
                "tags": 1,
                "trust_score": 1,
                "quality_score": 1
            }
        }
    ]

    return list(collection.aggregate(pipeline))
```

### Tag-Based Retrieval Analytics

```python
def analyze_tag_performance(collection):
    """Aggregate trust scores by tag."""
    pipeline = [
        {"$match": {"status": "ACTIVE"}},
        {"$unwind": "$tags"},
        {
            "$group": {
                "_id": "$tags",
                "avg_trust_score": {"$avg": "$trust_score"},
                "count": {"$sum": 1},
                "max_trust": {"$max": "$trust_score"}
            }
        },
        {"$sort": {"avg_trust_score": -1}}
    ]

    return list(collection.aggregate(pipeline))
```

### Generation Performance Summary

```python
def get_generation_summary(collection, generation_id: int):
    """Statistics for a specific generation."""
    pipeline = [
        {"$match": {"generation": generation_id}},
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "avg_trust": {"$avg": "$trust_score"},
                "avg_quality": {"$avg": "$quality_score"}
            }
        }
    ]

    return list(collection.aggregate(pipeline))
```

## Anti-Patterns to Avoid

**Missing indexes on frequently queried fields**:
```python
# BAD: No index on status
db.strategy_documents.find({"status": "ACTIVE"})  # COLLSCAN

# GOOD: Create compound index
db.strategy_documents.createIndex({"status": 1, "trust_score": -1})
```

**Not archiving before deleting documents**:
```python
# BAD: Direct delete
db.strategy_documents.delete_many({"status": "RETIRED"})

# GOOD: Archive first
docs = list(db.strategy_documents.find({"status": "RETIRED"}))
for doc in docs:
    archive_to_duckdb(duckdb_conn, doc)
db.strategy_documents.delete_many({"status": "RETIRED"})
```

**Skipping backup verification**:
```bash
# BAD: Trust backup without verification
mongodump --archive=backup.archive --gzip

# GOOD: Verify by restoring to temp database
mongorestore --uri="mongodb://localhost:27017/verify_temp" --archive=backup.archive --gzip
```

**Large batch updates without writeConcern**:
```python
# BAD: No acknowledgment
db.strategy_documents.update_many({}, {"$set": {"new_field": "value"}})

# GOOD: Confirm writes
result = db.strategy_documents.update_many(
    {},
    {"$set": {"new_field": "value"}},
    write_concern={"w": 1}
)
print(f"Updated {result.modified_count} documents")
```

**Not monitoring index hit rates**:
```python
# GOOD: Regularly check index usage
pipeline = [{"$indexStats": {}}]
stats = list(db.strategy_documents.aggregate(pipeline))
for idx in stats:
    if idx["accesses"]["ops"] == 0:
        print(f"Unused index: {idx['name']}")
```

**Schema changes without migration scripts**:
```python
# BAD: Ad-hoc update
db.strategy_documents.update_many({}, {"$set": {"new_field": "default"}})

# GOOD: Version-controlled migration
class Migration003AddNewField(Migration):
    version = 3
    description = "Add new_field with default value"
    # ... migration logic
```
