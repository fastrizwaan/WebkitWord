#!/usr/bin/env python3
# keyboard_shortcuts.py - setup keyboard shortcuts for the app and related methods
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, GLib, Gio, Pango, PangoCairo
    

def on_webview_key_pressed(self, controller, keyval, keycode, state):
    """Handle key press events on the webview"""
    win = None
    for window in self.windows:
        if hasattr(window, 'key_controller') and window.key_controller == controller:
            win = window
            break

    if not win:
        return False

    ctrl = (state & Gdk.ModifierType.CONTROL_MASK) != 0
    shift = (state & Gdk.ModifierType.SHIFT_MASK) != 0
    alt = (state & Gdk.ModifierType.ALT_MASK) != 0

    # Alt shortcuts for toolbar toggles
    if alt and not ctrl and not shift:
        if keyval == Gdk.KEY_f:
            self.toggle_file_toolbar(win)
            return True
        elif keyval == Gdk.KEY_h:
            self.toggle_headerbar(win)
            return True
        elif keyval == Gdk.KEY_s:
            self.toggle_statusbar(win)
            return True
        elif keyval == Gdk.KEY_t: 
            self.toggle_format_toolbar(win)
            return True

    if ctrl and alt:
        if keyval >= Gdk.KEY_0 and keyval <= Gdk.KEY_6:
            style_num = keyval - Gdk.KEY_0
            self.on_paragraph_style_shortcut(win, style_num)
            return True

    if ctrl and not alt:
        if keyval == Gdk.KEY_n:
            self.on_new_clicked(win, None)
            return True

        elif keyval == Gdk.KEY_o:
            self.on_open_clicked(win, None)
            return True
        elif keyval == Gdk.KEY_s and not shift:
            self.on_save_clicked(win, None)
            return True
        elif keyval == Gdk.KEY_S and shift:
            self.on_save_as_clicked(win, None)
            return True
        elif keyval == Gdk.KEY_p:
            self.on_print_clicked(win, None)
            return True
        elif keyval == Gdk.KEY_w and not shift:
            self.on_close_shortcut(win)
            return True

        elif keyval == Gdk.KEY_0:
            self.on_line_spacing_shortcut(win, 1.15)  # 1.15 for default spacing
            return True
        elif keyval == Gdk.KEY_1:
            self.on_line_spacing_shortcut(win, 1.0)  # 1.0 for single spacing
            return True
        elif keyval == Gdk.KEY_2:
            self.on_line_spacing_shortcut(win, 2.0)  # 2.0 for double spacing
            return True
        elif keyval == Gdk.KEY_5:
            self.on_line_spacing_shortcut(win, 1.5)  # 1.5 for one-and-half spacing
            return True
            
        elif keyval == Gdk.KEY_z and not shift:
            self.on_undo_shortcut(win)
            return True
        elif (keyval == Gdk.KEY_z and shift) or keyval == Gdk.KEY_y:
            self.on_redo_shortcut(win)
            return True
        elif keyval == Gdk.KEY_x and not shift:
            self.on_cut_clicked(win, None)
            return True
        elif keyval == Gdk.KEY_c:
            self.on_copy_clicked(win, None)
            return True
        elif keyval == Gdk.KEY_v:
            self.on_paste_clicked(win, None)
            return True

        elif keyval == Gdk.KEY_f and not shift:
            self.on_find_shortcut(win)
            return True
        elif keyval == Gdk.KEY_h and not shift:
            self.on_replace_shortcut(win)
            return True

        elif keyval == Gdk.KEY_a:
            self.on_select_all_clicked(win, None)
            return True
            
        elif keyval == Gdk.KEY_b:
            self.on_bold_shortcut(win)
            return True
        elif keyval == Gdk.KEY_i:
            self.on_italic_shortcut(win)
            return True
        elif keyval == Gdk.KEY_u:
            self.on_underline_shortcut(win)
            return True

        elif keyval == Gdk.KEY_plus:
            self.on_superscript_shortcut(win)
            return True  
            
        elif keyval == Gdk.KEY_equal:
            self.on_subscript_shortcut(win)
            return True  

        elif keyval == Gdk.KEY_l:
            self.on_align_left_shortcut(win)
            return True
        elif keyval == Gdk.KEY_e:
            self.on_align_center_shortcut(win)
            return True
        elif keyval == Gdk.KEY_r:
            self.on_align_right_shortcut(win)
            return True
        elif keyval == Gdk.KEY_j:
            self.on_align_justify_shortcut(win)
            return True

        elif keyval == Gdk.KEY_KP_Add:
            self.on_zoom_in_shortcut(win)
            return True
        elif keyval == Gdk.KEY_KP_Subtract:
            self.on_zoom_out_shortcut(win)
            return True
        elif keyval == Gdk.KEY_KP_0 or keyval == Gdk.KEY_KP_Insert:
            self.on_zoom_reset_shortcut(win)
            return True

    if ctrl and shift and not alt:
        if keyval == Gdk.KEY_W:
            self.on_close_others_shortcut(win)
            return True
        elif keyval == Gdk.KEY_X:
            self.on_strikeout_shortcut(win)
            return True
        elif keyval == Gdk.KEY_ampersand or keyval == Gdk.KEY_7:
            self.on_numbered_list_shortcut(win)
            return True
        elif keyval == Gdk.KEY_asterisk or keyval == Gdk.KEY_8:
            self.on_bullet_list_shortcut(win)
            return True
        elif keyval == Gdk.KEY_greater:  # > key (Shift+.)
            self.on_font_size_change_shortcut(win, 2)  # Increase by points in the font size list
            return True
        elif keyval == Gdk.KEY_less:  # < key (Shift+,)
            self.on_font_size_change_shortcut(win, -2)  # Decrease by points in the font size list
            return True
            
    if keyval == Gdk.KEY_F12 and not shift:
        self.on_numbered_list_shortcut(win)
        return True
    elif keyval == Gdk.KEY_F12 and shift:
        self.on_bullet_list_shortcut(win)
        return True

    if keyval == Gdk.KEY_ISO_Left_Tab or (keyval == Gdk.KEY_Tab and shift):
        return True
        
    if ctrl and not shift and not alt:
        # Add the font size adjustment with brackets
        if keyval == Gdk.KEY_bracketleft:  # [ key
            self.on_font_size_change_shortcut(win, -1)  # Decrease by 1 point
            return True
        elif keyval == Gdk.KEY_bracketright:  # ] key
            self.on_font_size_change_shortcut(win, 1)  # Increase by 1 point
            return True
   
    # Setup zoom scrolling using ctrl+scroll    
    self.setup_scroll_zoom(win)
    # Let other key events propagate normally
    return False
###################### Shortcut Related Methods    
# Find and Replace shortcuts
def on_replace_shortcut(self, win, *args):
    """Handle Ctrl+H shortcut for Find & Replace"""
    # Show find bar and focus on replace field
    find_bar = win.find_bar
    if hasattr(find_bar, 'get_child'):
        find_revealer = find_bar.get_child()
        if isinstance(find_revealer, Gtk.Revealer):
            find_revealer.set_reveal_child(True)
            
            # Get the find box content
            find_box = find_revealer.get_child()
            if isinstance(find_box, Gtk.Box):
                # Find the replace entry
                for child in find_box.observe_children():
                    if isinstance(child, Gtk.Entry) and hasattr(child, 'get_name') and child.get_name() == "replace_entry":
                        child.grab_focus()
                        break
    
    # Ensure find button is toggled on
    win.find_button.set_active(True)
    
    # Populate find field from selection
    self.populate_find_field_from_selection(win)
    
    win.statusbar.set_text("Find & Replace activated")
    return True

# Paragraph style shortcuts
def on_paragraph_style_shortcut(self, win, style_num):
    """Handle Ctrl+Alt+0 through Ctrl+Alt+6 for paragraph styles"""
    # Map the shortcut number to dropdown index
    # 0 = Normal, 1-6 = Heading 1-6
    win.paragraph_style_dropdown.set_selected(style_num)
    
    # Update the paragraph style
    self.on_paragraph_style_changed(win, win.paragraph_style_dropdown)
    
    # Get the style name for status message
    style_name = "Normal" if style_num == 0 else f"Heading {style_num}"
    win.statusbar.set_text(f"Applied {style_name} style")
    return True

# List shortcuts
def on_numbered_list_shortcut(self, win, *args):
    """Handle F12 or Ctrl+Shift+7 for numbered list"""
    # Toggle the numbered list button
    current_state = win.numbered_list_button.get_active()
    win.numbered_list_button.set_active(not current_state)
    return True

def on_bullet_list_shortcut(self, win, *args):
    """Handle Shift+F12 or Ctrl+Shift+8 for bullet list"""
    # Toggle the bullet list button
    current_state = win.bullet_list_button.get_active()
    win.bullet_list_button.set_active(not current_state)
    return True

# Alignment shortcuts
def on_align_left_shortcut(self, win, *args):
    """Handle Ctrl+L for left alignment"""
    # Find the left alignment button and set it active
    if 'left' in win.alignment_buttons:
        win.alignment_buttons['left'].set_active(True)
    return True

def on_align_center_shortcut(self, win, *args):
    """Handle Ctrl+E for center alignment"""
    # Find the center alignment button and set it active
    if 'center' in win.alignment_buttons:
        win.alignment_buttons['center'].set_active(True)
    return True

def on_align_right_shortcut(self, win, *args):
    """Handle Ctrl+R for right alignment"""
    # Find the right alignment button and set it active
    if 'right' in win.alignment_buttons:
        win.alignment_buttons['right'].set_active(True)
    return True

def on_align_justify_shortcut(self, win, *args):
    """Handle Ctrl+J for justified alignment"""
    # Find the justify alignment button and set it active
    if 'justify' in win.alignment_buttons:
        win.alignment_buttons['justify'].set_active(True)
    return True

# Zoom shortcuts
def on_zoom_in_shortcut(self, win, *args):
    """Handle Ctrl+= or Ctrl++ for zoom in"""
    current_zoom = win.zoom_scale.get_value()
    new_zoom = min(current_zoom + 10, 400)  # Increase by 10%, max 400%
    win.zoom_scale.set_value(new_zoom)
    win.statusbar.set_text(f"Zoom: {int(new_zoom)}%")
    return True

def on_zoom_out_shortcut(self, win, *args):
    """Handle Ctrl+- for zoom out"""
    current_zoom = win.zoom_scale.get_value()
    new_zoom = max(current_zoom - 10, 50)  # Decrease by 10%, min 50%
    win.zoom_scale.set_value(new_zoom)
    win.statusbar.set_text(f"Zoom: {int(new_zoom)}%")
    return True

def on_zoom_reset_shortcut(self, win, *args):
    """Handle Ctrl+0 for reset zoom to 100%"""
    win.zoom_scale.set_value(100)
    win.statusbar.set_text("Zoom: 100%")
    return True

####################
def setup_scroll_zoom(self, win):
    """Set up zooming with Ctrl+scroll wheel"""
    # Create a scroll controller for handling wheel events
    scroll_controller = Gtk.EventControllerScroll.new(
        Gtk.EventControllerScrollFlags.VERTICAL | 
        Gtk.EventControllerScrollFlags.DISCRETE
    )
    
    # Connect to the scroll event
    scroll_controller.connect("scroll", lambda ctrl, dx, dy: self.on_scroll(win, ctrl, dx, dy))
    
    # Add the controller to the webview
    win.webview.add_controller(scroll_controller)
    
    # Store the controller reference on the window
    win.scroll_controller = scroll_controller

def on_scroll(self, win, controller, dx, dy):
    """Handle scroll events for zooming"""
    # Check if Ctrl key is pressed
    state = controller.get_current_event_state()
    ctrl_pressed = (state & Gdk.ModifierType.CONTROL_MASK) != 0
    
    if ctrl_pressed:
        # Get current zoom level
        current_zoom = win.zoom_scale.get_value()
        
        # Calculate new zoom level - use larger steps for faster zooming
        step = 10  # 10% step size
        
        if dy < 0:
            # Scroll up - zoom in
            new_zoom = min(current_zoom + step, 400)  # Max 400%
        else:
            # Scroll down - zoom out
            new_zoom = max(current_zoom - step, 50)   # Min 50%
        
        # Only update if there's a change
        if new_zoom != current_zoom:
            # Update the zoom scale (which will trigger the zoom UI update)
            win.zoom_scale.set_value(new_zoom)
            
            # Update status
            win.statusbar.set_text(f"Zoom: {int(new_zoom)}%")
        
        # Prevent further handling of this scroll event
        return True
    
    # Not zooming, let the event propagate for normal scrolling
    return False

# Modify the apply_zoom method to improve the zooming experience
def apply_zoom(self, win, zoom_level):
    """Apply zoom level to the editor with improved user experience"""
    # Convert percentage to scale factor (1.0 = 100%)
    scale_factor = zoom_level / 100.0
    
    # Apply zoom using JavaScript
    js_code = f"""
    (function() {{
        // Apply zoom to body and editor
        document.body.style.zoom = "{scale_factor}";
        document.getElementById('editor').style.zoom = "{scale_factor}";
        
        // Store current zoom level for persistence
        window.currentZoomLevel = {zoom_level};
        
        
        
        return true;
    }})();
    """
    
    self.execute_js(win, js_code)
    
    # Also update the zoom button label in statusbar if it exists
    if hasattr(win, 'zoom_label'):
        win.zoom_label.set_text(f"{zoom_level}%")  
        

