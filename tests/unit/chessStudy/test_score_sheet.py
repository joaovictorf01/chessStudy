# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

"""The score sheet grouped by move number, as in Lichess's blind mode."""

import unittest

from chessStudy.score_sheet import ScoreSheetMove, score_sheet_lines


class ScoreSheetTest(unittest.TestCase):
	def test_white_and_black_share_a_line(self):
		moves = [
			ScoreSheetMove(1, True, "e4"),
			ScoreSheetMove(1, False, "e5"),
			ScoreSheetMove(2, True, "Nf3"),
		]
		self.assertEqual(score_sheet_lines(moves), ["1. e4, e5", "2. Nf3"])

	def test_starting_with_black(self):
		moves = [
			ScoreSheetMove(12, False, "Nf6"),
			ScoreSheetMove(13, True, "Qxf7#"),
		]
		self.assertEqual(score_sheet_lines(moves), ["12... Nf6", "13. Qxf7#"])

	def test_empty(self):
		self.assertEqual(score_sheet_lines([]), [])
