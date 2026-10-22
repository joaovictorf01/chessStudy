# coding: utf-8
# pyright: basic

# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

"""Message boxes and modal dialogs, on NVDA's `gui.message.MessageDialog`.

NVDA 2025.1 deprecated `gui.messageBox` and `gui.runScriptModalDialog`; these
are the add-on's replacements. Every function here must be called on the GUI
thread (menu handlers, scripts and `wx.CallAfter` callbacks all are).
"""

import platform
from typing import Callable

import addonHandler
import api
import ui
import versionInfo
import wx
import gui
from gui.message import DefaultButtonSet, DialogType, MessageDialog, ReturnCode, displayDialogAsModal

from ..error_details import error_details
from ..i18n import _


def _parent(parent: wx.Window | None) -> wx.Window | None:
	return parent if parent is not None else gui.mainFrame


def show_message(message: str, caption: str, *, parent: wx.Window | None = None) -> None:
	"""A modal message with an OK button, no icon and no sound."""
	MessageDialog(_parent(parent), message, caption).ShowModal()


def show_warning(message: str, caption: str, *, parent: wx.Window | None = None) -> None:
	"""A modal message with the exclamation icon and the Windows alert sound."""
	MessageDialog(_parent(parent), message, caption, DialogType.WARNING).ShowModal()


def show_error(
	message: str,
	caption: str,
	*,
	parent: wx.Window | None = None,
	details: str | None = None,
) -> None:
	"""A modal message with the cross icon and the Windows error sound.

	With `details`, a "Copy details" button puts them on the clipboard, so the
	person reporting the failure pastes them instead of copying by ear.
	"""
	dialog = MessageDialog(_parent(parent), message, caption, DialogType.ERROR)
	if details:
		dialog.addButton(
			ReturnCode.CUSTOM_1,
			# Translators: Button of an error message: copies the technical details to paste in a report.
			_("&Copy details"),
			callback=lambda payload: copy_details(details),
			closesDialog=False,
		)
	dialog.ShowModal()


def copy_details(details: str) -> None:
	if api.copyToClip(details):
		# Translators: Spoken after the technical details of an error were copied.
		ui.message(_("Details copied. Paste them in your message."))


def failure_details(what: str, error: BaseException) -> str:
	"""The versions, what failed and every cause, in English; see `error_details`."""
	try:
		addon_version = addonHandler.getCodeAddon().version
	except Exception:  # the details still help without the version
		addon_version = "?"
	return error_details(
		what,
		error,
		addon_version=addon_version,
		nvda_version=versionInfo.version,
		windows_version=platform.version(),
	)


def ask_yes_no(
	message: str,
	caption: str,
	*,
	parent: wx.Window | None = None,
	default_no: bool = False,
) -> bool:
	"""A modal question with Yes and No buttons; True when the user chose Yes.

	With `default_no`, No has the focus and answers Escape: for questions that
	guard something that cannot be undone from the dialog itself.
	"""
	if default_no:
		dialog = MessageDialog(_parent(parent), message, caption, DialogType.WARNING, buttons=None)
		dialog.addYesButton().addNoButton(defaultFocus=True, fallbackAction=True)
	else:
		dialog = MessageDialog(_parent(parent), message, caption, buttons=DefaultButtonSet.YES_NO)
	return dialog.ShowModal() == ReturnCode.YES


def run_modal(dialog: wx.Dialog, callback: Callable[[int], object] | None = None) -> None:
	"""Shows `dialog` modally on the next GUI cycle, hands the result to `callback` and destroys it.

	Scripts and menu handlers cannot block on `ShowModal` themselves; this is what
	`gui.runScriptModalDialog` did before it was deprecated.
	"""

	def run() -> None:
		result = displayDialogAsModal(dialog)
		if callback is not None:
			callback(result)
		dialog.Destroy()

	wx.CallAfter(run)


def ask_yes_no_from_script(
	message: str,
	caption: str,
	callback: Callable[[bool], object],
	*,
	parent: wx.Window | None = None,
) -> None:
	"""A Yes/No question asked from a script, which cannot block: the answer goes to `callback`.

	No is the focused button and the answer to Escape, so a question that
	guards a shortcut never lets the same keystroke through by accident.
	"""
	dialog = MessageDialog(_parent(parent), message, caption, buttons=None)
	dialog.addYesButton().addNoButton(defaultFocus=True, fallbackAction=True)
	run_modal(dialog, lambda result: callback(result == ReturnCode.YES))
