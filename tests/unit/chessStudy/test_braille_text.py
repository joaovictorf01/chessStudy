# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

"""The engine's answers on the braille display: only the words of what is spoken."""

import unittest

from chessStudy.braille_text import braille_text


class Pause:
	"""Stands for NVDA's BreakCommand and WaveFileCommand: anything that is not a string."""


class BrailleTextTest(unittest.TestCase):
	def test_sentences_joined_by_a_space(self):
		self.assertEqual(
			braille_text(["white slightly better, plus 0.4.", "Best move: Nf3."]),
			"white slightly better, plus 0.4. Best move: Nf3.",
		)

	def test_pauses_and_sounds_are_left_out(self):
		self.assertEqual(
			braille_text([Pause(), "Threat: Qxf7, white mates in 1.", Pause(), "Line: Kxf7.", Pause()]),
			"Threat: Qxf7, white mates in 1. Line: Kxf7.",
		)

	def test_empty_and_blank_strings_are_left_out(self):
		self.assertEqual(braille_text(["", "  ", "Nf3: inaccuracy."]), "Nf3: inaccuracy.")

	def test_nothing_to_show(self):
		self.assertEqual(braille_text([Pause()]), "")
