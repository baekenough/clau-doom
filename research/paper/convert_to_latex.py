#!/usr/bin/env python3
"""Convert PAPER_DRAFT.md (mixed markdown/LaTeX) to proper NeurIPS LaTeX format.

This script reads PAPER_DRAFT.md from the same directory and outputs PAPER_DRAFT.tex.
The input is a mixed markdown/LaTeX file that already contains LaTeX environments
(figure, table, math) and citations. The conversion adds NeurIPS preamble,
converts markdown headings and formatting, and wraps everything in proper
document structure.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def is_latex_environment_line(line: str) -> bool:
    """Check if line is part of a LaTeX environment."""
    latex_patterns = [
        r"^\\begin\{",
        r"^\\end\{",
        r"^\\centering",
        r"^\\includegraphics",
        r"^\\caption",
        r"^\\label",
        r"^\\toprule",
        r"^\\midrule",
        r"^\\bottomrule",
        r"^\\bibitem",
        r"^\s*\\noindent",
        r"^\s*\$\$",  # Display math
        r"^---$",  # Horizontal rule (will be removed)
    ]
    return any(re.match(pattern, line.strip()) for pattern in latex_patterns)


def convert_markdown_inline(text: str) -> str:
    """Convert markdown inline formatting to LaTeX.

    Handles **bold**, *italic*, but avoids converting inside math mode or LaTeX commands.
    """
    if not text.strip():
        return text

    # Skip lines that are already pure LaTeX
    if is_latex_environment_line(text):
        return text

    # Split by math delimiters to avoid converting inside math
    parts = re.split(r"(\$[^\$]+\$)", text)
    result_parts = []

    for i, part in enumerate(parts):
        # Odd indices are math mode content
        if i % 2 == 1:
            result_parts.append(part)
            continue

        # Even indices are regular text
        # Convert **bold** -> \textbf{bold}, but not inside LaTeX commands
        part = re.sub(
            r"\*\*([^\*]+)\*\*",
            lambda m: rf"\textbf{{{m.group(1)}}}" if not re.search(r"\\[a-zA-Z]+", m.group(1)) else m.group(0),
            part
        )

        # Convert *italic* -> \textit{italic}, but not inside LaTeX commands or ** patterns
        # Use negative lookahead/lookbehind to avoid ** patterns
        part = re.sub(
            r"(?<!\*)\*(?!\*)([^\*]+?)(?<!\*)\*(?!\*)",
            lambda m: rf"\textit{{{m.group(1)}}}" if not re.search(r"\\[a-zA-Z]+", m.group(1)) else m.group(0),
            part
        )

        result_parts.append(part)

    return "".join(result_parts)


def process_markdown_list(lines: List[str], start_idx: int) -> Tuple[str, int]:
    """Process markdown list (enumerated or itemized) and return LaTeX + next index.

    Returns:
        (latex_string, next_line_index)
    """
    if start_idx >= len(lines):
        return "", start_idx

    first_line = lines[start_idx].strip()
    is_enumerated = bool(re.match(r"^\d+\.", first_line))

    list_items = []
    i = start_idx

    # Collect all consecutive list items
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            break

        if is_enumerated:
            match = re.match(r"^\d+\.\s+(.+)$", line)
            if not match:
                break
            list_items.append(match.group(1))
        else:
            match = re.match(r"^[-*]\s+(.+)$", line)
            if not match:
                break
            list_items.append(match.group(1))

        i += 1

    # Generate LaTeX
    env_name = "enumerate" if is_enumerated else "itemize"
    latex_lines = [rf"\begin{{{env_name}}}"]

    for item in list_items:
        # Convert inline markdown in list items
        item_text = convert_markdown_inline(item)
        latex_lines.append(rf"\item {item_text}")

    latex_lines.append(rf"\end{{{env_name}}}")

    return "\n".join(latex_lines), i


def extract_abstract(lines: List[str]) -> Tuple[str, List[str]]:
    """Extract abstract and return (abstract_text, remaining_lines)."""
    abstract_text = ""
    remaining = []
    in_abstract = False
    abstract_started = False

    for line in lines:
        stripped = line.strip()

        # Look for **Abstract**:
        if re.match(r"^\*\*Abstract\*\*:", stripped):
            in_abstract = True
            abstract_started = True
            # Extract text after "**Abstract**:"
            abstract_content = re.sub(r"^\*\*Abstract\*\*:\s*", "", stripped)
            if abstract_content:
                abstract_text = abstract_content + " "
            continue

        if in_abstract:
            # Stop at next section or blank line followed by ##
            if re.match(r"^#+\s", stripped) or re.match(r"^\*\*Authors\*\*", stripped):
                in_abstract = False
                remaining.append(line)
            elif stripped:
                abstract_text += stripped + " "
            else:
                # Blank line within abstract - continue
                pass
        else:
            remaining.append(line)

    return abstract_text.strip(), remaining


def skip_authors_and_affiliation(lines: List[str]) -> List[str]:
    """Skip **Authors**: and **¹Affiliation**: lines."""
    result = []
    skip_next = False

    for line in lines:
        stripped = line.strip()
        if re.match(r"^\*\*Authors\*\*:", stripped):
            skip_next = True
            continue
        if re.match(r"^\*\*[¹\d]+Affiliation\*\*:", stripped):
            continue
        if skip_next and not stripped:
            skip_next = False
            continue

        result.append(line)

    return result


def convert_heading(line: str) -> str:
    """Convert markdown heading to LaTeX section command."""
    match = re.match(r"^(#+)\s+(\d+\.)+\s*(.+)$", line.strip())
    if not match:
        # No numbering
        match = re.match(r"^(#+)\s+(.+)$", line.strip())
        if not match:
            return line
        level = len(match.group(1))
        title = match.group(2)
    else:
        level = len(match.group(1))
        title = match.group(3)  # Remove numbering

    # Map heading levels
    if level == 1:
        return ""  # Title is in preamble
    elif level == 2:
        return rf"\section{{{title}}}"
    elif level == 3:
        return rf"\subsection{{{title}}}"
    elif level == 4:
        return rf"\subsubsection{{{title}}}"
    else:
        return rf"\paragraph{{{title}}}"


def convert_document(input_path: Path, output_path: Path) -> None:
    """Convert markdown/LaTeX mixed document to pure LaTeX."""
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Extract abstract first
    abstract_text, lines = extract_abstract(lines)

    # Skip authors and affiliation lines
    lines = skip_authors_and_affiliation(lines)

    # Start building output
    output_lines = []

    # Add NeurIPS preamble
    output_lines.extend([
        r"\documentclass{article}",
        r"\usepackage[preprint]{neurips_2025}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage{hyperref}",
        r"\usepackage{url}",
        r"\usepackage{booktabs}",
        r"\usepackage{amsfonts}",
        r"\usepackage{amsmath}",
        r"\usepackage{nicefrac}",
        r"\usepackage{microtype}",
        r"\usepackage{graphicx}",
        r"\usepackage{natbib}",
        "",
        r"\title{Movement Is All You Need: How 29 Systematic Experiments Falsified RAG-Based FPS Game Agent Optimization}",
        "",
        r"\author{",
        r"  Sang Yi \\",
        r"  [Affiliation to be added] \\",
        r"  \texttt{[email to be added]} \\",
        r"  \And",
        r"  Claude Code \\",
        r"  Anthropic \\",
        r"  AI Co-Investigator \\",
        r"}",
        "",
        r"\begin{document}",
        "",
        r"\maketitle",
        "",
    ])

    # Add abstract
    if abstract_text:
        output_lines.extend([
            r"\begin{abstract}",
            abstract_text,
            r"\end{abstract}",
            "",
        ])

    # Process body
    i = 0
    in_latex_env = False
    env_stack = []
    in_biblio = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip title line (first # heading)
        if i == 0 and re.match(r"^#\s+", stripped):
            i += 1
            continue

        # Handle horizontal rules
        if stripped == "---":
            output_lines.append("")  # Convert to blank line
            i += 1
            continue

        # Check for bibliography start
        if re.match(r"^\\bibitem", stripped):
            if not in_biblio:
                output_lines.append(r"\begin{thebibliography}{50}")
                in_biblio = True

        # Check for LaTeX environment start
        if re.match(r"^\\begin\{", stripped):
            in_latex_env = True
            match = re.match(r"^\\begin\{([^\}]+)\}", stripped)
            if match:
                env_stack.append(match.group(1))

        # Check for LaTeX environment end
        if re.match(r"^\\end\{", stripped):
            if env_stack:
                env_stack.pop()
            if not env_stack:
                in_latex_env = False

        # Pass through LaTeX environment lines unchanged
        if in_latex_env or is_latex_environment_line(line):
            output_lines.append(line.rstrip())
            i += 1
            continue

        # Handle markdown headings
        if re.match(r"^#+\s", stripped):
            latex_heading = convert_heading(line)
            if latex_heading:
                output_lines.append(latex_heading)
                i += 1
                continue

        # Handle markdown lists
        if re.match(r"^(\d+\.|-|\*)\s", stripped):
            list_latex, next_i = process_markdown_list(lines, i)
            output_lines.append(list_latex)
            i = next_i
            continue

        # Handle special paragraph markers
        if re.match(r"^\*\*Acknowledgments\*\*:", stripped):
            output_lines.append(r"\section*{Acknowledgments}")
            # Extract content after marker
            content = re.sub(r"^\*\*Acknowledgments\*\*:\s*", "", stripped)
            if content:
                output_lines.append(convert_markdown_inline(content))
            i += 1
            continue

        if re.match(r"^\*\*Reproducibility\*\*:", stripped):
            output_lines.append(r"\paragraph{Reproducibility}")
            content = re.sub(r"^\*\*Reproducibility\*\*:\s*", "", stripped)
            if content:
                output_lines.append(convert_markdown_inline(content))
            i += 1
            continue

        # Regular paragraph - convert inline markdown
        if stripped:
            converted = convert_markdown_inline(line)
            output_lines.append(converted.rstrip())
        else:
            output_lines.append("")

        i += 1

    # Close bibliography if opened
    if in_biblio:
        output_lines.append(r"\end{thebibliography}")

    # Add document end
    output_lines.append("")
    output_lines.append(r"\end{document}")

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    input_file = script_dir / "PAPER_DRAFT.md"
    output_file = script_dir / "PAPER_DRAFT.tex"

    if not input_file.exists():
        print(f"Error: {input_file} not found", file=sys.stderr)
        return 1

    try:
        convert_document(input_file, output_file)
        print(f"✓ Converted {input_file.name} → {output_file.name}")
        print(f"  Output: {output_file}")
        return 0
    except Exception as e:
        print(f"✗ Conversion failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
