# LaTeX Conversion Script

## Overview

`convert_to_latex.py` converts the mixed markdown/LaTeX `PAPER_DRAFT.md` to a proper NeurIPS 2025 LaTeX document `PAPER_DRAFT.tex`.

## Usage

```bash
# From the paper directory
./convert_to_latex.py

# Or with explicit python3
python3 convert_to_latex.py
```

## Input Format

The script expects `PAPER_DRAFT.md` in the same directory. The input file is a **mixed markdown/LaTeX** document that already contains:

- LaTeX figure environments (`\begin{figure}...\end{figure}`)
- LaTeX table environments (`\begin{table}...\end{table}`)
- LaTeX math (`$...$`, `$$...$$`)
- LaTeX citations (`\cite{...}`, `\citet{...}`)
- LaTeX labels (`\label{...}`) and references (`\ref{...}`)
- `\bibitem` bibliography entries

## Conversion Process

The script performs the following transformations:

### 1. Document Structure
- Adds NeurIPS 2025 preamble with required packages
- Extracts and wraps abstract in `\begin{abstract}...\end{abstract}`
- Skips author lines (handled in preamble)
- Adds `\maketitle`, `\begin{document}`, `\end{document}`

### 2. Markdown → LaTeX
- `## Section` → `\section{Section}`
- `### Subsection` → `\subsection{Subsection}`
- `#### Subsubsection` → `\subsubsection{Subsubsection}`
- Removes section numbering (LaTeX auto-numbers)

### 3. Inline Formatting
- `**bold**` → `\textbf{bold}` (skips inside LaTeX commands and math)
- `*italic*` → `\textit{italic}` (skips inside LaTeX commands and math)
- Preserves math mode content unchanged

### 4. Lists
- `1. item` → `\begin{enumerate}\item ...\end{enumerate}`
- `- item` or `* item` → `\begin{itemize}\item ...\end{itemize}`

### 5. Special Sections
- `**Acknowledgments**:` → `\section*{Acknowledgments}`
- `**Reproducibility**:` → `\paragraph{Reproducibility}`
- `\bibitem` entries → wrapped in `\begin{thebibliography}{50}...\end{thebibliography}`

### 6. Preservation
- **All existing LaTeX environments pass through unchanged**
- Figure, table, math, citation environments preserved
- No modification of content inside LaTeX environments

## Output

The script generates `PAPER_DRAFT.tex` in the same directory.

### Output Structure
```latex
\documentclass{article}
\usepackage[preprint]{neurips_2025}
... [packages]

\title{...}
\author{...}

\begin{document}
\maketitle

\begin{abstract}
...
\end{abstract}

\section{Introduction}
...

\begin{thebibliography}{50}
\bibitem{...}
...
\end{thebibliography}

\end{document}
```

## Compilation

After generating `PAPER_DRAFT.tex`, compile with:

```bash
pdflatex PAPER_DRAFT.tex
bibtex PAPER_DRAFT
pdflatex PAPER_DRAFT.tex
pdflatex PAPER_DRAFT.tex
```

Or use `latexmk`:
```bash
latexmk -pdf PAPER_DRAFT.tex
```

## Edge Cases Handled

### Math Mode Protection
The script detects `$...$` delimiters and skips inline markdown conversion inside math:
- `$**x**$` stays as `$**x**$` (not converted to `$\textbf{x}$`)

### LaTeX Command Protection
Lines starting with LaTeX commands are passed through unchanged:
- `\begin{figure}`, `\centering`, `\includegraphics`, etc.

### List Nesting
Handles both numbered and bulleted lists with proper LaTeX environments.

### Empty Lines
Preserves paragraph breaks and spacing.

## Troubleshoties

### Missing abstract
- Check that `**Abstract**:` appears in `PAPER_DRAFT.md`
- Abstract extraction stops at first `##` heading or `**Authors**`

### Malformed lists
- Ensure list items start with `1. `, `- `, or `* ` at line start
- Lists must have consecutive items (blank lines end the list)

### Bibliography not wrapped
- Check that bibliography entries start with `\bibitem`
- Script auto-detects first `\bibitem` and wraps in `thebibliography`

### LaTeX errors during compilation
- Check that all `\begin{}` have matching `\end{}`
- Verify citation keys exist in bibliography
- Ensure all required packages are installed

## Script Location

- **Path**: `/Users/sangyi/workspace/research/clau-doom/research/paper/convert_to_latex.py`
- **Input**: `PAPER_DRAFT.md` (same directory)
- **Output**: `PAPER_DRAFT.tex` (same directory)

## Dependencies

- Python 3.x (system python3)
- Standard library only (no external packages required)
