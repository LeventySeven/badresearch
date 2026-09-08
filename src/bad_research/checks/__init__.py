"""Deterministic report checks — pure functions, no LLM, no network, no state.

Each module here reproduces one defect that a model critic caught in a live run
and that a script can catch for free every run afterwards. The house rule is in
the repo's DIRECTION: a check that can only pass is not a check, so every module
here ships a planted-defect fixture under `tests/test_checks/fixtures/` and is
proven RED against it before it counts.

The second rule is precedence: correctness beats coverage. These checks are
deliberately narrow. A check that fires on valid input gets switched off by the
first person it annoys, and then it protects nobody — so where the two trade
off, they take the false negative.
"""

from __future__ import annotations

__all__: list[str] = []
