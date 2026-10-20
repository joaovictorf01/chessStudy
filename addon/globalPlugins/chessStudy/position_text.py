# coding: utf-8
# pyright: basic

# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

"""The whole position as text (README, "The position as text"), read in a window line by line.

Free of NVDA imports: the board opens the window. Whose move and the last
move come first, then each side's pieces by type, then castling, en passant
and material, then the board rank by rank, from the 8th to the 1st, and the FEN.
"""

from .i18n import _, ngettext
from .paths import import_bundled
from .spoken_messages import spoken_piece_name


with import_bundled():
	import chess


PIECE_ORDER = (chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN)
PIECE_POINTS = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}


def describe_position(board: chess.Board, last_move: str | None = None) -> str:
	"""`last_move` comes already written in the user's notation, with its move number."""
	lines = [_status(board)]
	if last_move:
		# Translators: Line of the position as text; {move} is the last move, e.g. "22... Nxf3+".
		lines.append(_("Last move: {move}.").format(move=last_move))
	for color in (chess.WHITE, chess.BLACK):
		lines.append("")
		if color == chess.WHITE:
			# Translators: Heading of the white pieces in the position as text.
			lines.append(_("White pieces:"))
		else:
			# Translators: Heading of the black pieces in the position as text.
			lines.append(_("Black pieces:"))
		lines.extend(_pieces_of(board, color))
	lines.append("")
	lines.extend(_castling(board))
	if board.has_legal_en_passant() and board.ep_square is not None:
		# Translators: Line of the position as text; {square} is where the pawn would land, e.g. "d6".
		lines.append(_("En passant possible on {square}.").format(square=chess.square_name(board.ep_square)))
	lines.append(_material(board))
	lines.append("")
	# Translators: Heading of the board described rank by rank, in the position as text.
	lines.append(_("Rank by rank:"))
	lines.extend(_rank(board, rank) for rank in range(7, -1, -1))
	lines.append("")
	# Translators: Last line of the position as text; {fen} is the position in FEN.
	lines.append(_("FEN: {fen}").format(fen=board.fen()))
	return "\n".join(lines)


def _status(board: chess.Board) -> str:
	white = board.turn == chess.WHITE
	if board.is_checkmate():
		# Translators: First line of the position as text when white is checkmated.
		white_text = _("White is checkmated.")
		# Translators: First line of the position as text when black is checkmated.
		black_text = _("Black is checkmated.")
	elif board.is_stalemate():
		# Translators: First line of the position as text in a stalemate.
		return _("Stalemate.")
	elif board.is_check():
		# Translators: First line of the position as text when white is to move and in check.
		white_text = _("White to move, in check.")
		# Translators: First line of the position as text when black is to move and in check.
		black_text = _("Black to move, in check.")
	else:
		# Translators: First line of the position as text when white is to move.
		white_text = _("White to move.")
		# Translators: First line of the position as text when black is to move.
		black_text = _("Black to move.")
	return white_text if white else black_text


def _capitalized(text: str) -> str:
	return text[:1].upper() + text[1:]


def _pieces_of(board: chess.Board, color: chess.Color) -> list[str]:
	lines = []
	for piece_type in PIECE_ORDER:
		squares = board.pieces(piece_type, color)
		if squares:
			# Translators: One line of the pieces in the position as text, e.g. "Rook: a1, f1".
			lines.append(
				_("{piece}: {squares}").format(
					piece=_capitalized(spoken_piece_name(piece_type)),
					squares=", ".join(chess.square_name(square) for square in squares),
				),
			)
	return lines


def _castling(board: chess.Board) -> list[str]:
	# One sentence per side and case, not a colour put into a sentence: the
	# languages need their own article and agreement ("As brancas ainda podem rocar").
	sentences = {
		# Translators: Line of the position as text.
		(chess.WHITE, True, True): _("White can still castle short and long."),
		# Translators: Line of the position as text.
		(chess.WHITE, True, False): _("White can still castle short."),
		# Translators: Line of the position as text.
		(chess.WHITE, False, True): _("White can still castle long."),
		# Translators: Line of the position as text.
		(chess.BLACK, True, True): _("Black can still castle short and long."),
		# Translators: Line of the position as text.
		(chess.BLACK, True, False): _("Black can still castle short."),
		# Translators: Line of the position as text.
		(chess.BLACK, False, True): _("Black can still castle long."),
	}
	lines = []
	for color in (chess.WHITE, chess.BLACK):
		key = (color, board.has_kingside_castling_rights(color), board.has_queenside_castling_rights(color))
		if key in sentences:
			lines.append(sentences[key])
	if not lines:
		# Translators: Line of the position as text when neither side can castle any more.
		lines.append(_("Neither side can castle."))
	return lines


def _points(board: chess.Board, color: chess.Color) -> int:
	return sum(PIECE_POINTS[piece.piece_type] for piece in board.piece_map().values() if piece.color == color)


def _material(board: chess.Board) -> str:
	balance = _points(board, chess.WHITE) - _points(board, chess.BLACK)
	if balance == 0:
		# Translators: Line of the position as text: both sides have the same material.
		return _("Material: equal.")
	points = abs(balance)
	if balance > 0:
		# Translators: Line of the position as text, e.g. "Material: White is up 3 points." (pawn 1, knight and bishop 3, rook 5, queen 9).
		text = ngettext(
			"Material: White is up {points} point.", "Material: White is up {points} points.", points
		)
	else:
		# Translators: Line of the position as text, e.g. "Material: Black is up 3 points." (pawn 1, knight and bishop 3, rook 5, queen 9).
		text = ngettext(
			"Material: Black is up {points} point.", "Material: Black is up {points} points.", points
		)
	return text.format(points=points)


def _rank(board: chess.Board, rank: int) -> str:
	occupied = []
	for file in range(8):
		square = chess.square(file, rank)
		piece = board.piece_at(square)
		if piece is not None:
			if piece.color == chess.WHITE:
				# Translators: One white piece in the rank by rank description, e.g. "a1 white rook".
				text = _("{square} white {piece}")
			else:
				# Translators: One black piece in the rank by rank description, e.g. "a8 black rook".
				text = _("{square} black {piece}")
			occupied.append(
				text.format(square=chess.square_name(square), piece=spoken_piece_name(piece.piece_type)),
			)
	if not occupied:
		# Translators: A rank with no pieces in the rank by rank description; {rank} is its number.
		return _("Rank {rank}: empty.").format(rank=rank + 1)
	# Translators: A rank in the rank by rank description, e.g. "Rank 8: a8 black rook, e8 black king."
	return _("Rank {rank}: {pieces}.").format(rank=rank + 1, pieces=", ".join(occupied))
