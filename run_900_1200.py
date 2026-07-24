#!/usr/bin/env python3
"""Collect unverified candidates for the legacy 900–1200 number shard.

The wrapper only selects problem numbers. ``solve_submit`` loads every actual
statement from a complete canonical snapshot and records its immutable source
contract; this module never reads local TeX as mathematical input.
"""

from pathlib import Path

import erdos_common as C
import solve_submit


RANGE_DIR = Path(__file__).resolve().parent / "range_900_1200" / "individual"


def range_problem_files(category: str):
    if category == "open":
        return sorted(RANGE_DIR.glob("problem_*.tex"), key=C.problem_number)
    return C.get_problem_files(category)


def main(argv=None) -> None:
    solve_submit.main(argv, problem_file_provider=range_problem_files)


if __name__ == "__main__":
    main()
