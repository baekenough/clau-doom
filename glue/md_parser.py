"""MD parser: Agent MD template variable substitution for DOE factor injection."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

VARIABLE_PATTERN = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")


class MDParser:
    """Parses and substitutes variables in agent MD templates."""

    @staticmethod
    def parse_template(md_content: str, variables: dict[str, str]) -> str:
        """Replace ${VARIABLE_NAME} placeholders with values from dict.

        Raises KeyError for undefined variables.
        """

        def replacer(match: re.Match) -> str:
            var_name = match.group(1)
            if var_name not in variables:
                raise KeyError(f"Undefined variable: ${{{var_name}}}")
            return str(variables[var_name])

        return VARIABLE_PATTERN.sub(replacer, md_content)

    @staticmethod
    def extract_variables(md_content: str) -> list[str]:
        """Return list of all unique ${VARIABLE} placeholder names."""
        return list(set(VARIABLE_PATTERN.findall(md_content)))

    @staticmethod
    def load_agent_config(md_path: str | Path) -> dict[str, Any]:
        """Parse agent MD file sections into a nested dict.

        Extracts sections starting with ## and key-value pairs in list items.
        """
        content = Path(md_path).read_text()
        config: dict[str, Any] = {}

        current_section = ""
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("## "):
                current_section = line[3:].strip().lower().replace(" ", "_")
                config[current_section] = {}
            elif line.startswith("- ") and current_section:
                parts = line[2:].split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value_str = parts[1].strip()
                    value: Any = value_str
                    # Try to parse numeric values
                    try:
                        if "." in value_str:
                            value = float(value_str)
                        else:
                            value = int(value_str)
                    except (ValueError, TypeError):
                        if value_str.upper() in ("ENABLED", "TRUE"):
                            value = True
                        elif value_str.upper() in ("DISABLED", "FALSE"):
                            value = False
                    config[current_section][key] = value

        return config
