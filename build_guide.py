#!/usr/bin/env python3
"""Render SETUP_GUIDE.md to SETUP_GUIDE.pdf.

A small, dependency-light Markdown renderer (headings, paragraphs, bullet
lists, and fenced code blocks) good enough for the setup guide.
"""

import re
from pathlib import Path

from fpdf import FPDF

BASE_DIR = Path(__file__).resolve().parent
SRC = BASE_DIR / "SETUP_GUIDE.md"
OUT = BASE_DIR / "SETUP_GUIDE.pdf"

NAVY = (20, 40, 80)
GREY = (90, 90, 90)
CODE_BG = (244, 244, 246)


def ascii_safe(text: str) -> str:
    """Map the few non-latin-1 chars used in the guide to ASCII equivalents."""
    return (text.replace("\u0151", "o").replace("\u0150", "O")  # Erdos
                .replace("\u2014", "-").replace("\u2013", "-")
                .replace("\u2019", "'").replace("\u2018", "'")
                .replace("\u201c", '"').replace("\u201d", '"')
                .replace("\u2192", "->"))


class Doc(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 6, "Erdos Solver - Setup Guide", align="R")
        self.ln(8)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY)
        self.cell(0, 6, f"Page {self.page_no()}", align="C")


def render_inline(text: str) -> str:
    # Strip markdown emphasis / inline-code markers (keep the text).
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]*)\*", r"\1", text)
    return ascii_safe(text)


def h1(pdf, text):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(0, 10, text)
    pdf.ln(2)


def h2(pdf, text):
    pdf.ln(3)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(0, 7.5, text)
    pdf.ln(1)


def para(pdf, text):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 5.4, text)
    pdf.ln(1.5)


def bullet(pdf, text):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 5.4, "-  " + text)


def code_block(pdf, lines):
    pdf.ln(1)
    pdf.set_font("Courier", "", 9)
    pdf.set_text_color(20, 20, 20)
    pdf.set_fill_color(*CODE_BG)
    for ln in lines:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 5.0, "  " + ascii_safe(ln), fill=True)
    pdf.ln(2)


def build():
    md = SRC.read_text(encoding="utf-8").splitlines()

    pdf = Doc(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(18, 16, 18)
    pdf.add_page()

    in_code = False
    code_lines: list[str] = []

    for raw in md:
        line = raw.rstrip("\n")

        if line.strip().startswith("```"):
            if in_code:
                code_block(pdf, code_lines)
                code_lines = []
            in_code = not in_code
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            continue

        if line.startswith("# "):
            h1(pdf, render_inline(line[2:]))
        elif line.startswith("## "):
            h2(pdf, render_inline(line[3:]))
        elif line.startswith("### "):
            h2(pdf, render_inline(line[4:]))
        elif line.lstrip().startswith(("- ", "* ")):
            bullet(pdf, render_inline(line.lstrip()[2:]))
        else:
            para(pdf, render_inline(line))

    if in_code and code_lines:
        code_block(pdf, code_lines)

    pdf.output(str(OUT))
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    build()
