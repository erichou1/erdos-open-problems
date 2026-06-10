#!/usr/bin/env python3
"""
Fetch verifiable and falsifiable Erdős problems and generate LaTeX files.
Also reorganizes the open problems into their own subfolder for consistency.
"""
import os
import re
import time
import yaml
import requests

import warnings
warnings.filterwarnings('ignore')

BASE_URL = "https://www.erdosproblems.com"
YAML_URL = "https://raw.githubusercontent.com/teorth/erdosproblems/main/data/problems.yaml"
REPO_DIR = "/Users/eric/workspace/erdos/erdos_problems"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (research bot; collecting Erdos problems for personal study)"
}

CATEGORIES = {
    "open":        {"states": ["open"],        "label": "Open (Unsolved)"},
    "verifiable":  {"states": ["verifiable"],  "label": "Verifiable"},
    "falsifiable": {"states": ["falsifiable"], "label": "Falsifiable"},
}


def download_yaml():
    print("Downloading problems.yaml...")
    r = requests.get(YAML_URL, headers=HEADERS, timeout=30, verify=False)
    r.raise_for_status()
    return yaml.safe_load(r.text)


def filter_problems(problems, states):
    return [p for p in problems if p.get('status', {}).get('state', '').lower() in states]


def fetch_latex_source(number):
    url = f"{BASE_URL}/latex/{number}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"  WARNING: failed to fetch problem {number}: {e}")
        return None


def extract_latex_content(html):
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    content = None
    for pat in [
        r'Random Open\s*\n+(.*?)(?=\n\n### References|\n\nBack to the problem)',
        r'Go\s*\n+(.*?)(?=\n\n### References|\n\nBack to the problem)',
    ]:
        m = re.search(pat, text, re.DOTALL)
        if m:
            content = m.group(1).strip()
            break

    if not content:
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

    refs_match = re.search(r'### References\s*\n+(.*?)(?=Back to the problem|$)', text, re.DOTALL)
    refs = refs_match.group(1).strip() if refs_match else ""
    return content, refs


def make_individual_tex(number, prob, statement, refs):
    state = prob.get('status', {}).get('state', 'unknown')
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

\noindent\textbf{{Status:}} {state.upper()} \quad \textbf{{{prize_str}}}

\noindent\textbf{{Tags:}} {tags}

\medskip
"""
    if comments:
        content += rf"\noindent\textbf{{Note:}} {comments}" + "\n\n\\medskip\n"

    content += "\n\\noindent\\textbf{Problem Statement:}\n\n"
    content += statement + "\n\n"

    if oeis and oeis != 'N/A':
        content += rf"\noindent\textbf{{Related OEIS sequences:}} {oeis}" + "\n\n"

    if refs:
        content += "\\bigskip\n\\noindent\\textbf{References:}\n\n\\begin{itemize}\n"
        for line in refs.strip().split('\n'):
            line = line.strip()
            if line:
                content += f"  \\item {line}\n"
        content += "\\end{itemize}\n\n"

    content += r"\bigskip" + "\n"
    content += r"\noindent\small{Source: \url{https://www.erdosproblems.com/" + str(number) + r"}}" + "\n"
    content += r"\end{document}" + "\n"
    return content


def make_combined_tex(problems_data, category_label):
    header = rf"""\documentclass{{article}}
\usepackage{{amsmath, amssymb, amsthm}}
\usepackage{{hyperref}}
\usepackage{{geometry}}
\usepackage{{titlesec}}
\geometry{{margin=1in}}

\title{{Erd\H{{o}}s Problems --- {category_label}\\[0.5em]\large A Collection of {len(problems_data)} Problems}}
\date{{Generated: {time.strftime("%Y-%m-%d")}}}
\author{{Source: \url{{https://www.erdosproblems.com}}}}

\begin{{document}}
\maketitle
\tableofcontents
\newpage

"""

    body = ""
    for number, prob, statement, refs in problems_data:
        state = prob.get('status', {}).get('state', 'unknown')
        prize = prob.get('prize', 'no')
        tags = ', '.join(prob.get('tags', []))
        last_update = prob.get('status', {}).get('last_update', '')
        comments = prob.get('comments', '')
        prize_str = f"\\${prize[1:]}" if prize.startswith('$') else (prize if prize != 'no' else 'none')

        body += rf"""
%% ============================================================
\section{{Problem \#{number}}}
\label{{prob:{number}}}

\noindent\textbf{{Status:}} {state.upper()} \quad|\quad \textbf{{Prize:}} {prize_str} \quad|\quad \textbf{{Updated:}} {last_update}

\noindent\textbf{{Tags:}} {tags}

\medskip
"""
        if comments:
            body += rf"\noindent\textit{{{comments}}}" + "\n\n"

        body += "\n\\noindent\\textbf{Statement:}\n\n"
        body += statement + "\n\n"
        body += r"\noindent\rule{\linewidth}{0.4pt}" + "\n\n"

    body += r"\end{document}" + "\n"
    return header + body


def process_category(cat_key, cat_info, problems):
    label = cat_info["label"]
    states = cat_info["states"]

    cat_dir = os.path.join(REPO_DIR, cat_key)
    ind_dir = os.path.join(cat_dir, "individual")
    os.makedirs(ind_dir, exist_ok=True)

    filtered = filter_problems(problems, states)
    print(f"\n--- {label} ({len(filtered)} problems) ---")

    # Skip fetching for open problems — files already exist in individual/
    # Just create the category folder structure with symlinks or copies
    if cat_key == "open":
        # For open, we already have individual/ at top level; just create
        # the category folder with a combined file (reuse existing individual files
        # by copying them into open/individual/)
        existing_ind = os.path.join(REPO_DIR, "individual")
        if os.path.isdir(existing_ind):
            print(f"  Copying existing open problem files into {ind_dir}...")
            import shutil
            for fname in os.listdir(existing_ind):
                src = os.path.join(existing_ind, fname)
                dst = os.path.join(ind_dir, fname)
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
            # Build all_data from existing files (no re-fetching)
            all_data = []
            for prob in filtered:
                number = prob['number']
                fpath = os.path.join(existing_ind, f"problem_{number}.tex")
                if os.path.exists(fpath):
                    with open(fpath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Extract statement between "Problem Statement:" and next \n\n
                    m = re.search(r'\\noindent\\textbf\{Problem Statement:\}\n\n(.*?)\n\n', content, re.DOTALL)
                    statement = m.group(1).strip() if m else "[See individual file]"
                    all_data.append((number, prob, statement, ""))
            combined = make_combined_tex(all_data, label)
            combined_path = os.path.join(cat_dir, "all_open_problems.tex")
            with open(combined_path, 'w', encoding='utf-8') as f:
                f.write(combined)
            print(f"  Wrote combined: {combined_path}")
            return

    # For other categories, fetch LaTeX from the web
    all_data = []
    for i, prob in enumerate(filtered):
        number = prob['number']
        print(f"  [{i+1}/{len(filtered)}] Fetching problem #{number}...", flush=True)

        html = fetch_latex_source(number)
        if html is None:
            statement = f"[Could not retrieve statement. Visit \\url{{https://www.erdosproblems.com/{number}}}]"
            refs = ""
        else:
            statement, refs = extract_latex_content(html)
            if not statement:
                statement = f"[Statement not parsed. Visit \\url{{https://www.erdosproblems.com/{number}}}]"

        tex = make_individual_tex(number, prob, statement, refs)
        fpath = os.path.join(ind_dir, f"problem_{number}.tex")
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(tex)

        all_data.append((number, prob, statement, refs))
        time.sleep(0.3)

    print(f"  Wrote {len(all_data)} individual files to {ind_dir}")

    combined = make_combined_tex(all_data, label)
    combined_fname = f"all_{cat_key}_problems.tex"
    combined_path = os.path.join(cat_dir, combined_fname)
    with open(combined_path, 'w', encoding='utf-8') as f:
        f.write(combined)
    print(f"  Wrote combined: {combined_path}")


def main():
    problems = download_yaml()
    print(f"Total problems in database: {len(problems)}")

    for cat_key, cat_info in CATEGORIES.items():
        process_category(cat_key, cat_info, problems)

    print("\nDone!")


if __name__ == "__main__":
    main()
