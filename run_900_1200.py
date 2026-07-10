import sys
from pathlib import Path

import erdos_common as C

_original = C.get_problem_files

def filtered_get_problem_files(category):
    if category == "open":
        folder = Path(__file__).resolve().parent / "range_900_1200" / "individual"
        return sorted(
            folder.glob("problem_*.tex"),
            key=C.problem_number
        )
    return _original(category)

C.get_problem_files = filtered_get_problem_files

import solve_submit

if __name__ == "__main__":
    solve_submit.main()
