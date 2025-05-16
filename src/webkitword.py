#!/usr/bin/env python3
import sys
import gi
import re
import os

# Hardware Acclerated Rendering (0); Software Rendering (1)
os.environ['WEBKIT_DISABLE_COMPOSITING_MODE'] = '1'

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('WebKit', '6.0')

from gi.repository import Gtk, Adw, Gdk, WebKit, GLib, Gio, Pango, PangoCairo, Gdk

# Import file operation functions directly
import file_operations # open, save, save as
import find
import formatting_operations
import insert_table
import show_html
import keyboard_shortcuts
 
class WebkitWordApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id='io.github.fastrizwaan.WebkitWord',
                        flags=Gio.ApplicationFlags.HANDLES_OPEN,
                        **kwargs)
        self.version = "v0.1"
        self.windows = []  # Track all open windows
        self.window_buttons = {}  # Track window menu buttons {window_id: button}
        self.connect('activate', self.on_activate)
        self.connect("open", self.on_open)
        
        # Set up default page setup
        self.default_page_setup = self.create_default_page_setup()
    
        # Window properties (migrated from WebkitWordWindow)
        self.modified = False
        self.auto_save_enabled = False
        self.auto_save_interval = 60
        self.current_file = None
        self.auto_save_source_id = None
        
        # Import methods from file_operations module
        file_operation_methods = [
            # File opening methods
            'on_open_clicked', 'on_open_new_window_response',
            'on_open_current_window_response', 'load_file',
            '_process_image_references', '_get_mime_type', 'cleanup_temp_files',
            'convert_with_libreoffice', 'show_loading_dialog',
            
            # File saving methods
            'on_save_clicked', '_on_save_dialog_response', 'show_save_dialog',
            'show_format_selection_dialog', 'on_save_as_clicked', 'show_custom_save_dialog',
            '_create_custom_save_dialog', '_get_shortened_path',
            '_on_browse_clicked','_on_dialog_response', '_on_format_selection_response',
            '_on_folder_selected', 'show_save_as_warning_dialog', '_on_save_warning_response',
            '_get_file_path_from_dialog', 'show_conversion_notification', 
            'update_save_sensitivity', '_handle_system_save_dialog_response',
            '_on_custom_dialog_response', '_open_system_save_dialog',
            
            
            # Format-specific save methods
            'save_as_mhtml', '_restore_editable_after_save', '_restore_editable_state', 
            '_do_mhtml_save_with_non_editable_content', 'save_webkit_callback', 'save_as_html',
            'save_as_text','save_as_markdown', '_simple_markdown_to_html',

            # Save as PDF
            'save_as_pdf', '_save_pdf_step1', '_save_pdf_step2', '_pdf_save_success',
            '_pdf_save_cleanup', '_cleanup_temp_dir', 'set_secondary_text',
            'show_page_setup_dialog', '_generate_pdf_with_settings', 
            '_on_pdf_print_finished', '_on_pdf_print_failed',
            # Callback handlers
            'save_html_callback', 'save_text_callback',
            'save_markdown_callback', 'save_completion_callback',
            
            # Legacy methods for backward compatibility
            '_on_save_response', '_on_save_as_response', '_on_get_html_content',
            '_on_file_saved',
            
            # webkit
            '_on_editor_ready_for_mhtml', '_check_mhtml_load_status', 
            '_handle_mhtml_load_check', '_check_mhtml_load_error',
            '_ensure_content_editable', '_ensure_mhtml_content_editable',
            '_handle_editable_status', '_inject_editable_script',
            'load_mhtml_with_webkit', '_load_mhtml_file', '_process_mhtml_resources',
            '_extract_mhtml_content', '_on_mhtml_content_extracted',
            '_load_html_with_webkit', '_extract_html_content', '_on_html_content_extracted',
            
        ]
        
        # Import methods from file_operations
        for method_name in file_operation_methods:
            if hasattr(file_operations, method_name):
                setattr(self, method_name, getattr(file_operations, method_name).__get__(self, WebkitWordApp))
                
        # Import methods from find module
        find_methods = [
            'create_find_bar', 'on_find_shortcut', 'on_find_clicked',
            'on_close_find_clicked', 'on_case_sensitive_toggled',
            'on_find_text_changed', 'on_search_result', 'on_find_next_clicked',
            'on_find_previous_clicked', 'on_replace_clicked', 
            'on_replace_all_clicked', 'on_replace_all_result', 
            'on_find_key_pressed', 'on_find_button_toggled',
            'populate_find_field_from_selection', '_on_get_selection_for_find',
            'search_functions_js'
        ]
        
        # Import methods from find module
        for method_name in find_methods:
            if hasattr(find, method_name):
                setattr(self, method_name, getattr(find, method_name).__get__(self, WebkitWordApp))

        # Import methods from keyboard_shortcuts module
        keyboard_shortcuts_methods = [
            'on_webview_key_pressed', 
            'on_replace_shortcut', 'on_paragraph_style_shortcut',
            'on_numbered_list_shortcut', 'on_bullet_list_shortcut',
            'on_align_left_shortcut', 'on_align_center_shortcut', 
            'on_align_right_shortcut', 'on_align_justify_shortcut',
            'on_zoom_in_shortcut', 'on_zoom_out_shortcut', 'on_zoom_reset_shortcut', 
            'setup_scroll_zoom', 'on_scroll', 'apply_zoom', 
        ]

        # Import methods from keyboard_shortcuts module
        for method_name in keyboard_shortcuts_methods:
            if hasattr(keyboard_shortcuts, method_name):
                setattr(self, method_name, getattr(keyboard_shortcuts, method_name).__get__(self,WebkitWordApp))
        

        # Import methods from formatting_toolbar module
        formatting_toolbar_methods = [
            'on_select_all_clicked', 'on_bold_shortcut', 'on_italic_shortcut',
            'on_underline_shortcut', 'on_strikeout_shortcut', 'on_subscript_shortcut',
            'on_superscript_shortcut', 'on_bold_toggled', 'on_italic_toggled',
            'on_underline_toggled', 'on_strikeout_toggled', 'on_subscript_toggled',
            'on_superscript_toggled', 'on_formatting_changed', 'on_indent_clicked',
            'on_outdent_clicked', 'on_bullet_list_toggled', 'on_numbered_list_toggled',
            '_update_alignment_buttons', 'on_align_left_toggled', 'on_align_center_toggled',
            'on_align_right_toggled', 'on_align_justify_toggled', '_update_alignment_buttons',
            'selection_change_js', 'on_paragraph_style_changed', 'on_font_changed',
            'on_font_size_changed', 'cleanup_editor_tags', 'create_color_button',
            'on_font_color_button_clicked', 'on_font_color_selected', 'on_font_color_automatic_clicked',
            'on_more_font_colors_clicked', 'on_font_color_dialog_response', 'apply_font_color',
            'on_bg_color_button_clicked', 'on_bg_color_selected', 'on_bg_color_automatic_clicked',
            'on_more_bg_colors_clicked', 'on_bg_color_dialog_response', 'apply_bg_color',
            'set_box_color', 'on_clear_formatting_clicked', 'on_change_case',
            'on_drop_cap_clicked', '_handle_drop_cap_result', 'on_show_formatting_marks_toggled',
            'on_line_spacing_shortcut', 'on_font_size_change_shortcut',
            
        ]

        # Import methods from formatting_toolbar module
        for method_name in formatting_toolbar_methods:
            if hasattr(formatting_operations, method_name):
                setattr(self, method_name, getattr(formatting_operations, method_name).__get__(self, WebkitWordApp))


        # Import methods from insert_table module
        insert_table_methods = [
            '_parse_color_string', '_is_dark_theme', '_rgba_to_color',
            '_update_margin_controls', 'on_margin_changed', 'on_table_float_clicked',
            'insert_table_js', 'table_theme_helpers_js', 'table_handles_css_js',
            'table_insert_functions_js', 'table_activation_js', 'table_drag_resize_js',
            'table_row_column_js', 'table_alignment_js', 'table_floating_js',
            'table_event_handlers_js', 'table_color_js', 'table_border_style_js',
            'create_table_toolbar', 'on_insert_table_clicked', 'on_table_dialog_response',
            'on_table_clicked', 'on_table_deleted', 'on_tables_deactivated',
            'on_webview_key_pressed', 'on_add_row_above_clicked', 'on_add_row_below_clicked',
            'on_add_column_before_clicked', 'on_add_column_after_clicked', 'on_delete_row_clicked',
            'on_delete_column_clicked', 'on_delete_table_clicked', 'on_table_align_left',
            'on_table_align_center', 'on_table_align_right', 'on_table_full_width',
            'on_close_table_toolbar_clicked', 'on_table_button_clicked', '_create_border_tab',
            '_create_margin_tab', '_create_color_tab', '_initialize_table_properties',
            '_on_get_table_properties', 'on_border_style_changed', 'on_border_width_changed',
            'on_border_shadow_changed', '_reset_default_margins', '_get_color_from_button',
            '_set_color_on_button', '_show_color_dialog', '_on_color_chosen', 
            '_on_color_dialog_response', '_apply_border_color', '_apply_table_color',
            '_apply_header_color', '_apply_cell_color', '_apply_row_color', '_apply_column_color',
            '_reset_default_colors', '_update_color_buttons_after_reset', 
            'on_border_display_option_clicked', '_apply_combined_borders', 'table_z_index_js',
            'on_bring_forward_clicked', 'on_send_backward_clicked', 
        ]

        # Import methods from insert_table module
        for method_name in insert_table_methods:
            if hasattr(insert_table, method_name):
                setattr(self, method_name, getattr(insert_table, method_name).__get__(self, WebkitWordApp))

        # Import methods from show_html module
        show_html_methods = [
            # File opening methods
            'on_show_html_clicked', 'show_html_dialog',
            'apply_html_changes', 'copy_html_to_clipboard',
            'handle_apply_html_result', 
        ]
        
        # Import methods from show_html
        for method_name in show_html_methods:
            if hasattr(show_html, method_name):
                setattr(self, method_name, getattr(show_html, method_name).__get__(self, WebkitWordApp))



        
    def do_startup(self):
        """Initialize application and set up CSS provider"""
        Adw.Application.do_startup(self)
        
        # Set up CSS provider
        self.setup_css_provider()
        
        # Create actions
        self.create_actions()


    def setup_css_provider(self):
        """Set up CSS provider for custom styling"""
        self.css_provider = Gtk.CssProvider()
        
        css_data = b"""
.toolbar-container { padding: 0px 0px; background-color: rgba(127, 127, 127, 0.05); }
.flat { background: none; }
.flat:hover { background: rgba(127, 127, 127, 0.25); }
.flat:checked { background: rgba(127, 127, 127, 0.25); }
colorbutton.flat, colorbutton.flat button { background: none; }
colorbutton.flat:hover, colorbutton.flat button:hover { background: rgba(127, 127, 127, 0.25); }
dropdown.flat, dropdown.flat button { background: none; border-radius: 5px; }
dropdown.flat:hover { background: rgba(127, 127, 127, 0.25); }
.flat-header { background: rgba(127, 127, 127, 0.05); border: none; box-shadow: none; padding: 0px; }
.button-box button { min-width: 80px; min-height: 36px; }
.highlighted { background-color: rgba(127, 127, 127, 0.15); }
.toolbar-group { margin: 0px 3px; }
.toolbar-separator { min-height: 0px; min-width: 1px; background-color: alpha(currentColor, 0.15); margin: 0px 0px; }
.color-indicator { min-height: 2px; min-width: 16px; margin-top: 1px; margin-bottom: 0px; border-radius: 2px; }
.color-box { padding: 0px; }




.linked button               {background-color: rgba(127, 127, 127, 0.10); border: solid 1px rgba(127, 127, 127, 0.00); }
.linked button:hover         {background-color: rgba(127, 127, 127, 0.35); border: solid 1px rgba(127, 127, 127, 0.30);}
.linked button:active        {background-color: rgba(127, 127, 127, 0.35); border: solid 1px rgba(127, 127, 127, 0.00);}
.linked button:checked       {background-color: rgba(127, 127, 127, 0.35); border: solid 1px rgba(127, 127, 127, 0.00);}
.linked button:checked:hover {background-color: rgba(127, 127, 127, 0.35); border: solid 1px rgba(127, 127, 127, 0.30);}

/* Corrected menubutton selectors - removed space after colon */
.linked menubutton:first-child  {
    border-top-left-radius: 5px; 
    border-bottom-left-radius: 5px; 
    border-top-right-radius: 0px; 
    border-bottom-right-radius: 0px;
}

.linked menubutton:last-child {
    border-top-left-radius: 0px; 
    border-bottom-left-radius: 0px; 
    border-top-right-radius: 5px; 
    border-bottom-right-radius: 5px; 
} 

/* Additional recommended fixes for consistent styling */
.linked menubutton button {
    background-color: rgba(127, 127, 127, 0.10);
    border: solid 1px rgba(127, 127, 127, 0.00);
}

.linked menubutton button:hover {
    background-color: rgba(127, 127, 127, 0.35);
    border: solid 1px rgba(127, 127, 127, 0.30);
}

.linked menubutton button:active, 
.linked menubutton button:checked {
    background-color: rgba(127, 127, 127, 0.35);
    border: solid 1px rgba(127, 127, 127, 0.00);
}

.linked menubutton button:checked:hover {
    background-color: rgba(127, 127, 127, 0.35);
    border: solid 1px rgba(127, 127, 127, 0.30);
}

.linked splitbutton > menubutton > button.toggle {
    border-top-left-radius: 0px; border-bottom-left-radius: 0px; border-top-right-radius: 0px; border-bottom-right-radius: 0px; padding: 0px 2px 0px 2px; }
.linked splitbutton > button  {
    border-top-left-radius: 0px; border-bottom-left-radius: 0px; border-top-right-radius: 0px; border-bottom-right-radius: 0px;}
.linked splitbutton:first-child > button  {
    border-top-left-radius: 5px; border-bottom-left-radius: 5px; border-top-right-radius: 0px; border-bottom-right-radius: 0px;}
.linked splitbutton:last-child > button  {
    border-top-left-radius: 0px; border-bottom-left-radius: 0px; border-top-right-radius: 0px; border-bottom-right-radius: 0px;}
.linked splitbutton:last-child > menubutton > button.toggle   {
    border-top-left-radius: 0px; border-bottom-left-radius: 0px; border-top-right-radius: 5px; border-bottom-right-radius: 5px;}

"""
        
        # Load the CSS data
        try:
            self.css_provider.load_from_data(css_data)
        except Exception as e:
            print(f"Error loading CSS data: {e}")
            return
        
        # Apply the CSS provider using the appropriate method based on GTK version
        try:
            # GTK4 method (modern approach)
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                self.css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except (AttributeError, TypeError) as e:
            # Fallback for GTK3 if the application is using an older version
            try:
                screen = Gdk.Screen.get_default()
                Gtk.StyleContext.add_provider_for_screen(
                    screen,
                    self.css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
            except Exception as e2:
                print(f"Error applying CSS provider: {e2}")
        
    def on_activate(self, app):
        """Handle application activation (new window)"""
        win = self.create_window()
        win.present()
        
        # Set focus after window is shown - this is crucial
        GLib.timeout_add(500, lambda: self.set_initial_focus(win))
        
        self.update_window_menu()


    def on_open(self, app, files, n_files, hint):
        """Handle file opening"""
        windows_added = False
        
        for file in files:
            file_path = file.get_path()
            existing_win = None
            for win in self.windows:
                if hasattr(win, 'current_file') and win.current_file and win.current_file.get_path() == file_path:
                    existing_win = win
                    break
            
            if existing_win:
                existing_win.present()
            else:
                win = self.create_window()
                self.load_file(win, file_path)
                win.present()
                windows_added = True
                
        if windows_added:
            self.update_window_menu()
                
    def setup_headerbar_content(self, win):
        """Create improved headerbar content with essential operations"""
        win.headerbar.set_margin_top(0)
        win.headerbar.set_margin_bottom(0)
        
        # --- LEFT SIDE OF HEADERBAR ---
        
        # Add file toolbar toggle button
        file_toolbar_toggle = Gtk.ToggleButton(icon_name="view-more-horizontal-symbolic")
        file_toolbar_toggle.set_tooltip_text("Show/Hide File Toolbar")
        file_toolbar_toggle.set_active(False)  # Hidden by default
        file_toolbar_toggle.connect("toggled", lambda btn: self.toggle_file_toolbar(win, btn))
        file_toolbar_toggle.add_css_class("flat")
        win.headerbar.pack_start(file_toolbar_toggle)
        

        # Find-Replace toggle button
        win.find_button = Gtk.ToggleButton(icon_name="edit-find-replace-symbolic")
        win.find_button.set_tooltip_text("Find and Replace (Ctrl+F)")
        win.find_button_handler_id = win.find_button.connect("toggled", lambda btn: self.on_find_button_toggled(win, btn))
        win.find_button.set_size_request(40, 36)        
        # --- CENTER TITLE ---
        
        # Set up the window title widget
        title_widget = Adw.WindowTitle()
        title_widget.set_title("Untitled  - Webkit Word")
        win.title_widget = title_widget  # Store for later updates
        
        # Save reference to update title 
        win.headerbar.set_title_widget(title_widget)
        
        # --- RIGHT SIDE OF HEADERBAR ---
        
        # Create menu button (last item on right side)
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        #menu_button.add_css_class("flat")  # Add flat style
        
        # Create menu
        menu = Gio.Menu()
        
        # File menu section
        file_section = Gio.Menu()
        file_section.append("New Window", "app.new-window")
        file_section.append("Open", "app.open")
        file_section.append("Save", "app.save")
        file_section.append("Save As", "app.save-as")
        menu.append_section("File", file_section)
        
        # View menu section
        view_section = Gio.Menu()
        view_section.append("Show/Hide File Toolbar", "app.toggle-file-toolbar")
        view_section.append("Show/Hide Format Toolbar", "app.toggle-format-toolbar")
        view_section.append("Show/Hide Statusbar", "app.toggle-statusbar")
        menu.append_section("View", view_section)
        
        # App menu section
        app_section = Gio.Menu()
        app_section.append("Preferences", "app.preferences")
        app_section.append("About", "app.about")
        app_section.append("Quit", "app.quit")
        menu.append_section("Application", app_section)
        
        menu_button.set_menu_model(menu)

        # Connect to popover's closed signal to restore focus to webview
        popover = menu_button.get_popover()
        if popover:
            popover.connect("closed", lambda _: win.webview.grab_focus())
            
            # In GTK 4, we use controller-based event handling instead of signals
            key_controller = Gtk.EventControllerKey.new()
            key_controller.connect("key-pressed", self.on_popover_key_pressed, popover, win)
            popover.add_controller(key_controller)
                    
        # Add menu button to header bar
        win.headerbar.pack_end(menu_button)

        self.add_window_menu_button(win)
            

    def on_popover_key_pressed(self, controller, keyval, keycode, state, popover, win):
        """Handle key pressed events in popovers (GTK 4 style)"""
        # Check if ESC key was pressed
        if keyval == Gdk.KEY_Escape:
            # Hide the popover
            popover.popdown()
            # Set focus back to webview
            win.webview.grab_focus()
            return True  # Event was handled
            
        return False  # Let other handlers process the event
      
## /Insert related code

    def on_cut_clicked(self, win, btn):
        """Handle cut button click"""
        self.execute_js(win, """
            (function() {
                let sel = window.getSelection();
                if (sel.rangeCount) {
                    document.execCommand('cut');
                    return true;
                }
                return false;
            })();
        """)
        win.statusbar.set_text("Cut to clipboard")
        win.webview.grab_focus()

    def on_copy_clicked(self, win, btn):
        """Handle copy button click"""
        self.execute_js(win, """
            (function() {
                let sel = window.getSelection();
                if (sel.rangeCount) {
                    document.execCommand('copy');
                    return true;
                }
                return false;
            })();
        """)
        win.statusbar.set_text("Copied to clipboard")
        win.webview.grab_focus()
        
    def on_paste_clicked(self, win, btn):
        """Handle paste button click"""
        # Try to get text from clipboard
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.read_text_async(None, self.on_text_received, win)
        win.statusbar.set_text("Pasting from clipboard...")
        win.webview.grab_focus()

    def on_text_received(self, clipboard, result, win):
        """Handle clipboard text retrieval"""
        try:
            text = clipboard.read_text_finish(result)
            if text:
                # Escape text for JavaScript
                import json
                text_json = json.dumps(text)
                # Insert the text at cursor position
                self.execute_js(win, f"""
                    (function() {{
                        document.execCommand('insertText', false, {text_json});
                        return true;
                    }})();
                """)
                win.statusbar.set_text("Pasted from clipboard")
            else:
                win.statusbar.set_text("No text in clipboard")
        except GLib.Error as e:
            print("Paste error:", e.message)
            win.statusbar.set_text(f"Paste failed: {e.message}")
            
    def on_zoom_changed(self, win, scale, zoom_button):
        """Handle zoom scale change"""
        zoom_level = int(scale.get_value())
        zoom_button.set_label(f"{zoom_level}%")
        win.zoom_level = zoom_level
        
        # Apply zoom to the editor
        self.apply_zoom(win, zoom_level)

    def on_zoom_preset_clicked(self, win, preset, scale, zoom_button, popover):
        """Handle zoom preset button click"""
        scale.set_value(preset)
        zoom_button.set_label(f"{preset}%")
        win.zoom_level = preset
        
        # Apply zoom to the editor
        self.apply_zoom(win, preset)
        
        # Close the popover
        popover.popdown()

    def apply_zoom(self, win, zoom_level):
        """Apply zoom level to the editor"""
        # Convert percentage to scale factor (1.0 = 100%)
        scale_factor = zoom_level / 100.0
        
        # Apply zoom using JavaScript
        js_code = f"""
        (function() {{
            document.body.style.zoom = "{scale_factor}";
            document.getElementById('editor').style.zoom = "{scale_factor}";
            return true;
        }})();
        """
        
        self.execute_js(win, js_code)
        #win.statusbar.set_text(f"Zoom level: {zoom_level}%")    
        



        





    def toggle_statusbar(self, win, *args):
        """Toggle the visibility of the statusbar with animation"""
        is_revealed = win.statusbar_revealer.get_reveal_child()
        win.statusbar_revealer.set_reveal_child(not is_revealed)
        if not is_revealed:
            win.statusbar.set_text("Statusbar shown")
        win.webview.grab_focus()            
        return True
    
    def toggle_headerbar(self, win, *args):
        """Toggle the visibility of the headerbar with animation"""
        is_revealed = win.headerbar_revealer.get_reveal_child()
        win.headerbar_revealer.set_reveal_child(not is_revealed)
        status = "hidden" if is_revealed else "shown"
        win.statusbar.set_text(f"Headerbar {status}")
        win.webview.grab_focus()            
        return True

    def toggle_file_toolbar(self, win, *args):
        """Toggle the visibility of the file toolbar with animation"""
        is_revealed = win.file_toolbar_revealer.get_reveal_child()
        win.file_toolbar_revealer.set_reveal_child(not is_revealed)
        status = "hidden" if is_revealed else "shown"
        win.statusbar.set_text(f"File toolbar {status}")
        
        # If the button is provided (from headerbar), update its state
        if len(args) > 0 and isinstance(args[0], Gtk.ToggleButton):
            toggle_button = args[0]
            # Block the handler if we have its ID
            if hasattr(toggle_button, 'toggle_handler_id'):
                toggle_button.handler_block(toggle_button.toggle_handler_id)
                toggle_button.set_active(not is_revealed)
                toggle_button.handler_unblock(toggle_button.toggle_handler_id)
        win.webview.grab_focus()            
        return True
        
    def toggle_format_toolbar(self, win, *args):
        """Toggle the visibility of the formatting toolbar with animation"""
        is_revealed = win.toolbar_revealer.get_reveal_child()
        win.toolbar_revealer.set_reveal_child(not is_revealed)
        status = "hidden" if is_revealed else "shown"
        win.statusbar.set_text(f"Format toolbar {status}")
        
        # If the button is provided (from headerbar), update its state
        if len(args) > 0 and isinstance(args[0], Gtk.ToggleButton):
            toggle_button = args[0]
            # Temporarily block signal handler to prevent recursion
            handlers = toggle_button.list_signal_handlers()
            for handler_id in handlers:
                toggle_button.handler_block(handler_id)
            
            toggle_button.set_active(not is_revealed)
            
            # Unblock the handlers
            for handler_id in handlers:
                toggle_button.handler_unblock(handler_id)
        win.webview.grab_focus()
        return True

    def on_close_shortcut(self, win, *args):
        """Handle Ctrl+W shortcut to close current window"""
        win.close()
        return True

    def on_close_others_shortcut(self, win, *args):
        """Handle Ctrl+Shift+W shortcut to close other windows"""
        self.on_close_other_windows(None, None)
        return True

######### get_editor_html and it's sub methods;                 

    def get_editor_html(self, content=""):
        """Return HTML for the editor with improved table and text box styles"""
        content = self._prepare_content(content)
        
        return f"""
        <!DOCTYPE html>
        <html style="height: 100%;">
        <head>
            {self._get_editor_head(content)}
        </head>
        <body>
            {self._get_editor_body()}
        </body>
        </html>
        """

    def _prepare_content(self, content):
        """Prepare content for HTML embedding by escaping special characters"""
        return content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

    def _get_editor_head(self, content):
        """Return the head section of the editor HTML"""
        return f"""
            <title>Webkit Word</title>
            <style>
                {self._get_base_styles()}
                {self._get_table_styles()}
                {self._get_floating_table_styles()}
                {self._get_text_box_styles()}
                {self._get_selection_styles()}
                {self._get_dark_mode_styles()}
                {self._get_light_mode_styles()}
            </style>
            <script>
                window.initialContent = "{content or '<div><font face="Sans" style="font-size: 11pt;"><br></font></div>'}";
                {self.get_editor_js()}
            </script>
        """

    def _get_editor_body(self):
        """Return the body section of the editor HTML"""
        return """
            <div id="editor" contenteditable="true"></div>
        """

    def _get_base_styles(self):
        """Return base CSS styles for the editor"""
        return """
            html, body {
                height: 100%;
                padding: 0;
                font-family: Sans;
            }
            #editor {
                padding: 0px;
                outline: none;
                height: 100%;
                font-family: Sans;
                font-size: 11pt;
                position: relative; /* Important for absolute positioning of floating tables */
                min-height: 300px;  /* Ensure there's space to drag tables */
            }
            #editor div {
                margin: 0;
                padding: 0;
            }
            #editor:empty:not(:focus):before {
                content: "Type here to start editing...";
                color: #aaa;
                font-style: italic;
                position: absolute;
                pointer-events: none;
                top: 10px;
                left: 10px;
            }
        """

    def _get_table_styles(self):
        """Return CSS styles for tables"""
        return """
            /* Table styles */
            table {
                border-collapse: collapse;
                margin: 0 0 10px 0;  /* Changed from margin: 10px 0 */
                position: relative;  /* Important for internal handles */
                resize: both;
                overflow: visible;   /* Changed from auto to visible to ensure handles are not clipped */
                min-width: 30px;
                min-height: 30px;
            }
            table.left-align {
                float: left;
                margin-right: 10px;
                margin-top: 0;  /* Ensure no top margin for floated tables */
                clear: none;
            }
            table.right-align {
                float: right;
                margin-left: 10px;
                margin-top: 0;  /* Ensure no top margin for floated tables */
                clear: none;
            }
            table.center-align {
                display: table;  /* Ensure block behavior is correct */
                margin-left: auto !important;
                margin-right: auto !important;
                margin-top: 0;
                float: none !important;
                clear: both;
                position: relative;
            }
            table.no-wrap {
                float: none;
                clear: both;
                width: 100%;
                margin-top: 0;
            }
            table td {
                padding: 5px;
                min-width: 30px;
                position: relative;
            }
            table th {
                padding: 5px;
                min-width: 30px;
                background-color: #f0f0f0;
            }
        """

    def _get_floating_table_styles(self):
        """Return CSS styles for floating tables"""
        return """
            /* Floating table styles - border removed from CSS and applied conditionally via JS */
            table.floating-table {
                position: absolute !important;
                z-index: 50;
                box-shadow: 0 3px 10px rgba(0,0,0,0.2);
                background-color: rgba(255, 255, 255, 0.95);
                cursor: grab;
            }
            
            table.floating-table:active {
                cursor: grabbing;
            }
            
            table.floating-table .table-drag-handle {
                width: 20px !important;
                height: 20px !important;
                border-radius: 3px;
                opacity: 0.9;
            }
        """

    def _get_text_box_styles(self):
        """Return CSS styles for text box tables"""
        return """
            /* Text box styles (enhanced table) */
            table.text-box-table {
                border: 1px solid #ccc !important;
                border-radius: 0px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                background-color: #fff;
                width: 80px;  /* Initial width */
                height: 80px; /* Initial height */
                min-width: 80px;
                min-height: 80px;
                resize: both !important; /* Ensure resizability */
            }
            
            table.text-box-table td {
                vertical-align: top;
            }
        """

    def _get_selection_styles(self):
        """Return CSS styles for text selection"""
        return """
            /* Ensure text boxes handle selection properly */
            #editor ::selection {
                background-color: #b5d7ff;
                color: inherit;
            }
        """

    def _get_dark_mode_styles(self):
        """Return CSS styles for dark mode"""
        return """
            @media (prefers-color-scheme: dark) {
                html, body {
                    background-color: #1e1e1e;
                    color: #c0c0c0;
                }
                table th {
                    background-color: #2a2a2a;
                }
                table.text-box-table {
                    border-color: #444 !important;
                    background-color: #2d2d2d;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                }
                table.floating-table {
                    background-color: rgba(45, 45, 45, 0.95);
                    box-shadow: 0 3px 10px rgba(0,0,0,0.5);
                }
                #editor ::selection {
                    background-color: #264f78;
                    color: inherit;
                }
            }
        """

    def _get_light_mode_styles(self):
        """Return CSS styles for light mode"""
        return """
            @media (prefers-color-scheme: light) {
                html, body {
                    background-color: #ffffff;
                    color: #000000;
                }
            }
        """
################ /get_editor_html 

    def get_editor_js(self):
        """Return the combined JavaScript logic for the editor."""
        return f"""
        // Global scope for persistence
        window.undoStack = [];
        window.redoStack = [];
        window.isUndoRedo = false;
        window.lastContent = "";
        
        // Search variables
        var searchResults = [];
        var searchIndex = -1;
        var currentSearchText = "";

        {self.save_state_js()}
        {self.perform_undo_js()}
        {self.perform_redo_js()}
        {self.find_last_text_node_js()}
        {self.get_stack_sizes_js()}
        {self.set_content_js()}
        {self.selection_change_js()}
        {self.search_functions_js()}
        {self.paragraph_and_line_spacing_js()}
        {self.insert_table_js()}
        {self.table_border_style_js()}
        {self.table_color_js()}
        {self.table_z_index_js()}
        {self.insert_link_js()}
        {self.rtl_toggle_js()}
        {self.wordart_js()}  // Add the Word Art JavaScript
        {self.init_editor_js()}
        """

    
    def save_state_js(self):
        """JavaScript to save the editor state to the undo stack."""
        return """
        function saveState() {
            window.undoStack.push(document.getElementById('editor').innerHTML);
            if (window.undoStack.length > 100) {
                window.undoStack.shift();
            }
        }
        """

    def perform_undo_js(self):
        """JavaScript to perform an undo operation."""
        return """
        function performUndo() {
            const editor = document.getElementById('editor');
            if (window.undoStack.length > 1) {
                let selection = window.getSelection();
                let range = selection.rangeCount > 0 ? selection.getRangeAt(0) : null;
                let cursorNode = range ? range.startContainer : null;
                let cursorOffset = range ? range.startOffset : 0;

                window.redoStack.push(window.undoStack.pop());
                window.isUndoRedo = true;
                editor.innerHTML = window.undoStack[window.undoStack.length - 1];
                window.lastContent = editor.innerHTML;
                window.isUndoRedo = false;

                editor.focus();
                try {
                    const newRange = document.createRange();
                    const sel = window.getSelection();
                    const textNode = findLastTextNode(editor) || editor;
                    const offset = textNode.nodeType === 3 ? textNode.length : 0;
                    newRange.setStart(textNode, offset);
                    newRange.setEnd(textNode, offset);
                    sel.removeAllRanges();
                    sel.addRange(newRange);
                } catch (e) {
                    console.log("Could not restore cursor position:", e);
                }
                return { success: true, isInitialState: window.undoStack.length === 1 };
            }
            return { success: false, isInitialState: window.undoStack.length === 1 };
        }
        """

    def perform_redo_js(self):
        """JavaScript to perform a redo operation."""
        return """
        function performRedo() {
            const editor = document.getElementById('editor');
            if (window.redoStack.length > 0) {
                let selection = window.getSelection();
                let range = selection.rangeCount > 0 ? selection.getRangeAt(0) : null;
                let cursorNode = range ? range.startContainer : null;
                let cursorOffset = range ? range.startOffset : 0;

                const state = window.redoStack.pop();
                window.undoStack.push(state);
                window.isUndoRedo = true;
                editor.innerHTML = state;
                window.lastContent = editor.innerHTML;
                window.isUndoRedo = false;

                editor.focus();
                try {
                    const newRange = document.createRange();
                    const sel = window.getSelection();
                    const textNode = findLastTextNode(editor) || editor;
                    const offset = textNode.nodeType === 3 ? textNode.length : 0;
                    newRange.setStart(textNode, offset);
                    newRange.setEnd(textNode, offset);
                    sel.removeAllRanges();
                    sel.addRange(newRange);
                } catch (e) {
                    console.log("Could not restore cursor position:", e);
                }
                return { success: true, isInitialState: window.undoStack.length === 1 };
            }
            return { success: false, isInitialState: window.undoStack.length === 1 };
        }
        """

    def find_last_text_node_js(self):
        """JavaScript to find the last text node for cursor restoration."""
        return """
        function findLastTextNode(node) {
            if (node.nodeType === 3) return node;
            for (let i = node.childNodes.length - 1; i >= 0; i--) {
                const found = findLastTextNode(node.childNodes[i]);
                if (found) return found;
            }
            return null;
        }
        """

    def get_stack_sizes_js(self):
        """JavaScript to get the sizes of undo and redo stacks."""
        return """
        function getStackSizes() {
            return {
                undoSize: window.undoStack.length,
                redoSize: window.redoStack.length
            };
        }
        """

    def set_content_js(self):
        """JavaScript to set the editor content and reset stacks."""
        return """
        function setContent(html) {
            const editor = document.getElementById('editor');
            if (!html || html.trim() === '') {
                editor.innerHTML = '<div><br></div>';
            } else if (!html.trim().match(/^<(div|p|h[1-6]|ul|ol|table)/i)) {
                editor.innerHTML = '<div>' + html + '</div>';
            } else {
                editor.innerHTML = html;
            }
            window.lastContent = editor.innerHTML;
            window.undoStack = [window.lastContent];
            window.redoStack = [];
            editor.focus();
        }
        """

    def selection_change_js(self):
        """JavaScript to track selection changes and update formatting buttons"""
        return """
        function updateFormattingState() {
            try {
                // Get basic formatting states
                const isBold = document.queryCommandState('bold');
                const isItalic = document.queryCommandState('italic');
                const isUnderline = document.queryCommandState('underline');
                const isStrikeThrough = document.queryCommandState('strikeThrough');
                const isSubscript = document.queryCommandState('subscript');
                const isSuperscript = document.queryCommandState('superscript');
                
                // Get the current paragraph formatting
                let paragraphStyle = 'Normal'; // Default
                const selection = window.getSelection();
                let fontFamily = '';
                let fontSize = '';
                
                if (selection.rangeCount > 0) {
                    const range = selection.getRangeAt(0);
                    const node = range.commonAncestorContainer;
                    
                    // Find the closest block element
                    const getNodeName = (node) => {
                        return node.nodeType === 1 ? node.nodeName.toLowerCase() : null;
                    };
                    
                    const getParentBlockElement = (node) => {
                        if (node.nodeType === 3) { // Text node
                            return getParentBlockElement(node.parentNode);
                        }
                        const tagName = getNodeName(node);
                        if (['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div'].includes(tagName)) {
                            return node;
                        }
                        if (node.parentNode && node.parentNode.id !== 'editor') {
                            return getParentBlockElement(node.parentNode);
                        }
                        return null;
                    };
                    
                    const blockElement = getParentBlockElement(node);
                    if (blockElement) {
                        const tagName = getNodeName(blockElement);
                        switch (tagName) {
                            case 'h1': paragraphStyle = 'Heading 1'; break;
                            case 'h2': paragraphStyle = 'Heading 2'; break;
                            case 'h3': paragraphStyle = 'Heading 3'; break;
                            case 'h4': paragraphStyle = 'Heading 4'; break;
                            case 'h5': paragraphStyle = 'Heading 5'; break;
                            case 'h6': paragraphStyle = 'Heading 6'; break;
                            default: paragraphStyle = 'Normal'; break;
                        }
                    }
                    
                    // Enhanced font size detection
                    // Start with the deepest element at cursor/selection
                    let currentElement = node;
                    if (currentElement.nodeType === 3) { // Text node
                        currentElement = currentElement.parentNode;
                    }
                    
                    // Work our way up the DOM tree to find font-size styles
                    while (currentElement && currentElement !== editor) {
                        // Check for inline font size
                        if (currentElement.style && currentElement.style.fontSize) {
                            fontSize = currentElement.style.fontSize;
                            break;
                        }
                        
                        // Check for font elements with size attribute
                        if (currentElement.tagName && currentElement.tagName.toLowerCase() === 'font' && currentElement.hasAttribute('size')) {
                            // This is a rough conversion from HTML font size (1-7) to points
                            const htmlSize = parseInt(currentElement.getAttribute('size'));
                            const sizeMap = {1: '8', 2: '10', 3: '12', 4: '14', 5: '18', 6: '24', 7: '36'};
                            fontSize = sizeMap[htmlSize] || '12';
                            break;
                        }
                        
                        // If we haven't found a font size yet, move up to parent
                        currentElement = currentElement.parentNode;
                    }
                    
                    // If we still don't have a font size, get it from computed style
                    if (!fontSize) {
                        // Use computed style as a fallback
                        const computedStyle = window.getComputedStyle(node.nodeType === 3 ? node.parentNode : node);
                        fontSize = computedStyle.fontSize;
                    }
                    
                    // Convert pixel sizes to points (approximate)
                    if (fontSize.endsWith('px')) {
                        const pxValue = parseFloat(fontSize);
                        fontSize = Math.round(pxValue * 0.75).toString();
                    } else if (fontSize.endsWith('pt')) {
                        fontSize = fontSize.replace('pt', '');
                    } else {
                        // For other units or no units, try to extract just the number
                        fontSize = fontSize.replace(/[^0-9.]/g, '');
                    }
                    
                    // Get font family using a similar approach
                    currentElement = node;
                    if (currentElement.nodeType === 3) {
                        currentElement = currentElement.parentNode;
                    }
                    
                    while (currentElement && currentElement !== editor) {
                        if (currentElement.style && currentElement.style.fontFamily) {
                            fontFamily = currentElement.style.fontFamily;
                            // Clean up quotes and fallbacks
                            fontFamily = fontFamily.split(',')[0].replace(/["']/g, '');
                            break;
                        }
                        
                        // Check for font elements with face attribute
                        if (currentElement.tagName && currentElement.tagName.toLowerCase() === 'font' && currentElement.hasAttribute('face')) {
                            fontFamily = currentElement.getAttribute('face');
                            break;
                        }
                        
                        currentElement = currentElement.parentNode;
                    }
                    
                    // If we still don't have a font family, get it from computed style
                    if (!fontFamily) {
                        const computedStyle = window.getComputedStyle(node.nodeType === 3 ? node.parentNode : node);
                        fontFamily = computedStyle.fontFamily.split(',')[0].replace(/["']/g, '');
                    }
                }
                
                // Send the state to Python - MAKE SURE subscript and superscript are included here
                window.webkit.messageHandlers.formattingChanged.postMessage(
                    JSON.stringify({
                        bold: isBold, 
                        italic: isItalic, 
                        underline: isUnderline,
                        strikeThrough: isStrikeThrough,
                        subscript: isSubscript,
                        superscript: isSuperscript,
                        paragraphStyle: paragraphStyle,
                        fontFamily: fontFamily,
                        fontSize: fontSize
                    })
                );
            } catch(e) {
                console.log("Error updating formatting state:", e);
            }
        }
        
        document.addEventListener('selectionchange', function() {
            // Only update if the selection is in our editor
            const selection = window.getSelection();
            if (selection.rangeCount > 0) {
                const range = selection.getRangeAt(0);
                const editor = document.getElementById('editor');
                
                // Check if the selection is within our editor
                if (editor.contains(range.commonAncestorContainer)) {
                    updateFormattingState();
                }
            }
        });
        """

    def init_editor_js(self):
        """JavaScript to initialize the editor and set up event listeners."""
        return f"""
        {self.setup_tab_key_handler_js()}
        {self.setup_first_focus_handler_js()}
        {self.setup_input_handler_js()}
        {self.dom_content_loaded_handler_js()}
        """

    def setup_tab_key_handler_js(self):
        """JavaScript to handle tab key behavior in the editor."""
        return """
        function setupTabKeyHandler(editor) {
            editor.addEventListener('keydown', function(e) {
                if (e.key === 'Tab') {
                    // Check if we're inside a table cell
                    const selection = window.getSelection();
                    if (selection.rangeCount > 0) {
                        let node = selection.anchorNode;
                        
                        // Find parent cell (TD or TH)
                        while (node && node !== editor) {
                            if (node.tagName === 'TD' || node.tagName === 'TH') {
                                // We're in a table cell
                                e.preventDefault();
                                
                                if (e.shiftKey) {
                                    // Shift+Tab: Navigate to previous cell
                                    navigateToPreviousCell(node);
                                } else {
                                    // Tab: Navigate to next cell
                                    navigateToNextCell(node);
                                }
                                
                                return; // Don't insert a tab character
                            }
                            node = node.parentNode;
                        }
                    }
                    
                    // Not in a table cell - insert tab as normal
                    e.preventDefault();
                    document.execCommand('insertHTML', false, '<span class="Apple-tab-span" style="white-space:pre">\\t</span>');
                    
                    // Trigger input event to register the change for undo/redo
                    const event = new Event('input', {
                        bubbles: true,
                        cancelable: true
                    });
                    editor.dispatchEvent(event);
                }
            });
        }
        
        // Function to navigate to the next table cell
        function navigateToNextCell(currentCell) {
            const currentRow = currentCell.parentNode;
            const currentTable = currentRow.closest('table');
            
            // Find next cell in the same row
            const nextCell = currentCell.nextElementSibling;
            
            if (nextCell) {
                // Move to next cell in same row
                focusCell(nextCell);
            } else {
                // End of row - move to first cell of next row
                const nextRow = currentRow.nextElementSibling;
                if (nextRow) {
                    const firstCell = nextRow.firstElementChild;
                    if (firstCell) {
                        focusCell(firstCell);
                    }
                } else {
                    // End of table - create a new row
                    const newRow = currentTable.insertRow(-1);
                    
                    // Create cells based on the current row's cell count
                    for (let i = 0; i < currentRow.cells.length; i++) {
                        const newCell = newRow.insertCell(i);
                        newCell.innerHTML = '&nbsp;';
                        
                        // Copy styles from the current row
                        const currentRowCell = currentRow.cells[i];
                        if (currentRowCell) {
                            // Copy border style
                            if (currentRowCell.style.border) {
                                newCell.style.border = currentRowCell.style.border;
                            } else {
                                newCell.style.border = '1px solid ' + getBorderColor();
                            }
                            // Copy padding style
                            if (currentRowCell.style.padding) {
                                newCell.style.padding = currentRowCell.style.padding;
                            } else {
                                newCell.style.padding = '5px';
                            }
                            // Copy background color if any
                            if (currentRowCell.style.backgroundColor) {
                                newCell.style.backgroundColor = currentRowCell.style.backgroundColor;
                            }
                        }
                    }
                    
                    // Focus the first cell of the new row
                    if (newRow.firstElementChild) {
                        focusCell(newRow.firstElementChild);
                    }
                    
                    // Notify that content changed
                    try {
                        window.webkit.messageHandlers.contentChanged.postMessage('changed');
                    } catch(e) {
                        console.log("Could not notify about content change:", e);
                    }
                }
            }
        }
        
        // Function to navigate to the previous table cell
        function navigateToPreviousCell(currentCell) {
            const currentRow = currentCell.parentNode;
            const currentTable = currentRow.closest('table');
            
            // Find previous cell in the same row
            const previousCell = currentCell.previousElementSibling;
            
            if (previousCell) {
                // Move to previous cell in same row
                focusCell(previousCell);
            } else {
                // Beginning of row - move to last cell of previous row
                const previousRow = currentRow.previousElementSibling;
                if (previousRow) {
                    const lastCell = previousRow.lastElementChild;
                    if (lastCell) {
                        focusCell(lastCell);
                    }
                } else {
                    // Beginning of table - stay in current cell
                    focusCell(currentCell);
                }
            }
        }
        
        // Function to focus a table cell and position cursor at beginning
        function focusCell(cell) {
            // Create a range at the beginning of the cell
            const range = document.createRange();
            const selection = window.getSelection();
            
            // Try to find the first text node in the cell
            let firstNode = cell;
            let firstTextNode = null;
            
            function findFirstTextNode(node) {
                if (node.nodeType === Node.TEXT_NODE && node.textContent.trim().length > 0) {
                    return node;
                }
                for (let child of node.childNodes) {
                    const result = findFirstTextNode(child);
                    if (result) return result;
                }
                return null;
            }
            
            firstTextNode = findFirstTextNode(cell);
            
            if (firstTextNode) {
                // Place cursor at the beginning of the text
                range.setStart(firstTextNode, 0);
                range.setEnd(firstTextNode, 0);
            } else {
                // No text node found - place cursor at the beginning of the cell
                range.setStart(cell, 0);
                range.setEnd(cell, 0);
            }
            
            // Clear any existing selection and apply the new range
            selection.removeAllRanges();
            selection.addRange(range);
            
            // Scroll the cell into view if needed
            cell.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            
            // Ensure the cell has focus
            cell.focus();
        }
        """

    def setup_first_focus_handler_js(self):
        """JavaScript to handle the first focus event."""
        return """
        function setupFirstFocusHandler(editor) {
            editor.addEventListener('focus', function onFirstFocus(e) {
                if (!editor.textContent.trim() && editor.innerHTML === '') {
                    editor.innerHTML = '<div><br></div>';
                    const range = document.createRange();
                    const sel = window.getSelection();
                    const firstDiv = editor.querySelector('div');
                    if (firstDiv) {
                        range.setStart(firstDiv, 0);
                        range.collapse(true);
                        sel.removeAllRanges();
                        sel.addRange(range);
                    }
                    editor.removeEventListener('focus', onFirstFocus);
                }
            });
        }
        """

    def setup_input_handler_js(self):
        """JavaScript to handle input events and content changes."""
        return """
        function setupInputHandler(editor) {
            editor.addEventListener('input', function(e) {
                if (document.getSelection().anchorNode === editor) {
                    document.execCommand('formatBlock', false, 'div');
                }
                if (!window.isUndoRedo) {
                    const currentContent = editor.innerHTML;
                    if (currentContent !== window.lastContent) {
                        saveState();
                        window.lastContent = currentContent;
                        window.redoStack = [];
                        try {
                            window.webkit.messageHandlers.contentChanged.postMessage("changed");
                        } catch(e) {
                            console.log("Could not notify about changes:", e);
                        }
                    }
                }
            });
        }
        """
        
    def dom_content_loaded_handler_js(self):
        """JavaScript to handle DOMContentLoaded event and initialize the editor."""
        return """
        document.addEventListener('DOMContentLoaded', function() {
            const editor = document.getElementById('editor');
            
            // Give the editor a proper tabindex to ensure it can capture keyboard focus
            editor.setAttribute('tabindex', '0');
            
            // Set up event handlers
            setupTabKeyHandler(editor);
            setupFirstFocusHandler(editor);
            setupInputHandler(editor);
            
            // Initialize content state
            window.lastContent = editor.innerHTML;
            saveState();
            editor.focus();
            
            // Load initial content if available
            if (window.initialContent) {
                setContent(window.initialContent);
            }
        });
        """
        
    def get_initial_html(self):
        return self.get_editor_html('<div><font face="Sans" style="font-size: 11pt;"><br></font></div>')
    
    def execute_js(self, win, script):
        """Execute JavaScript in the WebView"""
        win.webview.evaluate_javascript(script, -1, None, None, None, None, None)
    
    def extract_body_content(self, html):
        """Extract content from the body or just return the HTML if parsing fails"""
        try:
            # Simple regex to extract content between body tags
            import re
            body_match = re.search(r'<body[^>]*>([\s\S]*)<\/body>', html)
            if body_match:
                return body_match.group(1)
            return html
        except Exception:
            # In case of any error, return the original HTML
            return html
    
    # Undo/Redo related methods
    def on_content_changed(self, win, manager, result):
        # Check current modified state before changing it
        was_modified = win.modified
        
        # Set new state and update window title
        win.modified = True
        self.update_window_title(win)
        self.update_undo_redo_state(win)
        
        # Only update window menu if the modified state changed
        if not was_modified:  # If it wasn't modified before but now is
            self.update_window_menu()
        
    def update_undo_redo_state(self, win):
        """Update undo/redo button states with more robust error handling"""
        # First check if the necessary buttons exist
        has_undo_buttons = hasattr(win, 'undo_button') or hasattr(win, 'undo_button_toolbar')
        has_redo_buttons = hasattr(win, 'redo_button') or hasattr(win, 'redo_button_toolbar')
        
        # If we don't have any buttons to update, just return
        if not (has_undo_buttons or has_redo_buttons):
            return
            
        try:
            # Get stack sizes to update button states
            win.webview.evaluate_javascript(
                "JSON.stringify(getStackSizes());",  # Ensure we get a proper JSON string
                -1, None, None, None,
                lambda webview, result, data: self._on_get_stack_sizes(win, webview, result, data), 
                None
            )
        except Exception as e:
            print(f"Error updating undo/redo state: {e}")
            # Fallback - set default button states
            self._set_default_button_states(win, True, False)
        
            
    def on_undo_clicked(self, win, button):
        self.perform_undo(win)
        
    def on_redo_clicked(self, win, button):
        self.perform_redo(win)
        
    def on_undo_shortcut(self, win, *args):
        self.perform_undo(win)
        return True
        
    def on_redo_shortcut(self, win, *args):
        self.perform_redo(win)
        return True
        
    def perform_undo(self, win):
        try:
            win.webview.evaluate_javascript(
                "JSON.stringify(performUndo());",
                -1, None, None, None,
                lambda webview, result, data: self._on_undo_redo_performed(win, webview, result, data),
                "undo"
            )
            win.statusbar.set_text("Undo performed")
        except Exception as e:
            print(f"Error during undo: {e}")
            win.statusbar.set_text("Undo failed")
        win.webview.grab_focus()
        
    def perform_redo(self, win):
        try:
            win.webview.evaluate_javascript(
                "JSON.stringify(performRedo());",
                -1, None, None, None,
                lambda webview, result, data: self._on_undo_redo_performed(win, webview, result, data),
                "redo"
            )
            win.statusbar.set_text("Redo performed")
        except Exception as e:
            print(f"Error during redo: {e}")
            win.statusbar.set_text("Redo failed")
        win.webview.grab_focus()
        
    def _on_undo_redo_performed(self, win, webview, result, operation):
        try:
            js_result = webview.evaluate_javascript_finish(result)
            if js_result:
                result_str = (js_result.get_js_value().to_string() if hasattr(js_result, 'get_js_value') else
                              js_result.to_string() if hasattr(js_result, 'to_string') else str(js_result))
                import json
                result_data = json.loads(result_str)
                success = result_data.get('success', False)
                is_initial_state = result_data.get('isInitialState', False)

                if success:
                    win.statusbar.set_text(f"{operation.capitalize()} performed")
                    
                    # Check current modified state before changing it
                    was_modified = win.modified
                    
                    # Determine new state based on operation and result
                    new_modified_state = not (operation == "undo" and is_initial_state)
                    
                    # Set new state if it's different
                    if win.modified != new_modified_state:
                        win.modified = new_modified_state
                        self.update_window_title(win)
                        
                        # Only update window menu if modified state changed
                        self.update_window_menu()
                    
                    self.update_undo_redo_state(win)
                else:
                    win.statusbar.set_text(f"No more {operation} actions available")
        except Exception as e:
            print(f"Error during {operation}: {e}")
            win.statusbar.set_text(f"{operation.capitalize()} failed")
            
    # Event handlers
    def on_new_clicked(self, win, button):
        # Create a new window with a blank document
        new_win = self.create_window()
        new_win.present()
        GLib.timeout_add(500, lambda: self.set_initial_focus(new_win))
        self.update_window_menu()
        new_win.statusbar.set_text("New document created")
    
    def get_menu_title(self, win):
        if win.current_file:
            # Get the path as a string
            if hasattr(win.current_file, 'get_path'):
                path = win.current_file.get_path()
            else:
                path = win.current_file
            # Extract filename without extension and show modified marker
            filename = os.path.splitext(os.path.basename(path))[0]
            return f"{'  ⃰' if win.modified else ''}{filename}"
        else:
            return f"{'  ⃰' if win.modified else ''}Untitled"

    def update_window_title(self, win):
        """Update window title to show document name (without extension) and modified status"""
        if win.current_file:
            # Get the path as a string
            if hasattr(win.current_file, 'get_path'):
                path = win.current_file.get_path()
            else:
                path = win.current_file
            # Extract filename without extension
            filename = os.path.splitext(os.path.basename(path))[0]
            title = f"{'  ⃰' if win.modified else ''}{filename}"
            win.set_title(f"{title} - Webkit Word")
            
            # Update the title widget if it exists
            if hasattr(win, 'title_widget'):
                win.title_widget.set_title(f"{'  ⃰' if win.modified else ''}{filename} - Webkit Word")
        else:
            title = f"{'  ⃰' if win.modified else ''}Untitled"
            win.set_title(f"{title} - Webkit Word")
            
            # Update the title widget if it exists
            if hasattr(win, 'title_widget'):
                win.title_widget.set_title(f"{'  ⃰' if win.modified else ''}Untitled  - Webkit Word")


    # Window Close Request
    def on_window_close_request(self, win, *args):
        """Handle window close request with save confirmation if needed"""
        if win.modified:
            # Show confirmation dialog
            self.show_save_confirmation_dialog(win, lambda response: self._handle_close_confirmation(win, response))
            # Return True to stop the default close handler
            return True
        else:
            # No unsaved changes, proceed with closing
            self.remove_window(win)
            return False

    def _handle_close_confirmation(self, win, response):
        """Handle the response from the save confirmation dialog"""
        if response == "save":
            # Save and then close
            if win.current_file:
                # We have a file path, save directly
                win.webview.evaluate_javascript(
                    "document.getElementById('editor').innerHTML;",
                    -1, None, None, None,
                    lambda webview, result, data: self._on_save_before_close(win, webview, result, data),
                    None
                )
            else:
                # No file path, show save dialog
                dialog = Gtk.FileDialog()
                dialog.set_title("Save Before Closing")
                
                filter = Gtk.FileFilter()
                filter.set_name("HTML files")
                filter.add_pattern("*.html")
                filter.add_pattern("*.htm")
                
                filters = Gio.ListStore.new(Gtk.FileFilter)
                filters.append(filter)
                
                dialog.set_filters(filters)
                dialog.save(win, None, lambda dialog, result: self._on_save_response_before_close(win, dialog, result))
        elif response == "discard":
            # Mark as unmodified before closing
            win.modified = False
            
            # Close without saving
            self.remove_window(win)
            win.close()
        # If response is "cancel", do nothing and keep the window open

    def _on_save_before_close(self, win, webview, result, data):
        """Save the content and then close the window"""
        try:
            js_result = webview.evaluate_javascript_finish(result)
            if js_result:
                editor_content = (js_result.get_js_value().to_string() if hasattr(js_result, 'get_js_value') else
                               js_result.to_string() if hasattr(js_result, 'to_string') else str(js_result))
                
                # Define a callback that will close the window after saving
                def after_save(file, result):
                    try:
                        success, _ = file.replace_contents_finish(result)
                        if success:
                            win.modified = False  # Mark as unmodified
                            self.update_window_title(win)
                            # Now close the window
                            self.remove_window(win)
                            win.close()
                    except Exception as e:
                        print(f"Error during save before close: {e}")
                        # Close anyway in case of error
                        self.remove_window(win)
                        win.close()
                
                self.save_html_content(win, editor_content, win.current_file, after_save)
        except Exception as e:
            print(f"Error getting HTML content: {e}")
            # Close anyway in case of error
            self.remove_window(win)
            win.close()

    def _on_saved_close_window(self, file, result):
        """After saving, close the window"""
        try:
            success, _ = file.replace_contents_finish(result)
            # Find the window with this file
            for win in self.windows:
                if win.current_file and win.current_file.equal(file):
                    self.remove_window(win)
                    win.close()
                    break
        except Exception as e:
            print(f"Error saving before close: {e}")

    def _on_save_response_before_close(self, win, dialog, result):
        """Handle save dialog response before closing"""
        try:
            file = dialog.save_finish(result)
            if file:
                win.current_file = file
                win.webview.evaluate_javascript(
                    "document.getElementById('editor').innerHTML;",
                    -1, None, None, None,
                    lambda webview, result, data: self._on_save_before_close(win, webview, result, data),
                    None
                )
            else:
                # User cancelled save dialog, keep window open
                pass
        except GLib.Error as error:
            if error.domain != 'gtk-dialog-error-quark' or error.code != 2:  # Ignore cancel
                print(f"Error saving file: {error.message}")
            # Keep window open

    def show_save_confirmation_dialog(self, win, callback):
        """Show dialog asking if user wants to save changes before closing"""
        dialog = Adw.Dialog.new()
        dialog.set_title("Unsaved Changes")
        dialog.set_content_width(400)
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        
        # Warning icon
        warning_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
        warning_icon.set_pixel_size(48)
        warning_icon.set_margin_bottom(12)
        content_box.append(warning_icon)
        
        # Message
        document_name = "Untitled"
        if win.current_file:
            path = win.current_file.get_path() if hasattr(win.current_file, 'get_path') else win.current_file
            document_name = os.path.splitext(os.path.basename(path))[0]
            
        message_label = Gtk.Label()
        message_label.set_markup(f"<b>Save changes to \"{document_name}\" before closing?</b>")
        message_label.set_wrap(True)
        message_label.set_max_width_chars(40)
        content_box.append(message_label)
        
        description_label = Gtk.Label(label="If you don't save, your changes will be lost.")
        description_label.set_wrap(True)
        description_label.set_max_width_chars(40)
        content_box.append(description_label)
        
        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(12)
        
        # Discard button
        discard_button = Gtk.Button(label="Discard")
        discard_button.add_css_class("destructive-action")
        discard_button.connect("clicked", lambda btn: [dialog.close(), callback("discard")])
        button_box.append(discard_button)
        
        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda btn: [dialog.close(), callback("cancel")])
        button_box.append(cancel_button)
        
        # Save button
        save_button = Gtk.Button(label="Save")
        save_button.add_css_class("suggested-action")
        save_button.connect("clicked", lambda btn: [dialog.close(), callback("save")])
        button_box.append(save_button)
        
        content_box.append(button_box)
        
        # Present the dialog
        dialog.set_child(content_box)
        dialog.present(win)

    def create_actions(self):
        """Set up application actions"""
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit)
        self.add_action(quit_action)
        
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about)
        self.add_action(about_action)
        
        preferences_action = Gio.SimpleAction.new("preferences", None)
        preferences_action.connect("activate", self.on_preferences)
        self.add_action(preferences_action)
        
        # New window action
        new_window_action = Gio.SimpleAction.new("new-window", None)
        new_window_action.connect("activate", self.on_new_window)
        self.add_action(new_window_action)

        open_action = Gio.SimpleAction.new("open", None)
        open_action.connect("activate", self.on_open_action)
        self.add_action(open_action)
        
        save_action = Gio.SimpleAction.new("save", None)
        save_action.connect("activate", self.on_save_action)
        self.add_action(save_action)
        
        save_as_action = Gio.SimpleAction.new("save-as", None)
        save_as_action.connect("activate", self.on_save_as_action)
        self.add_action(save_as_action)
        
        # View actions
        toggle_file_toolbar_action = Gio.SimpleAction.new("toggle-file-toolbar", None)
        toggle_file_toolbar_action.connect("activate", self.on_toggle_file_toolbar_action)
        self.add_action(toggle_file_toolbar_action)
        
        toggle_format_toolbar_action = Gio.SimpleAction.new("toggle-format-toolbar", None)
        toggle_format_toolbar_action.connect("activate", self.on_toggle_format_toolbar_action)
        self.add_action(toggle_format_toolbar_action)
        
        toggle_statusbar_action = Gio.SimpleAction.new("toggle-statusbar", None)
        toggle_statusbar_action.connect("activate", self.on_toggle_statusbar_action)
        self.add_action(toggle_statusbar_action)
                
        # Close other windows action
        close_other_windows_action = Gio.SimpleAction.new("close-other-windows", None)
        close_other_windows_action.connect("activate", self.on_close_other_windows)
        self.add_action(close_other_windows_action)

        # Window switching action
        switch_window_action = Gio.SimpleAction.new(
            "switch-window", 
            GLib.VariantType.new("i")
        )
        switch_window_action.connect("activate", self.on_switch_window)
        self.add_action(switch_window_action)

    def create_window_menu(self):
        """Create a fresh window menu"""
        menu = Gio.Menu()
        actions_section = Gio.Menu()
        window_section = Gio.Menu()
        
        # Add "Close Other Windows" option at the top if there's more than one window
        if len(self.windows) > 1:
            actions_section.append("Close Other Windows", "app.close-other-windows")
            menu.append_section("Actions", actions_section)
        
        # Add all windows to the menu
        for i, win in enumerate(self.windows):
            title = self.get_menu_title(win)
            action_string = f"app.switch-window({i})"
            window_section.append(title, action_string)
        
        menu.append_section("Windows", window_section)
        return menu

    def update_window_menu(self):
        """Force update all window menu buttons"""
        fresh_menu = self.create_window_menu()
        
        # Should we show the window menu button?
        show_button = len(self.windows) > 1
        
        # Create a set of windows that still need a button
        windows_needing_buttons = set(self.windows)
        
        # First, update existing buttons
        buttons_to_remove = []
        for window_id, button in self.window_buttons.items():
            # Check if the window still exists
            window_exists = False
            for win in self.windows:
                if id(win) == window_id:
                    window_exists = True
                    windows_needing_buttons.remove(win)
                    break
            
            if window_exists:
                # Update existing button with fresh menu and visibility
                button.set_menu_model(fresh_menu)
                button.set_visible(show_button)
            else:
                # Window no longer exists, mark button for removal
                buttons_to_remove.append(window_id)
        
        # Remove buttons for closed windows
        for window_id in buttons_to_remove:
            del self.window_buttons[window_id]
        
        # Add buttons for new windows
        for win in windows_needing_buttons:
            self.add_window_menu_button(win, fresh_menu)
    
    def add_window_menu_button(self, win, menu_model=None):
        """Add a window menu button to a window or update an existing one"""
        # Look for existing window menu button
        window_button = None
        child = win.headerbar.get_first_child()
        while child:
            if (isinstance(child, Gtk.MenuButton) and 
                child.get_icon_name() == "multi-window-symbolic"):
                window_button = child
                break
            child = child.get_next_sibling()
        
        # Create a new menu model if not provided
        if menu_model is None:
            menu_model = self.create_window_menu()
        
        # Only show the window menu button if there's more than one window
        show_button = len(self.windows) > 1
        
        if window_button:
            # Update existing button's menu and visibility
            window_button.set_menu_model(menu_model)
            window_button.set_visible(show_button)
        elif show_button:
            # Only create a new button if we need to show it
            window_button = Gtk.MenuButton()
            window_button.set_icon_name("multi-window-symbolic")
            window_button.set_tooltip_text("Window List")
            window_button.set_menu_model(menu_model)
            window_button.set_visible(show_button)
            window_button.add_css_class("flat")
            win.headerbar.pack_end(window_button)
            
            # Store reference to the button
            self.window_buttons[id(win)] = window_button
        
        # Make sure we keep the reference if button exists
        if window_button:
            self.window_buttons[id(win)] = window_button
            
    def on_switch_window(self, action, param):
        """Handle window switching action"""
        index = param.get_int32()
        if 0 <= index < len(self.windows):
            self.windows[index].present()
            
    def on_new_window(self, action, param):
        """Create a new empty window"""
        win = self.create_window()
        win.present()
        # Update all window menus
        self.update_window_menu()

    def on_close_other_windows(self, action, param):
        """Close all windows except the active one with confirmation"""
        if len(self.windows) <= 1:
            return
            
        # Find the active window (the one that was most recently focused)
        active_window = None
        for win in self.windows:
            if win.is_active():
                active_window = win
                break
                
        # If no active window found, use the first one
        if not active_window and self.windows:
            active_window = self.windows[0]
            
        if not active_window:
            return
            
        # The number of windows that will be closed
        windows_to_close_count = len(self.windows) - 1
        
        # Create confirmation dialog using non-deprecated methods
        dialog = Adw.Dialog.new()
        dialog.set_title(f"Close {windows_to_close_count} Other Window{'s' if windows_to_close_count > 1 else ''}?")
        dialog.set_content_width(350)
        
        # Create dialog content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        
        # Message label
        message_label = Gtk.Label()
        message_label.set_text(f"Are you sure you want to close {windows_to_close_count} other window{'s' if windows_to_close_count > 1 else ''}?")
        message_label.set_wrap(True)
        message_label.set_max_width_chars(40)
        content_box.append(message_label)
        
        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(12)
        
        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda btn: dialog.close())
        button_box.append(cancel_button)
        
        # Close button (destructive)
        close_button = Gtk.Button(label="Close Windows")
        close_button.add_css_class("destructive-action")
        close_button.connect("clicked", lambda btn: self._on_close_others_response(dialog, active_window))
        button_box.append(close_button)
        
        content_box.append(button_box)
        
        # Set the dialog content and present
        dialog.set_child(content_box)
        dialog.present(active_window)

    def _on_close_others_response(self, dialog, active_window):
        """Handle the close action from the dialog"""
        # Close dialog
        dialog.close()
        
        # Get windows to close (all except active_window)
        windows_to_close = [win for win in self.windows if win != active_window]
        
        # Close each window
        for win in windows_to_close[:]:  # Use a copy of the list since we'll modify it
            win.close()
            
        # Make sure active window is still presented
        if active_window in self.windows:
            active_window.present()
            
        # Update window menu
        self.update_window_menu()

    def remove_window(self, window):
        """Properly remove a window and update menus"""
        if window in self.windows:
            # Remove window from list
            self.windows.remove(window)
            # Clean up button reference
            if id(window) in self.window_buttons:
                del self.window_buttons[id(window)]
            # Update menus in all remaining windows
            self.update_window_menu()
            
            # Focus the next window if available
            if self.windows:
                self.windows[0].present()


    def on_open_action(self, action, param):
        """Handle open action"""
        # Get the active window
        active_win = self.get_active_window()
        if active_win:
            self.on_open_clicked(active_win, None)

    def on_save_action(self, action, param):
        """Handle save action"""
        active_win = self.get_active_window()
        if active_win:
            self.on_save_clicked(active_win, None)

    def on_save_as_action(self, action, param):
        """Handle save as action"""
        active_win = self.get_active_window()
        if active_win:
            self.on_save_as_clicked(active_win, None)

    def on_toggle_file_toolbar_action(self, action, param):
        """Handle toggle file toolbar action"""
        active_win = self.get_active_window()
        if active_win:
            self.toggle_file_toolbar(active_win)

    def on_toggle_format_toolbar_action(self, action, param):
        """Handle toggle format toolbar action"""
        active_win = self.get_active_window()
        if active_win:
            self.toggle_format_toolbar(active_win)

    def on_toggle_statusbar_action(self, action, param):
        """Handle toggle statusbar action"""
        active_win = self.get_active_window()
        if active_win:
            self.toggle_statusbar(active_win)
    
    # On Quit
    def on_quit(self, action, param):
        """Quit the application with save confirmation if needed"""
        # Check if any window has unsaved changes
        windows_with_changes = [win for win in self.windows if win.modified]
        
        if windows_with_changes:
            # Prioritize the active window if it has unsaved changes
            active_window = None
            for win in self.windows:
                if win.is_active() and win.modified:
                    active_window = win
                    break
                    
            # If no active window with changes, use the first window with changes
            if not active_window and windows_with_changes:
                active_window = windows_with_changes[0]
            
            # Move the active window to the front of the list
            if active_window in windows_with_changes:
                windows_with_changes.remove(active_window)
                windows_with_changes.insert(0, active_window)
            
            # Start handling windows one by one
            self._handle_quit_with_unsaved_changes(windows_with_changes)
        else:
            # No unsaved changes, quit directly
            self.quit()

    def _handle_quit_with_unsaved_changes(self, windows_with_changes):
        """Handle unsaved changes during quit, one window at a time"""
        if not windows_with_changes:
            # All windows handled, check if we should quit
            if not self.windows:
                self.quit()
            return
            
        win = windows_with_changes[0]
        # Make sure the window is presented to the user
        win.present()
        # Show the confirmation dialog
        self.show_save_confirmation_dialog(win, lambda response: self._handle_quit_confirmation(
            response, windows_with_changes, win))

    def _handle_quit_confirmation(self, response, windows_with_changes, win):
        """Handle the response from the save confirmation dialog during quit"""
        if response == "save":
            # Save and then close this window
            if win.current_file:
                # We have a file path, save directly
                win.webview.evaluate_javascript(
                    "document.getElementById('editor').innerHTML;",
                    -1, None, None, None,
                    lambda webview, result, data: self._on_save_continue_quit(
                        win, webview, result, windows_with_changes),
                    None
                )
            else:
                # No file path, show save dialog
                dialog = Gtk.FileDialog()
                dialog.set_title("Save Before Quitting")
                
                filter = Gtk.FileFilter()
                filter.set_name("HTML files")
                filter.add_pattern("*.html")
                filter.add_pattern("*.htm")
                
                filters = Gio.ListStore.new(Gtk.FileFilter)
                filters.append(filter)
                
                dialog.set_filters(filters)
                dialog.save(win, None, lambda dialog, result: self._on_save_response_during_quit(
                    win, dialog, result, windows_with_changes))
        elif response == "discard":
            # Explicitly mark as unmodified before closing
            win.modified = False
            
            # Close this window without saving and continue with the next
            self.remove_window(win)
            win.close()
            
            # Continue with remaining windows
            remaining_windows = windows_with_changes[1:]
            if remaining_windows:
                GLib.idle_add(lambda: self._handle_quit_with_unsaved_changes(remaining_windows))
            elif not self.windows:
                # If all windows are closed, quit the application
                self.quit()
        elif response == "cancel":
            # Cancel the entire quit operation
            # Continue with other windows that might be open but not modified
            pass

    def _on_save_continue_quit(self, win, webview, result, windows_with_changes):
        """Save the content, close this window, and continue with the quit process"""
        try:
            js_result = webview.evaluate_javascript_finish(result)
            if js_result:
                editor_content = (js_result.get_js_value().to_string() if hasattr(js_result, 'get_js_value') else
                               js_result.to_string() if hasattr(js_result, 'to_string') else str(js_result))
                
                # Define a callback for after saving
                def after_save(file, result):
                    try:
                        success, _ = file.replace_contents_finish(result)
                        if success:
                            win.modified = False  # Mark as unmodified
                            self.update_window_title(win)
                        
                        # Close this window
                        self.remove_window(win)
                        win.close()
                        
                        # Continue with remaining windows
                        remaining_windows = windows_with_changes[1:]
                        if remaining_windows:
                            GLib.idle_add(lambda: self._handle_quit_with_unsaved_changes(remaining_windows))
                        elif not self.windows:
                            # If all windows are closed, quit the application
                            self.quit()
                    except Exception as e:
                        print(f"Error saving during quit: {e}")
                        # Close anyway and continue
                        self.remove_window(win)
                        win.close()
                        
                        # Continue with remaining windows
                        remaining_windows = windows_with_changes[1:]
                        if remaining_windows:
                            GLib.idle_add(lambda: self._handle_quit_with_unsaved_changes(remaining_windows))
                        elif not self.windows:
                            # If all windows are closed, quit the application
                            self.quit()
                
                # Save with our callback
                self.save_html_content(win, editor_content, win.current_file, after_save)
        except Exception as e:
            print(f"Error getting HTML content during quit: {e}")
            # Close anyway and continue
            self.remove_window(win)
            win.close()
            
            # Continue with remaining windows
            remaining_windows = windows_with_changes[1:]
            if remaining_windows:
                GLib.idle_add(lambda: self._handle_quit_with_unsaved_changes(remaining_windows))
            elif not self.windows:
                # If all windows are closed, quit the application
                self.quit()

    def _on_save_response_during_quit(self, win, dialog, result, windows_with_changes):
        """Handle save dialog response during quit"""
        try:
            file = dialog.save_finish(result)
            if file:
                win.current_file = file
                win.webview.evaluate_javascript(
                    "document.getElementById('editor').innerHTML;",
                    -1, None, None, None,
                    lambda webview, result, data: self._on_save_continue_quit(
                        win, webview, result, windows_with_changes),
                    None
                )
            else:
                # User cancelled save dialog, cancel quit for this window
                # but continue with other windows that might need attention
                remaining_windows = windows_with_changes[1:]
                if remaining_windows:
                    GLib.idle_add(lambda: self._handle_quit_with_unsaved_changes(remaining_windows))
        except GLib.Error as error:
            if error.domain != 'gtk-dialog-error-quark' or error.code != 2:  # Ignore cancel
                print(f"Error saving file during quit: {error.message}")
            # Continue with other windows
            remaining_windows = windows_with_changes[1:]
            if remaining_windows:
                GLib.idle_add(lambda: self._handle_quit_with_unsaved_changes(remaining_windows))
    
    def on_about(self, action, param):
        """Show about dialog"""
        parent_window = self.windows[0] if self.windows else None
        about = Adw.AboutWindow(
            transient_for=parent_window,
            application_name="Webkit Word",
            application_icon="io.github.fastrizwaan.WebkitWord",
            version=f"{self.version}",
            copyright="GNU General Public License (GPLv3+)",
            comments="rich text editor using webkit",
            website="https://github.com/fastrizwaan/webkitword",
            developer_name="Mohammed Asif Ali Rizvan",
            license_type=Gtk.License.GPL_3_0,
            issue_url="https://github.com/fastrizwaan/webkitword/issues"
        )
        about.present()
        parent_window.webview.grab_focus()

            
    def on_preferences(self, action, param):
        """Show preferences dialog with enhanced UI visibility options"""
        if not self.windows:
            return
                
        # Find the active window instead of just using the first window
        active_win = None
        for win in self.windows:
            if win.is_active():
                active_win = win
                break
        
        # If no active window found, use the first one as fallback
        if not active_win:
            active_win = self.windows[0]
                
        # Create dialog
        dialog = Adw.Dialog.new()
        dialog.set_title("Preferences")
        dialog.set_content_width(450)
        
        # Create content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        
        # Show/Hide UI elements section
        ui_header = Gtk.Label()
        ui_header.set_markup("<b>User Interface</b>")
        ui_header.set_halign(Gtk.Align.START)
        ui_header.set_margin_bottom(12)
        ui_header.set_margin_top(24)
        content_box.append(ui_header)
        
        # Show Headerbar option
        headerbar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        headerbar_box.set_margin_start(12)
        headerbar_box.set_margin_top(12)
        
        headerbar_label = Gtk.Label(label="Show Headerbar:")
        headerbar_label.set_halign(Gtk.Align.START)
        headerbar_label.set_hexpand(True)
        
        headerbar_switch = Gtk.Switch()
        headerbar_switch.set_active(active_win.headerbar_revealer.get_reveal_child())
        headerbar_switch.set_valign(Gtk.Align.CENTER)
        headerbar_switch.connect("state-set", lambda sw, state: active_win.headerbar_revealer.set_reveal_child(state))
        
        headerbar_box.append(headerbar_label)
        headerbar_box.append(headerbar_switch)
        content_box.append(headerbar_box)
        
        # Show File Toolbar option
        file_toolbar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        file_toolbar_box.set_margin_start(12)
        file_toolbar_box.set_margin_top(12)
        
        file_toolbar_label = Gtk.Label(label="Show File Toolbar:")
        file_toolbar_label.set_halign(Gtk.Align.START)
        file_toolbar_label.set_hexpand(True)
        
        file_toolbar_switch = Gtk.Switch()
        file_toolbar_switch.set_active(active_win.file_toolbar_revealer.get_reveal_child())
        file_toolbar_switch.set_valign(Gtk.Align.CENTER)
        file_toolbar_switch.connect("state-set", lambda sw, state: active_win.file_toolbar_revealer.set_reveal_child(state))
        
        file_toolbar_box.append(file_toolbar_label)
        file_toolbar_box.append(file_toolbar_switch)
        content_box.append(file_toolbar_box)
        
        # Show Format Toolbar option
        format_toolbar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        format_toolbar_box.set_margin_start(12)
        format_toolbar_box.set_margin_top(12)
        
        format_toolbar_label = Gtk.Label(label="Show Format Toolbar:")
        format_toolbar_label.set_halign(Gtk.Align.START)
        format_toolbar_label.set_hexpand(True)
        
        format_toolbar_switch = Gtk.Switch()
        format_toolbar_switch.set_active(active_win.toolbar_revealer.get_reveal_child())
        format_toolbar_switch.set_valign(Gtk.Align.CENTER)
        format_toolbar_switch.connect("state-set", lambda sw, state: active_win.toolbar_revealer.set_reveal_child(state))
        
        format_toolbar_box.append(format_toolbar_label)
        format_toolbar_box.append(format_toolbar_switch)
        content_box.append(format_toolbar_box)
        
        # Show Statusbar option
        statusbar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        statusbar_box.set_margin_start(12)
        statusbar_box.set_margin_top(12)
        
        statusbar_label = Gtk.Label(label="Show Statusbar:")
        statusbar_label.set_halign(Gtk.Align.START)
        statusbar_label.set_hexpand(True)
        
        statusbar_switch = Gtk.Switch()
        statusbar_switch.set_active(active_win.statusbar_revealer.get_reveal_child())
        statusbar_switch.set_valign(Gtk.Align.CENTER)
        statusbar_switch.connect("state-set", lambda sw, state: active_win.statusbar_revealer.set_reveal_child(state))
        
        statusbar_box.append(statusbar_label)
        statusbar_box.append(statusbar_switch)
        content_box.append(statusbar_box)
        
        # Auto-save section
        auto_save_section = Gtk.Label()
        auto_save_section.set_markup("<b>Auto Save</b>")
        auto_save_section.set_halign(Gtk.Align.START)
        auto_save_section.set_margin_bottom(12)
        auto_save_section.set_margin_top(24)
        content_box.append(auto_save_section)
        
        auto_save_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        auto_save_box.set_margin_start(12)
        
        auto_save_label = Gtk.Label(label="Auto Save:")
        auto_save_label.set_halign(Gtk.Align.START)
        auto_save_label.set_hexpand(True)
        
        auto_save_switch = Gtk.Switch()
        auto_save_switch.set_active(active_win.auto_save_enabled)
        auto_save_switch.set_valign(Gtk.Align.CENTER)
        
        auto_save_box.append(auto_save_label)
        auto_save_box.append(auto_save_switch)
        content_box.append(auto_save_box)
        
        # Interval settings
        interval_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        interval_box.set_margin_start(12)
        interval_box.set_margin_top(12)
        
        interval_label = Gtk.Label(label="Auto-save Interval (seconds):")
        interval_label.set_halign(Gtk.Align.START)
        interval_label.set_hexpand(True)
        
        adjustment = Gtk.Adjustment(
            value=active_win.auto_save_interval,
            lower=10,
            upper=600,
            step_increment=10
        )
        
        spinner = Gtk.SpinButton()
        spinner.set_adjustment(adjustment)
        spinner.set_valign(Gtk.Align.CENTER)
        
        interval_box.append(interval_label)
        interval_box.append(spinner)
        content_box.append(interval_box)
        
        # Dialog buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(24)
        
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda btn: dialog.close())
        button_box.append(cancel_button)
        
        ok_button = Gtk.Button(label="OK")
        ok_button.add_css_class("suggested-action")
        ok_button.connect("clicked", lambda btn: self.save_preferences(
            dialog, active_win, auto_save_switch.get_active(), spinner.get_value_as_int()
        ))
        button_box.append(ok_button)
        
        content_box.append(button_box)
        
        # Important: Store a reference to the dialog in the window
        active_win.preferences_dialog = dialog
        
        # Connect to the closed signal to clean up the reference
        dialog.connect("closed", lambda d: self.on_preferences_dialog_closed(active_win))
        
        # Set dialog content and show
        dialog.set_child(content_box)
        dialog.present(active_win)
        
    def on_preferences_dialog_closed(self, win):
        """Handle preferences dialog closed event"""
        # Remove the reference to allow proper cleanup
        if hasattr(win, 'preferences_dialog'):
            win.preferences_dialog = None
        win.webview.grab_focus()
        
    def save_preferences(self, dialog, win, auto_save_enabled, auto_save_interval):
        """Save preferences settings"""
        previous_auto_save = win.auto_save_enabled
        
        win.auto_save_enabled = auto_save_enabled
        win.auto_save_interval = auto_save_interval
        
        # Update auto-save timer if needed
        if auto_save_enabled != previous_auto_save:
            if auto_save_enabled:
                self.start_auto_save_timer(win)
                win.statusbar.set_text("Auto-save enabled")
            else:
                self.stop_auto_save_timer(win)
                win.statusbar.set_text("Auto-save disabled")
        elif auto_save_enabled:
            # Restart timer with new interval
            self.stop_auto_save_timer(win)
            self.start_auto_save_timer(win)
            win.statusbar.set_text(f"Auto-save interval set to {auto_save_interval} seconds")
        
        dialog.close()

    def start_auto_save_timer(self, win):
        """Start auto-save timer for a window"""
        if win.auto_save_source_id:
            GLib.source_remove(win.auto_save_source_id)
            
        # Set up auto-save timer
        win.auto_save_source_id = GLib.timeout_add_seconds(
            win.auto_save_interval,
            lambda: self.auto_save(win)
        )

    def stop_auto_save_timer(self, win):
        """Stop auto-save timer for a window"""
        if win.auto_save_source_id:
            GLib.source_remove(win.auto_save_source_id)
            win.auto_save_source_id = None

    def auto_save(self, win):
        """Perform auto-save if needed"""
        if win.modified and win.current_file:
            win.statusbar.set_text("Auto-saving...")
            win.webview.evaluate_javascript(
                "document.getElementById('editor').innerHTML;",
                -1, None, None, None,
                lambda webview, result, file: self._on_get_html_content_auto_save(win, webview, result, win.current_file),
                None
            )
        return win.auto_save_enabled  # Continue timer if enabled

    def _on_get_html_content_auto_save(self, win, webview, result, file):
        """Handle auto-save content retrieval"""
        try:
            js_result = webview.evaluate_javascript_finish(result)
            if js_result:
                editor_content = (js_result.get_js_value().to_string() if hasattr(js_result, 'get_js_value') else
                                js_result.to_string() if hasattr(js_result, 'to_string') else str(js_result))
                
                self.save_html_content(win, editor_content, file, 
                                      lambda file, result: self._on_auto_save_completed(win, file, result))
        except Exception as e:
            print(f"Error getting HTML content for auto-save: {e}")
            win.statusbar.set_text(f"Auto-save failed: {e}")

    def _on_auto_save_completed(self, win, file, result):
        """Handle auto-save completion"""
        try:
            success, _ = file.replace_contents_finish(result)
            if success:
                win.modified = False  # Reset modified flag after save
                self.update_window_title(win)
                win.statusbar.set_text(f"Auto-saved at {GLib.DateTime.new_now_local().format('%H:%M:%S')}")
            else:
                win.statusbar.set_text("Auto-save failed")
        except GLib.Error as error:
            print(f"Error during auto-save: {error.message}")
            win.statusbar.set_text(f"Auto-save failed: {error.message}")

    def show_error_dialog(self, win, message):
        """Show error message dialog"""
        dialog = Adw.Dialog.new()
        dialog.set_title("Error")
        dialog.set_content_width(350)
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        
        error_icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
        error_icon.set_pixel_size(48)
        error_icon.set_margin_bottom(12)
        content_box.append(error_icon)
        
        message_label = Gtk.Label(label=message)
        message_label.set_wrap(True)
        message_label.set_max_width_chars(40)
        content_box.append(message_label)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(12)
        
        ok_button = Gtk.Button(label="OK")
        ok_button.add_css_class("suggested-action")
        ok_button.connect("clicked", lambda btn: dialog.close())
        button_box.append(ok_button)
        
        content_box.append(button_box)
        
        dialog.set_child(content_box)
        dialog.present(win)

    # Show Caret in the window (for new and fresh start)
    def set_initial_focus(self, win):
        """Set focus to the WebView and its editor element after window is shown"""
        try:
            # First grab focus on the WebView widget itself
            win.webview.grab_focus()
            
            # Then focus the editor element inside the WebView
            js_code = """
            (function() {
                const editor = document.getElementById('editor');
                if (!editor) return false;
                
                editor.focus();
                
                // Set cursor position
                try {
                    const range = document.createRange();
                    const sel = window.getSelection();
                    
                    // Find or create a text node to place cursor
                    let textNode = null;
                    let firstDiv = editor.querySelector('div');
                    
                    if (!firstDiv) {
                        editor.innerHTML = '<div><br></div>';
                        firstDiv = editor.querySelector('div');
                    }
                    
                    if (firstDiv) {
                        range.setStart(firstDiv, 0);
                        range.collapse(true);
                        sel.removeAllRanges();
                        sel.addRange(range);
                    }
                } catch (e) {
                    console.log("Error setting cursor position:", e);
                }
                
                return true;
            })();
            """
            
            win.webview.evaluate_javascript(js_code, -1, None, None, None, None, None)
            return False  # Don't call again
        except Exception as e:
            print(f"Error setting initial focus: {e}")
            return False  # Don't call again

    def on_print_clicked(self, win, btn):
        """Handle print button click using WebKit's print operation"""
        win.statusbar.set_text("Preparing to print...")
        
        # Create a print operation with WebKit
        print_op = WebKit.PrintOperation.new(win.webview)
        
        # Apply page setup (window-specific or default)
        if hasattr(win, 'page_setup'):
            print_op.set_page_setup(win.page_setup)
        else:
            print_op.set_page_setup(self.default_page_setup)
        
        # Run the print dialog
        print_op.run_dialog(win)
        win.webview.grab_focus()
######################


#### Zoom statusbar
    def on_zoom_changed_statusbar(self, win, scale):
        """Handle zoom scale change with snapping to common values"""
        # Get the current value from the scale
        raw_value = scale.get_value()
        
        # Define common zoom levels to snap to
        common_zoom_levels = [50, 75, 100, 125, 150, 175, 200, 250, 300, 350, 400]
        
        # Find the closest common zoom level
        closest_zoom = min(common_zoom_levels, key=lambda x: abs(x - raw_value))
        
        # Check if we're close enough to snap
        snap_threshold = 5  # Snap if within 5% of a common value
        if abs(raw_value - closest_zoom) <= snap_threshold:
            # We're close to a common value, snap to it
            if raw_value != closest_zoom:  # Only set if different to avoid infinite recursion
                scale.set_value(closest_zoom)
            zoom_level = closest_zoom
        else:
            # Not close to a common value, use the rounded value
            zoom_level = int(raw_value)
        
        # Update the label and apply zoom
        win.zoom_label.set_text(f"{zoom_level}%")
        win.zoom_level = zoom_level
        
        # Apply zoom to the editor
        self.apply_zoom(win, zoom_level)
        win.webview.grab_focus()
        
    # Add these new methods for zoom control in the statusbar
    def on_zoom_toggle_clicked(self, win, button):
        """Handle zoom toggle button click"""
        is_active = button.get_active()
        win.zoom_revealer.set_reveal_child(is_active)
        
        # Update status text
        if is_active:
            win.statusbar.set_text("Zoom")
        else:
            # Restore previous status message or show 'Ready'
            win.statusbar.set_text("Ready")

    def on_zoom_in_clicked(self, win):
        """Handle zoom in button click"""
        current_value = win.zoom_scale.get_value()
        new_value = min(current_value + 10, 400)  # Increase by 10%, max 400%
        win.zoom_scale.set_value(new_value)

    def on_zoom_out_clicked(self, win):
        """Handle zoom out button click"""
        current_value = win.zoom_scale.get_value()
        new_value = max(current_value - 10, 50)  # Decrease by 10%, min 50%
        win.zoom_scale.set_value(new_value)

########################### line spacing and column
    def setup_spacing_actions(self, win):
        """Setup actions for paragraph and line spacing"""
        # Line spacing actions
        line_spacing_action = Gio.SimpleAction.new("line-spacing", GLib.VariantType.new("s"))
        line_spacing_action.connect("activate", lambda action, param: self.apply_quick_line_spacing(win, float(param.get_string())))
        win.add_action(line_spacing_action)
        
        line_spacing_dialog_action = Gio.SimpleAction.new("line-spacing-dialog", None)
        line_spacing_dialog_action.connect("activate", lambda action, param: self.on_line_spacing_clicked(win, action, param))
        win.add_action(line_spacing_dialog_action)
        
        # Paragraph spacing actions
        para_spacing_action = Gio.SimpleAction.new("paragraph-spacing", GLib.VariantType.new("s"))
        para_spacing_action.connect("activate", lambda action, param: self.apply_quick_paragraph_spacing(win, int(param.get_string())))
        win.add_action(para_spacing_action)
        
        para_spacing_dialog_action = Gio.SimpleAction.new("paragraph-spacing-dialog", None)
        para_spacing_dialog_action.connect("activate", lambda action, param: self.on_paragraph_spacing_clicked(win, action, param))
        win.add_action(para_spacing_dialog_action)
        
        # Column layout actions
        column_action = Gio.SimpleAction.new("set-columns", GLib.VariantType.new("s"))
        column_action.connect("activate", lambda action, param: self.apply_column_layout(win, int(param.get_string())))
        win.add_action(column_action)   

    def on_paragraph_spacing_clicked(self, win, action, param):
        """Show dialog to adjust paragraph spacing for individual or all paragraphs"""
        dialog = Adw.Dialog()
        dialog.set_title("Paragraph Spacing")
        
        # Create main content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        
        # Create spacing selection
        header = Gtk.Label()
        header.set_markup("<b>Paragraph Spacing Options:</b>")
        header.set_halign(Gtk.Align.START)
        content_box.append(header)
        
        # Radio buttons for scope selection
        scope_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scope_box.set_margin_top(12)
        scope_box.set_margin_bottom(12)
        
        scope_label = Gtk.Label(label="Apply to:")
        scope_label.set_halign(Gtk.Align.START)
        scope_box.append(scope_label)
        
        # Create radio buttons
        current_radio = Gtk.CheckButton(label="Current paragraph only")
        current_radio.set_active(True)
        scope_box.append(current_radio)
        
        all_radio = Gtk.CheckButton(label="All paragraphs")
        all_radio.set_group(current_radio)
        scope_box.append(all_radio)
        
        content_box.append(scope_box)
        
        # Spacing slider
        spacing_label = Gtk.Label(label="Spacing value:")
        spacing_label.set_halign(Gtk.Align.START)
        content_box.append(spacing_label)
        
        adjustment = Gtk.Adjustment.new(10, 0, 50, 1, 5, 0)
        spacing_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment)
        spacing_scale.set_hexpand(True)
        spacing_scale.set_digits(0)
        spacing_scale.set_draw_value(True)
        spacing_scale.add_mark(0, Gtk.PositionType.BOTTOM, "None")
        spacing_scale.add_mark(10, Gtk.PositionType.BOTTOM, "Default")
        spacing_scale.add_mark(30, Gtk.PositionType.BOTTOM, "Wide")
        content_box.append(spacing_scale)
        
        # Preset buttons
        presets_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        presets_box.set_homogeneous(True)
        presets_box.set_margin_top(12)
        
        none_button = Gtk.Button(label="None")
        none_button.connect("clicked", lambda btn: spacing_scale.set_value(0))
        presets_box.append(none_button)
        
        small_button = Gtk.Button(label="Small")
        small_button.connect("clicked", lambda btn: spacing_scale.set_value(5))
        presets_box.append(small_button)
        
        medium_button = Gtk.Button(label="Medium") 
        medium_button.connect("clicked", lambda btn: spacing_scale.set_value(15))
        presets_box.append(medium_button)
        
        large_button = Gtk.Button(label="Large")
        large_button.connect("clicked", lambda btn: spacing_scale.set_value(30))
        presets_box.append(large_button)
        
        content_box.append(presets_box)
        
        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(24)
        
        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda btn: dialog.close())
        button_box.append(cancel_button)
        
        # Apply button
        apply_button = Gtk.Button(label="Apply")
        apply_button.add_css_class("suggested-action")
        apply_button.connect("clicked", lambda btn: self.apply_paragraph_spacing(
            win, dialog, spacing_scale.get_value(), current_radio.get_active()))
        button_box.append(apply_button)
        
        content_box.append(button_box)
        
        # Set up the dialog content
        dialog.set_child(content_box)
        
        # Present the dialog
        dialog.present(win)

    def apply_paragraph_spacing(self, win, dialog, spacing, current_only):
        """Apply paragraph spacing to the current paragraph or all paragraphs"""
        if current_only:
            # Apply spacing to just the selected paragraphs
            js_code = f"""
            (function() {{
                return setParagraphSpacing({int(spacing)});
            }})();
            """
            self.execute_js(win, js_code)
        else:
            # Apply spacing to all paragraphs
            js_code = f"""
            (function() {{
                // First ensure all direct text content is wrapped
                wrapUnwrappedText(document.getElementById('editor'));
                
                // Target both p tags and div tags as paragraphs
                let paragraphs = document.getElementById('editor').querySelectorAll('p, div');
                
                // Apply to all paragraphs
                for (let i = 0; i < paragraphs.length; i++) {{
                    paragraphs[i].style.marginBottom = '{int(spacing)}px';
                }}
                
                return true;
            }})();
            """
            self.execute_js(win, js_code)
        
        win.statusbar.set_text(f"Paragraph spacing set to {int(spacing)}px")
        dialog.close()

    def apply_quick_paragraph_spacing(self, win, spacing):
        """Apply spacing to the selected paragraphs through menu action"""
        js_code = f"""
        (function() {{
            return setParagraphSpacing({spacing});
        }})();
        """
        self.execute_js(win, js_code)
        win.statusbar.set_text(f"Paragraph spacing set to {spacing}px")

    def on_line_spacing_clicked(self, win, action, param):
        """Show dialog to adjust line spacing for individual or all paragraphs"""
        dialog = Adw.Dialog()
        dialog.set_title("Line Spacing")
        
        # Create main content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        
        # Create spacing selection
        header = Gtk.Label()
        header.set_markup("<b>Line Spacing Options:</b>")
        header.set_halign(Gtk.Align.START)
        content_box.append(header)
        
        # Radio buttons for scope selection
        scope_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scope_box.set_margin_top(12)
        scope_box.set_margin_bottom(12)
        
        scope_label = Gtk.Label(label="Apply to:")
        scope_label.set_halign(Gtk.Align.START)
        scope_box.append(scope_label)
        
        # Create radio buttons
        current_radio = Gtk.CheckButton(label="Current paragraph only")
        current_radio.set_active(True)
        scope_box.append(current_radio)
        
        all_radio = Gtk.CheckButton(label="All paragraphs")
        all_radio.set_group(current_radio)
        scope_box.append(all_radio)
        
        content_box.append(scope_box)
        
        # Preset buttons
        presets_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        presets_label = Gtk.Label(label="Common spacing:")
        presets_label.set_halign(Gtk.Align.START)
        presets_box.append(presets_label)
        
        # First row of buttons
        buttons_box1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        buttons_box1.set_homogeneous(True)
        
        single_button = Gtk.Button(label="Single (1.0)")
        single_button.connect("clicked", lambda btn: self.apply_line_spacing(
            win, dialog, 1.0, current_radio.get_active()))
        buttons_box1.append(single_button)
        
        default_button = Gtk.Button(label="Default (1.15)")
        default_button.connect("clicked", lambda btn: self.apply_line_spacing(
            win, dialog, 1.15, current_radio.get_active()))
        buttons_box1.append(default_button)
        
        presets_box.append(buttons_box1)
        
        # Second row of buttons
        buttons_box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        buttons_box2.set_homogeneous(True)
        
        one_half_button = Gtk.Button(label="One and a half (1.5)")
        one_half_button.connect("clicked", lambda btn: self.apply_line_spacing(
            win, dialog, 1.5, current_radio.get_active()))
        buttons_box2.append(one_half_button)
        
        double_button = Gtk.Button(label="Double (2.0)")
        double_button.connect("clicked", lambda btn: self.apply_line_spacing(
            win, dialog, 2.0, current_radio.get_active()))
        buttons_box2.append(double_button)
        
        presets_box.append(buttons_box2)
        content_box.append(presets_box)
        
        # Custom spacing section
        custom_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        custom_box.set_margin_top(8)
        
        custom_label = Gtk.Label(label="Custom spacing:")
        custom_label.set_halign(Gtk.Align.START)
        custom_box.append(custom_label)
        
        # Add slider for custom spacing
        adjustment = Gtk.Adjustment.new(1.0, 0.8, 3.0, 0.05, 0.2, 0)
        spacing_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment)
        spacing_scale.set_hexpand(True)
        spacing_scale.set_digits(1)
        spacing_scale.set_draw_value(True)
        spacing_scale.add_mark(0.8, Gtk.PositionType.BOTTOM, "0.8")
        spacing_scale.add_mark(1.0, Gtk.PositionType.BOTTOM, "1.0")
        spacing_scale.add_mark(1.5, Gtk.PositionType.BOTTOM, "1.5")
        spacing_scale.add_mark(2.0, Gtk.PositionType.BOTTOM, "2.0")
        spacing_scale.add_mark(2.5, Gtk.PositionType.BOTTOM, "2.5")
        spacing_scale.add_mark(3.0, Gtk.PositionType.BOTTOM, "3.0")
        custom_box.append(spacing_scale)
        
        # Apply custom button
        custom_apply_button = Gtk.Button(label="Apply Custom Value")
        custom_apply_button.connect("clicked", lambda btn: self.apply_line_spacing(
            win, dialog, spacing_scale.get_value(), current_radio.get_active()))
        custom_apply_button.set_margin_top(8)
        custom_box.append(custom_apply_button)
        
        content_box.append(custom_box)
        
        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(24)
        
        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda btn: dialog.close())
        button_box.append(cancel_button)
        
        content_box.append(button_box)
        
        # Set up the dialog content
        dialog.set_child(content_box)
        
        # Present the dialog
        dialog.present(win)

    def apply_line_spacing(self, win, dialog, spacing, current_only):
        """Apply line spacing to the current paragraph or all paragraphs"""
        if current_only:
            # Apply spacing to just the selected paragraphs
            js_code = f"""
            (function() {{
                return setLineSpacing({spacing});
            }})();
            """
            self.execute_js(win, js_code)
        else:
            # Apply spacing to all paragraphs
            js_code = f"""
            (function() {{
                // First ensure all direct text content is wrapped
                wrapUnwrappedText(document.getElementById('editor'));
                
                // Target both p tags and div tags as paragraphs
                let paragraphs = document.getElementById('editor').querySelectorAll('p, div');
                
                // Apply to all paragraphs
                for (let i = 0; i < paragraphs.length; i++) {{
                    paragraphs[i].style.lineHeight = '{spacing}';
                }}
                
                return true;
            }})();
            """
            self.execute_js(win, js_code)
        
        win.statusbar.set_text(f"Line spacing set to {spacing}")
        dialog.close()
    def apply_quick_line_spacing(self, win, spacing):
        """Apply line spacing to the selected paragraphs through menu action"""
        js_code = f"""
        (function() {{
            return setLineSpacing({spacing});
        }})();
        """
        self.execute_js(win, js_code)
        win.statusbar.set_text(f"Line spacing set to {spacing}")


    def paragraph_and_line_spacing_js(self):
        """JavaScript for paragraph and line spacing functions"""
        return """
        // Function to set paragraph spacing
        function setParagraphSpacing(spacing) {
            const selection = window.getSelection();
            if (!selection.rangeCount) return false;
            
            // Strategy: Get all paragraphs in the selection range
            const range = selection.getRangeAt(0);
            const startNode = findContainerParagraph(range.startContainer);
            const endNode = findContainerParagraph(range.endContainer);
            
            // If we couldn't find containers, try a different approach
            if (!startNode || !endNode) {
                return setSimpleParagraphSpacing(spacing);
            }
            
            // Get all paragraphs in the selection range
            const paragraphs = getAllParagraphsInRange(startNode, endNode);
            
            // Apply spacing to all found paragraphs
            paragraphs.forEach(para => {
                para.style.marginBottom = spacing + 'px';
            });
            
            return true;
        }
        
        // Function to set line spacing
        function setLineSpacing(spacing) {
            const selection = window.getSelection();
            if (!selection.rangeCount) return false;
            
            // Strategy: Get all paragraphs in the selection range
            const range = selection.getRangeAt(0);
            const startNode = findContainerParagraph(range.startContainer);
            const endNode = findContainerParagraph(range.endContainer);
            
            // If we couldn't find containers, try a different approach
            if (!startNode || !endNode) {
                return setSimpleLineSpacing(spacing);
            }
            
            // Get all paragraphs in the selection range
            const paragraphs = getAllParagraphsInRange(startNode, endNode);
            
            // Apply spacing to all found paragraphs
            paragraphs.forEach(para => {
                para.style.lineHeight = spacing;
            });
            
            return true;
        }
        
        // Helper function to find the container paragraph of a node
        function findContainerParagraph(node) {
            while (node && node.id !== 'editor') {
                if (node.nodeType === 1 && 
                    (node.nodeName.toLowerCase() === 'p' || 
                     node.nodeName.toLowerCase() === 'div')) {
                    return node;
                }
                node = node.parentNode;
            }
            return null;
        }
        
        // Get all paragraphs between start and end node (inclusive)
        function getAllParagraphsInRange(startNode, endNode) {
            // If start and end are the same, just return that node
            if (startNode === endNode) {
                return [startNode];
            }
            
            // Get all paragraphs in the editor
            const allParagraphs = Array.from(document.getElementById('editor').querySelectorAll('p, div'));
            
            // Find the indices of our start and end nodes
            const startIndex = allParagraphs.indexOf(startNode);
            const endIndex = allParagraphs.indexOf(endNode);
            
            // Handle case where we can't find one of the nodes
            if (startIndex === -1 || endIndex === -1) {
                // Fall back to just the nodes we have
                return [startNode, endNode].filter(node => node !== null);
            }
            
            // Return all paragraphs between start and end (inclusive)
            return allParagraphs.slice(
                Math.min(startIndex, endIndex), 
                Math.max(startIndex, endIndex) + 1
            );
        }
        
        // Fallback method for paragraph spacing when selection is unusual
        function setSimpleParagraphSpacing(spacing) {
            const selection = window.getSelection();
            if (!selection.rangeCount) return false;
            
            let node = selection.getRangeAt(0).commonAncestorContainer;
            
            // Navigate up to find the paragraph node
            while (node && node.nodeType !== 1) {
                node = node.parentNode;
            }
            
            // Find the containing paragraph or div
            while (node && node.id !== 'editor' && 
                  (node.nodeName.toLowerCase() !== 'p' && 
                   node.nodeName.toLowerCase() !== 'div')) {
                node = node.parentNode;
            }
            
            if (node && node.id !== 'editor') {
                node.style.marginBottom = spacing + 'px';
                return true;
            }
            return false;
        }
        
        // Fallback method for line spacing when selection is unusual
        function setSimpleLineSpacing(spacing) {
            const selection = window.getSelection();
            if (!selection.rangeCount) return false;
            
            let node = selection.getRangeAt(0).commonAncestorContainer;
            
            // Navigate up to find the paragraph node
            while (node && node.nodeType !== 1) {
                node = node.parentNode;
            }
            
            // Find the containing paragraph or div
            while (node && node.id !== 'editor' && 
                  (node.nodeName.toLowerCase() !== 'p' && 
                   node.nodeName.toLowerCase() !== 'div')) {
                node = node.parentNode;
            }
            
            if (node && node.id !== 'editor') {
                node.style.lineHeight = spacing;
                return true;
            }
            return false;
        }
        
        // Function to wrap unwrapped text
        function wrapUnwrappedText(container) {
            let childNodes = Array.from(container.childNodes);
            for (let i = 0; i < childNodes.length; i++) {
                let node = childNodes[i];
                if (node.nodeType === 3 && node.nodeValue.trim() !== '') {
                    // It's a text node with content, wrap it
                    let wrapper = document.createElement('div');
                    node.parentNode.insertBefore(wrapper, node);
                    wrapper.appendChild(node);
                }
            }
        }
        // Function to apply column layout to a container
        function setColumnLayout(container, columns) {
            if (columns <= 1) {
                // Remove column styling
                container.style.columnCount = '';
                container.style.columnGap = '';
                container.style.columnRule = '';
            } else {
                // Apply column styling
                container.style.columnCount = columns;
                container.style.columnGap = '20px';
                container.style.columnRule = '1px solid #ccc';
            }
        }
        """      
        
############ column
     

    def apply_column_layout(self, win, columns):
        """Apply column layout to the selected content"""
        js_code = f"""
        (function() {{
            const selection = window.getSelection();
            if (!selection.rangeCount) return false;
            
            // Strategy similar to paragraph spacing
            const range = selection.getRangeAt(0);
            
            // First, try to get a structured element like div or p
            let container = null;
            
            // Check if selection is within a paragraph or div
            let node = range.commonAncestorContainer;
            if (node.nodeType === 3) {{ // Text node
                node = node.parentNode;
            }}
            
            // Find a suitable container or create one
            while (node && node.id !== 'editor') {{
                if (node.nodeName.toLowerCase() === 'div' || 
                    node.nodeName.toLowerCase() === 'p') {{
                    container = node;
                    break;
                }}
                node = node.parentNode;
            }}
            
            // If we didn't find a container, we'll need to create a wrapper
            if (!container || container.id === 'editor') {{
                // Create a wrapper around the selection
                document.execCommand('formatBlock', false, 'div');
                
                // Get the newly created div
                const newRange = selection.getRangeAt(0);
                node = newRange.commonAncestorContainer;
                if (node.nodeType === 3) {{
                    node = node.parentNode;
                }}
                
                // Find our new container
                while (node && node.id !== 'editor') {{
                    if (node.nodeName.toLowerCase() === 'div') {{
                        container = node;
                        break;
                    }}
                    node = node.parentNode;
                }}
            }}
            
            if (container) {{
                if ({columns} <= 1) {{
                    // Remove column styling
                    container.style.columnCount = '';
                    container.style.columnGap = '';
                    container.style.columnRule = '';
                    return true;
                }} else {{
                    // Apply column styling
                    container.style.columnCount = {columns};
                    container.style.columnGap = '20px';
                    container.style.columnRule = '1px solid #ccc';
                    return true;
                }}
            }}
            
            return false;
        }})();
        """
        self.execute_js(win, js_code)
        
        status_text = "Column layout removed" if columns <= 1 else f"Applied {columns}-column layout"
        win.statusbar.set_text(status_text)
        
############# Create Window
    def create_window(self):
        """Create a new window with separate headerbar and toolbar in ToolbarView"""
        win = Adw.ApplicationWindow(application=self)
        
        # Set window properties
        win.modified = False
        win.auto_save_enabled = False
        win.auto_save_interval = 60
        win.current_file = None
        win.auto_save_source_id = None
        
        win.set_default_size(1000, 768)
        win.set_title("Untitled - Webkit Word")
        
        # Create the modern ToolbarView container
        win.toolbar_view = Adw.ToolbarView()
        
        # Create the header bar
        win.headerbar = Adw.HeaderBar()
        win.headerbar.set_size_request(0,0)
        win.headerbar.set_margin_bottom(0)  # Ensure no bottom margin
        win.headerbar.set_margin_top(0)  # Ensure no bottom margin

        # Create a revealer for the header bar
        win.headerbar_revealer = Gtk.Revealer()
        win.headerbar_revealer.set_size_request(0,0)
        win.headerbar_revealer.set_margin_bottom(0)
        win.headerbar_revealer.set_margin_top(0)  
        win.headerbar_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        win.headerbar_revealer.set_transition_duration(250)
        win.headerbar_revealer.set_reveal_child(True)  # Visible by default
        win.headerbar_revealer.set_child(win.headerbar)

        # Set up the headerbar content
        self.setup_headerbar_content(win)
        
        # Create file toolbar revealer (new addition)
        win.file_toolbar_revealer = Gtk.Revealer()
        win.file_toolbar_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        win.file_toolbar_revealer.set_transition_duration(250)
        win.file_toolbar_revealer.set_reveal_child(False)  # Hidden by default
        win.file_toolbar_revealer.set_margin_top(0)
        win.file_toolbar_revealer.set_margin_bottom(0)
        
        # Create and set the file toolbar
        win.file_toolbar = self.create_file_toolbar(win)
        win.file_toolbar_revealer.set_child(win.file_toolbar)
        
        # Create toolbar revealer for smooth show/hide for the formatting toolbar
        win.toolbar_revealer = Gtk.Revealer()
        win.toolbar_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        win.toolbar_revealer.set_transition_duration(250)
        win.toolbar_revealer.set_reveal_child(True)  # Visible by default
        win.toolbar_revealer.set_margin_top(0)  # Ensure no top margin
        win.toolbar_revealer.set_margin_bottom(0)  # Ensure no top margin
        
        # Create WrapBox for flexible toolbar layout (for format toolbar)
        win.toolbars_wrapbox = Adw.WrapBox()
        win.toolbars_wrapbox.set_margin_start(4)
        win.toolbars_wrapbox.set_margin_end(2)
        win.toolbars_wrapbox.set_margin_top(1)
        win.toolbars_wrapbox.set_margin_bottom(2)
        win.toolbars_wrapbox.set_child_spacing(4)
        win.toolbars_wrapbox.set_line_spacing(4)
        
        # Add toolbar content (like formatting buttons, etc.)
        self.setup_toolbar_content(win)
        
        # Set toolbar WrapBox as the child of toolbar revealer
        win.toolbar_revealer.set_child(win.toolbars_wrapbox)
        
        # Set the toolbar revealers as top bars in the ToolbarView
        win.toolbar_view.add_top_bar(win.headerbar_revealer)
        win.toolbar_view.add_top_bar(win.file_toolbar_revealer)
        win.toolbar_view.add_top_bar(win.toolbar_revealer)
        
        # Create content area
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_box.set_vexpand(True)
        content_box.set_hexpand(True)
        
        # Create webview
        win.webview = WebKit.WebView()
        win.webview.set_vexpand(True)
        win.webview.set_hexpand(True) 
        win.webview.load_html(self.get_editor_html(), None)
        settings = win.webview.get_settings()
        try:
            settings.set_enable_developer_extras(True)
        except:
            pass
        
        # Set up message handlers
        self.setup_webview_message_handlers(win)
        
        # Set up key controller for shortcuts
        win.key_controller = Gtk.EventControllerKey.new()
        win.key_controller.connect("key-pressed", self.on_webview_key_pressed)
        win.webview.add_controller(win.key_controller)
        
        win.webview.load_html(self.get_initial_html(), None)
        content_box.append(win.webview)
        
        # Find bar with revealer
        win.find_bar = self.create_find_bar(win)
        content_box.append(win.find_bar)
        
        # Create table toolbar with revealer (hidden by default)
        win.table_toolbar_revealer = Gtk.Revealer()
        win.table_toolbar_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        win.table_toolbar_revealer.set_transition_duration(250)
        win.table_toolbar_revealer.set_reveal_child(False)  # Hidden by default
        
        # Create and add table toolbar
        win.table_toolbar = self.create_table_toolbar(win)
        win.table_toolbar_revealer.set_child(win.table_toolbar)
        content_box.append(win.table_toolbar_revealer)
        
        # Set the content box as the content of the ToolbarView
        win.toolbar_view.set_content(content_box)
        
        # Create statusbar with revealer
        win.statusbar_revealer = Gtk.Revealer()
        win.statusbar_revealer.add_css_class("flat-header")
        win.statusbar_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        win.statusbar_revealer.set_transition_duration(250)
        win.statusbar_revealer.set_reveal_child(True)  # Visible by default
        
        # Create statusbar content
        statusbar_box = self.setup_statusbar_content(win)
        win.statusbar_revealer.set_child(statusbar_box)
        
        # Add the statusbar revealer as a bottom bar in the ToolbarView
        win.toolbar_view.add_bottom_bar(win.statusbar_revealer)
        
        # Set the ToolbarView as the window content
        win.set_content(win.toolbar_view)
        
        # Add actions
        self.setup_window_actions(win)
        
        win.connect("close-request", self.on_window_close_request)
        
        # Add to windows list
        self.windows.append(win)
        
        return win


    def setup_webview_message_handlers(self, win):
        """Set up the WebKit message handlers"""
        try:
            user_content_manager = win.webview.get_user_content_manager()
            user_content_manager.register_script_message_handler("contentChanged")
            user_content_manager.connect("script-message-received::contentChanged", 
                                        lambda mgr, res: self.on_content_changed(win, mgr, res))
            
            # Add handler for formatting changes
            user_content_manager.register_script_message_handler("formattingChanged")
            user_content_manager.connect("script-message-received::formattingChanged", 
                                        lambda mgr, res: self.on_formatting_changed(win, mgr, res))
            
            # Table-related message handlers
            user_content_manager.register_script_message_handler("tableClicked")
            user_content_manager.register_script_message_handler("tableDeleted")
            user_content_manager.register_script_message_handler("tablesDeactivated")
            
            user_content_manager.connect("script-message-received::tableClicked", 
                                        lambda mgr, res: self.on_table_clicked(win, mgr, res))
            user_content_manager.connect("script-message-received::tableDeleted", 
                                        lambda mgr, res: self.on_table_deleted(win, mgr, res))
            user_content_manager.connect("script-message-received::tablesDeactivated", 
                                        lambda mgr, res: self.on_tables_deactivated(win, mgr, res))
        except:
            print("Warning: Could not set up JavaScript message handlers")


    def setup_statusbar_content(self, win):
        """Create the statusbar content"""
        # Create a box for the statusbar 
        statusbar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        statusbar_box.set_margin_start(10)
        statusbar_box.set_margin_end(10)
        statusbar_box.set_margin_top(0)
        statusbar_box.set_margin_bottom(4)
        
        # Create the text label
        win.statusbar = Gtk.Label(label="Ready")
        win.statusbar.set_halign(Gtk.Align.START)
        win.statusbar.set_hexpand(True)
        statusbar_box.append(win.statusbar)
        
        # Add zoom toggle button at the right side of the statusbar
        win.zoom_toggle_button = Gtk.ToggleButton()
        win.zoom_toggle_button.set_icon_name("org.gnome.Settings-accessibility-zoom-symbolic")
        win.zoom_toggle_button.set_tooltip_text("Toggle Zoom Controls")
        win.zoom_toggle_button.add_css_class("flat")
        win.zoom_toggle_button.connect("toggled", lambda btn: self.on_zoom_toggle_clicked(win, btn))
        statusbar_box.append(win.zoom_toggle_button)
        
        # Create zoom revealer for toggle functionality
        win.zoom_revealer = Gtk.Revealer()
        win.zoom_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        win.zoom_revealer.set_transition_duration(300)
        win.zoom_revealer.set_reveal_child(False)  # Hidden by default
        
        # Create zoom control element inside the revealer
        zoom_control_box = self.create_zoom_controls(win)
        win.zoom_revealer.set_child(zoom_control_box)
        
        # Add the zoom revealer to the statusbar, before the toggle button
        statusbar_box.insert_child_after(win.zoom_revealer, win.statusbar)
        
        return statusbar_box


    def create_zoom_controls(self, win):
        """Create zoom control elements"""
        zoom_control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        zoom_control_box.add_css_class("linked")  # Use linked styling for cleaner appearance
        zoom_control_box.set_halign(Gtk.Align.END)
        
        # Create zoom level label
        win.zoom_label = Gtk.Label(label="100%")
        win.zoom_label.set_width_chars(4)  # Set a fixed width for the label
        win.zoom_label.set_margin_start(0)
        zoom_control_box.append(win.zoom_label)
        
        # Add zoom out button
        zoom_out_button = Gtk.Button.new_from_icon_name("zoom-out-symbolic")
        zoom_out_button.set_tooltip_text("Zoom Out")
        zoom_out_button.connect("clicked", lambda btn: self.on_zoom_out_clicked(win))
        zoom_control_box.append(zoom_out_button)
        
        # Create the slider for zoom with just marks, no text
        adjustment = Gtk.Adjustment(
            value=100,     # Default value
            lower=50,      # Minimum value
            upper=400,     # Maximum value
            step_increment=10,  # Step size
            page_increment=50   # Page step size
        )

        win.zoom_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment)
        win.zoom_scale.set_draw_value(False)  # Don't show the value on the scale
        win.zoom_scale.set_size_request(100, -1)  # Set a reasonable width
        win.zoom_scale.set_round_digits(0)  # Round to integer values

        # Add only marks without any text
        for mark_value in [50, 100, 200, 300]:
            win.zoom_scale.add_mark(mark_value, Gtk.PositionType.BOTTOM, None)

        # Connect to our zoom handler
        win.zoom_scale.connect("value-changed", lambda s: self.on_zoom_changed_statusbar(win, s))
        zoom_control_box.append(win.zoom_scale)
        
        # Enable snapping to the marks
        win.zoom_scale.set_has_origin(False)  # Disable highlighting from origin to current value

        # Add zoom in button
        zoom_in_button = Gtk.Button.new_from_icon_name("zoom-in-symbolic")
        zoom_in_button.set_tooltip_text("Zoom In")
        zoom_in_button.connect("clicked", lambda btn: self.on_zoom_in_clicked(win))
        zoom_control_box.append(zoom_in_button)
        
        return zoom_control_box


    def setup_toolbar_content(self, win):
        """Create and set up toolbar content"""
        # Store the handlers for blocking
        win.bold_handler_id = None
        win.italic_handler_id = None
        win.underline_handler_id = None
        win.strikeout_handler_id = None
        win.subscript_handler_id = None
        win.superscript_handler_id = None
        win.paragraph_style_handler_id = None
        win.font_handler_id = None
        win.font_size_handler_id = None

        # Create paragraph styles dropdown
        self.setup_paragraph_style_dropdown(win)
        
        # Create font dropdown
        self.setup_font_dropdown(win)
        
        # Create font size dropdown
        self.setup_font_size_dropdown(win)
        
        # Add Paragraph, font, size linked button group
        para_font_size_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        para_font_size_box.add_css_class("linked")
        para_font_size_box.append(win.paragraph_style_dropdown)
        para_font_size_box.append(win.font_dropdown)
        para_font_size_box.append(win.font_size_dropdown)    
                    
        win.toolbars_wrapbox.append(para_font_size_box)
        
        # Add formatting controls
        self.add_formatting_controls(win)
        
        # Add all the other toolbar elements
        self.add_subscript_superscript_controls(win)
        self.add_formatting_marks_controls(win)
        self.add_indent_controls(win)
        self.add_spacing_controls(win)
        self.add_column_case_controls(win)
        self.add_list_controls(win)
        self.add_color_controls(win)
        self.add_alignment_controls(win)
        self.add_wordart_clear_controls(win)
        self.add_insert_controls(win)
        self.add_rtl_controls(win)
        self.add_html_controls(win)


    def setup_window_actions(self, win):
        """Set up window-specific actions"""
        # Add case change action to the window
        case_change_action = Gio.SimpleAction.new("change-case", GLib.VariantType.new("s"))
        case_change_action.connect("activate", lambda action, param: self.on_change_case(win, param.get_string()))
        win.add_action(case_change_action)
        
        # Add toggle actions for UI elements
        toggle_headerbar_action = Gio.SimpleAction.new("toggle-headerbar", None)
        toggle_headerbar_action.connect("activate", lambda action, param: self.toggle_headerbar(win))
        win.add_action(toggle_headerbar_action)
        
        toggle_toolbar_action = Gio.SimpleAction.new("toggle-toolbar", None)
        toggle_toolbar_action.connect("activate", lambda action, param: self.toggle_file_toolbar(win))
        win.add_action(toggle_toolbar_action)
        
        toggle_statusbar_action = Gio.SimpleAction.new("toggle-statusbar", None)
        toggle_statusbar_action.connect("activate", lambda action, param: self.toggle_statusbar(win))
        win.add_action(toggle_statusbar_action)
        
        # Set up spacing and formatting actions
        self.setup_spacing_actions(win)



############# /Create Window
    
            

        
##############
    def setup_paragraph_style_dropdown(self, win):
        """Create paragraph styles dropdown"""
        win.paragraph_style_dropdown = Gtk.DropDown()
        win.paragraph_style_dropdown.set_tooltip_text("Paragraph Style")
        win.paragraph_style_dropdown.set_focus_on_click(False)
        
        # Create string list for paragraph styles
        paragraph_styles = Gtk.StringList()
        paragraph_styles.append("Normal")
        paragraph_styles.append("Heading 1")
        paragraph_styles.append("Heading 2")
        paragraph_styles.append("Heading 3")
        paragraph_styles.append("Heading 4")
        paragraph_styles.append("Heading 5")
        paragraph_styles.append("Heading 6")
        win.paragraph_style_dropdown.set_model(paragraph_styles)
        win.paragraph_style_dropdown.set_selected(0)  # Default to Normal
        
        # Connect signal handler
        win.paragraph_style_handler_id = win.paragraph_style_dropdown.connect(
            "notify::selected", lambda dd, param: self.on_paragraph_style_changed(win, dd))
        win.paragraph_style_dropdown.set_size_request(64, -1)

    def setup_font_dropdown(self, win):
        """Create font family dropdown"""
        # Get available fonts from Pango
        font_map = PangoCairo.FontMap.get_default()
        font_families = font_map.list_families()
        
        # Create string list and sort alphabetically
        font_names = Gtk.StringList()
        sorted_families = sorted([family.get_name() for family in font_families])
        
        # Add all fonts in alphabetical order
        for family in sorted_families:
            font_names.append(family)
            
        # Create dropdown with fixed width
        win.font_dropdown = Gtk.DropDown()
        win.font_dropdown.set_tooltip_text("Font Family")
        win.font_dropdown.set_focus_on_click(False)
        win.font_dropdown.set_model(font_names)

        # Set fixed width and prevent expansion
        win.font_dropdown.set_size_request(163, -1)  # Reduced width in flat layout
        win.font_dropdown.set_hexpand(False)
        
        # Create a factory only for the BUTTON part of the dropdown
        button_factory = Gtk.SignalListItemFactory()
        
        def setup_button_label(factory, list_item):
            label = Gtk.Label()
            label.set_ellipsize(Pango.EllipsizeMode.END)  # Ellipsize button text
            label.set_xalign(0)
            label.set_margin_start(0)
            label.set_margin_end(0)
            # Set maximum width for the text
            label.set_max_width_chars(10)  # Limit to approximately 10 characters
            label.set_width_chars(10)      # Try to keep consistent width
            list_item.set_child(label)
        
        def bind_button_label(factory, list_item):
            position = list_item.get_position()
            label = list_item.get_child()
            label.set_text(font_names.get_string(position))
        
        button_factory.connect("setup", setup_button_label)
        button_factory.connect("bind", bind_button_label)
        
        # Apply the factory only to the dropdown display (not the list)
        win.font_dropdown.set_factory(button_factory)
        
        # For the popup list, create a standard factory without ellipsization
        list_factory = Gtk.SignalListItemFactory()
        
        def setup_list_label(factory, list_item):
            label = Gtk.Label()
            label.set_xalign(0)
            label.set_margin_start(2)
            label.set_margin_end(2)
            list_item.set_child(label)
        
        def bind_list_label(factory, list_item):
            position = list_item.get_position()
            label = list_item.get_child()
            label.set_text(font_names.get_string(position))
        
        list_factory.connect("setup", setup_list_label)
        list_factory.connect("bind", bind_list_label)
        
        # Apply the list factory to the dropdown list only
        win.font_dropdown.set_list_factory(list_factory)
        
        # Set initial font (first in list)
        win.font_dropdown.set_selected(0)
        
        # Connect signal handler
        win.font_handler_id = win.font_dropdown.connect(
            "notify::selected", lambda dd, param: self.on_font_changed(win, dd))

    def setup_font_size_dropdown(self, win):
        """Create font size dropdown"""
        # Create string list for font sizes
        font_sizes = Gtk.StringList()
        for size in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 21, 22, 24, 26, 28, 32, 36, 40, 42, 44, 48, 54, 60, 66, 72, 80, 88, 96]:
            font_sizes.append(str(size))
        
        # Create dropdown
        win.font_size_dropdown = Gtk.DropDown()
        win.font_size_dropdown.set_tooltip_text("Font Size")
        win.font_size_dropdown.set_focus_on_click(False)
        win.font_size_dropdown.set_model(font_sizes)
        
        # Set a reasonable width
        win.font_size_dropdown.set_size_request(65, -1)
        
        # Set initial size (12pt)
        initial_size = 6  # Index of size 12 in our list
        win.font_size_dropdown.set_selected(initial_size)
        
        # Connect signal handler
        win.font_size_handler_id = win.font_size_dropdown.connect(
            "notify::selected", lambda dd, param: self.on_font_size_changed(win, dd))

    def add_formatting_controls(self, win):
        """Add basic text formatting controls (bold, italic, underline, strikethrough)"""
        # Create button group (basic formatting - Bold, Italics, Underline, Strikethrough)
        bius_group = Gtk.Box(css_classes=["linked"], orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        bius_group.set_margin_start(0)
        bius_group.set_margin_end(0)
        
        # Bold button
        win.bold_button = Gtk.ToggleButton(icon_name="format-text-bold-symbolic")
        win.bold_button.set_tooltip_text("Bold (Ctrl+B)")
        win.bold_button.set_focus_on_click(False)
        win.bold_button.set_size_request(40, 36)
        win.bold_handler_id = win.bold_button.connect("toggled", lambda btn: self.on_bold_toggled(win, btn))
        bius_group.append(win.bold_button)          

        # Italic button
        win.italic_button = Gtk.ToggleButton(icon_name="format-text-italic-symbolic")
        win.italic_button.set_tooltip_text("Italic (Ctrl+I)")
        win.italic_button.set_focus_on_click(False)
        win.italic_button.set_size_request(40, 36)
        win.italic_handler_id = win.italic_button.connect("toggled", lambda btn: self.on_italic_toggled(win, btn))
        bius_group.append(win.italic_button)
        
        # Underline button
        win.underline_button = Gtk.ToggleButton(icon_name="format-text-underline-symbolic")
        win.underline_button.set_tooltip_text("Underline (Ctrl+U)")
        win.underline_button.set_focus_on_click(False)
        win.underline_button.set_size_request(40, 36)
        win.underline_handler_id = win.underline_button.connect("toggled", lambda btn: self.on_underline_toggled(win, btn))
        bius_group.append(win.underline_button)
        
        # Strikeout button
        win.strikeout_button = Gtk.ToggleButton(icon_name="format-text-strikethrough-symbolic")
        win.strikeout_button.set_tooltip_text("Strikeout")
        win.strikeout_button.set_focus_on_click(False)
        win.strikeout_button.set_size_request(40, 36)
        win.strikeout_handler_id = win.strikeout_button.connect("toggled", lambda btn: self.on_strikeout_toggled(win, btn))
        bius_group.append(win.strikeout_button)        

        win.toolbars_wrapbox.append(bius_group)

    def add_subscript_superscript_controls(self, win):
        """Add subscript and superscript controls"""
        subscript_group = Gtk.Box(css_classes=["linked"], orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        subscript_group.set_margin_start(0)
        subscript_group.set_margin_end(0)
        
        # Add subscript and superscript buttons if your handlers exist
        if hasattr(self, 'on_subscript_toggled'):
            win.subscript_button = Gtk.ToggleButton(icon_name="format-text-subscript-symbolic")
            win.subscript_button.set_tooltip_text("Subscript")
            win.subscript_button.add_css_class("flat")
            win.subscript_button.set_size_request(40, 36)
            win.subscript_handler_id = win.subscript_button.connect("toggled", 
                lambda btn: self.on_subscript_toggled(win, btn))
            subscript_group.append(win.subscript_button)
        
        if hasattr(self, 'on_superscript_toggled'):
            win.superscript_button = Gtk.ToggleButton(icon_name="format-text-superscript-symbolic")
            win.superscript_button.set_tooltip_text("Superscript")
            win.superscript_button.add_css_class("flat")
            win.superscript_button.set_size_request(40, 36)
            win.superscript_handler_id = win.superscript_button.connect("toggled", 
                lambda btn: self.on_superscript_toggled(win, btn))
            subscript_group.append(win.superscript_button)

        win.toolbars_wrapbox.append(subscript_group) 

    def add_formatting_marks_controls(self, win):
        """Add drop cap and formatting marks controls"""
        dropcap_formatting_marks_group = Gtk.Box(css_classes=["linked"], orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        dropcap_formatting_marks_group.set_margin_start(0)
        dropcap_formatting_marks_group.set_margin_end(0)
        win.format_marks_button = Gtk.ToggleButton(icon_name="format-show-marks-symbolic")
        win.format_marks_button.set_tooltip_text("Show Formatting Marks")
        win.format_marks_button.set_size_request(40, 36)
        win.format_marks_button.connect("toggled", lambda btn: self.on_show_formatting_marks_toggled(win, btn))
        dropcap_formatting_marks_group.append(win.format_marks_button)

        # Drop cap button
        win.drop_cap_button = Gtk.Button(icon_name="format-drop-cap-symbolic")
        win.drop_cap_button.set_tooltip_text("Drop Cap")
        win.drop_cap_button.set_size_request(40, 36)
        win.drop_cap_button.connect("clicked", lambda btn: self.on_drop_cap_clicked(win, btn))
        dropcap_formatting_marks_group.append(win.drop_cap_button)
        
        win.toolbars_wrapbox.append(dropcap_formatting_marks_group)

    def add_indent_controls(self, win):
        """Add indent and outdent controls"""
        # Create linked button group for list/indent controls
        indent_group = Gtk.Box(css_classes=["linked"], orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        
        # Indent button
        indent_button = Gtk.Button(icon_name="format-indent-more-symbolic")
        indent_button.set_tooltip_text("Increase Indent")
        indent_button.set_focus_on_click(False)
        indent_button.set_size_request(40, 36)
        indent_button.connect("clicked", lambda btn: self.on_indent_clicked(win, btn))
        indent_group.append(indent_button)
        
        # Outdent button
        outdent_button = Gtk.Button(icon_name="format-indent-less-symbolic")
        outdent_button.set_tooltip_text("Decrease Indent")
        outdent_button.set_focus_on_click(False)
        outdent_button.set_size_request(40, 36)
        outdent_button.connect("clicked", lambda btn: self.on_outdent_clicked(win, btn))
        indent_group.append(outdent_button)
        
        win.toolbars_wrapbox.append(indent_group)

    def add_spacing_controls(self, win):
        """Add line spacing and paragraph spacing controls"""
        # --- Spacing operations group (Line Spacing, Paragraph Spacing) ---
        spacing_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        spacing_group.add_css_class("linked")  # Apply linked styling
        spacing_group.set_margin_start(0)
        
        # Line spacing button menu
        line_spacing_button = Gtk.MenuButton(icon_name="format-line-spacing-symbolic")
        line_spacing_button.set_size_request(40, 36)
        line_spacing_button.set_tooltip_text("Line Spacing")

        # Create line spacing menu
        line_spacing_menu = Gio.Menu()
        
        # Add line spacing options
        line_spacing_menu.append("Single (1.0)", "win.line-spacing('1.0')")
        line_spacing_menu.append("Default (1.15)", "win.line-spacing('1.15')")
        line_spacing_menu.append("One and a half (1.5)", "win.line-spacing('1.5')")
        line_spacing_menu.append("Double (2.0)", "win.line-spacing('2.0')")
        line_spacing_menu.append("Custom...", "win.line-spacing-dialog")
        
        line_spacing_button.set_menu_model(line_spacing_menu)
        
        # Paragraph spacing button menu
        para_spacing_button = Gtk.MenuButton(icon_name="format-paragraph-spacing-symbolic")
        para_spacing_button.set_size_request(40, 36)
        para_spacing_button.set_tooltip_text("Paragraph Spacing")

        # Create paragraph spacing menu
        para_spacing_menu = Gio.Menu()
        
        # Add paragraph spacing options
        para_spacing_menu.append("None", "win.paragraph-spacing('0')")
        para_spacing_menu.append("Small (5px)", "win.paragraph-spacing('5')")
        para_spacing_menu.append("Medium (15px)", "win.paragraph-spacing('15')")
        para_spacing_menu.append("Large (30px)", "win.paragraph-spacing('30')")
        para_spacing_menu.append("Custom...", "win.paragraph-spacing-dialog")
        
        para_spacing_button.set_menu_model(para_spacing_menu)
        
        # Add buttons to spacing group
        spacing_group.append(line_spacing_button)
        spacing_group.append(para_spacing_button)

        # Add spacing group to toolbar
        win.toolbars_wrapbox.append(spacing_group)

    def add_column_case_controls(self, win):
        """Add column layout and text case controls"""
        column_case_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        column_case_group.add_css_class("linked")  # Apply linked styling
        column_case_group.set_margin_start(0)
        
        column_button = Gtk.MenuButton(icon_name="columns-symbolic")
        column_button.set_size_request(40, 36)
        column_button.set_tooltip_text("Column Layout")
        
        # Create column menu
        column_menu = Gio.Menu()
        
        # Add column options
        column_menu.append("Single Column", "win.set-columns('1')")
        column_menu.append("Two Columns", "win.set-columns('2')")
        column_menu.append("Three Columns", "win.set-columns('3')")
        column_menu.append("Four Columns", "win.set-columns('4')")
        column_menu.append("Remove Columns", "win.set-columns('0')")
        
        column_button.set_menu_model(column_menu)
        
        # Case change menu button
        case_menu_button = Gtk.MenuButton(icon_name="uppercase-symbolic")
        case_menu_button.set_tooltip_text("Change Case")
        case_menu_button.set_size_request(40, 36)

        # Create case change menu
        case_menu = Gio.Menu()
        case_menu.append("Sentence case.", "win.change-case::sentence")
        case_menu.append("lowercase", "win.change-case::lower")
        case_menu.append("UPPERCASE", "win.change-case::upper")
        case_menu.append("Capitalize Each Word", "win.change-case::title")
        case_menu.append("tOGGLE cASE", "win.change-case::toggle")
        case_menu.append("SMALL CAPS", "win.change-case::smallcaps")

        # Set the menu model for the button
        case_menu_button.set_menu_model(case_menu)

        # Add buttons to column case group
        column_case_group.append(column_button)
        column_case_group.append(case_menu_button)        
        
        # Add spacing group to toolbar
        win.toolbars_wrapbox.append(column_case_group)

    def add_list_controls(self, win):
        """Add bullet and numbered list controls"""
        list_group = Gtk.Box(css_classes=["linked"], orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        win.bullet_list_button = Gtk.ToggleButton(icon_name="view-list-bullet-symbolic")
        win.bullet_list_button.set_tooltip_text("Bullet List")
        win.bullet_list_button.set_focus_on_click(False)
        win.bullet_list_button.set_size_request(40, 36)
        # Store the handler ID directly on the button
        win.bullet_list_button.handler_id = win.bullet_list_button.connect("toggled", 
            lambda btn: self.on_bullet_list_toggled(win, btn))
        list_group.append(win.bullet_list_button)

        # Numbered List button
        win.numbered_list_button = Gtk.ToggleButton(icon_name="view-list-ordered-symbolic")
        win.numbered_list_button.set_tooltip_text("Numbered List")
        win.numbered_list_button.set_focus_on_click(False)
        win.numbered_list_button.set_size_request(40, 36)
        # Store the handler ID directly on the button
        win.numbered_list_button.handler_id = win.numbered_list_button.connect("toggled", 
            lambda btn: self.on_numbered_list_toggled(win, btn))
        list_group.append(win.numbered_list_button)

        win.toolbars_wrapbox.append(list_group)

    def add_color_controls(self, win):
        """Add text color and background color controls"""
        color_bg_group = Gtk.Box(css_classes=["linked"], orientation=Gtk.Orientation.HORIZONTAL, spacing=0)        
        color_bg_group.set_margin_start(0)
        color_bg_group.set_margin_end(0)

        # --- Text Color SplitButton ---
        # Create the main button part with icon and color indicator
        font_color_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Icon
        font_color_icon = Gtk.Image.new_from_icon_name("draw-text-symbolic")
        font_color_icon.set_margin_top(4)
        font_color_icon.set_margin_bottom(0)
        font_color_box.append(font_color_icon)
        
        # Color indicator
        win.font_color_indicator = Gtk.Box()
        win.font_color_indicator.add_css_class("color-indicator")
        win.font_color_indicator.set_size_request(16, 2)
        color = Gdk.RGBA()
        color.parse("transparent")
        self.set_box_color(win.font_color_indicator, color)
        font_color_box.append(win.font_color_indicator)

        # Create font color popover for the dropdown part
        font_color_popover = Gtk.Popover()
        font_color_popover.set_autohide(True)
        font_color_popover.set_has_arrow(False)

        font_color_box_menu = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        font_color_box_menu.set_margin_start(0)
        font_color_box_menu.set_margin_end(0)
        font_color_box_menu.set_margin_top(0)
        font_color_box_menu.set_margin_bottom(0)

        # Add "Automatic" option at the top
        automatic_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        automatic_row.set_margin_bottom(0)
        automatic_icon = Gtk.Image.new_from_icon_name("edit-undo-symbolic")
        automatic_label = Gtk.Label(label="Automatic")
        automatic_row.append(automatic_icon)
        automatic_row.append(automatic_label)

        automatic_button = Gtk.Button()
        automatic_button.set_child(automatic_row)
        automatic_button.connect("clicked", lambda btn: self.on_font_color_automatic_clicked(win, font_color_popover))
        font_color_box_menu.append(automatic_button)

        # Add separator
        fg_separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        fg_separator.set_margin_bottom(0)
        font_color_box_menu.append(fg_separator)

        # Create color grid
        font_color_grid = Gtk.Grid()
        font_color_grid.set_row_spacing(2)
        font_color_grid.set_column_spacing(2)
        font_color_grid.set_row_homogeneous(True)
        font_color_grid.set_column_homogeneous(True)
        font_color_grid.add_css_class("color-grid")
        
        # Basic colors for text
        text_colors = [
            "#000000", "#434343", "#666666", "#999999", "#b7b7b7", "#cccccc", "#d9d9d9", "#efefef", "#f3f3f3", "#ffffff",
            "#980000", "#ff0000", "#ff9900", "#ffff00", "#00ff00", "#00ffff", "#4a86e8", "#0000ff", "#9900ff", "#ff00ff",
            "#e6b8af", "#f4cccc", "#fce5cd", "#fff2cc", "#d9ead3", "#d0e0e3", "#c9daf8", "#cfe2f3", "#d9d2e9", "#ead1dc",
            "#dd7e6b", "#ea9999", "#f9cb9c", "#ffe599", "#b6d7a8", "#a2c4c9", "#a4c2f4", "#9fc5e8", "#b4a7d6", "#d5a6bd",
            "#cc4125", "#e06666", "#f6b26b", "#ffd966", "#93c47d", "#76a5af", "#6d9eeb", "#6fa8dc", "#8e7cc3", "#c27ba0",
            "#a61c00", "#cc0000", "#e69138", "#f1c232", "#6aa84f", "#45818e", "#3c78d8", "#3d85c6", "#674ea7", "#a64d79",
            "#85200c", "#990000", "#b45f06", "#bf9000", "#38761d", "#134f5c", "#1155cc", "#0b5394", "#351c75", "#741b47",
            "#5b0f00", "#660000", "#783f04", "#7f6000", "#274e13", "#0c343d", "#1c4587", "#073763", "#20124d", "#4c1130"
        ]

        # Create color buttons and add to grid
        row, col = 0, 0
        for color_hex in text_colors:
            color_button = self.create_color_button(color_hex)
            color_button.connect("clicked", lambda btn, c=color_hex: self.on_font_color_selected(win, c, font_color_popover))
            font_color_grid.attach(color_button, col, row, 1, 1)
            col += 1
            if col >= 10:  # 10 columns
                col = 0
                row += 1

        font_color_box_menu.append(font_color_grid)

        # Add "More Colors..." button
        more_colors_button = Gtk.Button(label="More Colors...")
        more_colors_button.set_margin_top(0)
        more_colors_button.connect("clicked", lambda btn: self.on_more_font_colors_clicked(win, font_color_popover))
        font_color_box_menu.append(more_colors_button)

        # Set content for popover
        font_color_popover.set_child(font_color_box_menu)

        # Create the SplitButton
        win.font_color_button = Adw.SplitButton()
        win.font_color_button.set_tooltip_text("Text Color")
        win.font_color_button.set_focus_on_click(False)
        win.font_color_button.set_size_request(40, 36)
        win.font_color_button.set_child(font_color_box)
        win.font_color_button.set_popover(font_color_popover)
        
        # Connect the click handler to apply the current color
        win.font_color_button.connect("clicked", lambda btn: self.on_font_color_button_clicked(win))
        color_bg_group.append(win.font_color_button)
        
        # --- Background Color SplitButton ---
        # Create the main button part with icon and color indicator
        bg_color_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Icon
        bg_color_icon = Gtk.Image.new_from_icon_name("marker-symbolic")
        bg_color_icon.set_margin_top(4)
        bg_color_icon.set_margin_bottom(0)
        bg_color_box.append(bg_color_icon)

        # Color indicator
        win.bg_color_indicator = Gtk.Box()
        win.bg_color_indicator.add_css_class("color-indicator")
        win.bg_color_indicator.set_size_request(16, 2)
        bg_color = Gdk.RGBA()
        bg_color.parse("transparent")
        self.set_box_color(win.bg_color_indicator, bg_color)
        bg_color_box.append(win.bg_color_indicator)

        # Create Background Color popover for the dropdown
        bg_color_popover = Gtk.Popover()
        bg_color_popover.set_autohide(True)
        bg_color_popover.set_has_arrow(False)
        bg_color_box_menu = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        bg_color_box_menu.set_margin_start(6)
        bg_color_box_menu.set_margin_end(6)
        bg_color_box_menu.set_margin_top(6)
        bg_color_box_menu.set_margin_bottom(6)
        
        # Add "Automatic" option at the top
        bg_automatic_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        bg_automatic_row.set_margin_bottom(0)
        bg_automatic_icon = Gtk.Image.new_from_icon_name("edit-undo-symbolic")
        bg_automatic_label = Gtk.Label(label="Automatic")
        bg_automatic_row.append(bg_automatic_icon)
        bg_automatic_row.append(bg_automatic_label)

        bg_automatic_button = Gtk.Button()
        bg_automatic_button.set_child(bg_automatic_row)
        bg_automatic_button.connect("clicked", lambda btn: self.on_bg_color_automatic_clicked(win, bg_color_popover))
        bg_color_box_menu.append(bg_automatic_button)

        # Add separator
        bg_separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        bg_separator.set_margin_bottom(0)
        bg_color_box_menu.append(bg_separator)

        # Create color grid
        bg_color_grid = Gtk.Grid()
        bg_color_grid.set_row_spacing(2)
        bg_color_grid.set_column_spacing(2)
        bg_color_grid.set_row_homogeneous(True)
        bg_color_grid.set_column_homogeneous(True)
        bg_color_grid.add_css_class("color-grid")

        # Basic colors for background (same palette as text)
        bg_colors = text_colors

        # Create color buttons and add to grid
        row, col = 0, 0
        for color_hex in bg_colors:
            color_button = self.create_color_button(color_hex)
            color_button.connect("clicked", lambda btn, c=color_hex: self.on_bg_color_selected(win, c, bg_color_popover))
            bg_color_grid.attach(color_button, col, row, 1, 1)
            col += 1
            if col >= 10:  # 10 columns
                col = 0
                row += 1

        bg_color_box_menu.append(bg_color_grid)
        
        # Add "More Colors..." button
        bg_more_colors_button = Gtk.Button(label="More Colors...")
        bg_more_colors_button.set_margin_top(6)
        bg_more_colors_button.connect("clicked", lambda btn: self.on_more_bg_colors_clicked(win, bg_color_popover))
        bg_color_box_menu.append(bg_more_colors_button)

        # Set content for popover
        bg_color_popover.set_child(bg_color_box_menu)

        # Create the SplitButton
        win.bg_color_button = Adw.SplitButton()
        win.bg_color_button.set_tooltip_text("Background Color")
        win.bg_color_button.set_focus_on_click(False)
        win.bg_color_button.set_size_request(40, 36)
        win.bg_color_button.set_child(bg_color_box)
        win.bg_color_button.set_popover(bg_color_popover)

        # Connect the click handler to apply the current color
        win.bg_color_button.connect("clicked", lambda btn: self.on_bg_color_button_clicked(win))
        color_bg_group.append(win.bg_color_button)
        
        win.toolbars_wrapbox.append(color_bg_group)      
        
        
        
        
####################    #    
    def on_font_color_button_clicked(self, win):
        """Handle font color button click (apply current color)"""
        # Get the current color from the indicator
        style_context = win.font_color_indicator.get_style_context()
        css_provider = None
        
        # Try to find the CSS provider for the color
        for provider in style_context.list_providers():
            css_provider = provider
            break
        
        if css_provider:
            # Get CSS data and extract color
            css_data = css_provider.to_string()
            import re
            color_match = re.search(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d\.]+)\)', css_data)
            if color_match:
                r, g, b, a = map(float, color_match.groups())
                # Convert to 0-1 range for RGBA
                r /= 255
                g /= 255
                b /= 255
                
                # Create color object
                color = Gdk.RGBA()
                color.red = r
                color.green = g
                color.blue = b
                color.alpha = float(a)
                
                # Apply color to selection
                self.apply_font_color(win, color)
            else:
                # No color set or transparent
                win.statusbar.set_text("No color selected")
        else:
            win.statusbar.set_text("No color selected")

    def on_font_color_selected(self, win, color_hex, popover):
        """Handle font color selection from the grid"""
        # Parse color
        color = Gdk.RGBA()
        color.parse(color_hex)
        
        # Apply to the indicator
        self.set_box_color(win.font_color_indicator, color)
        
        # Apply to selection
        self.apply_font_color(win, color)
        
        # Close popover
        popover.popdown()
        
        # Update status
        win.statusbar.set_text(f"Text color set to {color_hex}")

    def on_font_color_automatic_clicked(self, win, popover):
        """Handle automatic (default) font color selection"""
        # Set transparent indicator
        color = Gdk.RGBA()
        color.parse("transparent")
        self.set_box_color(win.font_color_indicator, color)
        
        # Remove font color from selection
        js_code = """
        (function() {
            document.execCommand('foreColor', false, '');
            return true;
        })();
        """
        self.execute_js(win, js_code)
        
        # Close popover
        popover.popdown()
        
        # Update status
        win.statusbar.set_text("Default text color restored")

    def on_more_font_colors_clicked(self, win, popover):
        """Show color chooser dialog for custom text color"""
        # Create a new color dialog
        color_dialog = Gtk.ColorDialog()
        color_dialog.set_title("Choose Text Color")
        
        # Get current color from indicator if possible
        style_context = win.font_color_indicator.get_style_context()
        current_color = Gdk.RGBA()
        current_color.parse("black")  # Default
        
        # Try to find the CSS provider for the color
        for provider in style_context.list_providers():
            css_data = provider.to_string()
            import re
            color_match = re.search(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d\.]+)\)', css_data)
            if color_match:
                r, g, b, a = map(float, color_match.groups())
                # Convert to 0-1 range for RGBA
                current_color.red = r / 255
                current_color.green = g / 255
                current_color.blue = b / 255
                current_color.alpha = float(a)
                break
        
        # Show the color dialog
        color_dialog.choose_rgba(
            win,  # Parent window
            current_color,  # Initial color
            None,  # No cancellable
            self.on_font_color_dialog_response,  # Callback
            popover  # User data to pass to callback
        )

    def on_font_color_dialog_response(self, dialog, result, popover):
        """Handle response from the font color dialog"""
        try:
            color = dialog.choose_rgba_finish(result)
            # Find the window
            for win in self.windows:
                if win.is_active():
                    # Apply to the indicator
                    self.set_box_color(win.font_color_indicator, color)
                    
                    # Apply to selection
                    self.apply_font_color(win, color)
                    
                    # Close popover
                    popover.popdown()
                    
                    # Update status
                    win.statusbar.set_text("Custom text color applied")
                    break
        except GLib.Error as error:
            # Color selection was cancelled
            pass

    def apply_font_color(self, win, color):
        """Apply font color to the current selection"""
        # Convert color to hex format for execCommand
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(color.red * 255),
            int(color.green * 255),
            int(color.blue * 255)
        )
        
        # Apply color to selection
        js_code = f"""
        (function() {{
            document.execCommand('foreColor', false, '{hex_color}');
            return true;
        }})();
        """
        self.execute_js(win, js_code)

    def on_bg_color_button_clicked(self, win):
        """Handle background color button click (apply current color)"""
        # Get the current color from the indicator
        style_context = win.bg_color_indicator.get_style_context()
        css_provider = None
        
        # Try to find the CSS provider for the color
        for provider in style_context.list_providers():
            css_provider = provider
            break
        
        if css_provider:
            # Get CSS data and extract color
            css_data = css_provider.to_string()
            import re
            color_match = re.search(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d\.]+)\)', css_data)
            if color_match:
                r, g, b, a = map(float, color_match.groups())
                # Convert to 0-1 range for RGBA
                r /= 255
                g /= 255
                b /= 255
                
                # Create color object
                color = Gdk.RGBA()
                color.red = r
                color.green = g
                color.blue = b
                color.alpha = float(a)
                
                # Apply color to selection
                self.apply_bg_color(win, color)
            else:
                # No color set or transparent
                win.statusbar.set_text("No background color selected")
        else:
            win.statusbar.set_text("No background color selected")

    def on_bg_color_selected(self, win, color_hex, popover):
        """Handle background color selection from the grid"""
        # Parse color
        color = Gdk.RGBA()
        color.parse(color_hex)
        
        # Apply to the indicator
        self.set_box_color(win.bg_color_indicator, color)
        
        # Apply to selection
        self.apply_bg_color(win, color)
        
        # Close popover
        popover.popdown()
        
        # Update status
        win.statusbar.set_text(f"Background color set to {color_hex}")

    def on_bg_color_automatic_clicked(self, win, popover):
        """Handle automatic (default) background color selection"""
        # Set transparent indicator
        color = Gdk.RGBA()
        color.parse("transparent")
        self.set_box_color(win.bg_color_indicator, color)
        
        # Remove background color from selection
        js_code = """
        (function() {
            document.execCommand('hiliteColor', false, '');
            return true;
        })();
        """
        self.execute_js(win, js_code)
        
        # Close popover
        popover.popdown()
        
        # Update status
        win.statusbar.set_text("Default background color restored")

    def on_more_bg_colors_clicked(self, win, popover):
        """Show color chooser dialog for custom background color"""
        # Create a new color dialog
        color_dialog = Gtk.ColorDialog()
        color_dialog.set_title("Choose Background Color")
        
        # Get current color from indicator if possible
        style_context = win.bg_color_indicator.get_style_context()
        current_color = Gdk.RGBA()
        current_color.parse("white")  # Default
        
        # Try to find the CSS provider for the color
        for provider in style_context.list_providers():
            css_data = provider.to_string()
            import re
            color_match = re.search(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d\.]+)\)', css_data)
            if color_match:
                r, g, b, a = map(float, color_match.groups())
                # Convert to 0-1 range for RGBA
                current_color.red = r / 255
                current_color.green = g / 255
                current_color.blue = b / 255
                current_color.alpha = float(a)
                break
        
        # Show the color dialog
        color_dialog.choose_rgba(
            win,  # Parent window
            current_color,  # Initial color
            None,  # No cancellable
            self.on_bg_color_dialog_response,  # Callback
            popover  # User data to pass to callback
        )

    def on_bg_color_dialog_response(self, dialog, result, popover):
        """Handle response from the background color dialog"""
        try:
            color = dialog.choose_rgba_finish(result)
            # Find the window
            for win in self.windows:
                if win.is_active():
                    # Apply to the indicator
                    self.set_box_color(win.bg_color_indicator, color)
                    
                    # Apply to selection
                    self.apply_bg_color(win, color)
                    
                    # Close popover
                    popover.popdown()
                    
                    # Update status
                    win.statusbar.set_text("Custom background color applied")
                    break
        except GLib.Error as error:
            # Color selection was cancelled
            pass

    def apply_bg_color(self, win, color):
        """Apply background color to the current selection"""
        # Convert color to hex format for execCommand
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(color.red * 255),
            int(color.green * 255),
            int(color.blue * 255)
        )
        
        # Apply color to selection
        js_code = f"""
        (function() {{
            document.execCommand('hiliteColor', false, '{hex_color}');
            return true;
        }})();
        """
        self.execute_js(win, js_code)
        
        
        
        
















###################
    def create_color_button(self, color_hex):
        """Create a button with a color swatch"""
        button = Gtk.Button()
        button.set_size_request(20, 20)
        
        # Create a drawing area for the color display
        color_box = Gtk.Box()
        color_box.set_size_request(16, 16)
        
        # Apply CSS styling for the color
        color_box.add_css_class("color-box")
        
        # Set the background color directly
        color = Gdk.RGBA()
        if color_hex == "transparent":
            # For transparent color
            color.parse("rgba(0,0,0,0)")
        else:
            # For regular colors
            color.parse(color_hex)
        
        self.set_box_color(color_box, color)
        
        # Set as button content
        button.set_child(color_box)
        
        # Add tooltip with hex color
        button.set_tooltip_text(color_hex)
        
        return button

    def set_box_color(self, box, color):
        """Set background color of a box element"""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            f"box {{ background-color: rgba({int(color.red*255)}, {int(color.green*255)}, {int(color.blue*255)}, {color.alpha}); }}".encode()
        )
        
        style_context = box.get_style_context()
        style_context.add_provider(
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
#####################        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    def add_alignment_controls(self, win):
        """Add text alignment controls"""
        # Create linked button group for alignment controls
        alignment_group = Gtk.Box(css_classes=["linked"], orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        
        # Align Left button
        align_left_button = Gtk.ToggleButton(icon_name="format-justify-left-symbolic")
        align_left_button.set_tooltip_text("Align Left")
        align_left_button.set_focus_on_click(False)
        align_left_button.set_size_request(40, 36)
        # Store the handler ID when connecting
        align_left_button.handler_id = align_left_button.connect("toggled", 
            lambda btn: self.on_align_left_toggled(win, btn))
        alignment_group.append(align_left_button)
        
        # Align Center button
        align_center_button = Gtk.ToggleButton(icon_name="format-justify-center-symbolic")
        align_center_button.set_tooltip_text("Align Center")
        align_center_button.set_focus_on_click(False)
        align_center_button.set_size_request(40, 36)
        # Store the handler ID when connecting
        align_center_button.handler_id = align_center_button.connect("toggled", 
            lambda btn: self.on_align_center_toggled(win, btn))
        alignment_group.append(align_center_button)

        # Align Right button
        align_right_button = Gtk.ToggleButton(icon_name="format-justify-right-symbolic")
        align_right_button.set_tooltip_text("Align Right")
        align_right_button.set_focus_on_click(False)
        align_right_button.set_size_request(40, 36)
        # Store the handler ID when connecting
        align_right_button.handler_id = align_right_button.connect("toggled", 
            lambda btn: self.on_align_right_toggled(win, btn))
        alignment_group.append(align_right_button)

        # Justify button
        align_justify_button = Gtk.ToggleButton(icon_name="format-justify-fill-symbolic")
        align_justify_button.set_tooltip_text("Justify")
        align_justify_button.set_focus_on_click(False)
        align_justify_button.set_size_request(40, 36)
        # Store the handler ID when connecting
        align_justify_button.handler_id = align_justify_button.connect("toggled", 
            lambda btn: self.on_align_justify_toggled(win, btn))
        alignment_group.append(align_justify_button)
        
        # Store references to alignment buttons for toggling
        win.alignment_buttons = {
            'left': align_left_button,
            'center': align_center_button, 
            'right': align_right_button,
            'justify': align_justify_button
        }

        win.toolbars_wrapbox.append(alignment_group)

    def add_wordart_clear_controls(self, win):
        """Add Word Art and clear formatting controls"""
        clear_group = Gtk.Box(css_classes=["linked"], orientation=Gtk.Orientation.HORIZONTAL, spacing=0)        
        clear_group.set_margin_start(0)
        clear_group.set_margin_end(0)
        
        # Add a Word Art button to the clear group
        wordart_button = Gtk.Button(icon_name="format-word-art-symbolic")  
        wordart_button.set_size_request(40, 36)
        wordart_button.set_tooltip_text("Insert Word Art")
        wordart_button.connect("clicked", lambda btn: self.on_wordart_clicked(win, btn))

        # Add the button to the insert group
        clear_group.append(wordart_button)          
        
        # Clear formatting button
        clear_formatting_button = Gtk.Button(icon_name="eraser-symbolic")
        clear_formatting_button.set_tooltip_text("Remove Text Formatting")
        clear_formatting_button.set_size_request(42, 36)
        clear_formatting_button.connect("clicked", lambda btn: self.on_clear_formatting_clicked(win, btn))
        clear_group.append(clear_formatting_button)

        win.toolbars_wrapbox.append(clear_group)

    def add_insert_controls(self, win):
        """Add insertion controls (table, text box, image, etc.)"""
        # --- Insert operations group (Table, Text Box, Image) ---
        insert_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        insert_group.add_css_class("linked")  # Apply linked styling
        insert_group.set_margin_start(0)

        # Insert table button
        table_button = Gtk.Button(icon_name="table-symbolic")  # Use a standard table icon
        table_button.set_size_request(40, 36)
        table_button.set_tooltip_text("Insert Table")
        table_button.connect("clicked", lambda btn: self.on_insert_table_clicked(win, btn))

        # Insert text box button
        text_box_button = Gtk.Button(icon_name="insert-text-symbolic")
        text_box_button.set_size_request(40, 36)
        text_box_button.set_tooltip_text("Insert Text Box")
        text_box_button.connect("clicked", lambda btn: self.on_insert_text_box_clicked(win, btn))        

        # Insert image button
        image_button = Gtk.Button(icon_name="insert-image-symbolic")
        image_button.set_size_request(40, 36)
        image_button.set_tooltip_text("Insert Image")
        image_button.connect("clicked", lambda btn: self.on_insert_image_clicked(win, btn))

        # Insert link button
        link_button = Gtk.Button(icon_name="insert-link-symbolic")
        link_button.set_size_request(40, 36)
        link_button.set_tooltip_text("Insert link")
        link_button.connect("clicked", lambda btn: self.on_insert_link_clicked(win, btn))

        # Insert date/time button
        insert_date_time_button = Gtk.Button(icon_name="today-symbolic")
        insert_date_time_button.set_size_request(40, 36)
        insert_date_time_button.set_tooltip_text("Insert Date/Time")
        insert_date_time_button.connect("clicked", lambda btn: self.on_insert_datetime_clicked(win, btn))
     
        # Add buttons to insert group
        insert_group.append(table_button)
        insert_group.append(text_box_button)
        insert_group.append(image_button)
        insert_group.append(link_button)
        insert_group.append(insert_date_time_button)
        
        # Add insert group to toolbar
        win.toolbars_wrapbox.append(insert_group)

    def add_rtl_controls(self, win):
        """Add RTL text direction controls"""
        # Create a toggle button group for text direction
        direction_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        direction_group.add_css_class("linked")
        direction_group.set_margin_start(0)

        # RTL toggle button
        win.rtl_button = Gtk.ToggleButton(icon_name="text-direction-ltr-symbolic")
        win.rtl_button.set_tooltip_text("Toggle Right-to-Left Text Direction")
        win.rtl_button.set_focus_on_click(False)
        win.rtl_button.set_size_request(40, 36)
        win.rtl_button.connect("toggled", lambda btn: self.on_rtl_toggled(win, btn))
        direction_group.append(win.rtl_button)

        # Add the direction group to the toolbar
        win.toolbars_wrapbox.append(direction_group)

    def add_html_controls(self, win):
        """Add HTML view/edit controls"""
        # Add the Show HTML button
        show_html_button = Gtk.Button(icon_name="text-x-generic-symbolic")
        show_html_button.set_tooltip_text("Show HTML")
        show_html_button.set_margin_start(10)
        show_html_button.connect("clicked", lambda btn: self.on_show_html_clicked(win, btn))
        win.toolbars_wrapbox.append(show_html_button)        
        
        
        
        
############### Text box related methods
    def on_insert_text_box_clicked(self, win, btn):
        """Handle text box insertion button click"""
        win.statusbar.set_text("Inserting text box...")
        
        # Create a dialog to configure the text box
        dialog = Adw.Dialog()
        dialog.set_title("Insert Text Box")
        dialog.set_content_width(350)
        
        # Create layout for dialog content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        
        # Width input with +/- buttons
        width_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        width_label = Gtk.Label(label="Width (px):")
        width_label.set_halign(Gtk.Align.START)
        width_label.set_hexpand(True)
        
        width_adjustment = Gtk.Adjustment(value=150, lower=50, upper=800, step_increment=10)
        width_spin = Gtk.SpinButton()
        width_spin.set_adjustment(width_adjustment)
        
        # Create a box for the spinner and +/- buttons
        width_spinner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        width_spinner_box.add_css_class("linked")

        
        width_spinner_box.append(width_spin)


        
        width_box.append(width_label)
        width_box.append(width_spinner_box)
        content_box.append(width_box)
        
        # Height input with +/- buttons
        height_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        height_label = Gtk.Label(label="Height (px):")
        height_label.set_halign(Gtk.Align.START)
        height_label.set_hexpand(True)
        
        height_adjustment = Gtk.Adjustment(value=100, lower=30, upper=600, step_increment=10)
        height_spin = Gtk.SpinButton()
        height_spin.set_adjustment(height_adjustment)
        
        # Create a box for the spinner and +/- buttons
        height_spinner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        height_spinner_box.add_css_class("linked")
        height_spinner_box.append(height_spin)

        
        height_box.append(height_label)
        height_box.append(height_spinner_box)
        content_box.append(height_box)
        
        # Border width with +/- buttons
        border_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        border_label = Gtk.Label(label="Border width:")
        border_label.set_halign(Gtk.Align.START)
        border_label.set_hexpand(True)
        
        border_adjustment = Gtk.Adjustment(value=1, lower=0, upper=5, step_increment=1)
        border_spin = Gtk.SpinButton()
        border_spin.set_adjustment(border_adjustment)
        
        # Create a box for the spinner and +/- buttons
        border_spinner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        border_spinner_box.add_css_class("linked")
        
        border_spinner_box.append(border_spin)

        
        border_box.append(border_label)
        border_box.append(border_spinner_box)
        content_box.append(border_box)
        
        # Floating option checkbox
        float_check = Gtk.CheckButton(label="Free-floating (text wraps around)")
        float_check.set_active(True)  # Enabled by default for text boxes
        content_box.append(float_check)
        
        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(16)
        
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda btn: dialog.close())
        
        insert_button = Gtk.Button(label="Insert")
        insert_button.add_css_class("suggested-action")
        insert_button.connect("clicked", lambda btn: self._on_textbox_dialog_response(
            win, dialog, 
            width_spin.get_value_as_int(),
            height_spin.get_value_as_int(),
            border_spin.get_value_as_int(),
            float_check.get_active()
        ))
        
        button_box.append(cancel_button)
        button_box.append(insert_button)
        content_box.append(button_box)
        
        # Set dialog content and present
        dialog.set_child(content_box)
        dialog.present(win)

    def _on_textbox_dialog_response(self, win, dialog, width, height, border_width, is_floating):
        """Handle response from the text box dialog"""
        dialog.close()
        
        # Create a modified insert_table call with 1 row, 1 column (single cell)
        js_code = f"""
        (function() {{
            // First check if the current selection is inside a table
            const isInsideTable = (function() {{
                const selection = window.getSelection();
                if (!selection.rangeCount) return false;
                
                let node = selection.anchorNode;
                while (node && node !== document.body) {{
                    if (node.tagName === 'TABLE') {{
                        return true;
                    }}
                    node = node.parentNode;
                }}
                return false;
            }})();
            
            // Insert a single-cell table with auto width
            insertTable(1, 1, false, {border_width}, "auto", {str(is_floating).lower()});
            
            // Get the newly created table
            setTimeout(() => {{
                const tables = document.querySelectorAll('table.editor-table');
                const newTable = tables[tables.length - 1] || document.querySelector('table:last-of-type');
                if (newTable) {{
                    // Apply styling specific to text box
                    newTable.classList.add('text-box');
                    
                    // Set specific width and height
                    newTable.style.width = '{width}px';
                    
                    // Set background to transparent
                    newTable.style.backgroundColor = 'transparent';
                    newTable.setAttribute('data-bg-color', 'transparent');
                    
                    // Add min-height to make it more box-like
                    const cell = newTable.querySelector('td');
                    if (cell) {{
                        cell.style.height = '{height}px';
                        cell.style.minHeight = '{height}px';
                        cell.style.padding = '10px';
                        cell.innerHTML = ''; // Clear default "Cell" text
                    }}
                    
                    // Set margins based on container
                    if (isInsideTable) {{
                        // Set all margins to 0 if inside another table
                        newTable.style.margin = '0px';
                        newTable.style.marginTop = '0px';
                        newTable.style.marginRight = '0px';
                        newTable.style.marginBottom = '0px';
                        newTable.style.marginLeft = '0px';
                        
                        // Store margin values as attributes
                        newTable.setAttribute('data-margin-top', '0');
                        newTable.setAttribute('data-margin-right', '0');
                        newTable.setAttribute('data-margin-bottom', '0');
                        newTable.setAttribute('data-margin-left', '0');
                    }}
                    
                    // Set rounded corners
                    newTable.style.borderRadius = '4px';
                    
                    // Set box shadow if it's floating
                    if ({str(is_floating).lower()}) {{
                        newTable.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.15)';
                        
                        // Ensure resize handle is visible and active
                        setTimeout(() => {{
                            // Make sure the table is activated to show handles
                            activateTable(newTable);
                            
                            // Enhance the resize functionality specifically for text boxes
                            const originalResizeTable = window.resizeTable;
                            
                            // Override the resizeTable function temporarily for this operation
                            window.resizeTable = function(e) {{
                                if (!isResizing || !activeTable) return;
                                
                                const deltaX = e.clientX - dragStartX;
                                const deltaY = e.clientY - dragStartY;
                                
                                // Adjust both width and height for text boxes
                                if (activeTable.classList.contains('text-box')) {{
                                    activeTable.style.width = (tableStartX + deltaX) + 'px';
                                    
                                    // Also adjust the cell height for text boxes
                                    const cell = activeTable.querySelector('td');
                                    if (cell) {{
                                        const newHeight = tableStartY + deltaY;
                                        cell.style.height = newHeight + 'px';
                                        cell.style.minHeight = newHeight + 'px';
                                    }}
                                }} else {{
                                    // Original behavior for regular tables
                                    activeTable.style.width = (tableStartX + deltaX) + 'px';
                                }}
                            }};
                            
                            // Modify the startTableResize function to capture height too
                            const originalStartTableResize = window.startTableResize;
                            window.startTableResize = function(e, tableElement) {{
                                e.preventDefault();
                                isResizing = true;
                                activeTable = tableElement;
                                dragStartX = e.clientX;
                                dragStartY = e.clientY;
                                
                                const style = window.getComputedStyle(tableElement);
                                tableStartX = parseInt(style.width) || tableElement.offsetWidth;
                                
                                // Also capture cell height for text boxes
                                if (tableElement.classList.contains('text-box')) {{
                                    const cell = tableElement.querySelector('td');
                                    if (cell) {{
                                        const cellStyle = window.getComputedStyle(cell);
                                        tableStartY = parseInt(cellStyle.height) || cell.offsetHeight;
                                    }} else {{
                                        tableStartY = parseInt(style.height) || tableElement.offsetHeight;
                                    }}
                                }} else {{
                                    tableStartY = parseInt(style.height) || tableElement.offsetHeight;
                                }}
                            }};
                        }}, 100);
                    }}
                }}
            }}, 50);
            
            return true;
        }})();
        """
        self.execute_js(win, js_code)
        
        # Update status message
        if is_floating:
            win.statusbar.set_text("Floating text box inserted")
        else:
            win.statusbar.set_text("Text box inserted")
############### /Text box related methods      
    def on_insert_image_clicked(self, win, btn):
        """Handle insertion of an image inside a table cell"""
        win.statusbar.set_text("Inserting image in table...")
        
        # Create dialog to configure the image table
        dialog = Adw.Dialog()
        dialog.set_title("Insert Image in Table")
        dialog.set_content_width(350)
        
        # Create layout for dialog content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        
        # Keep track of source type
        source_type = {"current": "file"}  # Use a dict to allow modification in nested functions
        
        # Source tabs for file vs URL
        source_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # Create tab buttons
        source_tabs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        source_tabs.add_css_class("linked")
        source_tabs.set_halign(Gtk.Align.CENTER)  # Center-align the tabs
        
        file_tab_btn = Gtk.ToggleButton(label="From File")
        file_tab_btn.set_active(True)  # Start with file tab active
        url_tab_btn = Gtk.ToggleButton(label="From URL")
        
        source_tabs.append(file_tab_btn)
        source_tabs.append(url_tab_btn)
        
        # Create stack for the different content areas
        source_stack = Gtk.Stack()
        source_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        source_stack.set_transition_duration(200)
        
        # FILE TAB CONTENT
        file_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # Image selection button
        image_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        image_label = Gtk.Label(label="Image:")
        image_label.set_halign(Gtk.Align.START)
        image_label.set_hexpand(True)
        
        image_button = Gtk.Button(label="Select Image...")
        image_button.set_hexpand(True)
        
        # Store the selected image path
        image_button.selected_path = None
        
        # Connect click handler for image selection
        image_button.connect("clicked", lambda btn: self._show_image_chooser(win, btn))
        
        image_box.append(image_label)
        image_box.append(image_button)
        file_box.append(image_box)
        
        # URL TAB CONTENT
        url_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # URL entry
        url_entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        url_label = Gtk.Label(label="URL:")
        url_label.set_halign(Gtk.Align.START)
        url_label.set_hexpand(True)
        
        url_entry = Gtk.Entry()
        url_entry.set_placeholder_text("https://example.com/image.jpg")
        url_entry.set_hexpand(True)
        url_entry.set_activates_default(True)  # Allow Enter key to submit
        
        url_entry_box.append(url_label)
        url_entry_box.append(url_entry)
        url_box.append(url_entry_box)
        
        # Add content to stack
        source_stack.add_named(file_box, "file")
        source_stack.add_named(url_box, "url")
        
        # Connect tab buttons to switch stack and update source type
        def on_file_tab_toggled(btn):
            if btn.get_active():
                url_tab_btn.set_active(False)  # Untoggle the other button
                source_stack.set_visible_child_name("file")
                source_type["current"] = "file"
                update_insert_button_state()
            elif not url_tab_btn.get_active():
                # If both are untoggled, re-toggle this one to ensure one is always active
                btn.set_active(True)
        
        def on_url_tab_toggled(btn):
            if btn.get_active():
                file_tab_btn.set_active(False)  # Untoggle the other button
                source_stack.set_visible_child_name("url")
                source_type["current"] = "url"
                update_insert_button_state()
            elif not file_tab_btn.get_active():
                # If both are untoggled, re-toggle this one to ensure one is always active
                btn.set_active(True)
                    
        file_tab_btn.connect("toggled", on_file_tab_toggled)
        url_tab_btn.connect("toggled", on_url_tab_toggled)
        
        # Add tabs and stack to source box
        source_box.append(source_tabs)
        source_box.append(source_stack)
        
        # Add source box to content
        content_box.append(source_box)
        
        # Width input with +/- buttons
        width_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        width_label = Gtk.Label(label="Width (px):")
        width_label.set_halign(Gtk.Align.START)
        width_label.set_hexpand(True)
        
        width_adjustment = Gtk.Adjustment(value=200, lower=50, upper=800, step_increment=10)
        width_spin = Gtk.SpinButton()
        width_spin.set_adjustment(width_adjustment)
        
        # Create a box for the spinner and +/- buttons
        width_spinner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        width_spinner_box.add_css_class("linked")
        
        width_spinner_box.append(width_spin)

        width_box.append(width_label)
        width_box.append(width_spinner_box)
        content_box.append(width_box)
        
        # Border width with +/- buttons
        border_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        border_label = Gtk.Label(label="Border width:")
        border_label.set_halign(Gtk.Align.START)
        border_label.set_hexpand(True)
        
        border_adjustment = Gtk.Adjustment(value=1, lower=0, upper=5, step_increment=1)
        border_spin = Gtk.SpinButton()
        border_spin.set_adjustment(border_adjustment)
        
        # Create a box for the spinner and +/- buttons
        border_spinner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        border_spinner_box.add_css_class("linked")
        
        border_spinner_box.append(border_spin)
        
        border_box.append(border_label)
        border_box.append(border_spinner_box)
        content_box.append(border_box)
        
        # Free-floating option checkbox
        float_check = Gtk.CheckButton(label="Free-floating (text wraps around)")
        float_check.set_active(True)  # Enabled by default
        content_box.append(float_check)
        
        # Caption checkbox
        caption_check = Gtk.CheckButton(label="Add caption")
        caption_check.set_active(True)
        content_box.append(caption_check)
        
        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(16)
        
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda btn: dialog.close())
        
        insert_button = Gtk.Button(label="Insert")
        insert_button.add_css_class("suggested-action")
        insert_button.set_sensitive(False)  # Disabled until image is selected
        
        # Function to update insert button sensitivity
        def update_insert_button_state(*args):
            if source_type["current"] == "file":
                # File tab is active
                insert_button.set_sensitive(image_button.selected_path is not None)
            else:
                # URL tab is active - enable if there's any URL text
                url_text = url_entry.get_text()
                insert_button.set_sensitive(url_text is not None and url_text.strip() != "")
        
        # Connect the insert button - this needs to handle both file and URL sources
        insert_button.connect("clicked", lambda btn: self._on_image_table_response(
            win, dialog, 
            image_button.selected_path if source_type["current"] == "file" else None,
            url_entry.get_text() if source_type["current"] == "url" else None,
            width_spin.get_value_as_int(),
            border_spin.get_value_as_int(),
            float_check.get_active(),
            caption_check.get_active()
        ))
        
        # Add callbacks for updating button state
        image_button.connect("notify::label", update_insert_button_state)
        url_entry.connect("changed", update_insert_button_state)
        
        button_box.append(cancel_button)
        button_box.append(insert_button)
        content_box.append(button_box)
        
        # Set dialog content and present
        dialog.set_child(content_box)
        dialog.present(win)
        
        # Set insert button as default action (can be activated by Enter key)
        dialog.set_default_widget(insert_button)
        
        # Make sure initial state is set correctly
        update_insert_button_state()
        
    def _show_image_chooser(self, win, image_button):
        """Show a file chooser for selecting an image using GTK4 FileDialog"""
        # Create a FileDialog (modern replacement for FileChooserDialog)
        dialog = Gtk.FileDialog()
        dialog.set_title("Select Image")
        
        # Create filter for image files
        image_filter = Gtk.FileFilter()
        image_filter.set_name("Image files")
        image_filter.add_mime_type("image/jpeg")
        image_filter.add_mime_type("image/png")
        image_filter.add_mime_type("image/gif")
        image_filter.add_mime_type("image/svg+xml")
        
        # Create a filter list store
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(image_filter)
        
        # Set the filters to the dialog
        dialog.set_filters(filters)
        
        # Show the open dialog asynchronously
        dialog.open(
            win,
            None,  # No cancellable object
            self._on_image_chooser_response,
            image_button
        )

    def _on_image_chooser_response(self, dialog, result, image_button):
        """Handle the response from the image chooser dialog"""
        try:
            file = dialog.open_finish(result)
            if file:
                # Get the path from the file
                file_path = file.get_path()
                
                # Store the path
                image_button.selected_path = file_path
                
                # Update the button label to show selected file
                import os
                filename = os.path.basename(file_path)
                if len(filename) > 20:
                    filename = filename[:17] + "..."
                image_button.set_label(filename)
        except GLib.Error as error:
            # Handle error (typically user cancellation)
            if error.domain != 'gtk-dialog-error-quark' or error.code != 2:  # Ignore cancel
                print(f"Error selecting image: {error.message}")

    def _on_image_table_response(self, win, dialog, image_path, image_url, width, border_width, is_floating, add_caption):
        """Handle response from the image table dialog"""
        from_url = image_url is not None and image_url.strip() != ""
        from_file = image_path is not None
        
        if not (from_url or from_file):
            dialog.close()
            return
            
        # Initialize variables for image source
        img_src = None
        filename = "image"
        
        # Set filename and prepare image source for JS
        if from_file:
            # Create base64 of the image for local file
            import base64
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Get image mime type
            import mimetypes
            mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
            
            # Image source for JS
            img_src = f"data:{mime_type};base64,{encoded_image}"
            
            # Get image filename for caption
            import os
            filename = os.path.basename(image_path)
        else:
            # For URL, use direct URL as source
            img_src = image_url.strip()
            
            # Extract filename from URL for caption
            import os
            from urllib.parse import urlparse
            parsed_url = urlparse(img_src)
            url_filename = os.path.basename(parsed_url.path)
            if url_filename and "." in url_filename:
                filename = url_filename
        
        dialog.close()
        
        # Insert a table with the image at the current selection point
        js_code = f"""
        (function() {{
            // Determine the current context - where we're inserting
            const selection = window.getSelection();
            if (!selection.rangeCount) return false;
            
            let node = selection.anchorNode;
            let insideTable = false;
            
            // Find if we're inside a table
            while (node && node !== document.body) {{
                if (node.tagName === 'TABLE') {{
                    insideTable = true;
                    break;
                }}
                node = node.parentNode;
            }}
            
            // Insert a single-cell table with auto width
            insertTable(1, 1, false, {border_width}, "auto", {str(is_floating).lower()});
            
            // Get the newly created table
            setTimeout(() => {{
                const tables = document.querySelectorAll('table.editor-table');
                const newTable = tables[tables.length - 1] || document.querySelector('table:last-of-type');
                if (newTable) {{
                    // Apply styling specific to image table
                    newTable.classList.add('image-table');
                    
                    // Set original width and store it as an attribute for later use
                    newTable.style.width = '{width}px';
                    newTable.setAttribute('data-original-width', '{width}');
                    
                    // Set background to transparent
                    newTable.style.backgroundColor = 'transparent';
                    newTable.setAttribute('data-bg-color', 'transparent');
                    
                    // Get the cell
                    const cell = newTable.querySelector('td');
                    if (cell) {{
                        // Set padding
                        cell.style.padding = '0';
                        
                        // Create a container div to hold the image and prevent dragging
                        const containerDiv = document.createElement('div');
                        containerDiv.style.width = '100%';
                        containerDiv.style.height = 'auto';
                        containerDiv.style.overflow = 'hidden'; // Prevent overflow
                        containerDiv.style.position = 'relative'; // For absolute positioning
                        
                        // Create the image HTML
                        const img = document.createElement('img');
                        img.src = '{img_src}';
                        img.style.maxWidth = '100%';
                        img.style.display = 'block';
                        img.style.width = '100%';
                        img.style.pointerEvents = 'none'; // Prevent direct interaction with the image
                        img.setAttribute('data-embedded', '{str(from_file).lower()}');
                        img.setAttribute('alt', '{filename}');
                        img.setAttribute('draggable', 'false'); // Prevent dragging
                        
                        // Add the image to the container
                        containerDiv.appendChild(img);
                        
                        // Clear the cell and add the container
                        cell.innerHTML = '';
                        cell.appendChild(containerDiv);
                        
                        // If caption is enabled, add it after the container
                        if ({str(add_caption).lower()}) {{
                            const captionDiv = document.createElement('div');
                            captionDiv.style.fontSize = '0.9em';
                            captionDiv.style.color = '#555';
                            captionDiv.style.marginTop = '5px';
                            captionDiv.style.textAlign = 'center';
                            captionDiv.textContent = '{filename}';
                            captionDiv.setAttribute('contenteditable', 'true'); // Make caption editable
                            
                            cell.appendChild(captionDiv);
                        }}
                        
                        // Add custom event handlers to prevent image dragging
                        cell.addEventListener('dragstart', function(e) {{
                            // Prevent all drag operations on this cell
                            e.preventDefault();
                            return false;
                        }}, true);
                        
                        // Prevent selection events inside the cell except for the caption
                        cell.addEventListener('mousedown', function(e) {{
                            // Allow selection only on caption
                            if (!e.target.hasAttribute('contenteditable')) {{
                                e.preventDefault();
                            }}
                        }}, true);
                    }}
                    
                    // Set margins based on container
                    if (insideTable) {{
                        // Set all margins to 0 if inside another table
                        newTable.style.margin = '0px';
                        newTable.style.marginTop = '0px';
                        newTable.style.marginRight = '0px';
                        newTable.style.marginBottom = '0px';
                        newTable.style.marginLeft = '0px';
                        
                        // Store margin values as attributes
                        newTable.setAttribute('data-margin-top', '0');
                        newTable.setAttribute('data-margin-right', '0');
                        newTable.setAttribute('data-margin-bottom', '0');
                        newTable.setAttribute('data-margin-left', '0');
                    }}
                    
                    // Set rounded corners
                    newTable.style.borderRadius = '4px';
                    
                    // Activate the table to show handles
                    activateTable(newTable);
                    
                    // Override resize to maintain aspect ratio
                    const originalResizeTable = window.resizeTable;
                    window.resizeTable = function(e) {{
                        if (!isResizing || !activeTable) return;
                        
                        const deltaX = e.clientX - dragStartX;
                        
                        if (activeTable.classList.contains('image-table')) {{
                            // Only adjust width for image tables - height will follow with aspect ratio
                            const newWidth = tableStartX + deltaX;
                            activeTable.style.width = newWidth + 'px';
                            // Update the original width attribute so alignment changes remember this size
                            activeTable.setAttribute('data-original-width', newWidth);
                        }} else {{
                            // Original behavior for regular tables
                            activeTable.style.width = (tableStartX + deltaX) + 'px';
                        }}
                    }};
                    
                    // Override the setTableAlignment function to maintain image size
                    const originalSetTableAlignment = window.setTableAlignment;
                    window.setTableAlignment = function(alignClass) {{
                        if (!activeTable) return;
                        
                        // Check if it's an image table
                        if (activeTable.classList.contains('image-table')) {{
                            // Get the original width
                            const originalWidth = activeTable.getAttribute('data-original-width') || '{width}';
                            
                            // Remove all alignment classes
                            activeTable.classList.remove('left-align', 'right-align', 'center-align', 'no-wrap', 'floating-table');
                            
                            // Add the requested alignment class
                            activeTable.classList.add(alignClass);
                            
                            // Reset positioning if it was previously floating
                            if (activeTable.style.position === 'absolute') {{
                                activeTable.style.position = 'relative';
                                activeTable.style.top = '';
                                activeTable.style.left = '';
                                activeTable.style.zIndex = '';
                            }}
                            
                            // Set width based on alignment, preserving original width where appropriate
                            if (alignClass === 'no-wrap') {{
                                activeTable.style.width = '100%';
                            }} else {{
                                // Use the original width for other alignments
                                activeTable.style.width = originalWidth + 'px';
                            }}
                        }} else {{
                            // Use original function for non-image tables
                            return originalSetTableAlignment(alignClass);
                        }}
                        
                        try {{
                            window.webkit.messageHandlers.contentChanged.postMessage('changed');
                        }} catch(e) {{
                            console.log("Could not notify about content change:", e);
                        }}
                    }};
                    
                    // Override the document-level selection to prevent image selection
                    const originalSelectionHandler = document.onselectionchange;
                    document.onselectionchange = function(e) {{
                        const selection = window.getSelection();
                        if (selection.rangeCount) {{
                            const range = selection.getRangeAt(0);
                            // If the selection is in the image table but not in an editable caption
                            if (newTable.contains(range.commonAncestorContainer)) {{
                                let node = range.commonAncestorContainer;
                                while (node && node !== document.body) {{
                                    if (node.hasAttribute && node.hasAttribute('contenteditable') && 
                                        node.getAttribute('contenteditable') === 'true') {{
                                        // Selection in editable caption is fine
                                        return originalSelectionHandler ? originalSelectionHandler(e) : true;
                                    }}
                                    node = node.parentNode;
                                }}
                                
                                // If we're here, we're selecting in the table but not in an editable element
                                // Check if we're selecting the img specifically
                                if (range.commonAncestorContainer.nodeName === 'IMG' || 
                                    (range.commonAncestorContainer.childNodes && 
                                     Array.from(range.commonAncestorContainer.childNodes).some(n => n.nodeName === 'IMG'))) {{
                                    // Prevent this selection
                                    selection.removeAllRanges();
                                    return false;
                                }}
                            }}
                        }}
                        return originalSelectionHandler ? originalSelectionHandler(e) : true;
                    }};
                }}
            }}, 50);
            
            return true;
        }})();
        """
        self.execute_js(win, js_code)
        
        # Update status message
        win.statusbar.set_text("Image inserted in table")


############### /Text box related methods   

########### insert link   
    def insert_link_js(self):
        """JavaScript for insert link and related functionality"""
        return """
        // Function to insert a link at the current cursor position
        function insertLink(url, text, title) {
            // Ensure we have valid parameters
            url = url || '#';
            text = text || url;
            title = title || '';
            
            // Create link HTML
            let linkHTML = '<a href="' + url + '"';
            
            // Add title attribute if provided
            if (title && title.trim() !== '') {
                linkHTML += ' title="' + title + '"';
            }
            
            // Add target attribute for external links
            if (url.startsWith('http://') || url.startsWith('https://')) {
                linkHTML += ' target="_blank" rel="noopener noreferrer"';
            }
            
            // Complete the link
            linkHTML += '>' + text + '</a>';
            
            // Get current selection
            const selection = window.getSelection();
            
            // If there's a selection, we'll use it as the link text
            if (selection.rangeCount > 0 && !selection.isCollapsed) {
                // Get the selected text
                const selectedText = selection.toString();
                
                // Use the selected text instead of the provided text
                if (selectedText.trim() !== '') {
                    linkHTML = '<a href="' + url + '"';
                    
                    if (title && title.trim() !== '') {
                        linkHTML += ' title="' + title + '"';
                    }
                    
                    if (url.startsWith('http://') || url.startsWith('https://')) {
                        linkHTML += ' target="_blank" rel="noopener noreferrer"';
                    }
                    
                    linkHTML += '>' + selectedText + '</a>';
                    
                    // Delete the selected text
                    document.execCommand('delete');
                }
            }
            
            // Insert the link
            document.execCommand('insertHTML', false, linkHTML);
            
            // Notify that content changed
            try {
                window.webkit.messageHandlers.contentChanged.postMessage('changed');
            } catch(e) {
                console.log("Could not notify about content change:", e);
            }
            
            return true;
        }
        
        // Function to check if the cursor is inside or near a link
        function getLinkAtCursor() {
            // Get current selection
            const selection = window.getSelection();
            if (!selection.rangeCount) return null;
            
            let node = selection.anchorNode;
            
            // If we're in a text node, get its parent
            if (node.nodeType === 3) {
                node = node.parentNode;
            }
            
            // Check if we're inside an A tag
            if (node.tagName === 'A') {
                return {
                    url: node.href || '',
                    text: node.textContent || '',
                    title: node.title || '',
                    element: node
                };
            }
            
            // Check if we're inside a child of an A tag
            while (node && node !== document.body) {
                if (node.tagName === 'A') {
                    return {
                        url: node.href || '',
                        text: node.textContent || '',
                        title: node.title || '',
                        element: node
                    };
                }
                node = node.parentNode;
            }
            
            // Not inside a link
            return null;
        }
        
        // Function to update a link
        function updateLink(element, url, text, title) {
            if (!element || element.tagName !== 'A') {
                // Try to find the link element in the document
                if (typeof element === 'string') {
                    // If element is a URL string, try to find by href
                    const links = document.querySelectorAll('a');
                    for (let i = 0; i < links.length; i++) {
                        if (links[i].href === element || 
                            links[i].getAttribute('href') === element) {
                            element = links[i];
                            break;
                        }
                    }
                } else if (element && element.url) {
                    // If element is a link info object
                    const links = document.querySelectorAll('a');
                    for (let i = 0; i < links.length; i++) {
                        if (links[i].href === element.url || 
                            links[i].getAttribute('href') === element.url) {
                            element = links[i];
                            break;
                        }
                    }
                }
                
                // If we still don't have a valid element, return false
                if (!element || element.tagName !== 'A') {
                    return false;
                }
            }
            
            // Update href
            element.href = url || '#';
            
            // Update text content if provided
            if (text && text.trim() !== '') {
                element.textContent = text;
            }
            
            // Update title
            if (title && title.trim() !== '') {
                element.title = title;
            } else {
                element.removeAttribute('title');
            }
            
            // Update target for external links
            if (url.startsWith('http://') || url.startsWith('https://')) {
                element.target = '_blank';
                element.rel = 'noopener noreferrer';
            } else {
                element.removeAttribute('target');
                element.removeAttribute('rel');
            }
            
            // Notify that content changed
            try {
                window.webkit.messageHandlers.contentChanged.postMessage('changed');
            } catch(e) {
                console.log("Could not notify about content change:", e);
            }
            
            return true;
        }
        
        // Function to remove a link (keeping the text)
        function removeLink(element) {
            // First try to find the link element if we're given a URL or link info
            if (!element || element.tagName !== 'A') {
                // If element is a URL string, try to find by href
                if (typeof element === 'string') {
                    const links = document.querySelectorAll('a');
                    for (let i = 0; i < links.length; i++) {
                        if (links[i].href === element || 
                            links[i].getAttribute('href') === element) {
                            element = links[i];
                            break;
                        }
                    }
                } else if (element && element.url) {
                    // If element is a link info object
                    const links = document.querySelectorAll('a');
                    for (let i = 0; i < links.length; i++) {
                        if (links[i].href === element.url || 
                            links[i].getAttribute('href') === element.url) {
                            element = links[i];
                            break;
                        }
                    }
                }
                
                // If we still don't have a valid element, return false
                if (!element || element.tagName !== 'A') {
                    return false;
                }
            }
            
            // Get the text content
            const text = element.textContent;
            
            // Create a text node to replace the link
            const textNode = document.createTextNode(text);
            
            // Replace the link with its text content
            element.parentNode.replaceChild(textNode, element);
            
            // Notify that content changed
            try {
                window.webkit.messageHandlers.contentChanged.postMessage('changed');
            } catch(e) {
                console.log("Could not notify about content change:", e);
            }
            
            return true;
        }
        """

    def on_insert_link_clicked(self, win, btn):
        """Show a dialog with URL and Text for link insertion"""
        # First, check if there's already a link at the cursor position
        js_code = """
        (function() {
            const linkInfo = getLinkAtCursor();
            return JSON.stringify(linkInfo);
        })();
        """
        
        win.webview.evaluate_javascript(
            js_code,
            -1, None, None, None,
            lambda webview, result, data: self._show_link_dialog(win, webview, result),
            None
        )
        win.webview.grab_focus()
        
    def _show_link_dialog(self, win, webview, result):
        """Show the link dialog with current link info if available"""
        try:
            js_result = webview.evaluate_javascript_finish(result)
            link_info = None
            
            if js_result:
                # Try different ways to get the string result based on WebKit version
                if hasattr(js_result, 'get_js_value'):
                    result_str = js_result.get_js_value().to_string()
                elif hasattr(js_result, 'to_string'):
                    result_str = js_result.to_string() 
                else:
                    result_str = str(js_result)
                    
                # Check if we have valid JSON (not "null")
                if result_str and result_str != "null":
                    import json
                    link_info = json.loads(result_str)
            
            # Create a dialog to configure the link
            dialog = Adw.Dialog()
            dialog.set_title("Insert Link" if not link_info else "Edit Link")
            dialog.set_content_width(400)
            
            # Create content box
            content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
            content_box.set_margin_top(24)
            content_box.set_margin_bottom(24)
            content_box.set_margin_start(24)
            content_box.set_margin_end(24)
            
            # URL input
            url_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            url_label = Gtk.Label(label="URL:")
            url_label.set_halign(Gtk.Align.START)
            url_label.set_hexpand(True)
            url_label.set_width_chars(8)
            
            url_entry = Gtk.Entry()
            url_entry.set_placeholder_text("https://example.com")
            url_entry.set_hexpand(True)
            
            # Set current URL if editing
            if link_info and 'url' in link_info:
                url_entry.set_text(link_info['url'])
            
            url_box.append(url_label)
            url_box.append(url_entry)
            content_box.append(url_box)
            
            # Text input
            text_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            text_label = Gtk.Label(label="Text:")
            text_label.set_halign(Gtk.Align.START)
            text_label.set_hexpand(True)
            text_label.set_width_chars(8)
            
            text_entry = Gtk.Entry()
            text_entry.set_placeholder_text("Link text")
            text_entry.set_hexpand(True)
            
            # Set current text if editing
            if link_info and 'text' in link_info:
                text_entry.set_text(link_info['text'])
            
            text_box.append(text_label)
            text_box.append(text_entry)
            content_box.append(text_box)
            
            # Title input (optional)
            title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            title_label = Gtk.Label(label="Title:")
            title_label.set_halign(Gtk.Align.START)
            title_label.set_hexpand(True)
            title_label.set_width_chars(8)
            
            title_entry = Gtk.Entry()
            title_entry.set_placeholder_text("Tooltip text (optional)")
            title_entry.set_hexpand(True)
            
            # Set current title if editing
            if link_info and 'title' in link_info:
                title_entry.set_text(link_info['title'])
            
            title_box.append(title_label)
            title_box.append(title_entry)
            content_box.append(title_box)
            
            # Button box
            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            button_box.set_halign(Gtk.Align.END)
            button_box.set_margin_top(16)
            
            # Add Remove button if editing
            if link_info:
                remove_button = Gtk.Button(label="Remove Link")
                remove_button.add_css_class("destructive-action")
                remove_button.connect("clicked", lambda btn: self._on_remove_link(win, dialog, link_info))
                button_box.append(remove_button)
                
                # Add spacer
                spacer = Gtk.Box()
                spacer.set_hexpand(True)
                button_box.append(spacer)
            
            # Cancel button
            cancel_button = Gtk.Button(label="Cancel")
            cancel_button.connect("clicked", lambda btn: dialog.close())
            
            # Insert/Update button
            action_button = Gtk.Button(label="Insert" if not link_info else "Update")
            action_button.add_css_class("suggested-action")
            action_button.connect("clicked", lambda btn: self._on_link_dialog_response(
                win, dialog, 
                url_entry.get_text(),
                text_entry.get_text(),
                title_entry.get_text(),
                link_info
            ))
            
            button_box.append(cancel_button)
            button_box.append(action_button)
            content_box.append(button_box)
            
            # Set dialog content and present
            dialog.set_child(content_box)
            dialog.present(win)
            
        except Exception as e:
            print(f"Error showing link dialog: {e}")
            win.statusbar.set_text("Error showing link dialog")

    def _on_link_dialog_response(self, win, dialog, url, text, title, link_info):
        """Handle the response from the link dialog"""
        dialog.close()
        
        # Validate URL (add https:// if missing)
        if url and not url.startswith("http://") and not url.startswith("https://") and url != "#":
            url = "https://" + url
        
        # If no URL is provided, use '#' as a placeholder
        if not url:
            url = "#"
        
        # If no text is provided, use the URL
        if not text:
            text = url
        
        # Escape quotes and special characters in URL, text and title
        import json
        url = json.dumps(url)[1:-1]  # Use JSON to properly escape
        text = json.dumps(text)[1:-1]
        title = json.dumps(title)[1:-1]
        
        if link_info:
            # Update existing link
            js_code = f"""
            (function() {{
                // Pass the link info object to find and update the link
                return updateLink({json.dumps(link_info)}, "{url}", "{text}", "{title}");
            }})();
            """
            self.execute_js(win, js_code)
            win.statusbar.set_text("Link updated")
        else:
            # Insert new link
            js_code = f"""
            (function() {{
                return insertLink("{url}", "{text}", "{title}");
            }})();
            """
            self.execute_js(win, js_code)
            win.statusbar.set_text("Link inserted")
        win.webview.grab_focus()
        
    def _on_remove_link(self, win, dialog, link_info):
        """Remove a link while keeping its text content"""
        dialog.close()
        
        # Use JSON to properly serialize the link_info object
        import json
        js_code = f"""
        (function() {{
            // Pass the link info object to find and remove the link
            return removeLink({json.dumps(link_info)});
        }})();
        """
        self.execute_js(win, js_code)
        win.statusbar.set_text("Link removed")
######################### /insert text #
    def on_insert_datetime_clicked(self, win, btn):
        """Show enhanced dialog to select date/time format with three-column layout in a scrolled window"""
        dialog = Adw.Dialog()
        dialog.set_title("Insert Date Time")
        
        # Create main content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        
        # Get current date and time for preview
        import datetime
        now = datetime.datetime.now()
        
        # Create a scrolled window to contain the grid
        scrolled_window = Gtk.ScrolledWindow()
        # Set dimensions to show at least 4 items vertically without scrolling
        scrolled_window.set_min_content_height(300)
        # Width to ensure all 3 columns are clearly visible
        scrolled_window.set_min_content_width(600)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        
        # Create a grid layout for the three columns
        format_grid = Gtk.Grid()
        format_grid.set_row_spacing(6)
        format_grid.set_column_spacing(6)
        format_grid.set_column_homogeneous(True)
        format_grid.set_margin_top(6)
        format_grid.set_margin_bottom(6)
        format_grid.set_margin_start(6)
        format_grid.set_margin_end(6)
        
        # Create headers for each column
        date_header = Gtk.Label()
        date_header.set_markup("<b>Date</b>")
        date_header.set_halign(Gtk.Align.CENTER)
        date_header.add_css_class("title-4")
        date_header.set_margin_bottom(6)
        
        time_header = Gtk.Label()
        time_header.set_markup("<b>Time</b>")
        time_header.set_halign(Gtk.Align.CENTER)
        time_header.add_css_class("title-4")
        time_header.set_margin_bottom(6)
        
        datetime_header = Gtk.Label()
        datetime_header.set_markup("<b>Date &amp; Time</b>")
        datetime_header.set_halign(Gtk.Align.CENTER)
        datetime_header.add_css_class("title-4")
        datetime_header.set_margin_bottom(6)
        
        # Add headers to the grid
        format_grid.attach(date_header, 0, 0, 1, 1)
        format_grid.attach(time_header, 1, 0, 1, 1)
        format_grid.attach(datetime_header, 2, 0, 1, 1)
        
        # Define format options
        date_formats = [
            {"name": "Short", "format": now.strftime("%m/%d/%Y"), "type": "date_short"},
            {"name": "Medium", "format": now.strftime("%b %d, %Y"), "type": "date_medium"},
            {"name": "Long", "format": now.strftime("%B %d, %Y"), "type": "date_long"},
            {"name": "Full", "format": now.strftime("%A, %B %d, %Y"), "type": "date_full"},
            {"name": "ISO", "format": now.strftime("%Y-%m-%d"), "type": "date_iso"},
            {"name": "European", "format": now.strftime("%d/%m/%Y"), "type": "date_euro"},
        ]
        
        time_formats = [
            {"name": "12-hour", "format": now.strftime("%I:%M %p"), "type": "time_12"},
            {"name": "24-hour", "format": now.strftime("%H:%M"), "type": "time_24"},
            {"name": "12h with seconds", "format": now.strftime("%I:%M:%S %p"), "type": "time_12_sec"},
            {"name": "24h with seconds", "format": now.strftime("%H:%M:%S"), "type": "time_24_sec"},
        ]
        
        datetime_formats = [
            {"name": "Short", "format": now.strftime("%m/%d/%Y %I:%M %p"), "type": "datetime_short"},
            {"name": "Medium", "format": now.strftime("%b %d, %Y %H:%M"), "type": "datetime_medium"},
            {"name": "Long", "format": now.strftime("%B %d, %Y at %I:%M %p"), "type": "datetime_long"},
            {"name": "ISO", "format": now.strftime("%Y-%m-%d %H:%M:%S"), "type": "datetime_iso"},
            {"name": "RFC", "format": now.strftime("%a, %d %b %Y %H:%M:%S"), "type": "datetime_rfc"},
        ]
        
        # Store all format buttons to access the selected one later
        win.format_buttons = []
        
        # Create Date format buttons (column 0)
        for i, fmt in enumerate(date_formats):
            button = Gtk.ToggleButton(label=fmt["name"])
            button.format_type = fmt["type"]
            button.format_value = fmt["format"]
            
            # Add tooltip showing the format preview
            button.set_tooltip_text(fmt["format"])
            
            # Add to button group for radio button behavior
            if win.format_buttons:
                button.set_group(win.format_buttons[0])
            
            win.format_buttons.append(button)
            
            # Create a box to arrange the button and preview
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            box.set_margin_top(2)
            box.set_margin_bottom(2)
            
            # Make button wider to better display text
            button.set_hexpand(True)
            button.set_size_request(-1, 36)  # Width: default, Height: 36px
            box.append(button)
            
            # Add small preview label
            preview = Gtk.Label(label=fmt["format"])
            preview.add_css_class("caption")
            preview.add_css_class("dim-label")
            preview.set_margin_top(2)
            box.append(preview)
            
            # Add to grid
            format_grid.attach(box, 0, i+1, 1, 1)
        
        # Create Time format buttons (column 1)
        for i, fmt in enumerate(time_formats):
            button = Gtk.ToggleButton(label=fmt["name"])
            button.format_type = fmt["type"]
            button.format_value = fmt["format"]
            
            # Add tooltip
            button.set_tooltip_text(fmt["format"])
            
            # Add to button group
            button.set_group(win.format_buttons[0])
            win.format_buttons.append(button)
            
            # Create a box to arrange the button and preview
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            box.set_margin_top(2)
            box.set_margin_bottom(2)
            
            # Make button wider to better display text
            button.set_hexpand(True)
            button.set_size_request(-1, 36)  # Width: default, Height: 36px
            box.append(button)
            
            # Add small preview label
            preview = Gtk.Label(label=fmt["format"])
            preview.add_css_class("caption")
            preview.add_css_class("dim-label")
            preview.set_margin_top(2)
            box.append(preview)
            
            # Add to grid
            format_grid.attach(box, 1, i+1, 1, 1)
        
        # Create Date & Time format buttons (column 2)
        for i, fmt in enumerate(datetime_formats):
            button = Gtk.ToggleButton(label=fmt["name"])
            button.format_type = fmt["type"]
            button.format_value = fmt["format"]
            
            # Add tooltip
            button.set_tooltip_text(fmt["format"])
            
            # Add to button group
            button.set_group(win.format_buttons[0])
            win.format_buttons.append(button)
            
            # Create a box to arrange the button and preview
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            box.set_margin_top(2)
            box.set_margin_bottom(2)
            
            # Make button wider to better display text
            button.set_hexpand(True)
            button.set_size_request(-1, 36)  # Width: default, Height: 36px
            box.append(button)
            
            # Add small preview label
            preview = Gtk.Label(label=fmt["format"])
            preview.add_css_class("caption")
            preview.add_css_class("dim-label")
            preview.set_margin_top(2)
            box.append(preview)
            
            # Add to grid
            format_grid.attach(box, 2, i+1, 1, 1)
        
        # Add grid to scrolled window
        scrolled_window.set_child(format_grid)
        
        # Add scrolled window to content box
        content_box.append(scrolled_window)
        
        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(4)
        
        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda btn: dialog.close())
        button_box.append(cancel_button)
        
        # Insert button
        insert_button = Gtk.Button(label="Insert")
        insert_button.add_css_class("suggested-action")
        insert_button.connect("clicked", lambda btn: self.insert_selected_datetime_format(win, dialog))
        button_box.append(insert_button)
        
        content_box.append(button_box)
        
        # Create a clamp to hold the content
        clamp = Adw.Clamp()
        clamp.set_child(content_box)
        
        # Set up the dialog content using a box
        dialog_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        dialog_content.append(clamp)
        
        # Connect the content to the dialog
        dialog.connect("closed", lambda d: None)  # Ensure proper cleanup
        dialog.set_child(dialog_content)
        
        # Present the dialog
        dialog.present(win)
        
        # Make first button active by default
        if win.format_buttons:
            win.format_buttons[0].set_active(True)

    def insert_selected_datetime_format(self, win, dialog):
        """Insert date/time with the selected format"""
        # Check if any format button is selected
        selected_button = None
        for button in win.format_buttons:
            if button.get_active():
                selected_button = button
                break
        
        if selected_button:
            # Get the pre-formatted value directly from the button
            formatted_date = selected_button.format_value
            
            # Insert the formatted date at the current cursor position
            js_code = f"""
            (function() {{
                document.execCommand('insertText', false, `{formatted_date}`);
                return true;
            }})();
            """
            win.webview.evaluate_javascript(js_code, -1, None, None, None, None, None)
            win.statusbar.set_text(f"Inserted {selected_button.format_type} format")
            dialog.close()
        else:
            # No selection - show a message
            self.show_error_dialog(win, "Please select a date/time format")

        win.webview.grab_focus()
############################
########### ltr rtl direction
    def rtl_toggle_js(self):
        """JavaScript for RTL/LTR toggling"""
        return """
        // Function to toggle right-to-left mode
        function toggleRTL() {
            const editor = document.getElementById('editor');
            if (!editor) return false;
            
            // Get current direction
            const currentDir = editor.dir || 'ltr';
            
            // Toggle direction
            const newDir = currentDir === 'ltr' ? 'rtl' : 'ltr';
            editor.dir = newDir;
            
            // Also update text-align based on direction for better appearance
            if (newDir === 'rtl') {
                editor.style.textAlign = 'right';
            } else {
                editor.style.textAlign = 'left';
            }
            
            // Return the new direction state for the UI to update
            return newDir === 'rtl';
        }
        
        // Function to check current RTL state
        function isRTL() {
            const editor = document.getElementById('editor');
            if (!editor) return false;
            
            return editor.dir === 'rtl';
        }
        """

    def on_rtl_toggled(self, win, button):
        """Handle RTL button toggle"""
        # Update button icon based on state
        if button.get_active():
            button.set_icon_name("format-text-direction-rtl-symbolic")
        else:
            button.set_icon_name("format-text-direction-ltr-symbolic")
        
        # Execute JavaScript to toggle RTL mode
        js_code = "toggleRTL();"
        win.webview.evaluate_javascript(
            js_code, 
            -1, None, None, None, 
            lambda webview, result, data: self.on_rtl_toggled_result(win, webview, result, button),
            None
        )

    def on_rtl_toggled_result(self, win, webview, result, button):
        """Handle result of RTL toggle"""
        try:
            js_result = webview.evaluate_javascript_finish(result)
            if js_result:
                # Extract boolean value from result based on WebKit version
                is_rtl = False
                if hasattr(js_result, 'get_js_value'):
                    is_rtl = js_result.get_js_value().to_boolean()
                elif hasattr(js_result, 'to_boolean'):
                    is_rtl = js_result.to_boolean()
                else:
                    # Try to convert string result to boolean
                    result_str = str(js_result).lower()
                    is_rtl = result_str == 'true'
                
                # Make sure button state matches the actual RTL state
                if button.get_active() != is_rtl:
                    button.set_active(is_rtl)
                
                # Update status message
                if is_rtl:
                    win.statusbar.set_text("Right-to-left mode enabled")
                else:
                    win.statusbar.set_text("Left-to-right mode enabled")
        except Exception as e:
            print(f"Error toggling RTL: {e}")
            win.statusbar.set_text(f"Error toggling text direction: {e}")

    def initialize_rtl_state(self, win):
        """Check the current RTL state when editor is loaded"""
        js_code = "isRTL();"
        win.webview.evaluate_javascript(
            js_code,
            -1, None, None, None,
            lambda webview, result, data: self._update_rtl_button(win, webview, result),
            None
        )

    def _update_rtl_button(self, win, webview, result):
        """Update the RTL button state based on editor's current direction"""
        try:
            js_result = webview.evaluate_javascript_finish(result)
            if js_result:
                # Extract boolean value from result
                is_rtl = False
                if hasattr(js_result, 'get_js_value'):
                    is_rtl = js_result.get_js_value().to_boolean()
                elif hasattr(js_result, 'to_boolean'):
                    is_rtl = js_result.to_boolean()
                else:
                    # Try to convert string result to boolean
                    result_str = str(js_result).lower()
                    is_rtl = result_str == 'true'
                
                # Update button state
                win.rtl_button.set_active(is_rtl)
                # Set correct icon
                win.rtl_button.set_icon_name(
                    "text-direction-rtl-symbolic" if is_rtl else "text-direction-ltr-symbolic"
                )
        except Exception as e:
            print(f"Error initializing RTL state: {e}")
########### /ltr rtl direction

    def on_wordart_clicked(self, win, btn):
        """Show dialog to select Word Art style"""
        dialog = Adw.Dialog()
        dialog.set_title("Insert Word Art")
        dialog.set_content_width(500)
        
        # Create main content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        
        # Text entry for Word Art content
        text_label = Gtk.Label(label="Text:")
        text_label.set_halign(Gtk.Align.START)
        text_label.set_margin_bottom(6)
        content_box.append(text_label)
        
        text_entry = Gtk.Entry()
        text_entry.set_placeholder_text("Enter text for Word Art")
        text_entry.set_margin_bottom(12)
        content_box.append(text_entry)
        
        # Style selection grid
        styles_label = Gtk.Label(label="Select a style:")
        styles_label.set_halign(Gtk.Align.START)
        styles_label.set_margin_bottom(6)
        content_box.append(styles_label)
        
        # Create a scrolled window to contain the style grid
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_min_content_height(300)
        scrolled_window.set_vexpand(True)
        
        # Create a grid for style options
        styles_grid = Gtk.Grid()
        styles_grid.set_row_spacing(12)
        styles_grid.set_column_spacing(12)
        styles_grid.set_row_homogeneous(True)
        styles_grid.set_column_homogeneous(True)
        
        # Define Word Art styles
        word_art_styles = [
            {"id": "shadow", "name": "Shadow", "preview": "Shadow"},
            {"id": "outline", "name": "Outline", "preview": "Outline"},
            {"id": "inset", "name": "Inset", "preview": "Inset"},
            {"id": "neon", "name": "Neon Glow", "preview": "Neon"},
            {"id": "retro", "name": "Retro", "preview": "Retro"},
            {"id": "emboss", "name": "Embossed", "preview": "Emboss"},
            {"id": "gradient", "name": "Gradient", "preview": "Gradient"},
            {"id": "fire", "name": "Fire", "preview": "Fire"},
            {"id": "comic", "name": "Comic", "preview": "Comic"},
            {"id": "metallic", "name": "Metallic", "preview": "Metal"},
            {"id": "3d", "name": "3D", "preview": "3D Text"},
            {"id": "glitch", "name": "Glitch", "preview": "Glitch"},
        ]
        
        # Generate CSS styles for previews - FIXED VERSION TO AVOID GTK WARNINGS
        styles_css = """
        .wordart-shadow { 
            text-shadow: 4px 4px 8px rgba(0,0,0,0.5); 
            font-weight: bold; 
            font-size: 18px; 
        }
        .wordart-outline { 
            color: white; 
            text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
            font-weight: bold; 
            font-size: 18px; 
        }
        .wordart-inset { 
            background-color: #666; 
            color: #aaa;
            text-shadow: 2px 2px 3px rgba(255,255,255,0.5);
            font-weight: bold; 
            font-size: 18px; 
        }
        .wordart-neon { 
            color: #fff;
            text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px #0073e6, 0 0 20px #0073e6;
            font-weight: bold; 
            font-size: 18px; 
        }
        .wordart-retro { 
            color: #fc0; 
            text-shadow: 2px 2px 0px #f00;
            font-family: monospace;
            font-weight: bold; 
            font-size: 18px;
        }
        .wordart-emboss { 
            color: #555;
            text-shadow: -1px -1px 1px #000, 1px 1px 1px #fff;
            font-weight: bold; 
            font-size: 18px; 
        }
        .wordart-gradient { 
            /* Use solid color for preview instead of gradient with background-clip */
            color: #e52e71;
            font-weight: bold; 
            font-size: 18px; 
        }
        .wordart-fire { 
            /* Use solid color for preview instead of gradient with background-clip */
            color: #ff5500;
            font-weight: bold; 
            font-size: 18px; 
        }
        .wordart-comic { 
            color: #fd0;
            text-shadow: -3px 0 4px #000;
            font-family: fantasy, 'Comic Sans MS', cursive;
            font-weight: bold;
            font-size: 18px;
        }
        .wordart-metallic { 
            /* Use solid color for preview instead of gradient with background-clip */
            color: #a0a0a0;
            text-shadow: 2px 2px 3px rgba(255,255,255,0.5);
            font-weight: bold; 
            font-size: 18px; 
        }
        .wordart-3d { 
            color: #5e17eb;
            text-shadow: 0px 1px 0px #c5bce4,
                       0px 2px 0px #a197c0,
                       0px 3px 0px #7c738e,
                       0px 4px 0px #58505f,
                       0px 5px 10px rgba(0, 0, 0, 0.6);
            font-weight: bold; 
            font-size: 18px; 
        }
        .wordart-glitch {
            color: #00fffc;
            text-shadow: 2px 0 #ff00c1, -2px 0 #fffc00;
            font-weight: bold; 
            font-size: 18px;
        }
        """
        
        # Apply CSS to the application
        provider = Gtk.CssProvider()
        provider.load_from_data(styles_css.encode())
        
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), 
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Store the selected style
        win.selected_wordart_style = None
        
        # Create a toggle button group for styles
        style_buttons = []
        
        # Add styles to the grid
        for i, style in enumerate(word_art_styles):
            row = i // 3
            col = i % 3
            
            # Create a frame for the style
            frame = Gtk.Frame()
            frame.set_margin_top(6)
            frame.set_margin_bottom(6)
            frame.set_margin_start(6)
            frame.set_margin_end(6)
            
            # Create a box for the style preview
            style_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            style_box.set_margin_top(12)
            style_box.set_margin_bottom(12)
            style_box.set_margin_start(12)
            style_box.set_margin_end(12)
            
            # Preview label with styling
            preview = Gtk.Label(label=style["preview"])
            preview.add_css_class(f"wordart-{style['id']}")
            preview.set_halign(Gtk.Align.CENTER)
            preview.set_margin_bottom(6)
            
            # Style name
            name_label = Gtk.Label(label=style["name"])
            name_label.set_halign(Gtk.Align.CENTER)
            
            # Toggle button for selection
            select_button = Gtk.ToggleButton(label="Select")
            select_button.style_id = style["id"]
            
            # Add to button group for radio behavior
            if style_buttons:
                select_button.set_group(style_buttons[0])
            style_buttons.append(select_button)
            
            # Add to box
            style_box.append(preview)
            style_box.append(name_label)
            style_box.append(select_button)
            
            # Add to frame
            frame.set_child(style_box)
            
            # Add to grid
            styles_grid.attach(frame, col, row, 1, 1)
        
        # Add the grid to the scrolled window
        scrolled_window.set_child(styles_grid)
        content_box.append(scrolled_window)
        
        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(16)
        
        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda btn: dialog.close())
        button_box.append(cancel_button)
        
        # Insert button
        insert_button = Gtk.Button(label="Insert")
        insert_button.add_css_class("suggested-action")
        
        # Function to get selected style
        def get_selected_style():
            for button in style_buttons:
                if button.get_active():
                    return button.style_id
            return None
        
        # Connect insert button
        insert_button.connect("clicked", lambda btn: self._on_wordart_dialog_response(
            win, dialog, text_entry.get_text(), get_selected_style()))
        
        button_box.append(insert_button)
        content_box.append(button_box)
        
        # Set dialog content and present
        dialog.set_child(content_box)
        dialog.present(win)
        
        # Activate first style button by default
        if style_buttons:
            style_buttons[0].set_active(True)        

    def _on_wordart_dialog_response(self, win, dialog, text, style_id):
        """Handle the response from the Word Art dialog"""
        # Close the dialog
        dialog.close()
        
        # Get selected text first
        win.webview.evaluate_javascript(
            "window.getSelection().toString();",
            -1, None, None, None,
            lambda webview, result, data: self._apply_wordart_with_selection(
                win, webview, result, text, style_id),
            None
        )

    def wordart_js(self):
        """JavaScript for Word Art functionality"""
        return """
        // Function to create Word Art with various styles
        function createWordArt(text, style) {
            // Clean text for HTML insertion
            const textContent = text.replace(/'/g, "\\'");
            
            // Create Word Art HTML based on style
            let wordArtHtml = '';
            
            switch (style) {
                case 'shadow':
                    wordArtHtml = `<span style="display: inline-block; text-shadow: 4px 4px 8px rgba(0,0,0,0.5); 
                                    font-weight: bold; font-size: 24px; padding: 10px 0;">${textContent}</span>`;
                    break;
                case 'outline':
                    wordArtHtml = `<span style="display: inline-block; color: white; 
                                    text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
                                    font-weight: bold; font-size: 24px; padding: 10px 0;">${textContent}</span>`;
                    break;
                // Add more styles here...
                default:
                    wordArtHtml = `<span style="display: inline-block; font-weight: bold; 
                                    font-size: 24px; padding: 10px 0;">${textContent}</span>`;
            }
            
            return wordArtHtml;
        }
        """

#################


    def _apply_wordart_with_selection(self, win, webview, result, input_text, style_id):
        """Apply Word Art using selection if available"""
        try:
            js_result = webview.evaluate_javascript_finish(result)
            selected_text = ""
            
            if js_result:
                # Get the selected text from the result
                if hasattr(js_result, 'get_js_value'):
                    selected_text = js_result.get_js_value().to_string()
                elif hasattr(js_result, 'to_string'):
                    selected_text = js_result.to_string()
                else:
                    selected_text = str(js_result)
                
                # Remove any surrounding quotes if present
                if selected_text.startswith('"') and selected_text.endswith('"'):
                    selected_text = selected_text[1:-1]
            
            # Use selected text if available, otherwise use input text
            final_text = selected_text if selected_text and selected_text.strip() else input_text
            
            if not final_text or not final_text.strip():
                # Show error if no text provided or selected
                self.show_error_dialog(win, "Please enter text or select existing text for the Word Art")
                return
            
            # Escape special characters in the text to avoid JS errors
            import json
            escaped_text = json.dumps(final_text)[1:-1]
            
            # Apply the Word Art style with a direct approach
            js_code = f"""
            (function() {{
                // Get current selection
                const selection = window.getSelection();
                const hasSelection = selection.rangeCount > 0 && selection.toString().trim() !== '';
                
                // Create the appropriate HTML based on the selected style
                let wordArtHtml = "";
                
                switch ('{style_id}') {{
                    case 'shadow':
                        wordArtHtml = '<span class="wordart-container" style="display: inline-block; position: relative; white-space: wrap; padding: 0 2px;"><span style="display: inline-block; text-shadow: 4px 4px 8px rgba(0,0,0,0.5); font-weight: bold; font-size: 24px; position: relative;">{escaped_text}</span></span>';
                        break;
                    case 'outline':
                        wordArtHtml = '<span class="wordart-container" style="display: inline-block; position: relative; white-space: wrap; padding: 0 2px;"><span style="display: inline-block; color: white; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000; font-weight: bold; font-size: 24px; position: relative;">{escaped_text}</span></span>';
                        break;
                    case 'inset':
                        wordArtHtml = '<span class="wordart-container" style="display: inline-block; position: relative; white-space: wrap; padding: 0 2px;"><span style="display: inline-block; background-color: #666; color: transparent; text-shadow: 2px 2px 3px rgba(255,255,255,0.5); -webkit-background-clip: text; background-clip: text; font-weight: bold; font-size: 24px; position: relative;">{escaped_text}</span></span>';
                        break;
                    case 'neon':
                        wordArtHtml = '<span class="wordart-container" style="display: inline-block; position: relative; white-space: wrap; padding: 0 2px;"><span style="display: inline-block; color: #fff; text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px #0073e6, 0 0 20px #0073e6; font-weight: bold; font-size: 24px; position: relative;">{escaped_text}</span></span>';
                        break;
                    case 'retro':
                        wordArtHtml = '<span class="wordart-container" style="display: inline-block; position: relative; white-space: wrap; padding: 0 2px;"><span style="display: inline-block; color: #fc0; text-shadow: 2px 2px 0px #f00; font-family: monospace; font-weight: bold; font-size: 24px; position: relative;">{escaped_text}</span></span>';
                        break;
                    case 'emboss':
                        wordArtHtml = '<span class="wordart-container" style="display: inline-block; position: relative; white-space: wrap; padding: 0 2px;"><span style="display: inline-block; color: #555; text-shadow: -1px -1px 1px #000, 1px 1px 1px #fff; font-weight: bold; font-size: 24px; position: relative;">{escaped_text}</span></span>';
                        break;
                    case 'gradient':
                        wordArtHtml = '<span class="wordart-container" style="display: inline-block; position: relative; white-space: wrap; padding: 0 2px;"><span style="display: inline-block; position: relative; font-weight: bold; font-size: 24px;"><span style="position: absolute; top: 0; left: 0; background: linear-gradient(to right, #ff8a00, #e52e71, #2d00f7); -webkit-background-clip: text; background-clip: text; color: transparent; pointer-events: none;">{escaped_text}</span><span style="color: transparent; position: relative; z-index: 1;">{escaped_text}</span></span></span>';
                        break;
                    case 'fire':
                        wordArtHtml = '<span class="wordart-container" style="display: inline-block; position: relative; white-space: wrap; padding: 0 2px;"><span style="display: inline-block; position: relative; font-weight: bold; font-size: 24px;"><span style="position: absolute; top: 0; left: 0; background: linear-gradient(0deg, #ff8c00, #ff0000); -webkit-background-clip: text; background-clip: text; color: transparent; pointer-events: none;">{escaped_text}</span><span style="color: transparent; position: relative; z-index: 1;">{escaped_text}</span></span></span>';
                        break;
                    case 'comic':
                        wordArtHtml = '<span class="wordart-container" style="display: inline-block; position: relative; white-space: wrap; padding: 0 2px;"><span style="display: inline-block; color: #fd0; text-shadow: -3px 0 4px #000; font-family: fantasy, \\'Comic Sans MS\\', cursive; font-weight: bold; font-size: 24px; position: relative;">{escaped_text}</span></span>';
                        break;
                    case 'metallic':
                        wordArtHtml = '<span class="wordart-container" style="display: inline-block; position: relative; white-space: wrap; padding: 0 2px;"><span style="display: inline-block; position: relative; font-weight: bold; font-size: 24px;"><span style="position: absolute; top: 0; left: 0; background: linear-gradient(to bottom, #d5d5d5 0%, #919191 98%); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 2px 2px 3px rgba(255,255,255,0.5); pointer-events: none;">{escaped_text}</span><span style="color: transparent; position: relative; z-index: 1;">{escaped_text}</span></span></span>';
                        break;
                    case '3d':
                        wordArtHtml = '<span class="wordart-container" style="display: inline-block; position: relative; white-space: wrap; padding: 0 2px;"><span style="display: inline-block; color: #5e17eb; text-shadow: 0px 1px 0px #c5bce4, 0px 2px 0px #a197c0, 0px 3px 0px #7c738e, 0px 4px 0px #58505f, 0px 5px 10px rgba(0, 0, 0, 0.6); font-weight: bold; font-size: 24px; position: relative;">{escaped_text}</span></span>';
                        break;
                    case 'glitch':
                        wordArtHtml = '<span class="wordart-container" style="display: inline-block; position: relative; white-space: wrap; padding: 0 2px;"><span style="display: inline-block; color: #00fffc; text-shadow: 2px 0 #ff00c1, -2px 0 #fffc00; font-weight: bold; font-size: 24px; position: relative;">{escaped_text}</span></span>';
                        break;
                    default:
                        wordArtHtml = '<span class="wordart-container" style="display: inline-block; position: relative; white-space: wrap; padding: 0 2px;"><span style="display: inline-block; font-weight: bold; font-size: 24px; position: relative;">{escaped_text}</span></span>';
                }}
                
                // If there's a selection, replace it
                if (hasSelection) {{
                    // First delete the selected content
                    document.execCommand('delete');
                    
                    // Then insert the word art
                    document.execCommand('insertHTML', false, wordArtHtml);
                }} else {{
                    // Just insert the word art at cursor position
                    document.execCommand('insertHTML', false, wordArtHtml);
                }}
                
                // Add a small script to enhance the editor behavior
                setTimeout(() => {{
                    // Mark all wordart containers as initialized to prevent duplicate event listeners
                    document.querySelectorAll('.wordart-container:not([data-initialized])').forEach(container => {{
                        container.setAttribute('data-initialized', 'true');
                    }});
                }}, 50);
                
                // Notify that content changed
                try {{
                    window.webkit.messageHandlers.contentChanged.postMessage('changed');
                }} catch(e) {{
                    console.log("Could not notify about content change:", e);
                }}
                
                return true;
            }})();
            """
            
            # Execute the JavaScript
            self.execute_js(win, js_code)
            
            # Update status bar
            if selected_text and selected_text.strip():
                win.statusbar.set_text(f"Word Art {style_id} style applied to selected text")
            else:
                win.statusbar.set_text(f"Word Art inserted with {style_id} style")
                
        except Exception as e:
            print(f"Error applying Word Art: {e}")
            win.statusbar.set_text(f"Error applying Word Art: {e}")        

    def on_font_size_change_shortcut(self, win, points_change):
        """Handle font size change via keyboard shortcuts (Ctrl+[ / Ctrl+] or Ctrl+Shift+< / Ctrl+Shift+>)
        
        Args:
            win: The window object
            points_change: Integer representing the size change in points
        """
        # First, get the current font size from the dropdown
        dropdown = win.font_size_dropdown
        selected_item = dropdown.get_selected_item()
        current_size_pt = selected_item.get_string()
        
        # Convert to integer
        try:
            current_size = int(current_size_pt)
        except ValueError:
            current_size = 12  # Default if conversion fails
        
        # Get all available sizes from the font size dropdown
        font_sizes = []
        model = dropdown.get_model()
        for i in range(model.get_n_items()):
            font_sizes.append(int(model.get_string(i)))
        
        # Find the next size in the sequence based on direction
        if points_change > 0:  # Increasing
            new_size = None
            for size in sorted(font_sizes):
                if size > current_size:
                    new_size = size
                    break
            if new_size is None:
                new_size = max(font_sizes)
        else:  # Decreasing
            new_size = None
            for size in sorted(font_sizes, reverse=True):
                if size < current_size:
                    new_size = size
                    break
            if new_size is None:
                new_size = min(font_sizes)
        
        # Update the dropdown selection
        for i, size in enumerate(font_sizes):
            if size == new_size:
                if win.font_size_handler_id:
                    win.font_size_dropdown.handler_block(win.font_size_handler_id)
                dropdown.set_selected(i)
                if win.font_size_handler_id:
                    win.font_size_dropdown.handler_unblock(win.font_size_handler_id)
                break
        
        # Apply the font size change with better cursor positioning
        js_code = f"""
        (function() {{
            // Store the new font size globally
            if (!window.fontSizeState) {{
                window.fontSizeState = {{}};
            }}
            window.fontSizeState.nextSize = '{new_size}pt';
            
            // Get editor and selection
            const editor = document.getElementById('editor');
            const selection = window.getSelection();
            
            if (!selection.rangeCount) return false;
            
            const range = selection.getRangeAt(0);
            
            // If text is selected, apply font size to selection
            if (!range.collapsed) {{
                // Apply font size to selected text
                document.execCommand('fontSize', false, '7');
                
                const fontElements = editor.querySelectorAll('font[size="7"]');
                for (const font of fontElements) {{
                    font.removeAttribute('size');
                    font.style.fontSize = '{new_size}pt';
                }}
                
                // Clean up the DOM
                cleanupEditorTags();
                
                // Record state
                saveState();
                window.lastContent = editor.innerHTML;
                window.redoStack = [];
                
                try {{
                    window.webkit.messageHandlers.contentChanged.postMessage("changed");
                }} catch(e) {{
                    console.log("Could not notify about changes:", e);
                }}
            }} else {{
                // No text selected - we'll set up the size for the next typed character
                
                // Clear any existing handlers
                if (window.fontSizeHandler) {{
                    editor.removeEventListener('input', window.fontSizeHandler);
                    window.fontSizeHandler = null;
                }}
                
                window.fontSizeHandler = function(e) {{
                    // Remove the handler immediately to ensure it only runs once
                    editor.removeEventListener('input', window.fontSizeHandler);
                    window.fontSizeHandler = null;
                    
                    // Size to apply
                    const fontSize = window.fontSizeState.nextSize;
                    
                    // Get the current selection
                    const sel = window.getSelection();
                    if (!sel.rangeCount) return;
                    
                    const currRange = sel.getRangeAt(0);
                    
                    // We need text nodes for this to work
                    if (!currRange.startContainer || currRange.startContainer.nodeType !== 3) return;
                    
                    // If nothing was typed or no offset, ignore
                    if (currRange.startOffset <= 0) return;
                    
                    try {{
                        // Create a range just for the last typed character
                        const charRange = document.createRange();
                        charRange.setStart(currRange.startContainer, currRange.startOffset - 1);
                        charRange.setEnd(currRange.startContainer, currRange.startOffset);
                        
                        // Remember where the cursor is
                        const endContainer = currRange.endContainer;
                        const endOffset = currRange.endOffset;
                        
                        // Select just the typed character
                        sel.removeAllRanges();
                        sel.addRange(charRange);
                        
                        // Apply formatting to the selected character
                        document.execCommand('fontSize', false, '7');
                        
                        // Update the font elements with the correct size
                        const fontElements = editor.querySelectorAll('font[size="7"]');
                        for (const font of fontElements) {{
                            font.removeAttribute('size');
                            font.style.fontSize = fontSize;
                        }}
                        
                        // Important: Set the cursor AFTER the new character
                        // The DOM structure has changed, so we need to find where to put the cursor
                        // We know we want to place it after the newly formatted character
                        
                        // Create a new selection at the right place
                        const newRange = document.createRange();
                        
                        // Find the newly created font element
                        const newFontElements = Array.from(editor.querySelectorAll('font')).filter(
                            font => font.style.fontSize === fontSize
                        );
                        
                        if (newFontElements.length > 0) {{
                            // Find the last text node inside this font element
                            const lastFont = newFontElements[newFontElements.length - 1];
                            let lastTextNode = null;
                            
                            // Function to find the last text node in an element
                            function findLastTextNode(node) {{
                                if (node.nodeType === 3) return node;
                                
                                let result = null;
                                for (let i = node.childNodes.length - 1; i >= 0; i--) {{
                                    result = findLastTextNode(node.childNodes[i]);
                                    if (result) return result;
                                }}
                                
                                return null;
                            }}
                            
                            lastTextNode = findLastTextNode(lastFont);
                            
                            if (lastTextNode) {{
                                // Place cursor at the end of the text node
                                newRange.setStart(lastTextNode, lastTextNode.length);
                                newRange.setEnd(lastTextNode, lastTextNode.length);
                            }} else {{
                                // If no text node found, place cursor after the font element
                                const parent = lastFont.parentNode;
                                const index = Array.from(parent.childNodes).indexOf(lastFont);
                                newRange.setStart(parent, index + 1);
                                newRange.setEnd(parent, index + 1);
                            }}
                        }} else {{
                            // If we can't find the font element, try to restore to original position
                            try {{
                                newRange.setStart(endContainer, endOffset);
                                newRange.setEnd(endContainer, endOffset);
                            }} catch (e) {{
                                // If that fails too, just set cursor at the start of editor
                                newRange.setStart(editor, 0);
                                newRange.setEnd(editor, 0);
                            }}
                        }}
                        
                        // Apply the new selection
                        sel.removeAllRanges();
                        sel.addRange(newRange);
                        
                        // Clean up the DOM
                        cleanupEditorTags();
                        
                        // Record state
                        saveState();
                        window.lastContent = editor.innerHTML;
                        window.redoStack = [];
                        
                        try {{
                            window.webkit.messageHandlers.contentChanged.postMessage("changed");
                        }} catch(e) {{
                            console.log("Could not notify about changes:", e);
                        }}
                    }} catch (error) {{
                        console.error("Error applying font size:", error);
                    }}
                }};
                
                // Add the input handler
                editor.addEventListener('input', window.fontSizeHandler);
                
                // Add a handler to clean up if user clicks elsewhere
                if (window.fontSizeClickHandler) {{
                    document.removeEventListener('mousedown', window.fontSizeClickHandler);
                }}
                
                window.fontSizeClickHandler = function() {{
                    if (window.fontSizeHandler) {{
                        editor.removeEventListener('input', window.fontSizeHandler);
                        window.fontSizeHandler = null;
                    }}
                    document.removeEventListener('mousedown', window.fontSizeClickHandler);
                }};
                
                document.addEventListener('mousedown', window.fontSizeClickHandler);
            }}
            
            return true;
        }})();
        """
        
        # Execute the JavaScript code
        self.execute_js(win, js_code)
        
        # Update status message
        msg_action = "increased" if points_change > 0 else "decreased"
        win.statusbar.set_text(f"Font size {msg_action} to {new_size}pt")
        
        # Keep focus on webview
        win.webview.grab_focus()

##############


    def create_file_toolbar(self, win):
        """Create the file toolbar with buttons mirroring the headerbar operations"""
        # Create a box for the file toolbar
        file_toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        #file_toolbar.add_css_class("toolbar-container")
        file_toolbar.set_margin_start(2)
        file_toolbar.set_margin_end(0)
        file_toolbar.set_margin_top(4)
        file_toolbar.set_margin_bottom(4)
        
        # --- File Operations Group ---
        file_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        file_group.add_css_class("linked")
        file_group.add_css_class("toolbar-group")
        
        # New button
        new_button = Gtk.Button(icon_name="document-new-symbolic")
        new_button.set_tooltip_text("New Document")
        new_button.connect("clicked", lambda btn: self.on_new_clicked(win, btn))
        new_button.set_size_request(40, 36)
        
        # Open button
        open_button = Gtk.Button(icon_name="document-open-symbolic")
        open_button.set_tooltip_text("Open File")
        open_button.connect("clicked", lambda btn: self.on_open_clicked(win, btn))
        open_button.set_size_request(40, 36)
        
        # Save button
        save_button = Gtk.Button(icon_name="document-save-symbolic")
        save_button.set_tooltip_text("Save File")
        save_button.connect("clicked", lambda btn: self.on_save_clicked(win, btn))
        save_button.set_size_request(40, 36)
        
        # Save As button
        save_as_button = Gtk.Button(icon_name="document-save-as-symbolic")
        save_as_button.set_tooltip_text("Save File As")
        save_as_button.connect("clicked", lambda btn: self.on_save_as_clicked(win, btn))
        save_as_button.set_size_request(40, 36)
        
        # Add file operation buttons to the group
        file_group.append(new_button)
        file_group.append(open_button)
        file_group.append(save_button)
        file_group.append(save_as_button)
        
        # Add the file group to the toolbar
        file_toolbar.append(file_group)
        
        # --- Edit Operations Group ---
        edit_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        edit_group.add_css_class("linked")
        edit_group.add_css_class("toolbar-group")
        
        # Select All button
        select_all_button = Gtk.Button(icon_name="edit-select-all-symbolic")
        select_all_button.set_tooltip_text("Select All")
        select_all_button.connect("clicked", lambda btn: self.on_select_all_clicked(win, btn))
        select_all_button.set_size_request(40, 36)
        
        # Cut button
        cut_button = Gtk.Button(icon_name="edit-cut-symbolic")
        cut_button.set_tooltip_text("Cut")
        cut_button.connect("clicked", lambda btn: self.on_cut_clicked(win, btn))
        cut_button.set_size_request(40, 36)
        
        # Copy button
        copy_button = Gtk.Button(icon_name="edit-copy-symbolic")
        copy_button.set_tooltip_text("Copy")
        copy_button.connect("clicked", lambda btn: self.on_copy_clicked(win, btn))
        copy_button.set_size_request(40, 36)
        
        # Paste button
        paste_button = Gtk.Button(icon_name="edit-paste-symbolic")
        paste_button.set_tooltip_text("Paste")
        paste_button.connect("clicked", lambda btn: self.on_paste_clicked(win, btn))
        paste_button.set_size_request(40, 36)
        
        # Add edit operation buttons to the group
        edit_group.append(select_all_button)
        edit_group.append(cut_button)
        edit_group.append(copy_button)
        edit_group.append(paste_button)
        
        # Add the edit group to the toolbar
        file_toolbar.append(edit_group)
        
        # --- Undo/Redo Group ---
        undo_redo_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        undo_redo_group.add_css_class("linked")
        undo_redo_group.add_css_class("toolbar-group")
        
        # Undo button
        undo_button = Gtk.Button(icon_name="edit-undo-symbolic")
        undo_button.set_tooltip_text("Undo")
        undo_button.connect("clicked", lambda btn: self.on_undo_clicked(win, btn))
        undo_button.set_size_request(40, 36)
        
        # Redo button
        redo_button = Gtk.Button(icon_name="edit-redo-symbolic")
        redo_button.set_tooltip_text("Redo")
        redo_button.connect("clicked", lambda btn: self.on_redo_clicked(win, btn))
        redo_button.set_size_request(40, 36)
        
        # Connect to the same undo/redo state as the main buttons
        win.undo_button_toolbar = undo_button
        win.redo_button_toolbar = redo_button
        
        # Add undo/redo buttons to the group
        undo_redo_group.append(undo_button)
        undo_redo_group.append(redo_button)
        
        # Add the undo/redo group to the toolbar
        file_toolbar.append(undo_redo_group)
        
        # --- Print/Find Group ---
        print_find_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        print_find_group.add_css_class("linked")
        print_find_group.add_css_class("toolbar-group")

        # Page Setup button - NEW!
        page_setup_button = Gtk.Button(icon_name="document-page-setup-symbolic")
        page_setup_button.set_tooltip_text("Page Setup")
        page_setup_button.connect("clicked", lambda btn: self.on_page_setup_clicked(win, btn))
        page_setup_button.set_size_request(40, 36)      
          
        # Print button
        print_button = Gtk.Button(icon_name="document-print-symbolic")
        print_button.set_tooltip_text("Print Document")
        print_button.connect("clicked", lambda btn: self.on_print_clicked(win, btn) if hasattr(self, "on_print_clicked") else None)
        print_button.set_size_request(40, 36)
        
        # Find-Replace button
        find_button = Gtk.ToggleButton(icon_name="edit-find-replace-symbolic")
        find_button.set_tooltip_text("Find and Replace")
        find_button.connect("toggled", lambda btn: self.on_find_button_toggled(win, btn))
        find_button.set_size_request(40, 36)
        
        # Sync with the main find button
        win.find_button_toolbar = find_button
        
        # Add print/find buttons to the group
        print_find_group.append(page_setup_button)
        print_find_group.append(print_button)
        print_find_group.append(find_button)
        
        # Add the print/find group to the toolbar
        file_toolbar.append(print_find_group)
        
        return file_toolbar


    # Add synchronization for find button state
    def on_find_button_toggled(self, win, button):
        """Handle find button toggling from either the headerbar or toolbar"""
        is_active = button.get_active()
        
        # Ensure both find buttons are in sync
        if hasattr(win, 'find_button') and button != win.find_button:
            # Block signal to prevent recursion
            win.find_button.handler_block(win.find_button_handler_id)
            win.find_button.set_active(is_active)
            win.find_button.handler_unblock(win.find_button_handler_id)
        
        if hasattr(win, 'find_button_toolbar') and button != win.find_button_toolbar:
            # We don't have handler ID for toolbar button, so need to disconnect temporarily
            handlers = win.find_button_toolbar.list_signal_handlers()
            for handler_id in handlers:
                win.find_button_toolbar.handler_block(handler_id)
            win.find_button_toolbar.set_active(is_active)
            for handler_id in handlers:
                win.find_button_toolbar.handler_unblock(handler_id)
        
        # Show or hide the find bar based on the active state
        win.find_bar_revealer.set_reveal_child(is_active)
        
        if is_active:
            # Set focus to the find entry
            GLib.idle_add(lambda: win.find_entry.grab_focus())
            win.statusbar.set_text("Find mode activated")
        else:
            # Return focus to the editor
            GLib.idle_add(lambda: win.webview.grab_focus())
            win.statusbar.set_text("Find mode deactivated")        



#########
    def on_find_shortcut(self, win):
        """Handle Ctrl+F shortcut to show the find bar"""
        # Get current state of find bar
        current_state = win.find_bar_revealer.get_reveal_child()
        new_state = not current_state
        
        # Update find bar state directly (this should always be safe)
        win.find_bar_revealer.set_reveal_child(new_state)
        
        # Now try to update buttons if they exist
        if hasattr(win, 'find_button') and hasattr(win, 'find_button_handler_id'):
            # Block signal handler to prevent recursion
            win.find_button.handler_block(win.find_button_handler_id)
            win.find_button.set_active(new_state)
            win.find_button.handler_unblock(win.find_button_handler_id)
        
        # Also update toolbar find button if it exists
        if hasattr(win, 'find_button_toolbar'):
            try:
                handlers = win.find_button_toolbar.list_signal_handlers()
                for handler_id in handlers:
                    win.find_button_toolbar.handler_block(handler_id)
                win.find_button_toolbar.set_active(new_state)
                for handler_id in handlers:
                    win.find_button_toolbar.handler_unblock(handler_id)
            except (AttributeError, TypeError):
                # Fallback if list_signal_handlers not available or other issue
                win.find_button_toolbar.set_active(new_state)
        
        # Update focus and status
        if new_state:
            # Set focus to the find entry when activated
            GLib.idle_add(lambda: win.find_entry.grab_focus())
            win.statusbar.set_text("Find mode activated")
        else:
            # Return focus to the editor when deactivated
            GLib.idle_add(lambda: win.webview.grab_focus())
            win.statusbar.set_text("Find mode deactivated")
        
        return True
##############
# Replace the _on_get_stack_sizes method with this more robust version:

    def _on_get_stack_sizes(self, win, webview, result, user_data):
        """Handle stack sizes information, with robust attribute checking"""
        try:
            js_result = webview.evaluate_javascript_finish(result)
            if js_result:
                # Try different approaches to get the result based on WebKit version
                try:
                    # Newer WebKit APIs
                    if hasattr(js_result, 'get_js_value'):
                        stack_sizes = js_result.get_js_value().to_string()
                    # Direct value access - works in some WebKit versions
                    elif hasattr(js_result, 'to_string'):
                        stack_sizes = js_result.to_string()
                    elif hasattr(js_result, 'get_string'):
                        stack_sizes = js_result.get_string()
                    else:
                        # Fallback - try converting to string directly
                        stack_sizes = str(js_result)
                    
                    # Parse the JSON result
                    import json
                    try:
                        # Remove any surrounding quotes if present
                        if stack_sizes.startswith('"') and stack_sizes.endswith('"'):
                            stack_sizes = stack_sizes[1:-1]
                        
                        # Try to parse as JSON
                        sizes = json.loads(stack_sizes)
                        # Update button states
                        can_undo = sizes.get('undoSize', 0) > 1
                        can_redo = sizes.get('redoSize', 0) > 0
                        
                        # Update headerbar buttons if they exist
                        if hasattr(win, 'undo_button'):
                            win.undo_button.set_sensitive(can_undo)
                        if hasattr(win, 'redo_button'):
                            win.redo_button.set_sensitive(can_redo)
                        
                        # Update toolbar buttons if they exist
                        if hasattr(win, 'undo_button_toolbar'):
                            win.undo_button_toolbar.set_sensitive(can_undo)
                        if hasattr(win, 'redo_button_toolbar'):
                            win.redo_button_toolbar.set_sensitive(can_redo)
                            
                    except json.JSONDecodeError as je:
                        print(f"Error parsing JSON: {je}, value was: {stack_sizes}")
                        # Set reasonable defaults for buttons that exist
                        self._set_default_button_states(win, True, False)
                except Exception as inner_e:
                    print(f"Inner error processing JS result: {inner_e}")
                    # Set reasonable defaults
                    self._set_default_button_states(win, True, False)
        except Exception as e:
            print(f"Error getting stack sizes: {e}")
            # Set reasonable defaults in case of error
            self._set_default_button_states(win, True, False)

    # Add this helper method to safely set button states
    def _set_default_button_states(self, win, undo_state, redo_state):
        """Safely set button states with attribute checking"""
        # Update headerbar buttons if they exist
        if hasattr(win, 'undo_button'):
            win.undo_button.set_sensitive(undo_state)
        if hasattr(win, 'redo_button'):
            win.redo_button.set_sensitive(redo_state)
        
        # Update toolbar buttons if they exist
        if hasattr(win, 'undo_button_toolbar'):
            win.undo_button_toolbar.set_sensitive(undo_state)
        if hasattr(win, 'redo_button_toolbar'):
            win.redo_button_toolbar.set_sensitive(redo_state)

    # page setup
    def create_default_page_setup(self):
        """Create default page setup with A4 paper and standard margins"""
        page_setup = Gtk.PageSetup.new()
        
        # Set A4 paper size
        paper_size = Gtk.PaperSize.new(Gtk.PAPER_NAME_A4)
        page_setup.set_paper_size(paper_size)
        
        # Set portrait orientation
        page_setup.set_orientation(Gtk.PageOrientation.PORTRAIT)
        
        # Set 1-inch margins (72 points)
        page_setup.set_top_margin(72.0, Gtk.Unit.POINTS)
        page_setup.set_right_margin(72.0, Gtk.Unit.POINTS)
        page_setup.set_bottom_margin(72.0, Gtk.Unit.POINTS)
        page_setup.set_left_margin(72.0, Gtk.Unit.POINTS)
        
        return page_setup

    def on_page_setup_clicked(self, win, btn):
        """Handle page setup button click"""
        # Use specific window's page setup if it exists, otherwise use app defaults
        if not hasattr(win, 'page_setup'):
            win.page_setup = self.default_page_setup.copy()
        
        self.show_general_page_setup_dialog(win)


    def show_general_page_setup_dialog(self, win):
        """Show page setup dialog for setting default print options"""
        dialog = Adw.Dialog()
        dialog.set_title("Page Setup")
        dialog.set_content_width(400)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)

        header_label = Gtk.Label()
        header_label.set_markup("<b>Page Options</b>")
        header_label.set_halign(Gtk.Align.START)
        content_box.append(header_label)

        # Paper size
        paper_size_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        paper_size_label = Gtk.Label(label="Paper Size:")
        paper_size_label.set_halign(Gtk.Align.START)
        paper_size_label.set_hexpand(True)
        paper_sizes = Gtk.StringList()
        for size in ("A4", "US Letter", "Legal", "A3", "A5"):
            paper_sizes.append(size)
        paper_size_dropdown = Gtk.DropDown.new(paper_sizes, None)
        
        # Try to use existing page setup if available
        selected_size_index = 0  # Default to A4
        if hasattr(win, 'page_setup') and win.page_setup:
            paper_size = win.page_setup.get_paper_size()
            paper_name = paper_size.get_name()
            for i, size in enumerate(["A4", "US LETTER", "LEGAL", "A3", "A5"]):
                if paper_name.upper() == size:
                    selected_size_index = i
                    break
        
        paper_size_dropdown.set_selected(selected_size_index)
        paper_size_box.append(paper_size_label)
        paper_size_box.append(paper_size_dropdown)
        content_box.append(paper_size_box)

        # Orientation (radio via CheckButton grouping)
        orientation_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        orientation_label = Gtk.Label(label="Orientation:")
        orientation_label.set_halign(Gtk.Align.START)
        orientation_label.set_hexpand(True)
        portrait_radio = Gtk.CheckButton(label="Portrait")
        landscape_radio = Gtk.CheckButton(label="Landscape")
        landscape_radio.set_group(portrait_radio)
        
        # Set current orientation if available
        if hasattr(win, 'page_setup') and win.page_setup:
            orientation = win.page_setup.get_orientation()
            portrait_radio.set_active(orientation == Gtk.PageOrientation.PORTRAIT)
            landscape_radio.set_active(orientation == Gtk.PageOrientation.LANDSCAPE)
        else:
            portrait_radio.set_active(True)  # Default
        
        orientation_box.append(orientation_label)
        orientation_box.append(portrait_radio)
        orientation_box.append(landscape_radio)
        content_box.append(orientation_box)

        # Margins header
        margins_label = Gtk.Label()
        margins_label.set_markup("<b>Margins</b>")
        margins_label.set_halign(Gtk.Align.START)
        margins_label.set_margin_top(16)
        content_box.append(margins_label)

        # Conversion factors and limits
        factors = {"in": 72.0, "mm": 72.0/25.4, "cm": 72.0/2.54, "pt": 1.0}
        bounds = {
            "in": (0.0, 5.0, 0.05),
            "mm": (0.0, 100.0, 1.0),
            "cm": (0.0, 10.0, 0.1),
            "pt": (0.0, 300.0, 1.0)
        }
        units_map = {0: "in", 1: "mm", 2: "cm", 3: "pt"}

        def from_points(val, unit):
            """Convert point value to the specified unit"""
            return val / factors[unit]

        def to_points(val, unit):
            """Convert value in specified unit to points"""
            return val * factors[unit]

        # Helper to create spin
        def make_spin(unit="in"):
            low, high, step = bounds[unit]
            adj = Gtk.Adjustment.new(1.0, low, high, step, step*5, 0.0)
            spin = Gtk.SpinButton()
            spin.set_adjustment(adj)
            digits = 0 if unit == "pt" else (1 if unit in ("mm", "cm") else 2)
            spin.set_digits(digits)
            return spin, adj

        # Units dropdown - create first so we know the current unit
        units_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        units_box.set_margin_start(12)
        units_label = Gtk.Label(label="Units:")
        units_label.set_halign(Gtk.Align.START)
        units_list = Gtk.StringList()
        for u in ("inches (in)", "millimeters (mm)", "centimeters (cm)", "points (pt)"):
            units_list.append(u)
        units_dropdown = Gtk.DropDown.new(units_list, None)
        units_dropdown.set_selected(0)  # Default to inches
        units_dropdown.current_unit = "in"
        units_box.append(units_label)
        units_box.append(units_dropdown)
        content_box.append(units_box)

        # Create spinners with appropriate initial unit
        current_unit = units_dropdown.current_unit
        top_spin, top_adj = make_spin(current_unit)
        right_spin, right_adj = make_spin(current_unit)
        bottom_spin, bottom_adj = make_spin(current_unit)
        left_spin, left_adj = make_spin(current_unit)

        # Set current margins if available (converted to the current unit)
        if hasattr(win, 'page_setup') and win.page_setup:
            # Get values in points
            top_pt = win.page_setup.get_top_margin(Gtk.Unit.POINTS)
            right_pt = win.page_setup.get_right_margin(Gtk.Unit.POINTS)
            bottom_pt = win.page_setup.get_bottom_margin(Gtk.Unit.POINTS)
            left_pt = win.page_setup.get_left_margin(Gtk.Unit.POINTS)
            
            # Convert to current unit and set in spinners
            top_spin.set_value(from_points(top_pt, current_unit))
            right_spin.set_value(from_points(right_pt, current_unit))
            bottom_spin.set_value(from_points(bottom_pt, current_unit))
            left_spin.set_value(from_points(left_pt, current_unit))
        else:
            # Set reasonable defaults in current unit
            default_margin_pt = 72.0  # 1 inch in points
            top_spin.set_value(from_points(default_margin_pt, current_unit))
            right_spin.set_value(from_points(default_margin_pt, current_unit))
            bottom_spin.set_value(from_points(default_margin_pt, current_unit))
            left_spin.set_value(from_points(default_margin_pt, current_unit))

        def on_unit_changed(dropdown, _):
            # Get old and new units
            old = dropdown.current_unit
            new = units_map[dropdown.get_selected()]
            
            # For each spinner, convert its value from old unit to points, then to the new unit
            for spin, adj in ((top_spin, top_adj), (right_spin, right_adj),
                              (bottom_spin, bottom_adj), (left_spin, left_adj)):
                # Convert from old unit to points, then to new unit
                pts = to_points(spin.get_value(), old)
                
                # Update spinner settings for the new unit
                low, high, step = bounds[new]
                adj.set_lower(low)
                adj.set_upper(high)
                adj.set_step_increment(step)
                
                # Set appropriate decimal places based on the unit
                digits = 0 if new == "pt" else (1 if new in ("mm", "cm") else 2)
                spin.set_digits(digits)
                
                # Set the new value (after adjusting spinner settings)
                new_val = from_points(pts, new)
                spin.set_value(new_val)
                
            # Update the current unit
            dropdown.current_unit = new

        units_dropdown.connect("notify::selected", on_unit_changed)

        # Layout margin grid
        margins_grid = Gtk.Grid()
        margins_grid.set_row_spacing(8)
        margins_grid.set_column_spacing(12)
        margins_grid.set_margin_start(12)
        
        labels_spins = [("Top:", top_spin), ("Right:", right_spin),
                      ("Bottom:", bottom_spin), ("Left:", left_spin)]
                      
        for idx, (lbl, spin) in enumerate(labels_spins):
            l = Gtk.Label(label=lbl)
            l.set_halign(Gtk.Align.START)
            margins_grid.attach(l, 0, idx, 1, 1)
            margins_grid.attach(spin, 1, idx, 1, 1)
        
        content_box.append(margins_grid)

        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(24)
        
        cancel = Gtk.Button(label="Cancel")
        apply = Gtk.Button(label="Apply")
        apply.add_css_class("suggested-action")

        def on_apply(btn):
            # Get paper size
            idx = paper_size_dropdown.get_selected()
            name = paper_sizes.get_string(idx)
            paper_name = getattr(Gtk, f"PAPER_NAME_{name.upper().replace(' ', '_')}", Gtk.PAPER_NAME_A4)
            
            # Get orientation
            orient = Gtk.PageOrientation.LANDSCAPE if landscape_radio.get_active() else Gtk.PageOrientation.PORTRAIT
            
            # Get margins and convert to points
            unit = units_dropdown.current_unit
            top_margin = to_points(top_spin.get_value(), unit)
            right_margin = to_points(right_spin.get_value(), unit)
            bottom_margin = to_points(bottom_spin.get_value(), unit)
            left_margin = to_points(left_spin.get_value(), unit)
            
            # Create page setup
            page_setup = Gtk.PageSetup.new()
            page_setup.set_paper_size(Gtk.PaperSize.new(paper_name))
            page_setup.set_orientation(orient)
            page_setup.set_top_margin(top_margin, Gtk.Unit.POINTS)
            page_setup.set_right_margin(right_margin, Gtk.Unit.POINTS)
            page_setup.set_bottom_margin(bottom_margin, Gtk.Unit.POINTS)
            page_setup.set_left_margin(left_margin, Gtk.Unit.POINTS)
            
            # Store the page setup in the window for future use
            win.page_setup = page_setup
            dialog.close()
            win.statusbar.set_text("Page setup saved")
            win.webview.grab_focus()
        def on_cancel(btn):
             dialog.close()
             win.webview.grab_focus()
            
        apply.connect("clicked", on_apply)
        cancel.connect("clicked", on_cancel)
        button_box.append(cancel)
        button_box.append(apply)
        content_box.append(button_box)

        dialog.set_child(content_box)
        dialog.present(win)
######################

def main():
    app = WebkitWordApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    Adw.init()
    sys.exit(main())    
