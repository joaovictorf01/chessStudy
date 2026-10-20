# coding: utf-8
# pyright: basic

# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

"""A move typed as text: SAN as on Lichess (Nf3, exd5, O-O, e8=Q) or the two squares (g1f3, e7e8q).

Free of NVDA imports: the board opens the field and speaks what this decides.
Typing is forgiving, as on Lichess: case does not matter ("nf3", "NF3"),
check and annotation signs are ignored, 0-0 is castling, and the promotion
sign is optional ("e8q"). A lowercase b is the b pawn when that move is legal,
otherwise the bishop; Bxc4 with a capital B is always the bishop.
"""

import dataclasses
import re
import typing as t

from .i18n import _
from .paths import import_bundled


with import_bundled():
	import chess


# Two squares, optionally separated (g1f3, g1-f3, g1 f3, e7e8q, e7-e8=Q).
_SQUARES = re.compile(r"^([a-h][1-8])[-x: ]?([a-h][1-8])=?([qrbn])?$")
_CASTLING = re.compile(r"^[o0](-[o0]){1,2}$")
_PROMOTION = re.compile(r"^(.*[18])=?([qrbn])$")
_PIECE_LETTERS = "nbrqk"


@dataclasses.dataclass(frozen=True)
class TypedMove:
	"""What the text says: a legal move, or the sentence that says why not."""

	move: t.Optional[chess.Move] = None
	# Only the two squares of a promotion were typed: the board asks for the piece.
	needs_promotion: bool = False
	problem: str = ""


def read_typed_move(board: chess.Board, text: str) -> TypedMove:
	cleaned = _clean(text)
	if not cleaned:
		# Translators: Spoken when the move field was confirmed empty.
		return TypedMove(problem=_("No move typed."))
	squares = _SQUARES.match(cleaned)
	if squares:
		return _read_squares(board, text, *squares.groups())
	return _read_san(board, text, cleaned)


def _clean(text: str) -> str:
	cleaned = text.strip().lower()
	cleaned = re.sub(r"[+#!?]+$", "", cleaned)
	cleaned = re.sub(r"\s+", " ", cleaned)
	return cleaned


def _read_squares(board, text, origin, destination, promotion) -> TypedMove:
	from_square = chess.parse_square(origin)
	to_square = chess.parse_square(destination)
	if promotion:
		move = chess.Move(from_square, to_square, promotion=chess.Piece.from_symbol(promotion).piece_type)
		if move in board.legal_moves:
			return TypedMove(move=move)
		return _illegal(text)
	move = chess.Move(from_square, to_square)
	if move in board.legal_moves:
		return TypedMove(move=move)
	if chess.Move(from_square, to_square, promotion=chess.QUEEN) in board.legal_moves:
		return TypedMove(move=move, needs_promotion=True)
	return _illegal(text)


def _read_san(board, text, cleaned) -> TypedMove:
	if " " in cleaned:
		return _unreadable(text)
	ambiguous = False
	for candidate in _san_candidates(text.strip(), cleaned):
		try:
			return TypedMove(move=board.parse_san(candidate))
		except chess.AmbiguousMoveError:
			ambiguous = True
		except ValueError:
			# Not legal or not SAN in this reading; the next reading may be.
			continue
	if ambiguous:
		return TypedMove(
			# Translators: Spoken when a typed move fits two pieces; {move} is what was typed.
			problem=_("{move}: two pieces can make that move. Add the file or rank, such as Nbd2.").format(
				move=text.strip(),
			),
		)
	return _illegal(text) if _looks_like_san(cleaned) else _unreadable(text)


def _san_candidates(original: str, cleaned: str) -> t.Iterator[str]:
	"""The readings of the text, in order of preference."""
	if _CASTLING.match(cleaned):
		yield cleaned.replace("0", "O").replace("o", "O")
		return
	promotion = _PROMOTION.match(cleaned)
	if promotion:
		cleaned = f"{promotion.group(1)}={promotion.group(2).upper()}"
	first = cleaned[0]
	as_piece = first.upper() + cleaned[1:]
	typed_capital = original[:1].isupper()
	if first == "b" and typed_capital:
		# Bxc4 with a capital B is the bishop, never the b pawn.
		yield as_piece
		return
	if first in "abcdefgh":
		yield cleaned
	if first in _PIECE_LETTERS:
		yield as_piece
	if "@" in cleaned:
		# A Crazyhouse drop: N@f3, or @f3 for a pawn.
		yield as_piece


def _looks_like_san(cleaned: str) -> bool:
	if _CASTLING.match(cleaned):
		return True
	return bool(re.match(r"^[nbrqk]?[a-h]?[1-8]?x?[a-h][1-8](=[qrbn])?$|^[nbrqkp]?@[a-h][1-8]$", cleaned))


def _illegal(text: str) -> TypedMove:
	# Translators: Spoken when the typed move cannot be played here; {move} is what was typed.
	return TypedMove(problem=_("{move} is not a legal move here.").format(move=text.strip()))


def _unreadable(text: str) -> TypedMove:
	return TypedMove(
		# Translators: Spoken when the typed text is not a move; {move} is what was typed.
		problem=_(
			"Could not read {move} as a move. Type it as Nf3, exd5, O-O, or the two squares, g1f3."
		).format(
			move=text.strip(),
		),
	)
