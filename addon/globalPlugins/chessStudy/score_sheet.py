# coding: utf-8
# pyright: basic

# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

"""The score sheet (F4) as lines: one per move number, White's and Black's moves together.

The way Lichess's blind mode writes the move list: "1. e4, e5", "2. Nf3, Nc6",
in the order they were played. A game that starts with Black to move (a
puzzle, an edited position) opens with "12... Nf6". Free of NVDA imports:
the board keeps the list and shows the lines.
"""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class ScoreSheetMove:
	number: int  # the full move number, as in the FEN
	white: bool  # who played it
	text: str  # the move as written in the sheet, in the chosen notation


def score_sheet_lines(moves: list[ScoreSheetMove]) -> list[str]:
	"""The lines of the sheet, the first move first."""
	lines: list[str] = []
	open_number: int | None = None  # the number of a line that still waits for Black's move
	for move in moves:
		if not move.white and open_number == move.number:
			lines[-1] += f", {move.text}"
			open_number = None
		elif move.white:
			lines.append(f"{move.number}. {move.text}")
			open_number = move.number
		else:
			lines.append(f"{move.number}... {move.text}")
			open_number = None
	return lines
