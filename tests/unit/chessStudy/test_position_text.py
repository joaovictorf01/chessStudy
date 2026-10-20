# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

"""The whole position as text (README, "The position as text")."""

import unittest

from chessStudy.paths import import_bundled
from chessStudy.position_text import describe_position

with import_bundled():
	import chess


class PositionTextTest(unittest.TestCase):
	def test_starting_position(self):
		lines = describe_position(chess.Board()).splitlines()
		self.assertEqual(lines[0], "White to move.")
		self.assertIn("White pieces:", lines)
		self.assertIn("Rook: a1, h1", lines)
		self.assertIn("Pawn: a2, b2, c2, d2, e2, f2, g2, h2", lines)
		self.assertIn("Knight: b8, g8", lines)
		self.assertIn("White can still castle short and long.", lines)
		self.assertIn("Black can still castle short and long.", lines)
		self.assertIn("Material: equal.", lines)
		self.assertIn("Rank 5: empty.", lines)
		self.assertEqual(
			lines[-10],
			"Rank 8: a8 black rook, b8 black knight, c8 black bishop, d8 black queen, "
			"e8 black king, f8 black bishop, g8 black knight, h8 black rook.",
		)

	def test_the_fen_closes_the_text(self):
		self.assertEqual(describe_position(chess.Board()).splitlines()[-1], f"FEN: {chess.STARTING_FEN}")

	def test_pieces_come_king_first_and_each_side_under_its_heading(self):
		lines = describe_position(chess.Board()).splitlines()
		white = lines.index("White pieces:")
		black = lines.index("Black pieces:")
		self.assertEqual(lines[white + 1 : white + 7][0], "King: e1")
		self.assertEqual(lines[white + 2], "Queen: d1")
		self.assertEqual(lines[black + 1], "King: e8")

	def test_last_move_check_and_material(self):
		board = chess.Board("4k3/8/8/8/8/8/3q4/R3K3 w Q - 0 30")
		text = describe_position(board, last_move="29... Qd2+")
		lines = text.splitlines()
		self.assertEqual(lines[0], "White to move, in check.")
		self.assertEqual(lines[1], "Last move: 29... Qd2+.")
		self.assertIn("White can still castle long.", lines)
		self.assertIn("Material: Black is up 4 points.", lines)
		self.assertNotIn("Black can still castle", text)

	def test_one_point(self):
		board = chess.Board("4k3/8/8/8/8/8/4P3/4K3 b - - 0 1")
		self.assertIn("Material: White is up 1 point.", describe_position(board).splitlines())

	def test_no_castling_and_en_passant(self):
		board = chess.Board("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 2")
		lines = describe_position(board).splitlines()
		self.assertIn("Neither side can castle.", lines)
		self.assertIn("En passant possible on d6.", lines)

	def test_mate_and_stalemate(self):
		mate = chess.Board("4k3/4Q3/4K3/8/8/8/8/8 b - - 0 1")
		self.assertEqual(describe_position(mate).splitlines()[0], "Black is checkmated.")
		stalemate = chess.Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
		self.assertEqual(describe_position(stalemate).splitlines()[0], "Stalemate.")
