# Erdős Open Problems — LaTeX Collection

This repository contains LaTeX files for all currently **open (unsolved)** Erdős problems
from [erdosproblems.com](https://www.erdosproblems.com).

**Generated:** 2026-06-09  
**Source database:** https://github.com/teorth/erdosproblems  
**Total open problems collected:** 622

## Structure

- `all_open_problems.tex` — Single combined LaTeX file with all problems, table of contents, separated by section
- `individual/problem_NNN.tex` — One LaTeX file per problem

## Compile

```bash
pdflatex all_open_problems.tex
```

Or for an individual problem:
```bash
pdflatex individual/problem_1.tex
```

## Source

Problems sourced from Tom Bloom's [Erdős Problems](https://www.erdosproblems.com) database,
which is openly maintained at https://github.com/teorth/erdosproblems.

This repository is auto-generated for research and study purposes.
