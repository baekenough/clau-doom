"""Root pytest conftest: prevent collection of test_* functions in source modules."""

collect_ignore_glob = [
    "glue/analysis/*",
    "glue/validation/*",
    "glue/data/*",
]
