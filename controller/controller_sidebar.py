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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib

from viewgtk.viewgtk_sidebar import *
import helpers.helpers as helpers

import math


class SidebarController(object):
    ''' Init and controll sidebar '''
    
    def __init__(self, sidebar, workspace_controller, main_window):

        self.sidebar = sidebar
        self.workspace_controller = workspace_controller
        self.main_window = main_window
        
        self.sidebar_position = self.workspace_controller.settings.get_value('window_state', 'sidebar_paned_position')
        self.sidebar_animating = False
        self.hide_sidebar(False, False)

        # detect dark mode
        dm = 'True' if helpers.is_dark_mode(self.sidebar) else 'False'

        # tabbed pages: name, icon name, tooltip, widget
        self.pages = list()
        self.pages.append(['greek_letters', 'own-symbols-greek-letters-symbolic', 'Greek Letters', 
                           'SidebarPageSymbolsList("greek_letters", 20, ' + dm + ')'])
        self.pages.append(['arrows', 'own-symbols-arrows-symbolic', 'Arrows', 
                           'SidebarPageSymbolsList("arrows", 42, ' + dm + ')'])
        self.pages.append(['relations', 'own-symbols-relations-symbolic', 'Relations', 
                           'SidebarPageSymbolsList("relations", 30, ' + dm + ')'])
        self.pages.append(['operators', 'own-symbols-operators-symbolic', 'Operators', 
                           'SidebarPageSymbolsList("operators", 44, ' + dm + ')'])
        self.pages.append(['delimiters', 'own-symbols-delimiters-symbolic', 'Delimiters', 
                           'SidebarPageSymbolsList("delimiters", 10, ' + dm + ')'])
        self.pages.append(['misc_math', 'own-symbols-misc-math-symbolic', 'Misc. Math', 
                           'SidebarPageSymbolsList("misc_math", 38, ' + dm + ')'])
        self.pages.append(['misc_text', 'own-symbols-misc-text-symbolic', 'Misc. Symbols', 
                           'SidebarPageSymbolsList("misc_text", 36, ' + dm + ')'])
        self.page_views = list()
        self.init_page_stack()

        self.sidebar.show_all()

    def init_page_stack(self):
        self.tab_buttons = list()
        for page in self.pages:
            if len(self.tab_buttons) == 0:
                button = Gtk.RadioToolButton()
            else:
                button = Gtk.RadioToolButton.new_from_widget(self.tab_buttons[0])
            button.set_icon_name(page[1])
            button.set_focus_on_click(False)
            button.set_tooltip_text(page[2])
            if len(self.tab_buttons) == 0:
                button.get_style_context().add_class('first')

            self.tab_buttons.append(button)
            self.sidebar.tabs.insert(button, -1)
            page_view = eval(page[3])
            self.sidebar.stack.add_named(page_view, page[0])
            self.init_symbols_page(page_view)
            self.page_views.append(page_view)
            page_view.connect('size-allocate', self.on_stack_size_allocate)
            button.connect('clicked', self.on_tab_button_clicked, page[0])

    def init_symbols_page(self, page_view):
        for symbol in page_view.symbols:
            button = symbol[3]
            button.set_focus_on_click(False)
            button.get_child().set_size_request(page_view.symbol_width, -1)
            button.set_action_name('app.insert-symbol')
            button.set_action_target_value(GLib.Variant('as', [symbol[1]]))
        
    '''
    *** signal handlers for buttons in sidebar
    '''
    
    def on_tab_button_clicked(self, button, page_name):
        self.sidebar.stack.set_visible_child_name(page_name)
    
    '''
    *** manage borders of images
    '''

    def on_stack_size_allocate(self, symbol_page, allocation, data=None):
        if symbol_page.size != (allocation.width, allocation.height):
            symbol_page.size = (allocation.width, allocation.height)
            if isinstance(symbol_page, SidebarPageSymbolsList):
                width_with_border = symbol_page.symbols[0][3].get_preferred_width()[0]
                width_avail = (allocation.width + 1) # +1px for removed child borders
                symbols_per_line = (width_avail // width_with_border)
                number_of_lines = math.ceil(len(symbol_page.symbols) / symbols_per_line)

                height_with_border = symbol_page.symbols[0][3].get_preferred_height()[0]
                for line_no in range(1, number_of_lines):
                    # get max for each element
                    max_height = 0
                    for el_no in range(0, symbols_per_line):
                        try:
                            symbol = symbol_page.symbols[(line_no * symbols_per_line) + 1 + el_no]
                        except IndexError:
                            el_height = 0
                        else:
                            el_height = symbol[3].get_preferred_height()[0]
                            if symbol[3].get_style_context().has_class('no_bottom_border'):
                                el_height += 1
                        if el_height > max_height: max_height = el_height
                    height_with_border += max_height
                height_avail = (allocation.height + 1) # +1px for removed child borders
                for number, image in enumerate(symbol_page.symbols):
                    if (number % symbols_per_line) == (symbols_per_line - 1):
                        image[3].get_style_context().add_class('no_right_border')
                    else:
                        image[3].get_style_context().remove_class('no_right_border')
                    if (number >= (number_of_lines - 1) * symbols_per_line) and (height_avail <= height_with_border):
                        image[3].get_style_context().add_class('no_bottom_border')
                    else:
                        image[3].get_style_context().remove_class('no_bottom_border')

    def hide_sidebar(self, animate=False, set_toggle=True):
        if not self.sidebar_animating:
            if self.main_window.sidebar_visible:
                self.sidebar_position = self.main_window.sidebar_paned.get_position()
            self.animate_sidebar(False, animate, set_toggle)
    
    def show_sidebar(self, animate=False, set_toggle=True):
        if not self.sidebar_animating:
            self.animate_sidebar(True, animate, set_toggle)

    def animate_sidebar(self, show_sidebar=False, animate=False, set_toggle=True):
        def set_position_on_tick(paned, frame_clock_cb, user_data=None):
            show_sidebar, set_toggle = user_data
            now = frame_clock_cb.get_frame_time()
            if now < end_time and paned.get_position != end:
                t = self.ease((now - start_time) / (end_time - start_time))
                paned.set_position(int(start + t * (end - start)))
                return True
            else:
                paned.set_position(end)
                if not show_sidebar:
                    self.sidebar.hide()
                    self.main_window.sidebar_visible = False
                else:
                    self.main_window.sidebar_paned.child_set_property(self.sidebar, 'shrink', False)
                    self.main_window.sidebar_visible = True
                if set_toggle: self.main_window.shortcuts_bar.sidebar_toggle.set_active(show_sidebar)
                self.sidebar.set_size_request(-1, -1)
                self.sidebar_animating = False
                return False

        frame_clock = self.main_window.sidebar_paned.get_frame_clock()
        duration = 200
        if show_sidebar:
            self.sidebar.show_all()
            start = 0
            end = self.sidebar_position
            self.sidebar.set_size_request(end, -1)
        else:
            start = self.main_window.sidebar_paned.get_position()
            end = 0
            self.sidebar.set_size_request(start, -1)
        if frame_clock != None and animate:
            if self.main_window.sidebar_paned.get_position() != end:
                start_time = frame_clock.get_frame_time()
                end_time = start_time + 1000 * duration
                self.sidebar_animating = True
                self.main_window.sidebar_paned.add_tick_callback(set_position_on_tick, (show_sidebar, set_toggle))
                self.main_window.sidebar_paned.child_set_property(self.sidebar, 'shrink', True)
        else:
            self.main_window.sidebar_paned.set_position(end)
            if show_sidebar:
                self.sidebar.show_all()
                self.main_window.sidebar_visible = True
                self.main_window.sidebar_paned.child_set_property(self.sidebar, 'shrink', False)
            else:
                self.sidebar.hide()
                self.main_window.sidebar_visible = False
            self.sidebar.set_size_request(-1, -1)
            if set_toggle: self.main_window.shortcuts_bar.sidebar_toggle.set_active(show_sidebar)

    def ease(self, time):
        return (time - 1)**3 + 1;

