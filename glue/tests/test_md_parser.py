"""Tests for MD parser."""

import pytest

from glue.md_parser import MDParser

TEMPLATE_PATH = "research/templates/DOOM_PLAYER_GEN1.md"


def test_parse_template_basic():
    template = "memory_weight: ${MEMORY_WEIGHT}"
    result = MDParser.parse_template(template, {"MEMORY_WEIGHT": "0.3"})
    assert result == "memory_weight: 0.3"


def test_parse_template_multiple():
    template = "${MEMORY_WEIGHT} and ${STRENGTH_WEIGHT}"
    result = MDParser.parse_template(
        template, {"MEMORY_WEIGHT": "0.3", "STRENGTH_WEIGHT": "0.7"}
    )
    assert result == "0.3 and 0.7"


def test_parse_template_undefined():
    template = "${UNDEFINED_VAR}"
    with pytest.raises(KeyError, match="UNDEFINED_VAR"):
        MDParser.parse_template(template, {})


def test_extract_variables():
    content = "${MEMORY_WEIGHT} and ${STRENGTH_WEIGHT} and ${MEMORY_WEIGHT}"
    vars_found = MDParser.extract_variables(content)
    assert set(vars_found) == {"MEMORY_WEIGHT", "STRENGTH_WEIGHT"}


def test_extract_variables_empty():
    assert MDParser.extract_variables("no variables here") == []


def test_load_agent_config():
    config = MDParser.load_agent_config(TEMPLATE_PATH)
    assert "parameters" in config
    params = config["parameters"]
    assert "health_threshold" in params
    assert params["health_threshold"] == 0.3


def test_load_agent_config_decision_hierarchy():
    config = MDParser.load_agent_config(TEMPLATE_PATH)
    assert "decision_hierarchy" in config
    dh = config["decision_hierarchy"]
    assert dh.get("L0 (MD Rules)") is True
    # L1 and L2 are template variables before substitution
    assert dh.get("L1 (DuckDB Cache)") == "${L1_ENABLED}"
    assert dh.get("L2 (OpenSearch kNN)") == "${L2_ENABLED}"


def test_parse_template_preserves_surrounding():
    template = "before ${VAR} after"
    result = MDParser.parse_template(template, {"VAR": "value"})
    assert result == "before value after"
