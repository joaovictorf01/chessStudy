# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

"""A move typed in the field (README, "Typing a move"): SAN or the two squares, forgiving as on Lichess."""

import unittest

from chessStudy.paths import import_bundled
from chessStudy.typed_move import read_typed_move

with import_bundled():
	import chess
	import chess.variant


def board_after(*san_moves: str, fen: str = chess.STARTING_FEN) -> chess.Board:
	board = chess.Board(fen)
	for san in san_moves:
		board.push_san(san)
	return board


class SanTest(unittest.TestCase):
	def test_san_as_written(self):
		self.assertEqual(read_typed_move(chess.Board(), "Nf3").move, chess.Move.from_uci("g1f3"))
		self.assertEqual(read_typed_move(chess.Board(), "e4").move, chess.Move.from_uci("e2e4"))

	def test_case_does_not_matter(self):
		for text in ("nf3", "NF3", " Nf3 "):
			with self.subTest(text=text):
				self.assertEqual(read_typed_move(chess.Board(), text).move, chess.Move.from_uci("g1f3"))

	def test_capture_check_and_annotation_signs(self):
		board = board_after("e4", "d5")
		self.assertEqual(read_typed_move(board, "exd5").move, chess.Move.from_uci("e4d5"))
		self.assertEqual(read_typed_move(board, "exd5!?").move, chess.Move.from_uci("e4d5"))
		board = board_after("e4", "e5", "Qh5", "Nc6", "Bc4", "Nf6")
		self.assertEqual(read_typed_move(board, "Qxf7#").move, chess.Move.from_uci("h5f7"))

	def test_castling_with_letters_or_zeros(self):
		board = board_after("e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5")
		for text in ("O-O", "o-o", "0-0"):
			with self.subTest(text=text):
				self.assertEqual(read_typed_move(board, text).move, chess.Move.from_uci("e1g1"))

	def test_lowercase_b_is_the_pawn_when_it_can_take(self):
		# Both the b pawn and the bishop on e2 can take on c4.
		board = chess.Board("4k3/8/8/8/2p5/1P6/4B3/4K3 w - - 0 1")
		self.assertEqual(read_typed_move(board, "bxc4").move, chess.Move.from_uci("b3c4"))
		self.assertEqual(read_typed_move(board, "Bxc4").move, chess.Move.from_uci("e2c4"))

	def test_lowercase_b_is_the_bishop_when_no_pawn_can(self):
		board = board_after("e4", "e5")
		self.assertEqual(read_typed_move(board, "bc4").move, chess.Move.from_uci("f1c4"))

	def test_promotion_with_or_without_the_sign(self):
		board = chess.Board("8/4P3/8/8/8/8/k7/4K3 w - - 0 1")
		for text in ("e8=Q", "e8q", "E8=q"):
			with self.subTest(text=text):
				self.assertEqual(read_typed_move(board, text).move, chess.Move.from_uci("e7e8q"))
		self.assertEqual(read_typed_move(board, "e8=N").move, chess.Move.from_uci("e7e8n"))

	def test_two_pieces_for_the_same_move_ask_for_the_file(self):
		board = chess.Board("4k3/8/8/8/8/8/8/1N2KN2 w - - 0 1")
		typed = read_typed_move(board, "Nd2")
		self.assertIsNone(typed.move)
		self.assertIn("Nbd2", typed.problem)
		self.assertEqual(read_typed_move(board, "nfd2").move, chess.Move.from_uci("f1d2"))

	def test_crazyhouse_drop(self):
		board = chess.variant.CrazyhouseBoard("4k3/8/8/8/8/8/8/4K3[N] w - - 0 1")
		self.assertEqual(read_typed_move(board, "N@f3").move, chess.Move.from_uci("N@f3"))


class SquaresTest(unittest.TestCase):
	def test_the_two_squares(self):
		for text in ("g1f3", "G1F3", "g1-f3", "g1 f3"):
			with self.subTest(text=text):
				self.assertEqual(read_typed_move(chess.Board(), text).move, chess.Move.from_uci("g1f3"))

	def test_castling_as_the_king_move(self):
		board = board_after("e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5")
		self.assertEqual(read_typed_move(board, "e1g1").move, chess.Move.from_uci("e1g1"))

	def test_promotion_piece_given(self):
		board = chess.Board("8/4P3/8/8/8/8/k7/4K3 w - - 0 1")
		typed = read_typed_move(board, "e7e8n")
		self.assertEqual(typed.move, chess.Move.from_uci("e7e8n"))
		self.assertFalse(typed.needs_promotion)

	def test_promotion_without_the_piece_asks_for_it(self):
		board = chess.Board("8/4P3/8/8/8/8/k7/4K3 w - - 0 1")
		typed = read_typed_move(board, "e7e8")
		self.assertTrue(typed.needs_promotion)
		self.assertEqual((typed.move.from_square, typed.move.to_square), (chess.E7, chess.E8))


class ProblemTest(unittest.TestCase):
	def test_empty(self):
		typed = read_typed_move(chess.Board(), "   ")
		self.assertIsNone(typed.move)
		self.assertEqual(typed.problem, "No move typed.")

	def test_illegal_move_says_what_was_typed(self):
		for text in ("e5", "Nf6", "e2e5", "O-O"):
			with self.subTest(text=text):
				typed = read_typed_move(chess.Board(), text)
				self.assertIsNone(typed.move)
				self.assertEqual(typed.problem, f"{text} is not a legal move here.")

	def test_text_that_is_not_a_move(self):
		typed = read_typed_move(chess.Board(), "knight to f3")
		self.assertIsNone(typed.move)
		self.assertIn("Could not read knight to f3 as a move", typed.problem)
