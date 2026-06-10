#!/usr/bin/env python3
"""Generate PIPELINE_GUIDE.pdf — a short guide to the Erdős solver pipeline."""

from fpdf import FPDF

NAVY = (20, 40, 80)
GREY = (90, 90, 90)
CODE_BG = (244, 244, 246)


class Guide(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 6, "Erdos Solver Pipeline Guide", align="R")
        self.ln(8)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY)
        self.cell(0, 6, f"Page {self.page_no()}", align="C")


def h1(pdf, text):
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(0, 9, text)
    pdf.ln(1)


def h2(pdf, text):
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(0, 7, text)
    pdf.ln(0.5)


def body(pdf, text):
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 5.4, text)
    pdf.ln(1)


def bullet(pdf, label, text):
    pdf.set_x(pdf.l_margin + 2)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(*NAVY)
    w = pdf.get_string_width(label + "  ") + 1
    pdf.cell(w, 5.4, f"- {label}")
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 5.4, text)


def code(pdf, lines):
    pdf.ln(1)
    pdf.set_font("Courier", "", 9)
    pdf.set_fill_color(*CODE_BG)
    pdf.set_text_color(20, 20, 20)
    for ln in lines:
        pdf.set_x(pdf.l_margin)
        pdf.cell(0, 5.2, "  " + ln, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def build():
    pdf = Guide(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(18, 16, 18)
    pdf.add_page()

    h1(pdf, "Erdos Solver Pipeline")
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*GREY)
    pdf.multi_cell(0, 5, "Browser automation that submits open Erdos problems to "
                         "ChatGPT and DeepSeek, extracts the answers, saves them, "
                         "and labels each chat [solved]/[unsolved] + confidence.")
    pdf.ln(3)

    h2(pdf, "Overview")
    body(pdf, "The pipeline runs in two stages per platform. A submit stage opens "
              "one chat per problem and sends the research-mode prompt. A rename "
              "stage revisits each chat, waits for generation to finish, extracts "
              "the answer, writes it to disk, and renames the chat with the verdict "
              "and confidence. ChatGPT and DeepSeek share the prompt and parsing "
              "logic via the common modules.")

    h2(pdf, "Components")
    bullet(pdf, "erdos_common.py", "Shared prompt, answer parsing (is_solved, "
                "extract_confidence), browser launch, and ChatGPT page helpers.")
    bullet(pdf, "deepseek_common.py", "DeepSeek page helpers; re-uses the prompt "
                "and parsers from erdos_common.")
    bullet(pdf, "solve_submit.py / deepseek_submit.py", "Submit problems to chats "
                "(no waiting). Record each problem -> chat URL in a chat map.")
    bullet(pdf, "solve_rename.py / deepseek_rename.py", "Watch the chats, save "
                "answers, and rename with the result label.")
    bullet(pdf, "fetch_erdos.py / fetch_categories.py", "Download and categorize "
                "the Erdos problem set into erdos_problems/.")

    h2(pdf, "How to run")
    body(pdf, "1. One-time login (opens a browser to authenticate):")
    code(pdf, ["python3 solve_submit.py --login",
               "python3 deepseek_submit.py --login"])
    body(pdf, "2. Submit a batch of open problems (reverse order shown):")
    code(pdf, ["python3 solve_submit.py --reverse --start 0 --limit 208",
               "python3 deepseek_submit.py --reverse --start 0 --limit 208 --delay 60"])
    body(pdf, "3. Collect answers and rename chats (run as a watch loop):")
    code(pdf, ["python3 solve_rename.py --watch --interval 60",
               "python3 deepseek_rename.py --watch --interval 45"])

    h2(pdf, "Output")
    body(pdf, "Solutions are written to erdos_problems/solutions/<category>/ "
              "(ChatGPT) and erdos_problems/solutions_deepseek/<category>/ "
              "(DeepSeek). Each chat title becomes:")
    code(pdf, ["Erdos #<n> [solved]  88%",
               "Erdos #<n> [unsolved]  12%"])

    h2(pdf, "Configuration & privacy")
    body(pdf, "The private ChatGPT project URL is read from the "
              "CHATGPT_PROJECT_URL environment variable (it is not committed). "
              "Browser profiles, chat maps, and logs are git-ignored because they "
              "contain session cookies and private conversation IDs.")
    code(pdf, ['export CHATGPT_PROJECT_URL="https://chatgpt.com/g/<your-project>/project"'])

    pdf.output("PIPELINE_GUIDE.pdf")
    print("wrote PIPELINE_GUIDE.pdf")


if __name__ == "__main__":
    build()
