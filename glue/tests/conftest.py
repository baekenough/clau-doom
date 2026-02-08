"""Pytest configuration for glue tests."""

# Tell pytest not to collect test functions from source modules
collect_ignore = [
    "../analysis/statistical_tests.py",
    "../analysis/diagnostics.py",
]
