#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import re

import app.settings as settingscontroller

import dialogs.about.about as about_dialog
import dialogs.build_save.build_save as build_save_dialog
import dialogs.building_failed.building_failed as building_failed_dialog
import dialogs.close_confirmation.close_confirmation as close_confirmation_dialog
import dialogs.document_wizard.document_wizard as document_wizard
import dialogs.interpreter_missing.interpreter_missing as interpreter_missing_dialog
import dialogs.preferences.preferences as preferences_dialog
import dialogs.open_document.open_document as open_document_dialog
import dialogs.replace_confirmation.replace_confirmation as replace_confirmation_dialog
import dialogs.save_document.save_document as save_document_dialog
import dialogs.keyboard_shortcuts.keyboard_shortcuts as keyboard_shortcuts_dialog


class ServiceLocator(object):

    dialogs = dict()
    settings = None
    build_log_doc_regex = re.compile('( *\((.*\.tex))')
    build_log_item_regex = re.compile('((?:Overfull \\\\hbox|Underfull \\\\hbox|No file .*\.|File .* does not exist\.|! I can\'t find file\.|! File .* not found\.|(?:LaTeX|pdfTeX|LuaTeX|Package|Class) .*Warning.*:|LaTeX Font Warning:|! Undefined control sequence\.|! Package .* Error:|! (?:LaTeX|LuaTeX) Error:).*\\n)')
    build_log_badbox_line_number_regex = re.compile('lines ([0-9]+)--([0-9]+)')
    build_log_other_line_number_regex = re.compile('(l.| input line )([0-9]+)( |.)')

    def init_dialogs(main_window, workspace):
        settings = ServiceLocator.get_settings()
        ServiceLocator.dialogs['about'] = about_dialog.AboutDialog(main_window)
        ServiceLocator.dialogs['building_failed'] = building_failed_dialog.BuildingFailedDialog(main_window)
        ServiceLocator.dialogs['build_save'] = build_save_dialog.BuildSaveDialog(main_window)
        ServiceLocator.dialogs['close_confirmation'] = close_confirmation_dialog.CloseConfirmationDialog(main_window, workspace)
        ServiceLocator.dialogs['document_wizard'] = document_wizard.DocumentWizard(main_window, workspace, settings)
        ServiceLocator.dialogs['interpreter_missing'] = interpreter_missing_dialog.InterpreterMissingDialog(main_window)
        ServiceLocator.dialogs['preferences'] = preferences_dialog.PreferencesDialog(main_window, settings)
        ServiceLocator.dialogs['open_document'] = open_document_dialog.OpenDocumentDialog(main_window)
        ServiceLocator.dialogs['replace_confirmation'] = replace_confirmation_dialog.ReplaceConfirmationDialog(main_window)
        ServiceLocator.dialogs['save_document'] = save_document_dialog.SaveDocumentDialog(main_window, workspace)
        ServiceLocator.dialogs['keyboard_shortcuts'] = keyboard_shortcuts_dialog.KeyboardShortcutsDialog(main_window)
    
    def get_dialog(dialog_type):
        return ServiceLocator.dialogs[dialog_type]

    def init_main_window(main_window):
        ServiceLocator.main_window = main_window

    def get_main_window():
        return ServiceLocator.main_window
    
    def get_build_log_doc_regex():
        return ServiceLocator.build_log_doc_regex
    
    def get_build_log_item_regex():
        return ServiceLocator.build_log_item_regex
    
    def get_build_log_badbox_line_number_regex():
        return ServiceLocator.build_log_badbox_line_number_regex
    
    def get_build_log_other_line_number_regex():
        return ServiceLocator.build_log_other_line_number_regex
    
    def get_settings():
        if ServiceLocator.settings == None:
            ServiceLocator.settings = settingscontroller.Settings()
        return ServiceLocator.settings


