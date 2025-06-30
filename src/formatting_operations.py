#!/usr/bin/env python3
# formatting_operations.py - formatting related methods
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, GLib, Gio, Pango, PangoCairo

def on_bold_shortcut(self, win, *args):
    """Handle Ctrl+B shortcut for bold formatting"""
    # Execute the bold command directly in JavaScript
    self.execute_js(win, """
        document.execCommand('bold', false, null);
        // Return the current state so we can update the button
        document.queryCommandState('bold');
    """)
    
    # Immediately toggle the button state to provide instant feedback
    if win.bold_handler_id is not None:
        win.bold_button.handler_block(win.bold_handler_id)
        win.bold_button.set_active(not win.bold_button.get_active())
        win.bold_button.handler_unblock(win.bold_handler_id)
    
    win.statusbar.set_text("Bold formatting applied")
    return True

def on_italic_shortcut(self, win, *args):
    """Handle Ctrl+I shortcut for italic formatting"""
    # Execute the italic command directly in JavaScript
    self.execute_js(win, """
        document.execCommand('italic', false, null);
        // Return the current state so we can update the button
        document.queryCommandState('italic');
    """)
    
    # Immediately toggle the button state to provide instant feedback
    if win.italic_handler_id is not None:
        win.italic_button.handler_block(win.italic_handler_id)
        win.italic_button.set_active(not win.italic_button.get_active())
        win.italic_button.handler_unblock(win.italic_handler_id)
    
    win.statusbar.set_text("Italic formatting applied")
    return True

def on_underline_shortcut(self, win, *args):
    """Handle Ctrl+U shortcut for underline formatting"""
    # Execute the underline command directly in JavaScript
    self.execute_js(win, """
        document.execCommand('underline', false, null);
        // Return the current state so we can update the button
        document.queryCommandState('underline');
    """)
    
    # Immediately toggle the button state to provide instant feedback
    if win.underline_handler_id is not None:
        win.underline_button.handler_block(win.underline_handler_id)
        win.underline_button.set_active(not win.underline_button.get_active())
        win.underline_button.handler_unblock(win.underline_handler_id)
    
    win.statusbar.set_text("Underline formatting applied")
    return True

def on_strikeout_shortcut(self, win, *args):
    """Handle Ctrl+Shift+X shortcut for strikeout formatting"""
    # Execute the strikeout command directly in JavaScript
    self.execute_js(win, """
        document.execCommand('strikeThrough', false, null);
        // Return the current state so we can update the button
        document.queryCommandState('strikeThrough');
    """)
    
    # Immediately toggle the button state to provide instant feedback
    if win.strikeout_handler_id is not None:
        win.strikeout_button.handler_block(win.strikeout_handler_id)
        win.strikeout_button.set_active(not win.strikeout_button.get_active())
        win.strikeout_button.handler_unblock(win.strikeout_handler_id)
    
    win.statusbar.set_text("Strikeout formatting applied")
    return True

def on_subscript_shortcut(self, win, *args):
    """Handle Ctrl+, shortcut for subscript formatting"""
    # Check if superscript is active and deactivate it if needed
    if win.superscript_button.get_active():
        # Block superscript handler to prevent infinite loop
        if win.superscript_handler_id is not None:
            win.superscript_button.handler_block(win.superscript_handler_id)
        
        # Deactivate superscript button
        win.superscript_button.set_active(False)
        
        # Unblock superscript handler
        if win.superscript_handler_id is not None:
            win.superscript_button.handler_unblock(win.superscript_handler_id)
    
    # Execute the subscript command directly in JavaScript
    self.execute_js(win, """
        document.execCommand('subscript', false, null);
        // Return the current state so we can update the button
        document.queryCommandState('subscript');
    """)
    
    # Immediately toggle the button state to provide instant feedback
    if win.subscript_handler_id is not None:
        win.subscript_button.handler_block(win.subscript_handler_id)
        win.subscript_button.set_active(not win.subscript_button.get_active())
        win.subscript_button.handler_unblock(win.subscript_handler_id)
    
    win.statusbar.set_text("Subscript formatting applied")
    return True

def on_superscript_shortcut(self, win, *args):
    """Handle Ctrl+. shortcut for superscript formatting"""
    # Check if subscript is active and deactivate it if needed
    if win.subscript_button.get_active():
        # Block subscript handler to prevent infinite loop
        if win.subscript_handler_id is not None:
            win.subscript_button.handler_block(win.subscript_handler_id)
        
        # Deactivate subscript button
        win.subscript_button.set_active(False)
        
        # Unblock subscript handler
        if win.subscript_handler_id is not None:
            win.subscript_button.handler_unblock(win.subscript_handler_id)
    
    # Execute the superscript command directly in JavaScript
    self.execute_js(win, """
        document.execCommand('superscript', false, null);
        // Return the current state so we can update the button
        document.queryCommandState('superscript');
    """)
    
    # Immediately toggle the button state to provide instant feedback
    if win.superscript_handler_id is not None:
        win.superscript_button.handler_block(win.superscript_handler_id)
        win.superscript_button.set_active(not win.superscript_button.get_active())
        win.superscript_button.handler_unblock(win.superscript_handler_id)
    
    win.statusbar.set_text("Superscript formatting applied")
    return True

def on_bold_toggled(self, win, button):
    """Handle bold toggle button state changes"""
    # Block the handler temporarily
    if win.bold_handler_id is not None:
        button.handler_block(win.bold_handler_id)
    
    try:
        # Apply formatting
        self.execute_js(win, "document.execCommand('bold', false, null);")
        
        # Check if find bar has focus before setting focus to webview
        find_bar_active = win.find_bar_revealer.get_reveal_child()
        find_entry_has_focus = False
        
        if find_bar_active:
            find_entry_has_focus = win.find_entry.has_focus() or win.replace_entry.has_focus()
        
        # Only grab focus to webview if find entries don't have focus
        if not find_entry_has_focus:
            win.webview.grab_focus()
    finally:
        # Unblock the handler
        if win.bold_handler_id is not None:
            button.handler_unblock(win.bold_handler_id)

def on_italic_toggled(self, win, button):
    """Handle italic toggle button state changes"""
    # Block the handler temporarily
    if win.italic_handler_id is not None:
        button.handler_block(win.italic_handler_id)
    
    try:
        # Apply formatting
        self.execute_js(win, "document.execCommand('italic', false, null);")
        
        # Check if find bar has focus before setting focus to webview
        find_bar_active = win.find_bar_revealer.get_reveal_child()
        find_entry_has_focus = False
        
        if find_bar_active:
            find_entry_has_focus = win.find_entry.has_focus() or win.replace_entry.has_focus()
        
        # Only grab focus to webview if find entries don't have focus
        if not find_entry_has_focus:
            win.webview.grab_focus()
    finally:
        # Unblock the handler
        if win.italic_handler_id is not None:
            button.handler_unblock(win.italic_handler_id)

def on_underline_toggled(self, win, button):
    """Handle underline toggle button state changes"""
    # Block the handler temporarily
    if win.underline_handler_id is not None:
        button.handler_block(win.underline_handler_id)
    
    try:
        # Apply formatting
        self.execute_js(win, "document.execCommand('underline', false, null);")
        
        # Check if find bar has focus before setting focus to webview
        find_bar_active = win.find_bar_revealer.get_reveal_child()
        find_entry_has_focus = False
        
        if find_bar_active:
            find_entry_has_focus = win.find_entry.has_focus() or win.replace_entry.has_focus()
        
        # Only grab focus to webview if find entries don't have focus
        if not find_entry_has_focus:
            win.webview.grab_focus()
    finally:
        # Unblock the handler
        if win.underline_handler_id is not None:
            button.handler_unblock(win.underline_handler_id)

def on_strikeout_toggled(self, win, button):
    """Handle strikeout toggle button state changes"""
    # Block the handler temporarily
    if win.strikeout_handler_id is not None:
        button.handler_block(win.strikeout_handler_id)
    
    try:
        # Apply formatting
        self.execute_js(win, "document.execCommand('strikeThrough', false, null);")
        
        # Check if find bar has focus before setting focus to webview
        find_bar_active = win.find_bar_revealer.get_reveal_child()
        find_entry_has_focus = False
        
        if find_bar_active:
            find_entry_has_focus = win.find_entry.has_focus() or win.replace_entry.has_focus()
        
        # Only grab focus to webview if find entries don't have focus
        if not find_entry_has_focus:
            win.webview.grab_focus()
    finally:
        # Unblock the handler
        if win.strikeout_handler_id is not None:
            button.handler_unblock(win.strikeout_handler_id)

def on_subscript_toggled(self, win, button):
    """Handle subscript toggle button state changes"""
    # Block the handler temporarily
    if win.subscript_handler_id is not None:
        button.handler_block(win.subscript_handler_id)
    
    try:
        # Get current button state (after toggle)
        is_active = button.get_active()
        
        # If activating subscript, ensure superscript is deactivated
        if is_active and win.superscript_button.get_active():
            # Block superscript handler to prevent infinite loop
            if win.superscript_handler_id is not None:
                win.superscript_button.handler_block(win.superscript_handler_id)
            
            # Deactivate superscript button
            win.superscript_button.set_active(False)
            
            # Unblock superscript handler
            if win.superscript_handler_id is not None:
                win.superscript_button.handler_unblock(win.superscript_handler_id)
        
        # Apply formatting
        self.execute_js(win, "document.execCommand('subscript', false, null);")
        
        # Check if find bar has focus before setting focus to webview
        find_bar_active = win.find_bar_revealer.get_reveal_child()
        find_entry_has_focus = False
        
        if find_bar_active:
            find_entry_has_focus = win.find_entry.has_focus() or win.replace_entry.has_focus()
        
        # Only grab focus to webview if find entries don't have focus
        if not find_entry_has_focus:
            win.webview.grab_focus()
    finally:
        # Unblock the handler
        if win.subscript_handler_id is not None:
            button.handler_unblock(win.subscript_handler_id)

# Update the superscript toggle handler to deactivate subscript if needed
def on_superscript_toggled(self, win, button):
    """Handle superscript toggle button state changes"""
    # Block the handler temporarily
    if win.superscript_handler_id is not None:
        button.handler_block(win.superscript_handler_id)
    
    try:
        # Get current button state (after toggle)
        is_active = button.get_active()
        
        # If activating superscript, ensure subscript is deactivated
        if is_active and win.subscript_button.get_active():
            # Block subscript handler to prevent infinite loop
            if win.subscript_handler_id is not None:
                win.subscript_button.handler_block(win.subscript_handler_id)
            
            # Deactivate subscript button
            win.subscript_button.set_active(False)
            
            # Unblock subscript handler
            if win.subscript_handler_id is not None:
                win.subscript_button.handler_unblock(win.subscript_handler_id)
        
        # Apply formatting
        self.execute_js(win, "document.execCommand('superscript', false, null);")
        
        # Check if find bar has focus before setting focus to webview
        find_bar_active = win.find_bar_revealer.get_reveal_child()
        find_entry_has_focus = False
        
        if find_bar_active:
            find_entry_has_focus = win.find_entry.has_focus() or win.replace_entry.has_focus()
        
        # Only grab focus to webview if find entries don't have focus
        if not find_entry_has_focus:
            win.webview.grab_focus()
    finally:
        # Unblock the handler
        if win.superscript_handler_id is not None:
            button.handler_unblock(win.superscript_handler_id)


def on_formatting_changed(self, win, manager, result):
    """Update toggle button states based on current formatting"""
    try:
        # Extract the message differently based on WebKit version
        message = None
        if hasattr(result, 'get_js_value'):
            message = result.get_js_value().to_string()
        elif hasattr(result, 'to_string'):
            message = result.to_string()
        elif hasattr(result, 'get_value'):
            message = result.get_value().get_string()
        else:
            # Try to get the value directly
            try:
                message = str(result)
            except:
                print("Could not extract message from result")
                return
        
        # Parse the JSON
        import json
        format_state = json.loads(message)
        
        # Update basic formatting button states without triggering their handlers
        if win.bold_handler_id is not None:
            win.bold_button.handler_block(win.bold_handler_id)
            win.bold_button.set_active(format_state.get('bold', False))
            win.bold_button.handler_unblock(win.bold_handler_id)
        
        if win.italic_handler_id is not None:
            win.italic_button.handler_block(win.italic_handler_id)
            win.italic_button.set_active(format_state.get('italic', False))
            win.italic_button.handler_unblock(win.italic_handler_id)
        
        if win.underline_handler_id is not None:
            win.underline_button.handler_block(win.underline_handler_id)
            win.underline_button.set_active(format_state.get('underline', False))
            win.underline_button.handler_unblock(win.underline_handler_id)
            
        if win.strikeout_handler_id is not None:
            win.strikeout_button.handler_block(win.strikeout_handler_id)
            win.strikeout_button.set_active(format_state.get('strikeThrough', False))
            win.strikeout_button.handler_unblock(win.strikeout_handler_id)
        
        # Update subscript and superscript buttons
        if win.subscript_handler_id is not None:
            win.subscript_button.handler_block(win.subscript_handler_id)
            win.subscript_button.set_active(format_state.get('subscript', False))
            win.subscript_button.handler_unblock(win.subscript_handler_id)
            
        if win.superscript_handler_id is not None:
            win.superscript_button.handler_block(win.superscript_handler_id)
            win.superscript_button.set_active(format_state.get('superscript', False))
            win.superscript_button.handler_unblock(win.superscript_handler_id)
        
        # Update list button states if they exist
        if hasattr(win, 'bullet_list_button') and hasattr(win.bullet_list_button, 'handler_id'):
            win.bullet_list_button.handler_block(win.bullet_list_button.handler_id)
            win.bullet_list_button.set_active(format_state.get('bulletList', False))
            win.bullet_list_button.handler_unblock(win.bullet_list_button.handler_id)
        
        if hasattr(win, 'numbered_list_button') and hasattr(win.numbered_list_button, 'handler_id'):
            win.numbered_list_button.handler_block(win.numbered_list_button.handler_id)
            win.numbered_list_button.set_active(format_state.get('numberedList', False))
            win.numbered_list_button.handler_unblock(win.numbered_list_button.handler_id)
        
        # Update alignment button states
        if hasattr(win, 'alignment_buttons'):
            current_alignment = format_state.get('alignment', 'left')
            for align_type, button in win.alignment_buttons.items():
                if hasattr(button, 'handler_id'):
                    button.handler_block(button.handler_id)
                    button.set_active(align_type == current_alignment)
                    button.handler_unblock(button.handler_id)
        
        # Update paragraph style dropdown
        paragraph_style = format_state.get('paragraphStyle', 'Normal')
        if win.paragraph_style_handler_id is not None and hasattr(win, 'paragraph_style_dropdown'):
            # Map paragraph style to dropdown index
            style_indices = {
                'Normal': 0,
                'Heading 1': 1,
                'Heading 2': 2,
                'Heading 3': 3,
                'Heading 4': 4,
                'Heading 5': 5,
                'Heading 6': 6
            }
            index = style_indices.get(paragraph_style, 0)
            
            # Update the dropdown without triggering the handler
            win.paragraph_style_dropdown.handler_block(win.paragraph_style_handler_id)
            win.paragraph_style_dropdown.set_selected(index)
            win.paragraph_style_dropdown.handler_unblock(win.paragraph_style_handler_id)
        
        # Update font family dropdown
        font_family = format_state.get('fontFamily', '')
        if win.font_handler_id is not None and hasattr(win, 'font_dropdown') and font_family:
            # Find the index of the font in the dropdown
            font_model = win.font_dropdown.get_model()
            found_index = -1
            
            # Iterate through the model to find the matching font
            for i in range(font_model.get_n_items()):
                item = font_model.get_item(i)
                if item and item.get_string().lower() == font_family.lower():
                    found_index = i
                    break
            
            if found_index >= 0:
                # Update the dropdown without triggering the handler
                win.font_dropdown.handler_block(win.font_handler_id)
                win.font_dropdown.set_selected(found_index)
                win.font_dropdown.handler_unblock(win.font_handler_id)
        
        # Update font size dropdown
        font_size = format_state.get('fontSize', '')
        if win.font_size_handler_id is not None and hasattr(win, 'font_size_dropdown') and font_size:
            # Find the index of the size in the dropdown
            size_model = win.font_size_dropdown.get_model()
            found_index = -1
            
            # Iterate through the model to find the matching size
            for i in range(size_model.get_n_items()):
                item = size_model.get_item(i)
                if item and item.get_string() == font_size:
                    found_index = i
                    break
            
            if found_index >= 0:
                # Update the dropdown without triggering the handler
                win.font_size_dropdown.handler_block(win.font_size_handler_id)
                win.font_size_dropdown.set_selected(found_index)
                win.font_size_dropdown.handler_unblock(win.font_size_handler_id)
            
    except Exception as e:
        print(f"Error updating formatting buttons: {e}")


def on_indent_clicked(self, win, button):
    """Handle indent button click"""
    js_code = """
    (function() {
        document.execCommand('indent', false, null);
        return true;
    })();
    """
    
    self.execute_js(win, js_code)
    win.statusbar.set_text("Increased indent")
    win.webview.grab_focus()

def on_outdent_clicked(self, win, button):
    """Handle outdent button click"""
    js_code = """
    (function() {
        document.execCommand('outdent', false, null);
        return true;
    })();
    """
    
    self.execute_js(win, js_code)
    win.statusbar.set_text("Decreased indent")
    win.webview.grab_focus()

def on_bullet_list_toggled(self, win, button):
    """Handle bullet list button toggle"""
    js_code = """
    (function() {
        document.execCommand('insertUnorderedList', false, null);
        return document.queryCommandState('insertUnorderedList');
    })();
    """
    
    self.execute_js(win, js_code)
    win.statusbar.set_text("Toggled bullet list")
    win.webview.grab_focus()

def on_numbered_list_toggled(self, win, button):
    """Handle numbered list button toggle"""
    js_code = """
    (function() {
        document.execCommand('insertOrderedList', false, null);
        return document.queryCommandState('insertOrderedList');
    })();
    """
    
    self.execute_js(win, js_code)
    win.statusbar.set_text("Toggled numbered list")
    win.webview.grab_focus()

def _update_alignment_buttons(self, win, active_alignment):
    """Update alignment toggle button states"""
    for align_type, button in win.alignment_buttons.items():
        # Temporarily block signal handlers to prevent recursion
        handler_id = button.handler_id if hasattr(button, 'handler_id') else None
        if handler_id:
            button.handler_block(handler_id)
        
        # Set active state based on current alignment
        button.set_active(align_type == active_alignment)
        
        # Unblock signal handlers
        if handler_id:
            button.handler_unblock(handler_id)

def on_align_left_toggled(self, win, button):
    """Handle align left button toggle"""
    # Execute alignment command with list support
    js_code = """
    (function() {
        applyAlignmentWithListSupport('left');
        return 'left';  // Return the alignment type
        
        function applyAlignmentWithListSupport(alignment) {
            // Get the current selection
            const selection = window.getSelection();
            if (selection.rangeCount === 0) return;
            
            const range = selection.getRangeAt(0);
            
            // First, apply standard alignment using execCommand
            document.execCommand('justifyLeft', false, null);
            
            // Get all affected list elements
            const commonAncestor = range.commonAncestorContainer;
            let container;
            
            if (commonAncestor.nodeType === 3) { // Text node
                container = commonAncestor.parentNode;
            } else {
                container = commonAncestor;
            }
            
            // Find if we're dealing with a list
            const listContainer = findListContainer(container);
            
            if (listContainer) {
                // Apply additional CSS for list alignment
                const listItems = listContainer.querySelectorAll('li');
                listItems.forEach(li => {
                    // Set the CSS for list item alignment
                    li.style.textAlign = 'left';
                    li.style.listStylePosition = 'outside'; // Default
                });
                
                // Reset the list container padding/margin
                listContainer.style.paddingLeft = '';
                listContainer.style.marginLeft = '';
            }
        }
        
        // Helper function to find the list container (ul/ol)
        function findListContainer(element) {
            while (element && element !== document.body) {
                if (element.tagName === 'UL' || element.tagName === 'OL') {
                    return element;
                }
                element = element.parentNode;
            }
            return null;
        }
    })();
    """
    
    self.execute_js(win, js_code)
    
    # Update all alignment buttons
    self._update_alignment_buttons(win, 'left')
    
    win.statusbar.set_text("Aligned text left")
    win.webview.grab_focus()

def on_align_center_toggled(self, win, button):
    """Handle align center button toggle"""
    # Execute alignment command with list support
    js_code = """
    (function() {
        applyAlignmentWithListSupport('center');
        return 'center';  // Return the alignment type
        
        function applyAlignmentWithListSupport(alignment) {
            // Get the current selection
            const selection = window.getSelection();
            if (selection.rangeCount === 0) return;
            
            const range = selection.getRangeAt(0);
            
            // First, apply standard alignment using execCommand
            document.execCommand('justifyCenter', false, null);
            
            // Get all affected list elements
            const commonAncestor = range.commonAncestorContainer;
            let container;
            
            if (commonAncestor.nodeType === 3) { // Text node
                container = commonAncestor.parentNode;
            } else {
                container = commonAncestor;
            }
            
            // Find if we're dealing with a list
            const listContainer = findListContainer(container);
            
            if (listContainer) {
                // Apply additional CSS for list alignment
                const listItems = listContainer.querySelectorAll('li');
                listItems.forEach(li => {
                    // Set the CSS for list item alignment
                    li.style.textAlign = 'center';
                    li.style.listStylePosition = 'inside';
                });
                
                // Adjust the list container too
                listContainer.style.paddingLeft = '0';
                listContainer.style.marginLeft = '0';
            }
        }
        
        // Helper function to find the list container (ul/ol)
        function findListContainer(element) {
            while (element && element !== document.body) {
                if (element.tagName === 'UL' || element.tagName === 'OL') {
                    return element;
                }
                element = element.parentNode;
            }
            return null;
        }
    })();
    """
    
    self.execute_js(win, js_code)
    
    # Update all alignment buttons
    self._update_alignment_buttons(win, 'center')
    
    win.statusbar.set_text("Aligned text center")
    win.webview.grab_focus()

def on_align_right_toggled(self, win, button):
    """Handle align right button toggle"""
    # Execute alignment command with list support
    js_code = """
    (function() {
        applyAlignmentWithListSupport('right');
        return 'right';  // Return the alignment type
        
        function applyAlignmentWithListSupport(alignment) {
            // Get the current selection
            const selection = window.getSelection();
            if (selection.rangeCount === 0) return;
            
            const range = selection.getRangeAt(0);
            
            // First, apply standard alignment using execCommand
            document.execCommand('justifyRight', false, null);
            
            // Get all affected list elements
            const commonAncestor = range.commonAncestorContainer;
            let container;
            
            if (commonAncestor.nodeType === 3) { // Text node
                container = commonAncestor.parentNode;
            } else {
                container = commonAncestor;
            }
            
            // Find if we're dealing with a list
            const listContainer = findListContainer(container);
            
            if (listContainer) {
                // Apply additional CSS for list alignment
                const listItems = listContainer.querySelectorAll('li');
                listItems.forEach(li => {
                    // Set the CSS for list item alignment
                    li.style.textAlign = 'right';
                    li.style.listStylePosition = 'inside';
                });
                
                // Adjust the list container too
                listContainer.style.paddingLeft = '0';
                listContainer.style.marginLeft = '0';
            }
        }
        
        // Helper function to find the list container (ul/ol)
        function findListContainer(element) {
            while (element && element !== document.body) {
                if (element.tagName === 'UL' || element.tagName === 'OL') {
                    return element;
                }
                element = element.parentNode;
            }
            return null;
        }
    })();
    """
    
    self.execute_js(win, js_code)
    
    # Update all alignment buttons
    self._update_alignment_buttons(win, 'right')
    
    win.statusbar.set_text("Aligned text right")
    win.webview.grab_focus()

def on_align_justify_toggled(self, win, button):
    """Handle justify button toggle"""
    # Execute alignment command with list support
    js_code = """
    (function() {
        applyAlignmentWithListSupport('justify');
        return 'justify';  // Return the alignment type
        
        function applyAlignmentWithListSupport(alignment) {
            // Get the current selection
            const selection = window.getSelection();
            if (selection.rangeCount === 0) return;
            
            const range = selection.getRangeAt(0);
            
            // First, apply standard alignment using execCommand
            document.execCommand('justifyFull', false, null);
            
            // Get all affected list elements
            const commonAncestor = range.commonAncestorContainer;
            let container;
            
            if (commonAncestor.nodeType === 3) { // Text node
                container = commonAncestor.parentNode;
            } else {
                container = commonAncestor;
            }
            
            // Find if we're dealing with a list
            const listContainer = findListContainer(container);
            
            if (listContainer) {
                // Apply additional CSS for list alignment
                const listItems = listContainer.querySelectorAll('li');
                listItems.forEach(li => {
                    // Set the CSS for list item alignment
                    li.style.textAlign = 'justify';
                    li.style.listStylePosition = 'inside';
                });
                
                // Adjust the list container too
                listContainer.style.paddingLeft = '0';
                listContainer.style.marginLeft = '0';
            }
        }
        
        // Helper function to find the list container (ul/ol)
        function findListContainer(element) {
            while (element && element !== document.body) {
                if (element.tagName === 'UL' || element.tagName === 'OL') {
                    return element;
                }
                element = element.parentNode;
            }
            return null;
        }
    })();
    """
    
    self.execute_js(win, js_code)
    
    # Update all alignment buttons
    self._update_alignment_buttons(win, 'justify')
    
    win.statusbar.set_text("Justified text")
    win.webview.grab_focus()

# Also fix the _update_alignment_buttons method
def _update_alignment_buttons(self, win, active_alignment):
    """Update alignment toggle button states"""
    for align_type, button in win.alignment_buttons.items():
        # Each button should have its handler_id stored directly
        if hasattr(button, 'handler_id'):
            button.handler_block(button.handler_id)
        
        # Set active state based on current alignment
        button.set_active(align_type == active_alignment)
        
        # Unblock signal handlers
        if hasattr(button, 'handler_id'):
            button.handler_unblock(button.handler_id)

# Update the selection_change_js method to also track list and alignment states
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
            
            // Get list states
            const isUnorderedList = document.queryCommandState('insertUnorderedList');
            const isOrderedList = document.queryCommandState('insertOrderedList');
            
            // Get alignment states
            const isJustifyLeft = document.queryCommandState('justifyLeft');
            const isJustifyCenter = document.queryCommandState('justifyCenter');
            const isJustifyRight = document.queryCommandState('justifyRight');
            const isJustifyFull = document.queryCommandState('justifyFull');
            
            // Determine the current alignment
            let currentAlignment = 'left'; // Default
            if (isJustifyCenter) currentAlignment = 'center';
            else if (isJustifyRight) currentAlignment = 'right';
            else if (isJustifyFull) currentAlignment = 'justify';
            
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
            
            // Send the state to Python - Now including list and alignment states
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
                    fontSize: fontSize,
                    bulletList: isUnorderedList,
                    numberedList: isOrderedList,
                    alignment: currentAlignment
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
# ---- PARAGRAPH STYLE HANDLER ----
def on_paragraph_style_changed(self, win, dropdown):
    """Handle paragraph style dropdown change"""
    # Get selected style index
    selected = dropdown.get_selected()
    
    # Map selected index to HTML tag
    style_tags = {
        0: "p",       # Normal
        1: "h1",      # Heading 1
        2: "h2",      # Heading 2
        3: "h3",      # Heading 3
        4: "h4",      # Heading 4
        5: "h5",      # Heading 5
        6: "h6"       # Heading 6
    }
    
    # Get the tag to apply
    tag = style_tags.get(selected, "p")
    
    # Apply the selected style using formatBlock command
    js_code = f"""
    (function() {{
        document.execCommand('formatBlock', false, '<{tag}>');
        return true;
    }})();
    """
    
    self.execute_js(win, js_code)
    win.statusbar.set_text(f"Applied {dropdown.get_selected_item().get_string()} style")
    win.webview.grab_focus()

# ---- FONT FAMILY HANDLER ----
def on_font_changed(self, win, dropdown):
    """Handle font family dropdown change"""
    # Get the selected font
    selected_item = dropdown.get_selected_item()
    
    # Skip if it's a separator
    if selected_item.get_string() == "──────────":
        # Revert to previous selection
        if hasattr(win, 'previous_font_selection'):
            dropdown.set_selected(win.previous_font_selection)
        return
    
    # Store current selection for future reference
    win.previous_font_selection = dropdown.get_selected()
    
    # Get the font name
    font_name = selected_item.get_string()
    
    # Apply the font family
    js_code = f"""
    (function() {{
        document.execCommand('fontName', false, '{font_name}');
        return true;
    }})();
    """
    
    self.execute_js(win, js_code)
    win.statusbar.set_text(f"Applied font: {font_name}")
    win.webview.grab_focus()

# ---- FONT SIZE HANDLER ----
def on_font_size_changed(self, win, dropdown):
    """Handle font size dropdown change using direct font-size styling"""
    # Get the selected size
    selected_item = dropdown.get_selected_item()
    size_pt = selected_item.get_string()
    
    # Apply font size using execCommand with proper style attribute
    js_code = f"""
    (function() {{
        // Get the editor
        const editor = document.getElementById('editor');
        const selection = window.getSelection();
        
        if (selection.rangeCount > 0) {{
            const range = selection.getRangeAt(0);
            
            // If text is selected
            if (!range.collapsed) {{
                // Use execCommand to apply the font size
                document.execCommand('fontSize', false, '7');
                
                // Find all font elements with size=7 and set the correct size
                const fontElements = editor.querySelectorAll('font[size="7"]');
                for (const font of fontElements) {{
                    font.removeAttribute('size');
                    font.style.fontSize = '{size_pt}pt';
                }}
                
                // Clean up redundant nested font tags
                cleanupEditorTags();
                
                // Record undo state
                saveState();
                window.lastContent = editor.innerHTML;
                window.redoStack = [];
                try {{
                    window.webkit.messageHandlers.contentChanged.postMessage("changed");
                }} catch(e) {{
                    console.log("Could not notify about changes:", e);
                }}
            }} else {{
                // For cursor position (no selection)
                // Store font size for next character
                editor.setAttribute('data-next-font-size', '{size_pt}pt');
                
                // Add handler for next input
                const handleInput = function(e) {{
                    // Remove the handler after first use
                    editor.removeEventListener('input', handleInput);
                    
                    // Get the font size
                    const fontSize = editor.getAttribute('data-next-font-size');
                    if (!fontSize) return;
                    
                    // Get the current selection
                    const sel = window.getSelection();
                    if (sel.rangeCount > 0) {{
                        // Try to select the last character typed
                        const range = sel.getRangeAt(0);
                        if (range.startOffset > 0) {{
                            try {{
                                // Select the last character
                                range.setStart(range.startContainer, range.startOffset - 1);
                                
                                // Apply font size
                                document.execCommand('fontSize', false, '7');
                                
                                // Update the font elements
                                const fontElements = editor.querySelectorAll('font[size="7"]');
                                for (const font of fontElements) {{
                                    font.removeAttribute('size');
                                    font.style.fontSize = fontSize;
                                }}
                                
                                // Restore cursor position
                                range.collapse(false);
                                sel.removeAllRanges();
                                sel.addRange(range);
                                
                                // Clean up tags
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
                        }}
                    }}
                }};
                
                editor.addEventListener('input', handleInput);
            }}
        }}
        
        // Combined function to clean up tags
        function cleanupEditorTags() {{
            // Clean up redundant nested font tags
            function cleanupNestedFontTags() {{
                const fontTags = editor.querySelectorAll('font');
                
                // Process each font tag
                for (let i = 0; i < fontTags.length; i++) {{
                    const font = fontTags[i];
                    
                    // Check if this font tag has nested font tags
                    const nestedFonts = font.querySelectorAll('font');
                    
                    for (let j = 0; j < nestedFonts.length; j++) {{
                        const nestedFont = nestedFonts[j];
                        
                        // If nested font has no attributes, replace it with its contents
                        if (!nestedFont.hasAttribute('style') && 
                            !nestedFont.hasAttribute('face') && 
                            !nestedFont.hasAttribute('color') &&
                            !nestedFont.hasAttribute('size')) {{
                            
                            const fragment = document.createDocumentFragment();
                            while (nestedFont.firstChild) {{
                                fragment.appendChild(nestedFont.firstChild);
                            }}
                            
                            nestedFont.parentNode.replaceChild(fragment, nestedFont);
                        }}
                    }}
                }}
            }}
            
            // Clean up empty tags
            function cleanupEmptyTags() {{
                // Find all font and span elements
                const elements = [...editor.querySelectorAll('font'), ...editor.querySelectorAll('span')];
                
                // Process in reverse to handle nested elements
                for (let i = elements.length - 1; i >= 0; i--) {{
                    const el = elements[i];
                    if (el.textContent.trim() === '') {{
                        el.parentNode.removeChild(el);
                    }}
                }}
            }}
            
            // Run the cleanup functions multiple times to handle nested cases
            for (let i = 0; i < 2; i++) {{
                cleanupNestedFontTags();
                cleanupEmptyTags();
            }}
        }}
        
        return true;
    }})();
    """
    
    # Execute the JavaScript code
    self.execute_js(win, js_code)
    
    # Run another cleanup after a short delay to catch any remaining issues
    GLib.timeout_add(100, lambda: self.cleanup_editor_tags(win))
    
    win.statusbar.set_text(f"Applied font size: {size_pt}pt")
    win.webview.grab_focus()

def cleanup_editor_tags(self, win):
    """Clean up both empty tags and redundant nested font tags in the editor content"""
    js_code = """
    (function() {
        // Get the editor
        const editor = document.getElementById('editor');
        
        // Clean up redundant nested font tags
        function cleanupNestedFontTags() {
            const fontTags = editor.querySelectorAll('font');
            
            // Process each font tag
            for (let i = 0; i < fontTags.length; i++) {
                const font = fontTags[i];
                
                // Check if this font tag has nested font tags
                const nestedFonts = font.querySelectorAll('font');
                
                for (let j = 0; j < nestedFonts.length; j++) {
                    const nestedFont = nestedFonts[j];
                    
                    // If nested font has no attributes, replace it with its contents
                    if (!nestedFont.hasAttribute('style') && 
                        !nestedFont.hasAttribute('face') && 
                        !nestedFont.hasAttribute('color') &&
                        !nestedFont.hasAttribute('size')) {
                        
                        const fragment = document.createDocumentFragment();
                        while (nestedFont.firstChild) {
                            fragment.appendChild(nestedFont.firstChild);
                        }
                        
                        nestedFont.parentNode.replaceChild(fragment, nestedFont);
                    }
                }
            }
        }
        
        // Clean up empty tags
        function cleanupEmptyTags() {
            // Find all font and span elements
            const elements = [...editor.querySelectorAll('font'), ...editor.querySelectorAll('span')];
            
            // Process in reverse to handle nested elements
            for (let i = elements.length - 1; i >= 0; i--) {
                const el = elements[i];
                if (el.textContent.trim() === '') {
                    el.parentNode.removeChild(el);
                }
            }
        }
        
        // Run the cleanup functions multiple times to handle nested cases
        for (let i = 0; i < 3; i++) {
            cleanupNestedFontTags();
            cleanupEmptyTags();
        }
        
        return true;
    })();
    """
    self.execute_js(win, js_code)
    
def create_color_button(self, color_hex):
    """Create a button with a color swatch"""
    button = Gtk.Button()
    button.set_size_request(18, 18)
    
    # Create a colored box
    color_box = Gtk.Box()
    color_box.set_size_request(16, 16)
    color_box.add_css_class("color-box")
    
    # Set the background color
    css_provider = Gtk.CssProvider()
    css = f".color-box {{ background-color: {color_hex}; border: 1px solid rgba(0,0,0,0.2); border-radius: 2px; }}"
    css_provider.load_from_data(css.encode())
    
    # Apply the CSS
    style_context = color_box.get_style_context()
    style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    
    button.set_child(color_box)
    return button

def on_font_color_button_clicked(self, win):
    """Handle font color button click (the main button, not the dropdown)"""
    # Get the currently selected color from the indicator
    if hasattr(win, 'current_font_color'):
        color_hex = win.current_font_color
    else:
        color_hex = "#000000"  # Default to black
        win.current_font_color = color_hex
    
    # Apply color to selected text
    self.apply_font_color(win, color_hex)

def on_font_color_selected(self, win, color_hex, popover):
    """Handle selection of a specific font color"""
    # Save the current color
    win.current_font_color = color_hex
    
    # Update the indicator color
    rgba = Gdk.RGBA()
    rgba.parse(color_hex)
    self.set_box_color(win.font_color_indicator, rgba)
    
    # Apply color to selected text
    self.apply_font_color(win, color_hex)
    
    # Close the popover
    popover.popdown()

def on_font_color_automatic_clicked(self, win, popover):
    """Reset font color to automatic (remove color formatting)"""
    # Reset the stored color preference 
    win.current_font_color = "inherit"
    
    # Set the indicator color back to black (representing automatic)
    rgba = Gdk.RGBA()
    rgba.parse("#000000")
    self.set_box_color(win.font_color_indicator, rgba)
    
    # Apply to selected text
    self.apply_font_color(win, "inherit")
    
    # Close the popover
    popover.popdown()

def on_more_font_colors_clicked(self, win, popover):
    """Show a color chooser dialog for more font colors"""
    # Close the popover first
    popover.popdown()
    
    # Create a color chooser dialog
    dialog = Gtk.ColorDialog()
    dialog.set_title("Select Text Color")
    
    # Get the current color to use as default
    if hasattr(win, 'current_font_color') and win.current_font_color != "inherit":
        rgba = Gdk.RGBA()
        rgba.parse(win.current_font_color)
    else:
        rgba = Gdk.RGBA()
        rgba.parse("#000000")  # Default black
    
    # Show the dialog asynchronously
    dialog.choose_rgba(
        win,  # parent window
        rgba,  # initial color
        None,  # cancellable
        lambda dialog, result: self.on_font_color_dialog_response(win, dialog, result)
    )

def on_font_color_dialog_response(self, win, dialog, result):
    """Handle response from the font color chooser dialog"""
    try:
        rgba = dialog.choose_rgba_finish(result)
        if rgba:
            # Convert RGBA to hex
            color_hex = "#{:02x}{:02x}{:02x}".format(
                int(rgba.red * 255),
                int(rgba.green * 255),
                int(rgba.blue * 255)
            )
            
            # Update current color
            win.current_font_color = color_hex
            
            # Update indicator color
            self.set_box_color(win.font_color_indicator, rgba)
            
            # Apply to selected text
            self.apply_font_color(win, color_hex)
    except GLib.Error as error:
        # Handle errors, e.g., user cancelled
        pass

def apply_font_color(self, win, color_hex):
    """Apply selected font color to text or set it for future typing"""
    js_code = f"""
    (function() {{
        // Get the editor
        const editor = document.getElementById('editor');
        const selection = window.getSelection();
        
        if (selection.rangeCount > 0) {{
            const range = selection.getRangeAt(0);
            
            // If text is selected
            if (!range.collapsed) {{
                // Use execCommand to apply the color
                document.execCommand('foreColor', false, '{color_hex}');
                
                // Clean up redundant nested tags
                cleanupEditorTags();
                
                // Record undo state
                saveState();
                window.lastContent = editor.innerHTML;
                window.redoStack = [];
                try {{
                    window.webkit.messageHandlers.contentChanged.postMessage("changed");
                }} catch(e) {{
                    console.log("Could not notify about changes:", e);
                }}
            }} else {{
                // For cursor position (no selection)
                // Store color for next character
                editor.setAttribute('data-next-font-color', '{color_hex}');
                
                // Add handler for next input
                const handleInput = function(e) {{
                    // Remove the handler after first use
                    editor.removeEventListener('input', handleInput);
                    
                    // Get the color
                    const fontColor = editor.getAttribute('data-next-font-color');
                    if (!fontColor) return;
                    
                    // Get the current selection
                    const sel = window.getSelection();
                    if (sel.rangeCount > 0) {{
                        // Try to select the last character typed
                        const range = sel.getRangeAt(0);
                        if (range.startOffset > 0) {{
                            try {{
                                // Select the last character
                                range.setStart(range.startContainer, range.startOffset - 1);
                                
                                // Apply color
                                document.execCommand('foreColor', false, fontColor);
                                
                                // Restore cursor position
                                range.collapse(false);
                                sel.removeAllRanges();
                                sel.addRange(range);
                                
                                // Clean up tags
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
                                console.error("Error applying font color:", error);
                            }}
                        }}
                    }}
                }};
                
                editor.addEventListener('input', handleInput);
            }}
        }}
        
        return true;
    }})();
    """
    
    self.execute_js(win, js_code)
    win.statusbar.set_text(f"Text color set to: {color_hex}")
    win.webview.grab_focus()

def on_bg_color_button_clicked(self, win):
    """Handle background color button click (the main button, not the dropdown)"""
    # Get the currently selected color from the indicator
    if hasattr(win, 'current_bg_color'):
        color_hex = win.current_bg_color
    else:
        color_hex = "#FFFF00"  # Default to yellow
        win.current_bg_color = color_hex
    
    # Apply color to selected text
    self.apply_bg_color(win, color_hex)

def on_bg_color_selected(self, win, color_hex, popover):
    """Handle selection of a specific background color"""
    # Save the current color
    win.current_bg_color = color_hex
    
    # Update the indicator color
    rgba = Gdk.RGBA()
    rgba.parse(color_hex)
    self.set_box_color(win.bg_color_indicator, rgba)
    
    # Apply color to selected text
    self.apply_bg_color(win, color_hex)
    
    # Close the popover
    popover.popdown()

def on_bg_color_automatic_clicked(self, win, popover):
    """Reset background color to automatic (remove background color formatting)"""
    # Reset the stored color preference
    win.current_bg_color = "transparent"
    
    # Set the indicator color to transparent
    rgba = Gdk.RGBA()
    rgba.parse("transparent")
    self.set_box_color(win.bg_color_indicator, rgba)
    
    # Apply to selected text
    self.apply_bg_color(win, "transparent")
    
    # Close the popover
    popover.popdown()

def on_more_bg_colors_clicked(self, win, popover):
    """Show a color chooser dialog for more background colors"""
    # Close the popover first
    popover.popdown()
    
    # Create a color chooser dialog
    dialog = Gtk.ColorDialog()
    dialog.set_title("Select Background Color")
    
    # Get the current color to use as default
    if hasattr(win, 'current_bg_color') and win.current_bg_color != "transparent":
        rgba = Gdk.RGBA()
        rgba.parse(win.current_bg_color)
    else:
        rgba = Gdk.RGBA()
        rgba.parse("#FFFF00")  # Default yellow
    
    # Show the dialog asynchronously
    dialog.choose_rgba(
        win,  # parent window
        rgba,  # initial color
        None,  # cancellable
        lambda dialog, result: self.on_bg_color_dialog_response(win, dialog, result)
    )

def on_bg_color_dialog_response(self, win, dialog, result):
    """Handle response from the background color chooser dialog"""
    try:
        rgba = dialog.choose_rgba_finish(result)
        if rgba:
            # Convert RGBA to hex
            color_hex = "#{:02x}{:02x}{:02x}".format(
                int(rgba.red * 255),
                int(rgba.green * 255),
                int(rgba.blue * 255)
            )
            
            # Update current color
            win.current_bg_color = color_hex
            
            # Update indicator color
            self.set_box_color(win.bg_color_indicator, rgba)
            
            # Apply to selected text
            self.apply_bg_color(win, color_hex)
    except GLib.Error as error:
        # Handle errors, e.g., user cancelled
        pass

def apply_bg_color(self, win, color_hex):
    """Apply selected background color to text or set it for future typing"""
    js_code = f"""
    (function() {{
        // Get the editor
        const editor = document.getElementById('editor');
        const selection = window.getSelection();
        
        if (selection.rangeCount > 0) {{
            const range = selection.getRangeAt(0);
            
            // If text is selected
            if (!range.collapsed) {{
                // Use execCommand to apply the background color
                document.execCommand('hiliteColor', false, '{color_hex}');
                
                // Clean up redundant nested tags
                cleanupEditorTags();
                
                // Record undo state
                saveState();
                window.lastContent = editor.innerHTML;
                window.redoStack = [];
                try {{
                    window.webkit.messageHandlers.contentChanged.postMessage("changed");
                }} catch(e) {{
                    console.log("Could not notify about changes:", e);
                }}
            }} else {{
                // For cursor position (no selection)
                // Store color for next character
                editor.setAttribute('data-next-bg-color', '{color_hex}');
                
                // Add handler for next input
                const handleInput = function(e) {{
                    // Remove the handler after first use
                    editor.removeEventListener('input', handleInput);
                    
                    // Get the color
                    const bgColor = editor.getAttribute('data-next-bg-color');
                    if (!bgColor) return;
                    
                    // Get the current selection
                    const sel = window.getSelection();
                    if (sel.rangeCount > 0) {{
                        // Try to select the last character typed
                        const range = sel.getRangeAt(0);
                        if (range.startOffset > 0) {{
                            try {{
                                // Select the last character
                                range.setStart(range.startContainer, range.startOffset - 1);
                                
                                // Apply background color
                                document.execCommand('hiliteColor', false, bgColor);
                                
                                // Restore cursor position
                                range.collapse(false);
                                sel.removeAllRanges();
                                sel.addRange(range);
                                
                                // Clean up tags
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
                                console.error("Error applying background color:", error);
                            }}
                        }}
                    }}
                }};
                
                editor.addEventListener('input', handleInput);
            }}
        }}
        
        return true;
    }})();
    """
    
    self.execute_js(win, js_code)
    win.statusbar.set_text(f"Background color set to: {color_hex}")
    win.webview.grab_focus()
    
def set_box_color(self, box, color):
    """Set the background color of a box using CSS"""
    # Create a CSS provider
    css_provider = Gtk.CssProvider()
    
    # Generate CSS based on color
    if isinstance(color, Gdk.RGBA):
        if color.alpha == 0:  # Transparent
            css = ".color-indicator { background-color: transparent; border: 1px dashed rgba(127, 127, 127, 0.5); }"
        else:
            css = f".color-indicator {{ background-color: rgba({int(color.red*255)}, {int(color.green*255)}, {int(color.blue*255)}, {color.alpha}); }}"
    elif color == "transparent":
        css = ".color-indicator { background-color: transparent; border: 1px dashed rgba(127, 127, 127, 0.5); }"
    else:
        css = f".color-indicator {{ background-color: {color}; }}"
    
    # Load the CSS
    css_provider.load_from_data(css.encode())
    
    # Apply to the box
    style_context = box.get_style_context()
    style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

def on_clear_formatting_clicked(self, win, button):
    """Remove all character formatting from selected text while preserving structure and selection"""
    js_code = """
    (function() {
        // Use the Selection API
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            
            // Check if there's selected text
            if (!range.collapsed) {
                try {
                    // Store the current selection
                    const originalRange = range.cloneRange();
                    
                    // Get the editor
                    const editor = document.getElementById('editor');
                    
                    // Create a document fragment containing the selection
                    const fragment = originalRange.cloneContents();
                    
                    // Create a temporary div to work with the content
                    const tempDiv = document.createElement('div');
                    tempDiv.appendChild(fragment);
                    
                    // Store the original HTML with structure
                    const originalHTML = tempDiv.innerHTML;
                    
                    // Apply removeFormat command which preserves structure
                    document.execCommand('removeFormat');
                    
                    // Also remove font tags and specific inline styles
                    // without using insertText (which destroys structure)
                    const nodes = selection.getRangeAt(0).commonAncestorContainer.querySelectorAll(
                        'span[style], font, b, i, u, strike, strong, em, sub, sup'
                    );
                    
                    // Process nodes that are within our selection
                    for (const node of nodes) {
                        if (selection.containsNode(node, true)) {
                            // Replace the node with its text content
                            if (node.innerHTML && node.innerHTML.trim()) {
                                const wrapper = document.createElement(node.nodeName === 'DIV' ? 'div' : 'span');
                                wrapper.innerHTML = node.innerHTML;
                                node.parentNode.replaceChild(wrapper, node);
                            }
                        }
                    }
                    
                    // Clean up empty and redundant spans
                    setTimeout(() => {
                        const emptySpans = editor.querySelectorAll('span:empty');
                        for (const span of emptySpans) {
                            if (span.parentNode) {
                                span.parentNode.removeChild(span);
                            }
                        }
                        
                        // Record undo state
                        if (window.saveState) {
                            saveState();
                            window.lastContent = editor.innerHTML;
                            window.redoStack = [];
                            try {
                                window.webkit.messageHandlers.contentChanged.postMessage("changed");
                            } catch(e) {
                                console.log("Could not notify about changes:", e);
                            }
                        }
                    }, 0);
                    
                    return true;
                } catch (e) {
                    console.error("Error removing formatting:", e);
                }
            }
        }
        return false;
    })();
    """
    
    self.execute_js(win, js_code)
    win.statusbar.set_text("Text formatting removed")
    win.webview.grab_focus()
def on_change_case(self, win, case_type):
    """Change case of selected HTML content, preserving structure and formatting."""

    js_transformations = {
        "sentence": """
            function transformText(text) {
                if (!text) return text;
                text = text.toLowerCase();
                return text.replace(/([.!?]\\s+|^)([a-z])/g, function(match, p1, p2) {
                    return p1 + p2.toUpperCase();
                });
            }
        """,
        "lower": "function transformText(text) { return text.toLowerCase(); }",
        "upper": "function transformText(text) { return text.toUpperCase(); }",
        "title": """
            function transformText(text) {
                return text.replace(/\\b\\w+/g, function(word) {
                    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
                });
            }
        """,
        "toggle": """
            function transformText(text) {
                return text.split('').map(function(char) {
                    return char === char.toUpperCase() ? char.toLowerCase() : char.toUpperCase();
                }).join('');
            }
        """,
        "smallcaps": """
            function transformText(text) {
                return '<span style="font-variant: small-caps;">' + text + '</span>';
            }
        """
    }

    transform_function = js_transformations.get(case_type, js_transformations["lower"])

    js_code = f"""
    (function() {{
        const selection = window.getSelection();
        if (!selection.rangeCount) return;
        const range = selection.getRangeAt(0);
        if (range.collapsed) return;

        const editor = document.getElementById('editor');
        const frag = range.cloneContents();
        const container = document.createElement("div");
        container.appendChild(frag);
        let html = container.innerHTML;

        {transform_function}

        if ('{case_type}' === 'smallcaps') {{
            html = transformText(html);
        }} else {{
            const temp = document.createElement("div");
            temp.innerHTML = html;
            function walkTextNodes(node) {{
                if (node.nodeType === Node.TEXT_NODE) {{
                    node.textContent = transformText(node.textContent);
                }} else {{
                    for (let child of node.childNodes) {{
                        walkTextNodes(child);
                    }}
                }}
            }}
            walkTextNodes(temp);
            html = temp.innerHTML;
        }}

        range.deleteContents();
        range.insertNode(document.createRange().createContextualFragment(html));

        selection.removeAllRanges();
        selection.addRange(range);

        saveState();
        window.lastContent = editor.innerHTML;
        window.redoStack = [];
        try {{
            window.webkit.messageHandlers.contentChanged.postMessage("changed");
        }} catch(e) {{
            console.log("Could not notify about changes:", e);
        }}
    }})();
    """

    self.execute_js(win, js_code)

    status_messages = {
        "sentence": "Applied sentence case",
        "lower": "Applied lowercase",
        "upper": "Applied UPPERCASE",
        "title": "Applied Title Case",
        "toggle": "Applied tOGGLE cASE",
        "smallcaps": "Applied small caps"
    }

    win.statusbar.set_text(status_messages.get(case_type, "Changed text case"))
    win.webview.grab_focus()

    
def on_select_all_clicked(self, win, *args):
    """Handle Ctrl+A shortcut for selecting all content"""
    # Execute JavaScript to select all content in the editor
    js_code = """
    (function() {
        // Get the editor element
        const editor = document.getElementById('editor');
        
        // Focus the editor first to ensure selection works
        editor.focus();
        
        // Create a range to select all content
        const range = document.createRange();
        range.selectNodeContents(editor);
        
        // Get the selection and apply the range
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        
        return true;
    })();
    """
    
    self.execute_js(win, js_code)
    win.statusbar.set_text("Selected all content")
    return True
############### formatting marks, drop cap
def on_drop_cap_clicked(self, win, button):
    """Handle drop cap button click with inline styles for better compatibility"""
    js_code = """
    (function() {
        // Find the container paragraph or div
        let selection = window.getSelection();
        if (selection.rangeCount > 0) {
            let range = selection.getRangeAt(0);
            let parentEl = range.commonAncestorContainer;
            
            // Get containing paragraph or div
            if (parentEl.nodeType !== Node.ELEMENT_NODE) {
                parentEl = parentEl.parentNode;
            }
            
            // Find paragraph or div parent
            while (parentEl && parentEl.nodeName.toLowerCase() !== 'p' && parentEl.nodeName.toLowerCase() !== 'div') {
                parentEl = parentEl.parentNode;
                if (!parentEl || parentEl.nodeName.toLowerCase() === 'body') {
                    break;
                }
            }
            
            // Track result type
            let result = "none";
            
            if (parentEl && (parentEl.nodeName.toLowerCase() === 'p' || parentEl.nodeName.toLowerCase() === 'div')) {
                try {
                    // Check if drop cap already exists - now we look for spans with inline styles instead
                    const existingDropCap = parentEl.querySelector('span[style*="float: left"][style*="font-size"]');
                    
                    if (existingDropCap) {
                        // Remove the drop cap formatting
                        const text = existingDropCap.textContent;
                        const textNode = document.createTextNode(text);
                        existingDropCap.parentNode.replaceChild(textNode, existingDropCap);
                        
                        // Normalize text nodes to join adjacent text
                        parentEl.normalize();
                        result = "removed";
                    } else {
                        // Apply drop cap to the paragraph
                        const text = parentEl.textContent.trim();
                        if (text && text.length > 0) {
                            // Find the first letter
                            let firstChar = '';
                            for (let i = 0; i < text.length; i++) {
                                if (text[i].match(/[a-zA-Z0-9]/)) {
                                    firstChar = text[i];
                                    break;
                                }
                            }
                            
                            if (firstChar) {
                                // Find the node with the first letter
                                const textNodes = [];
                                const walker = document.createTreeWalker(
                                    parentEl,
                                    NodeFilter.SHOW_TEXT,
                                    null,
                                    false
                                );
                                
                                // Collect all text nodes
                                let node;
                                while (node = walker.nextNode()) {
                                    if (node.nodeValue.trim()) {
                                        textNodes.push(node);
                                    }
                                }
                                
                                // Find the node with the first letter
                                let targetNode = null;
                                let index = -1;
                                
                                for (let i = 0; i < textNodes.length; i++) {
                                    const nodeText = textNodes[i].nodeValue;
                                    const idx = nodeText.indexOf(firstChar);
                                    
                                    if (idx !== -1) {
                                        targetNode = textNodes[i];
                                        index = idx;
                                        break;
                                    }
                                }
                                
                                if (targetNode) {
                                    // Create a drop cap with inline styles instead of a class
                                    const dropCap = document.createElement('span');
                                    dropCap.style.cssText = "float: left; font-size: 3.2em; font-weight: bold; line-height: 0.8; margin-right: 0.08em; margin-top: 0.05em; padding-bottom: 0.05em;";
                                    dropCap.textContent = firstChar;
                                    
                                    // Only replace the first character, not the whole text node
                                    const beforeText = targetNode.nodeValue.substring(0, index);
                                    const afterText = targetNode.nodeValue.substring(index + 1);
                                    
                                    // Create a text node for before text if needed
                                    if (beforeText) {
                                        const beforeNode = document.createTextNode(beforeText);
                                        targetNode.parentNode.insertBefore(beforeNode, targetNode);
                                    }
                                    
                                    // Insert the drop cap
                                    targetNode.parentNode.insertBefore(dropCap, targetNode);
                                    
                                    // Update the target node to contain only the text after the first letter
                                    targetNode.nodeValue = afterText;
                                    
                                    result = "applied";
                                }
                            }
                        } else {
                            result = "no-text";
                        }
                    }
                } catch (err) {
                    console.error("Error in drop cap processing:", err);
                    result = "error";
                }
            }
            
            // Signal content changed if we modified the document
            if (result === "applied" || result === "removed") {
                try {
                    window.webkit.messageHandlers.contentChanged.postMessage("changed");
                } catch (e) {
                    console.error("Error notifying about content change:", e);
                }
            }
            
            return result;
        }
        return "none";
    })();
    """
    
    # Execute the JavaScript
    win.webview.evaluate_javascript(
        js_code,
        -1, None, None, None,
        lambda webview, result, data: self._handle_drop_cap_result(win, webview, result),
        None
    )
    win.webview.grab_focus()
    
def _handle_drop_cap_result(self, win, webview, result):
    """Handle the result from drop cap operation"""
    try:
        js_result = webview.evaluate_javascript_finish(result)
        if js_result:
            # Get the result string based on WebKit version
            result_str = ""
            if hasattr(js_result, 'get_js_value'):
                result_str = js_result.get_js_value().to_string()
            elif hasattr(js_result, 'to_string'):
                result_str = js_result.to_string()
            else:
                result_str = str(js_result)
            
            # Remove any quotes that might be around the result
            result_str = result_str.strip('"\'')
            
            # Update status based on result
            if result_str == "applied":
                win.statusbar.set_text("Applied drop cap to paragraph")
            elif result_str == "removed":
                win.statusbar.set_text("Removed drop cap from paragraph")
            elif result_str == "error":
                win.statusbar.set_text("Error toggling drop cap")
            elif result_str == "no-text":
                win.statusbar.set_text("No text found to apply drop cap to")
            else:
                win.statusbar.set_text("No paragraph selected for drop cap")
    except Exception as e:
        print(f"Error handling drop cap result: {e}")
        win.statusbar.set_text("Error applying drop cap")

def on_show_formatting_marks_toggled(self, win, button):
    """Handle show formatting marks button toggle with improved LibreOffice-like implementation"""
    is_active = button.get_active()
    
    # Execute JavaScript to toggle formatting marks
    js_code = f"""
    (function() {{
        // Define the formatting marks toggle functionality
        let styleSheet = document.getElementById('editorStyles');
        if (!styleSheet) {{
            styleSheet = document.createElement('style');
            styleSheet.id = 'editorStyles';
            document.head.appendChild(styleSheet);
        }}
        
        if ({str(is_active).lower()}) {{
            // Add CSS to show formatting marks - LibreOffice style
            styleSheet.textContent += `
            /* Paragraph marks */
            #editor p:not(:empty)::after, 
            #editor div:not(:empty)::after {{
                content: "¶";
                color: #999;
                margin-left: 2px;
                font-size: 0.8em;
                opacity: 0.8;
            }}
            
            /* Tab marks - using right arrow character */
            #editor .tab-mark::before {{
                content: "→";
                color: #999;
                opacity: 0.8;
                display: inline-block;
                width: 1em;
            }}
            
            /* Space marks - using middle dot character */
            #editor .space-mark::before {{
                content: "·";
                color: #999;
                font-size: 0.8em;
                opacity: 0.8;
                display: inline;
                position: relative;
            }}
            
            /* Line break marks */
            #editor br::after {{
                content: "↵";
                color: #999;
                opacity: 0.8;
                font-size: 0.8em;
                line-height: 1;
            }}`;
            
            // Add classes to editor
            document.getElementById('editor').classList.add('show-formatting');
            
            // Function to mark spaces and tabs
            function markFormatting() {{
                try {{
                    const editor = document.getElementById('editor');
                    const textNodes = [];
                    
                    // Find all text nodes in the editor
                    function findTextNodes(node) {{
                        if (node.nodeType === 3) {{ // Text node
                            if (node.nodeValue.includes(' ') || node.nodeValue.includes('\\t')) {{
                                textNodes.push(node);
                            }}
                        }} else if (node.nodeType === 1) {{ // Element node
                            // Don't process certain elements
                            if (node.classList && 
                                (node.classList.contains('space-mark') || 
                                 node.classList.contains('tab-mark'))) {{
                                return;
                            }}
                            
                            for (let i = 0; i < node.childNodes.length; i++) {{
                                findTextNodes(node.childNodes[i]);
                            }}
                        }}
                    }}
                    
                    findTextNodes(editor);
                    
                    // Process text nodes - replace spaces and tabs with marked spans
                    textNodes.forEach(textNode => {{
                        if (!textNode.parentNode) return;
                        
                        const parent = textNode.parentNode;
                        const text = textNode.nodeValue;
                        
                        // Don't process if parent is a special element
                        if (parent.classList && 
                            (parent.classList.contains('space-mark') || 
                             parent.classList.contains('tab-mark'))) {{
                            return;
                        }}
                        
                        // Check if this node has spaces or tabs
                        if ((text.includes(' ') || text.includes('\\t'))) {{
                            // Create a document fragment for the new content
                            const fragment = document.createDocumentFragment();
                            let currentText = '';
                            
                            // Process each character to handle spaces and tabs
                            for (let i = 0; i < text.length; i++) {{
                                const char = text[i];
                                
                                if (char === ' ') {{
                                    // Add any accumulated text
                                    if (currentText) {{
                                        fragment.appendChild(document.createTextNode(currentText));
                                        currentText = '';
                                    }}
                                    
                                    // Create a space marker
                                    const spaceSpan = document.createElement('span');
                                    spaceSpan.classList.add('space-mark');
                                    spaceSpan.innerHTML = ' ';
                                    fragment.appendChild(spaceSpan);
                                }} 
                                else if (char === '\\t') {{
                                    // Add any accumulated text
                                    if (currentText) {{
                                        fragment.appendChild(document.createTextNode(currentText));
                                        currentText = '';
                                    }}
                                    
                                    // Create a tab marker
                                    const tabSpan = document.createElement('span');
                                    tabSpan.classList.add('tab-mark');
                                    tabSpan.innerHTML = ' ';  // Using a space for tab content
                                    fragment.appendChild(tabSpan);
                                }} 
                                else {{
                                    // Accumulate regular text
                                    currentText += char;
                                }}
                            }}
                            
                            // Add any remaining text
                            if (currentText) {{
                                fragment.appendChild(document.createTextNode(currentText));
                            }}
                            
                            // Replace the original text node with our fragment
                            parent.replaceChild(fragment, textNode);
                        }}
                    }});
                }} catch (err) {{
                    console.error("Error in formatting marks processing:", err);
                }}
            }}
            
            // Call the function to mark formatting
            markFormatting();
            
            // Set up a mutation observer to mark formatting in new content
            const observer = new MutationObserver(mutations => {{
                for (const mutation of mutations) {{
                    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {{
                        // Only process if we're not currently processing
                        if (!observer._processing) {{
                            observer._processing = true;
                            setTimeout(() => {{
                                markFormatting();
                                observer._processing = false;
                            }}, 0);
                        }}
                    }}
                }}
            }});
            
            // Start observing changes to the editor
            observer.observe(document.getElementById('editor'), {{ 
                childList: true, 
                subtree: true, 
                characterData: true 
            }});
            
            // Store the observer in a property so we can disconnect it later
            document.getElementById('editor')._formattingObserver = observer;
            
        }} else {{
            // IMPORTANT: Completely remove the formatting styles
            // First, save any existing non-formatting styles
            const originalStyles = styleSheet.textContent
                .replace(/#editor p[^{{]*?::after[\\s\\S]*?}}|#editor div[^{{]*?::after[\\s\\S]*?}}|#editor .tab-mark::before[\\s\\S]*?}}|#editor .space-mark::before[\\s\\S]*?}}|#editor br::after[\\s\\S]*?}}/g, '');
            
            // Set the stylesheet content to just the non-formatting styles
            styleSheet.textContent = originalStyles;
            
            // Remove formatting marks class
            document.getElementById('editor').classList.remove('show-formatting');
            
            // Disconnect the observer if it exists
            const editor = document.getElementById('editor');
            if (editor._formattingObserver) {{
                editor._formattingObserver.disconnect();
                delete editor._formattingObserver;
            }}
            
            // Function to remove formatting marks
            function removeFormatting() {{
                // Remove space markers
                const spaceMarks = editor.querySelectorAll('.space-mark');
                spaceMarks.forEach(mark => {{
                    const space = document.createTextNode(' ');
                    mark.parentNode.replaceChild(space, mark);
                }});
                
                // Remove tab markers
                const tabMarks = editor.querySelectorAll('.tab-mark');
                tabMarks.forEach(mark => {{
                    const tab = document.createTextNode('\\t');
                    mark.parentNode.replaceChild(tab, mark);
                }});
                
                // Normalize text nodes to join adjacent text
                editor.normalize();
            }}
            
            // Remove formatting marks
            removeFormatting();
        }}
        return true;
    }})();
    """
    
    # Execute the JavaScript
    self.execute_js(win, js_code)
    
    # Update status bar
    if is_active:
        win.statusbar.set_text("Showing formatting marks")
    else:
        win.statusbar.set_text("Hiding formatting marks")

        
def on_line_spacing_shortcut(self, win, spacing):
    """Handle Ctrl+0, Ctrl+1, Ctrl+2, and Ctrl+5 shortcuts for line spacing"""
    # Create JavaScript code to apply the line spacing to the selected paragraphs
    js_code = f"""
    (function() {{
        // Get the current selection
        const selection = window.getSelection();
        if (selection.rangeCount === 0) return false;
        
        const range = selection.getRangeAt(0);
        const startNode = range.startContainer;
        const endNode = range.endContainer;
        
        // Find all affected paragraphs within the selection
        let affectedParagraphs = [];
        
        // Helper function to find the closest paragraph or div parent
        function findParagraphParent(node) {{
            while (node && node !== document.body) {{
                if (node.nodeName === 'P' || 
                    node.nodeName === 'DIV' || 
                    node.nodeName === 'H1' || 
                    node.nodeName === 'H2' || 
                    node.nodeName === 'H3' || 
                    node.nodeName === 'H4' || 
                    node.nodeName === 'H5' || 
                    node.nodeName === 'H6' || 
                    node.nodeName === 'LI') {{
                    return node;
                }}
                node = node.parentNode;
            }}
            return null;
        }}
        
        // If selection is collapsed (cursor), just get the current paragraph
        if (range.collapsed) {{
            const paragraph = findParagraphParent(startNode);
            if (paragraph) {{
                affectedParagraphs.push(paragraph);
            }}
        }} else {{
            // Get all paragraph elements in the editor
            const editor = document.getElementById('editor');
            const allParagraphs = editor.querySelectorAll('p, div, h1, h2, h3, h4, h5, h6, li');
            
            // Determine selection boundaries
            let started = false;
            
            // Check if a node is within the selection
            function isNodeInSelection(node) {{
                try {{
                    const nodeRange = document.createRange();
                    nodeRange.selectNodeContents(node);
                    
                    return (
                        range.compareBoundaryPoints(Range.START_TO_END, nodeRange) <= 0 &&
                        range.compareBoundaryPoints(Range.END_TO_START, nodeRange) >= 0
                    ) || selection.containsNode(node, true);
                }} catch (e) {{
                    return false;
                }}
            }}
            
            // Find paragraphs that are within or intersect with the selection
            for (const paragraph of allParagraphs) {{
                if (isNodeInSelection(paragraph)) {{
                    affectedParagraphs.push(paragraph);
                }}
            }}
            
            // If no paragraphs found, try to find the containing paragraph
            if (affectedParagraphs.length === 0) {{
                const startPara = findParagraphParent(startNode);
                if (startPara) {{
                    affectedParagraphs.push(startPara);
                }}
            }}
        }}
        
        // Apply line spacing to all affected paragraphs
        let modified = false;
        for (const paragraph of affectedParagraphs) {{
            // Set the line height directly on the style
            paragraph.style.lineHeight = "{spacing}";
            modified = true;
        }}
        
        // Signal that the content has changed if we modified anything
        if (modified) {{
            try {{
                window.webkit.messageHandlers.contentChanged.postMessage("changed");
            }} catch (e) {{
                console.error("Error signaling content change:", e);
            }}
            
            // Record undo state if the function exists
            if (typeof saveState === 'function') {{
                saveState();
                window.lastContent = document.getElementById('editor').innerHTML;
                window.redoStack = [];
            }}
        }}
        
        return modified;
    }})();
    """
    
    # Execute the JavaScript
    self.execute_js(win, js_code)
    
    # Update status bar with appropriate text based on spacing value
    if spacing == 1.0:
        spacing_text = "single"
    elif spacing == 1.15:
        spacing_text = "default (1.15)"
    elif spacing == 1.5:
        spacing_text = "one and a half (1.5)"
    elif spacing == 2.0:
        spacing_text = "double"
    else:
        spacing_text = str(spacing)
        
    win.statusbar.set_text(f"Applied {spacing_text} line spacing")
    return True
    
    
