# coding: utf-8
# pyright: basic

# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

"""The text of a speech sequence, for the braille display.

A spoken answer is a list of sentences with pauses and sounds between them;
braille needs only the words. Free of NVDA imports, so the rule is tested
without NVDA; `speaking.speak_and_show` hands the result to NVDA's braille.
"""

import typing


def braille_text(sequence: typing.Iterable[typing.Any]) -> str:
	"""The sentences of `sequence`, one space apart; pauses, sounds and empty strings are left out."""
	return " ".join(item.strip() for item in sequence if isinstance(item, str) and item.strip())
