# coding: utf-8
# pyright: basic

# Copyright (c) 2021 Blind Pandas Team
# This file is covered by the GNU General Public License.

"""Speaking through NVDA: the add-on's speech queue and a helper for building sequences."""

import braille
import speech

from .braille_text import braille_text


def intersperse(lst, item) -> speech.SpeechSequence:
	"""Puts `item` between every two elements: [a, b, c] -> [a, item, b, item, c].

	Used to place a pause (BreakCommand) between the parts of an announcement.
	Taken from: https://stackoverflow.com/a/5921708
	"""
	result = [item] * (len(lst) * 2 - 1)
	result[0::2] = lst
	return result


def speak_next(speech_sequence: speech.SpeechSequence, priority=speech.priorities.Spri.NEXT) -> None:
	"""Speaks after what's already queued, without interrupting what NVDA is currently saying."""
	speech.speak(speech_sequence, priority=priority)


def speak_and_show(speech_sequence: speech.SpeechSequence) -> None:
	"""Speaks like `speak_next`, and shows the words on the braille display.

	For the engine's answers: long enough that a braille user wants to read them
	at their own pace. How long they stay is NVDA's "Show messages" braille setting.
	"""
	speak_next(speech_sequence)
	text = braille_text(speech_sequence)
	if text and braille.handler is not None:
		braille.handler.message(text)
