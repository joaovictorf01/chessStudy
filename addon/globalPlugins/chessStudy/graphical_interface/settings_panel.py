# coding: utf-8
# pyright: basic

"""Preferences panel: the training plan that applies by default.

What is specific to this screen is the layout, the summary text, and what
happens on confirm -- saving the preferences. Everything else comes from
`TacticsSetupMixin`, since it is identical to the session dialog.
"""

import wx
import gui
from gui import guiHelper

from ..addon_config import (
	TacticsDefaults,
	get_autosave_analysis,
	get_games_folder,
	get_move_notation,
	get_tactics_defaults,
	save_autosave_analysis,
	save_games_folder,
	save_review_options,
	save_move_notation,
	save_tactics_defaults,
)
from ..notation import NOTATION_STYLES
from ..i18n import _
from ..tactic.db import reset_tactics_progress
from ..theme_catalog import parse_theme_filter
from ..trainer import uses_custom_themes
from .messages import ask_yes_no, failure_details, show_error, show_message
from .review_dialog import build_review_controls, options_from
from .tactics_setup import TacticsSetupMixin


class ChessboardSettingsDialog(TacticsSetupMixin, gui.SettingsDialog):
	# Translators: Title of the Chess Study settings dialog.
	title = _("Chess Study")

	def __init__(self, *args, **kwargs):
		# Before super(): NVDA's SettingsDialog calls makeSettings() from
		# within its own constructor. See _init_trainer_state.
		self._init_trainer_state()
		super().__init__(*args, **kwargs)

	def makeSettings(self, settingsSizer):
		defaults = get_tactics_defaults()
		self._theme_filter_text = defaults.theme
		helper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		introLabel = wx.StaticText(
			self,
			-1,
			# Translators: Intro text of the Chess Study settings dialog.
			_("Configure the default trainer plan used when you open Chess Study tactics."),
			style=wx.ST_ELLIPSIZE_END,
		)
		introLabel.Wrap(self.GetSize().Width)
		helper.addItem(introLabel)

		self._build_database_row(helper, self._default_database_value(defaults.db_path))
		self._build_choice_rows(
			helper,
			defaults,
			# Translators: Label for the default training plan combo box.
			_("Default training plan"),
			# Translators: Label for the default challenge level combo box.
			_("Default challenge level"),
		)
		self._build_summary_row(helper)
		# Translators: Label for the default themes field.
		self._build_theme_rows(helper, _("Default themes"))
		self.resetTacticsButton = helper.addItem(
			# Translators: Button in the settings that erases the tactics history (attempts, rating, reviews).
			wx.Button(self, -1, _("R&eset tactics progress...")),
		)
		self.Bind(wx.EVT_BUTTON, self.onResetTactics, self.resetTacticsButton)

		# Translators: Label of the combo box that chooses how moves are spoken.
		notationLabel = wx.StaticText(self, -1, _("Move &notation"))
		self.notationChoice = wx.Choice(self, -1, choices=[label for _style, label in NOTATION_STYLES])
		current = get_move_notation()
		self.notationChoice.SetSelection(
			next((index for index, (style, _label) in enumerate(NOTATION_STYLES) if style == current), 0),
		)
		guiHelper.associateElements(notationLabel, self.notationChoice)
		helper.addItem(notationLabel)
		helper.addItem(self.notationChoice)

		# The same grouping NVDA uses for the portable copy folder: the group's
		# label is what the screen reader says for the path field.
		# Translators: Label of the group with the folder where the analysis board saves games.
		groupSizer = wx.StaticBoxSizer(wx.VERTICAL, self, label=_("Games folder"))
		groupHelper = helper.addItem(guiHelper.BoxSizerHelper(self, sizer=groupSizer))
		gamesFolder = groupHelper.addItem(
			guiHelper.PathSelectionHelper(
				groupSizer.GetStaticBox(),
				# Translators: Button that browses for the games folder.
				_("Browse &folder..."),
				# Translators: Title of the dialog that chooses the games folder.
				_("Choose the folder for your games"),
			),
		)
		self.gamesFolderTextCtrl = gamesFolder.pathControl
		self.gamesFolderTextCtrl.SetValue(get_games_folder())
		self.autosaveCheckBox = helper.addItem(
			# Translators: Checkbox in the settings: the analysis board saves every change by itself.
			wx.CheckBox(self, label=_("Save analysed games &automatically, once they have a file")),
		)
		self.autosaveCheckBox.SetValue(get_autosave_analysis())
		self.reviewControls = build_review_controls(self, helper)
		self._bind_shared_events()

	def postInit(self):
		self._update_trainer_summary()
		self._update_theme_summary()
		self._refresh_theme_controls()
		self.databasePathTextCtrl.SetFocus()

	def _theme_picker_prompt(self):
		# Translators: Prompt in the theme picker, when choosing the saved default themes.
		return _("Choose one or more Lichess themes to use in the custom default trainer plan.")

	def _refresh_theme_controls(self):
		is_custom = uses_custom_themes(self._trainer_preset_id())
		self.selectThemesButton.Enable(is_custom)
		self.clearThemesButton.Enable(is_custom and bool(parse_theme_filter(self._theme_filter_text)))

	def onResetTactics(self, event):
		# Translators: Title of the question and messages about resetting the tactics progress.
		caption = _("Reset tactics progress")
		if not ask_yes_no(
			# Translators: Question before resetting the tactics progress.
			_(
				"This erases your tactics history now: every puzzle attempt, your rating and the review "
				"queue. Endgame progress and these settings are kept, and a copy of the history is saved "
				"first. Reset tactics progress?",
			),
			caption,
			parent=self,
			default_no=True,
		):
			return
		try:
			backup = reset_tactics_progress()
		except Exception as error:
			show_error(
				# Translators: Shown when resetting the tactics progress failed; nothing was erased.
				_("Could not reset the tactics progress. Your history was not changed."),
				caption,
				parent=self,
				details=failure_details("Reset tactics progress", error),
			)
			return
		if backup is None:
			# Translators: Shown after a reset when there was no tactics history yet.
			message = _("There was no tactics history yet. Nothing was erased.")
		else:
			# Translators: Shown after the tactics progress was reset. {name} is the backup file, {folder} its folder.
			message = _(
				"Tactics progress reset. Your rating starts again from 1500. "
				"The previous history was saved as {name} in {folder}.",
			).format(name=backup.name, folder=backup.parent)
		show_message(message, caption, parent=self)

	def onOk(self, event):
		save_tactics_defaults(
			TacticsDefaults(
				db_path=self.databasePathTextCtrl.GetValue().strip(),
				theme=self._theme_filter_text,
				trainer_preset=self._trainer_preset_id(),
				challenge_level=self._challenge_id(),
			),
		)
		save_move_notation(NOTATION_STYLES[self.notationChoice.GetSelection()][0])
		save_games_folder(self.gamesFolderTextCtrl.GetValue())
		save_autosave_analysis(self.autosaveCheckBox.GetValue())
		save_review_options(options_from(self.reviewControls))
		super().onOk(event)
