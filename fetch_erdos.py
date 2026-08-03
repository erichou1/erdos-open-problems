#!/usr/bin/env python3
"""
Fetch all unsolved (open) Erdős problems and generate LaTeX files.
"""
import os
import re
import time
import yaml

from erdos_ingest import NetworkBoundaryError, fetch_url

BASE_URL = "https://www.erdosproblems.com"
YAML_URL = "https://raw.githubusercontent.com/teorth/erdosproblems/main/data/problems.yaml"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "erdos_problems")
INDIVIDUAL_DIR = os.path.join(OUT_DIR, "individual")

os.makedirs(INDIVIDUAL_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (research bot; collecting Erdos open problems for personal study)"
}
MAX_YAML_BYTES = 16 * 1024 * 1024
MAX_LATEX_BYTES = 4 * 1024 * 1024

def download_yaml():
    print("Downloading problems.yaml...")
    payload = fetch_url(
        YAML_URL,
        timeout=30,
        max_bytes=MAX_YAML_BYTES,
        user_agent=HEADERS["User-Agent"],
    )
    return yaml.safe_load(payload.decode("utf-8"))

def get_open_problems(problems):
    """Return list of problem dicts with state == 'open'."""
    open_probs = []
    for p in problems:
        state = p.get('status', {}).get('state', '')
        if state.lower() == 'open':
            open_probs.append(p)
    return open_probs

def fetch_latex_source(number):
    """Fetch LaTeX source text for a problem number."""
    url = f"{BASE_URL}/latex/{number}"
    try:
        return fetch_url(
            url,
            timeout=20,
            max_bytes=MAX_LATEX_BYTES,
            user_agent=HEADERS["User-Agent"],
        ).decode("utf-8")
    except NetworkBoundaryError:
        raise
    except Exception as e:
        print(f"  WARNING: failed to fetch problem {number}: {e}")
        return None

def extract_latex_content(html, number, prob):
    """
    Extract the LaTeX problem statement and remarks from the HTML page.
    The latex pages contain the raw LaTeX inline.
    """
    # The page shows LaTeX content after navigation. We look for the main content block.
    # The structure seems to be: problem statement first, then remarks, then references.
    
    # Remove script and style tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    
    # Try to extract the main content: after the navigation bar, before the references section
    # Find the raw LaTeX text – it appears as plain text between the navigation and "Back to the problem"
    
    # Look for content between the page chrome
    # The pattern seems to be: after the navigation div, the LaTeX content appears
    
    # Strip all remaining HTML tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Collapse whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    # Find the problem statement: it starts after the navigation junk
    # Look for pattern: after "Random Open" (navigation link), content starts
    # and ends before "References" or "Back to the problem"
    
    # Try to find the actual LaTeX content
    # Strategy: find the block between navigation and references
    marker_start_patterns = [
        r'Random Open\s*\n+(.*?)(?=\n\n### References|\n\nBack to the problem)',
        r'Go\s*\n+(.*?)(?=\n\n### References|\n\nBack to the problem)',
    ]
    
    content = None
    for pat in marker_start_patterns:
        m = re.search(pat, text, re.DOTALL)
        if m:
            content = m.group(1).strip()
            break
    
    if not content:
        # Fallback: take everything that looks like LaTeX
        # Find lines with $...$ or \[ ... \] patterns
        lines = text.split('\n')
        latex_lines = []
        in_content = False
        for line in lines:
            line = line.strip()
            if 'Random Open' in line or ('Go' in line and 'Dual View' in line):
                in_content = True
                continue
            if in_content:
                if 'Back to the problem' in line or line.startswith('[Back to'):
                    break
                if '### References' in line:
                    break
                latex_lines.append(line)
        content = '\n'.join(latex_lines).strip()
    
    # Extract references section
    refs_match = re.search(r'### References\s*\n+(.*?)(?=Back to the problem|$)', text, re.DOTALL)
    refs = refs_match.group(1).strip() if refs_match else ""
    
    return content, refs

def make_individual_tex(number, prob, statement, refs):
    """Generate a standalone LaTeX file for one problem."""
    prize = prob.get('prize', 'no')
    tags = ', '.join(prob.get('tags', []))
    oeis = ', '.join(prob.get('oeis', []))
    last_update = prob.get('status', {}).get('last_update', '')
    comments = prob.get('comments', '')
    
    prize_str = f"Prize: \\${prize[1:]}" if prize.startswith('$') else (f"Prize: {prize}" if prize != 'no' else 'No prize')
    
    content = rf"""\documentclass{{article}}
\usepackage{{amsmath, amssymb, amsthm}}
\usepackage{{hyperref}}
\usepackage{{geometry}}
\geometry{{margin=1in}}

\title{{Erd\H{{o}}s Problem \#{number}}}
\date{{Last updated: {last_update}}}
\author{{Source: erdosproblems.com}}

\begin{{document}}
\maketitle

\noindent\textbf{{Status:}} OPEN \quad \textbf{{{prize_str}}}

\noindent\textbf{{Tags:}} {tags}

\medskip
"""
    if comments:
        content += rf"""\noindent\textbf{{Note:}} {comments}

\medskip
"""

    content += "\n\\noindent\\textbf{Problem Statement:}\n\n"
    content += statement + "\n\n"

    if oeis and oeis != 'N/A':
        content += rf"""\noindent\textbf{{Related OEIS sequences:}} {oeis}

"""

    if refs:
        content += "\\bigskip\n\\noindent\\textbf{References:}\n\n\\begin{itemize}\n"
        for line in refs.strip().split('\n'):
            line = line.strip()
            if line:
                content += f"  \\item {line}\n"
        content += "\\end{itemize}\n\n"

    content += r"""
\bigskip
\noindent\small{Source: \url{https://www.erdosproblems.com/""" + str(number) + r"""}}
\end{document}
"""
    return content

def make_combined_tex(open_problems_data):
    """Generate a single combined LaTeX file with all open problems."""
    header = r"""\documentclass{article}
\usepackage{amsmath, amssymb, amsthm}
\usepackage{hyperref}
\usepackage{geometry}
\usepackage{titlesec}
\geometry{margin=1in}

\title{Erd\H{o}s Open Problems\\[0.5em]\large A Collection of All Currently Unsolved Erd\H{o}s Problems}
\date{Generated: """ + time.strftime("%Y-%m-%d") + r"""}
\author{Source: \url{https://www.erdosproblems.com}}

\begin{document}
\maketitle
\tableofcontents
\newpage

"""

    body = ""
    for number, prob, statement, refs in open_problems_data:
        prize = prob.get('prize', 'no')
        tags = ', '.join(prob.get('tags', []))
        last_update = prob.get('status', {}).get('last_update', '')
        comments = prob.get('comments', '')
        prize_str = f"\\${prize[1:]}" if prize.startswith('$') else (prize if prize != 'no' else 'none')

        body += rf"""
%% ============================================================
\section{{Problem \#{number}}}
\label{{prob:{number}}}

\noindent\textbf{{Status:}} OPEN \quad|\quad \textbf{{Prize:}} {prize_str} \quad|\quad \textbf{{Updated:}} {last_update}

\noindent\textbf{{Tags:}} {tags}

\medskip
"""
        if comments:
            body += rf"\noindent\textit{{{comments}}}" + "\n\n"

        body += "\n\\noindent\\textbf{Statement:}\n\n"
        body += statement + "\n\n"
        body += r"\noindent\rule{\linewidth}{0.4pt}" + "\n\n"

    footer = r"\end{document}" + "\n"
    return header + body + footer

def main():
    # Step 1: Download and parse YAML
    problems = download_yaml()
    print(f"Total problems in database: {len(problems)}")

    open_probs = get_open_problems(problems)
    print(f"Open (unsolved) problems: {len(open_probs)}")

    # Step 2: Fetch LaTeX for each open problem
    all_data = []
    for i, prob in enumerate(open_probs):
        number = prob['number']
        print(f"[{i+1}/{len(open_probs)}] Fetching problem #{number}...", flush=True)

        html = fetch_latex_source(number)
        if html is None:
            statement = f"[Could not retrieve statement for problem \\#{number}. Visit \\url{{https://www.erdosproblems.com/{number}}}]"
            refs = ""
        else:
            statement, refs = extract_latex_content(html, number, prob)
            if not statement:
                statement = f"[Statement not parsed. Visit \\url{{https://www.erdosproblems.com/{number}}}]"

        # Write individual file
        tex = make_individual_tex(number, prob, statement, refs)
        filename = os.path.join(INDIVIDUAL_DIR, f"problem_{number}.tex")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(tex)

        all_data.append((number, prob, statement, refs))

        # Rate limit: be polite to the server
        time.sleep(0.3)

    print(f"\nWrote {len(all_data)} individual .tex files to {INDIVIDUAL_DIR}")

    # Step 3: Write combined file
    combined = make_combined_tex(all_data)
    combined_path = os.path.join(OUT_DIR, "all_open_problems.tex")
    with open(combined_path, 'w', encoding='utf-8') as f:
        f.write(combined)
    print(f"Wrote combined file: {combined_path}")

    # Step 4: Write a README
    readme = f"""# Erdős Open Problems — LaTeX Collection

This repository contains LaTeX files for all currently **open (unsolved)** Erdős problems
from [erdosproblems.com](https://www.erdosproblems.com).

**Generated:** {time.strftime("%Y-%m-%d")}  
**Source database:** https://github.com/teorth/erdosproblems  
**Total open problems collected:** {len(all_data)}

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
"""
    with open(os.path.join(OUT_DIR, "README.md"), 'w') as f:
        f.write(readme)

    print("Done!")
    print(f"Output directory: {OUT_DIR}")

if __name__ == "__main__":
    main()
