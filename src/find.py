#!/usr/bin/env python3
import gi
import re
from gi.repository import Gtk, Gdk, GLib

# This module contains find-related methods for the HTML Editor application

def create_find_bar(self, win):
    """Create find/replace bar with revealer for smooth animations"""
    # Create a revealer to animate the find bar
    win.find_bar_revealer = Gtk.Revealer()
    win.find_bar_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
    win.find_bar_revealer.set_transition_duration(250)
    win.find_bar_revealer.set_reveal_child(False)  # Initially hidden
    win.find_bar_revealer.set_margin_top(0)
    win.find_bar_revealer.add_css_class("flat-header")
    
    # Main container
    find_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    find_bar.set_margin_start(0)
    find_bar.set_margin_end(0)
    find_bar.set_margin_top(6)
    find_bar.set_margin_bottom(6)
    find_bar.add_css_class("search-bar")
    
    # Use Gtk.SearchEntry for find functionality
    win.find_entry = Gtk.SearchEntry()
    win.find_entry.set_margin_start(6)
    win.find_entry.set_placeholder_text("Search")
    win.find_entry.set_tooltip_text("Find text in document")
    win.find_entry.set_hexpand(True)
    win.find_entry.connect("search-changed", lambda entry: self.on_find_text_changed(win, entry))
    win.find_entry.connect("activate", lambda entry: self.on_find_next_clicked(win, None))
    
    # Add key controller specifically for the search entry
    find_key_controller = Gtk.EventControllerKey.new()
    find_key_controller.connect("key-pressed", lambda c, k, kc, s: self.on_find_key_pressed(win, c, k, kc, s))
    win.find_entry.add_controller(find_key_controller)
    
    # Previous/Next buttons
    nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    nav_box.add_css_class("linked")
    nav_box.set_margin_start(2)
    
    nav_box.append(win.find_entry)
    
    prev_button = Gtk.Button(icon_name="go-up-symbolic")
    prev_button.set_tooltip_text("Previous match")
    prev_button.connect("clicked", lambda btn: self.on_find_previous_clicked(win, btn))
    nav_box.append(prev_button)
    
    next_button = Gtk.Button(icon_name="go-down-symbolic")
    next_button.set_tooltip_text("Next match")
    next_button.connect("clicked", lambda btn: self.on_find_next_clicked(win, btn))
    nav_box.append(next_button)
    
    
    find_bar.append(nav_box)

    # Add case-sensitive toggle button with uppercase icon
    win.case_sensitive_button = Gtk.ToggleButton()
    case_icon = Gtk.Image.new_from_icon_name("uppercase-symbolic")
    win.case_sensitive_button.set_child(case_icon)
    win.case_sensitive_button.set_tooltip_text("Match case")
    win.case_sensitive_button.add_css_class("flat")
    win.case_sensitive_button.connect("toggled", lambda btn: self.on_case_sensitive_toggled(win, btn))
    find_bar.append(win.case_sensitive_button)
    
    # Create a separator
    separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
    separator.set_margin_start(0)
    separator.set_margin_end(0)
    find_bar.append(separator)
    
    # Replace entry with icon
    replace_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    replace_box.add_css_class("linked")
    
    # Create a styled entry for replace
    win.replace_entry = Gtk.Entry()
    win.replace_entry.set_placeholder_text("Replace")
    win.replace_entry.set_hexpand(True)
    
    # Add a replace icon to the entry
    win.replace_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "edit-find-replace-symbolic")
    
    # Add key controller specifically for the replace entry
    replace_key_controller = Gtk.EventControllerKey.new()
    replace_key_controller.connect("key-pressed", lambda c, k, kc, s: self.on_find_key_pressed(win, c, k, kc, s))
    win.replace_entry.add_controller(replace_key_controller)
    
    #replace_box.append(win.replace_entry)
    find_bar.append(replace_box)


    # Replace and Replace All buttons with icons
    rep_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    rep_box.add_css_class("linked")
    rep_box.set_margin_start(2)
    rep_box.set_margin_end(6)
    rep_box.append(win.replace_entry)
    
    # Replace button with icon
    replace_button = Gtk.Button(icon_name="replace-symbolic")
    replace_button.set_tooltip_text("Replace")
    replace_button.add_css_class("linked")
    replace_button.connect("clicked", lambda btn: self.on_replace_clicked(win, btn))


    # Replace All button with icon
    replace_all_button = Gtk.Button(icon_name="replace-all-symbolic")
    replace_all_button.set_tooltip_text("Replace All")
    replace_all_button.add_css_class("linked")
    replace_all_button.connect("clicked", lambda btn: self.on_replace_all_clicked(win, btn))

    rep_box.append(replace_button)
    rep_box.append(replace_all_button)

    find_bar.append(rep_box)
        
    # Use a spacer to push the close button to the right
    spacer = Gtk.Box()
    spacer.set_hexpand(True)
    #find_bar.append(spacer)
    
    # Status label to show match counts or errors (placed before close button)
    win.status_label = Gtk.Label()
    win.status_label.set_margin_start(8)
    win.status_label.set_margin_end(8)
    win.status_label.set_width_chars(15)
    win.status_label.set_xalign(0)  # Align text to the left
    #find_bar.append(win.status_label)
    
    # Close button
    close_button = Gtk.Button(icon_name="window-close-symbolic")
    close_button.set_tooltip_text("Close search bar")
    close_button.connect("clicked", lambda btn: self.on_close_find_clicked(win, btn))
    close_button.add_css_class("flat")
    close_button.set_margin_end(6)
    #find_bar.append(close_button)
    
    # Set the find bar as the child of the revealer
    win.find_bar_revealer.set_child(find_bar)
    
    return win.find_bar_revealer

def on_find_shortcut(self, win, *args):
    """Handle Ctrl+F shortcut specifically"""
    # Get current visibility state
    is_visible = win.find_bar_revealer.get_reveal_child()
    
    # Toggle to the opposite state
    new_state = not is_visible
    
    # Block signal handler before updating the toggle button
    if hasattr(win, 'find_button_handler_id') and win.find_button_handler_id:
        win.find_button.handler_block(win.find_button_handler_id)
    
    # Update button state first
    win.find_button.set_active(new_state)
    
    # Update find bar visibility
    win.find_bar_revealer.set_reveal_child(new_state)
    
    # Unblock signal handler
    if hasattr(win, 'find_button_handler_id') and win.find_button_handler_id:
        win.find_button.handler_unblock(win.find_button_handler_id)
    
    # Use a small delay to properly handle the focus
    def handle_focus():
        if new_state:
            # If showing the bar, grab focus
            win.find_entry.grab_focus()
            win.statusbar.set_text("Find and replace activated")
            
            # Check if there's selected text to populate the find field
            self.populate_find_field_from_selection(win)
        else:
            # Clear highlights when hiding
            js_code = "clearSearch();"
            win.webview.evaluate_javascript(js_code, -1, None, None, None, None)
            
            # Clear find and replace entry text
            win.find_entry.set_text("")
            win.replace_entry.set_text("")
            
            win.webview.grab_focus()
            win.statusbar.set_text("Find and replace closed")
        return False  # Don't call again
    
    GLib.timeout_add(100, handle_focus)
    
    return True  # Event was handled

def on_find_clicked(self, action=None, param=None):
    """Handle Find command - toggle the find bar visibility"""
    # Get the active window
    active_win = None
    for win in self.windows:
        if win.is_active():
            active_win = win
            break
    
    # If no active window, use the first one
    if not active_win and self.windows:
        active_win = self.windows[0]
            
    if active_win:
        # Get current visibility state
        is_visible = active_win.find_bar_revealer.get_reveal_child()
        
        # Toggle to the opposite state
        new_state = not is_visible
        
        # Use a small delay to ensure focus handling occurs after the visibility change
        def toggle_find_bar():
            # First update the find bar visibility
            active_win.find_bar_revealer.set_reveal_child(new_state)
            
            # Block signal handler before updating the toggle button
            if hasattr(active_win, 'find_button'):
                if hasattr(active_win, 'find_button_handler_id') and active_win.find_button_handler_id:
                    active_win.find_button.handler_block(active_win.find_button_handler_id)
                
                # Update button state to match the find bar visibility
                active_win.find_button.set_active(new_state)
                
                # Unblock signal handler
                if hasattr(active_win, 'find_button_handler_id') and active_win.find_button_handler_id:
                    active_win.find_button.handler_unblock(active_win.find_button_handler_id)
            
            if new_state:
                # If showing the bar, grab focus
                active_win.find_entry.grab_focus()
                active_win.statusbar.set_text("Find and replace activated")
                
                # Check if there's selected text to populate the find field
                self.populate_find_field_from_selection(active_win)
            else:
                # Clear highlights when hiding
                js_code = "clearSearch();"
                active_win.webview.evaluate_javascript(js_code, -1, None, None, None, None)
                
                # Clear find and replace entry text
                active_win.find_entry.set_text("")
                active_win.replace_entry.set_text("")
                
                active_win.webview.grab_focus()
                active_win.statusbar.set_text("Find and replace closed")
            
            return False  # Don't call again
        
        # Schedule the toggle with a short delay to allow the key event to complete
        GLib.timeout_add(50, toggle_find_bar)
        
        return True  # Event was handled

def on_close_find_clicked(self, win, button, param=None):
    """Handle close find bar button"""
    if win:
        # Clear search and replace text
        win.find_entry.set_text("")
        win.replace_entry.set_text("")
        
        win.find_bar_revealer.set_reveal_child(False)
        
        # Also update the toggle button state
        if hasattr(win, 'find_button'):
            win.find_button.set_active(False)
            
        # Clear any highlighting
        js_code = "clearSearch();"
        win.webview.evaluate_javascript(js_code, -1, None, None, None, None)
        win.webview.grab_focus()
        win.statusbar.set_text("Find and replace closed")

def on_case_sensitive_toggled(self, win, button):
    """Handle case-sensitive toggle button state changes"""
    # Get the current state
    is_case_sensitive = button.get_active()
    
    # Update the search with current settings
    search_text = win.find_entry.get_text()
    if search_text:
        # Re-run the search with the updated case sensitivity setting
        self.on_find_text_changed(win, win.find_entry)
        
    status_text = "Case-sensitive search enabled" if is_case_sensitive else "Case-sensitive search disabled"
    win.statusbar.set_text(status_text)

def on_find_text_changed(self, win, entry):
    """Handle find text changes with support for multi-line text"""
    search_text = entry.get_text()
    if search_text:
        # Get the case sensitivity setting
        is_case_sensitive = win.case_sensitive_button.get_active() if hasattr(win, 'case_sensitive_button') else False
        
        # Properly escape for JavaScript including newlines
        import json
        search_text_json = json.dumps(search_text)  # This properly escapes all special chars including newlines
        
        js_code = f"""
        searchAndHighlight({search_text_json}, {str(is_case_sensitive).lower()});
        """
        win.webview.evaluate_javascript(js_code, -1, None, None, None, 
                                    lambda webview, result: self.on_search_result(win, webview, result))

def on_search_result(self, win, webview, result):
    """Handle search result"""
    try:
        js_result = webview.evaluate_javascript_finish(result)
        if js_result and not js_result.is_null():
            count = js_result.to_int32()
            if count > 0:
                status_message = f"Found {count} matches"
                win.status_label.set_text(status_message)
                win.statusbar.set_text(status_message)  # Also update the statusbar
            else:
                status_message = "No matches found"
                win.status_label.set_text(status_message)
                win.statusbar.set_text(status_message)  # Also update the statusbar
    except Exception as e:
        print(f"Error in search: {e}")
        status_message = "Search error"
        win.status_label.set_text(status_message)
        win.statusbar.set_text(status_message)  # Also update the statusbar

def on_find_next_clicked(self, win, button):
    """Move to next search result"""
    js_code = "findNext();"
    win.webview.evaluate_javascript(js_code, -1, None, None, None, None)

def on_find_previous_clicked(self, win, button):
    """Move to previous search result"""
    js_code = "findPrevious();"
    win.webview.evaluate_javascript(js_code, -1, None, None, None, None)

def on_replace_clicked(self, win, button):
    """Replace current selection with replace text"""
    replace_text = win.replace_entry.get_text()
    
    # Properly escape for JavaScript including newlines
    import json
    replace_text_json = json.dumps(replace_text)
    
    js_code = f"""
    replaceSelection({replace_text_json});
    """
    win.webview.evaluate_javascript(js_code, -1, None, None, None, None)

def on_replace_all_clicked(self, win, button):
    """Replace all instances of search text with replace text"""
    search_text = win.find_entry.get_text()
    replace_text = win.replace_entry.get_text()
    
    if not search_text:
        return
    
    # Properly escape for JavaScript including newlines
    import json
    search_text_json = json.dumps(search_text)
    replace_text_json = json.dumps(replace_text)
    
    js_code = f"""
    replaceAll({search_text_json}, {replace_text_json});
    """
    win.webview.evaluate_javascript(js_code, -1, None, None, None, 
                                lambda webview, result: self.on_replace_all_result(win, webview, result))

def on_replace_all_result(self, win, webview, result):
    """Handle replace all result"""
    try:
        js_result = webview.evaluate_javascript_finish(result)
        if js_result and not js_result.is_null():
            count = js_result.to_int32()
            status_message = f"Replaced {count} occurrences"
            win.statusbar.set_text(status_message)  # Also update the statusbar
    except Exception as e:
        print(f"Error in replace all: {e}")
        status_message = "Replace error"
        win.statusbar.set_text(status_message)

def on_find_key_pressed(self, win, controller, keyval, keycode, state):
    """Handle key presses in the find bar"""
    # Check if Escape key was pressed
    if keyval == Gdk.KEY_Escape:
        # Clear search and replace text
        win.find_entry.set_text("")
        win.replace_entry.set_text("")
        
        # Close the find bar
        self.on_close_find_clicked(win, None)
        return True
    return False

def on_find_button_toggled(self, win, button):
    """Handle find button toggle state changes"""
    is_active = button.get_active()
    is_visible = win.find_bar_revealer.get_reveal_child()
    
    # Only take action if the button state doesn't match the find bar visibility
    if is_active != is_visible:
        win.find_bar_revealer.set_reveal_child(is_active)
        
        if is_active:
            # Show find bar
            win.find_entry.grab_focus()
            win.statusbar.set_text("Find and replace activated")
            
            # Check if there's selected text to populate the find field
            self.populate_find_field_from_selection(win)
        else:
            # Hide find bar
            js_code = "clearSearch();"
            win.webview.evaluate_javascript(js_code, -1, None, None, None, None)
            
            # Clear find and replace entry text
            win.find_entry.set_text("")
            win.replace_entry.set_text("")
            
            win.webview.grab_focus()
            win.statusbar.set_text("Find and replace closed")

def populate_find_field_from_selection(self, win):
    """Populate find entry with selected text if any"""
    js_code = """
    (function() {
        const selection = window.getSelection();
        if (selection && selection.toString().trim().length > 0) {
            return selection.toString();
        }
        return "";
    })();
    """
    win.webview.evaluate_javascript(
        js_code, -1, None, None, None,
        # The lambda needs to accept the third argument (user_data)
        lambda webview, result, user_data=None: self._on_get_selection_for_find(win, webview, result),
        None
    )

def _on_get_selection_for_find(self, win, webview, result):
    """Handle getting selection text for find field"""
    try:
        js_result = webview.evaluate_javascript_finish(result)
        if js_result and not js_result.is_null():
            selection_text = ""
            
            # Try different methods to extract the string value
            if hasattr(js_result, 'get_js_value'):
                selection_text = js_result.get_js_value().to_string()
            elif hasattr(js_result, 'to_string'):
                selection_text = js_result.to_string()
            elif hasattr(js_result, 'get_string'):
                selection_text = js_result.get_string()
            
            if selection_text and selection_text.strip():
                # Set the find entry text to the selection
                win.find_entry.set_text(selection_text.strip())
                
                # Trigger the search automatically
                self.on_find_text_changed(win, win.find_entry)
    except Exception as e:
        print(f"Error getting selection for find: {e}")
        
def search_functions_js(self):
    """JavaScript for search and replace functionality with improved handling of replacements and formatting."""
    # Use Python raw string to avoid escape sequence issues
    return r"""
    // Search variables
    var searchResults = [];
    var searchIndex = -1;
    var currentSearchText = "";
    var originalFormattingInfo = []; // Store information about original formatting
    var replacedSegments = new Set(); // Track which segments have been replaced

    // Search functions
    function clearSearch() {
        searchResults = [];
        searchIndex = -1;
        currentSearchText = "";
        
        // Remove all highlighting while preserving formatting
        let editor = document.getElementById('editor');
        let highlights = editor.querySelectorAll('.search-highlight');
        
        if (highlights.length) {
            for (let i = 0; i < highlights.length; i++) {
                let highlight = highlights[i];
                unwrapHighlight(highlight);
            }
            
            // Clear the formatting info but keep replaced segments
            originalFormattingInfo = [];
            
            editor.normalize();
            return true;
        }
        return false;
    }

    // Helper function to properly unwrap highlights
    function unwrapHighlight(highlight) {
        // Create a document fragment
        let fragment = document.createDocumentFragment();
        
        // Move all children to the fragment
        while (highlight.firstChild) {
            fragment.appendChild(highlight.firstChild);
        }
        
        // Replace the highlight with its contents
        if (highlight.parentNode) {
            highlight.parentNode.replaceChild(fragment, highlight);
        }
    }

    // When creating highlights, store original formatting information
    function storeFormattingInfo(range) {
        let formattingInfo = [];
        let fragment = range.cloneContents();
        
        // Process all nodes in the fragment
        function processNode(node) {
            if (node.nodeType === Node.TEXT_NODE) {
                // Text node - add as plain text
                formattingInfo.push({
                    text: node.textContent,
                    format: null
                });
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                // Element node - check for formatting elements
                let format = null;
                
                // Identify formatting elements
                if (node.nodeName === 'B' || node.nodeName === 'STRONG') {
                    format = 'b';
                } else if (node.nodeName === 'I' || node.nodeName === 'EM') {
                    format = 'i';
                } else if (node.nodeName === 'U') {
                    format = 'u';
                } else if (node.nodeName === 'STRIKE' || node.nodeName === 'S' || node.nodeName === 'DEL') {
                    format = 'strike';
                } else if (node.nodeName === 'SPAN') {
                    format = 'span';
                }
                
                if (node.childNodes.length === 0) {
                    // Empty element
                    return;
                } else if (node.childNodes.length === 1 && node.firstChild.nodeType === Node.TEXT_NODE) {
                    // Simple case: single text node child
                    formattingInfo.push({
                        text: node.textContent,
                        format: format
                    });
                } else {
                    // Complex case: multiple children or nested elements
                    // For simplicity, we'll treat this as plain text with the outer format
                    // A more complex implementation would recursively process children
                    formattingInfo.push({
                        text: node.textContent,
                        format: format
                    });
                }
            }
        }
        
        // Process all top-level nodes in the fragment
        for (let i = 0; i < fragment.childNodes.length; i++) {
            processNode(fragment.childNodes[i]);
        }
        
        // If the fragment is empty, try to create a text segment from the range
        if (formattingInfo.length === 0 && range.toString()) {
            formattingInfo.push({
                text: range.toString(),
                format: null
            });
        }
        
        return formattingInfo;
    }

    function normalizeSpaces(text) {
        // Replace non-breaking spaces with regular spaces for search purposes
        return text.replace(/\u00A0/g, ' ');
    }

    function searchAndHighlight(searchText, isCaseSensitive) {
        // First clear any existing search
        clearSearch();
        
        // Reset formatting info array
        originalFormattingInfo = [];
        
        if (!searchText) return 0;
        currentSearchText = searchText;
        
        // Store current case sensitivity setting
        window.isCaseSensitive = isCaseSensitive;
        
        // Check if this is a multi-line search
        if (searchText.includes('\n')) {
            // Return a special value to indicate multi-line search
            return -1;
        }
        
        // Normalize the search text - replace &nbsp; with space for searching
        searchText = normalizeSpaces(searchText);
        
        let editor = document.getElementById('editor');
        searchResults = [];
        searchIndex = -1;
        let count = 0;
        
        // Simplified approach: get the full text content of the editor
        let fullText = '';
        let textNodes = [];  // Store all text nodes in order
        
        // Use TreeWalker to find all text nodes in correct order
        let walker = document.createTreeWalker(
            editor,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        // Collect all text nodes and build the full text
        let node;
        while (node = walker.nextNode()) {
            // Normalize the node text content to handle &nbsp;
            let nodeText = normalizeSpaces(node.textContent);
            
            textNodes.push({
                node: node,
                startIndex: fullText.length,
                text: nodeText,
                originalText: node.textContent
            });
            fullText += nodeText;
        }
        
        // Now search the full text
        let searchPattern = searchText;
        let textToSearch = fullText;
        
        // If case-insensitive, convert both to lowercase for comparison
        if (!isCaseSensitive) {
            searchPattern = searchText.toLowerCase();
            textToSearch = fullText.toLowerCase();
        }
        
        // Find all matches
        let index = textToSearch.indexOf(searchPattern);
        while (index !== -1) {
            let startPos = index;
            let endPos = index + searchText.length - 1;  // End position is inclusive
            
            // Find which text nodes contain our match
            let startNode = null;
            let startOffset = 0;
            let endNode = null;
            let endOffset = 0;
            
            // Find start node and offset
            for (let i = 0; i < textNodes.length; i++) {
                let nodeInfo = textNodes[i];
                let nodeEndIndex = nodeInfo.startIndex + nodeInfo.text.length - 1;
                
                if (startPos >= nodeInfo.startIndex && startPos <= nodeEndIndex) {
                    startNode = nodeInfo.node;
                    // We need to account for any differences between original and normalized text
                    let normalizedOffset = startPos - nodeInfo.startIndex;
                    startOffset = mapNormalizedToOriginalOffset(nodeInfo.originalText, nodeInfo.text, normalizedOffset);
                    break;
                }
            }
            
            // Find end node and offset
            for (let i = 0; i < textNodes.length; i++) {
                let nodeInfo = textNodes[i];
                let nodeEndIndex = nodeInfo.startIndex + nodeInfo.text.length - 1;
                
                if (endPos >= nodeInfo.startIndex && endPos <= nodeEndIndex) {
                    endNode = nodeInfo.node;
                    // We need to account for any differences between original and normalized text
                    let normalizedOffset = endPos - nodeInfo.startIndex;
                    endOffset = mapNormalizedToOriginalOffset(nodeInfo.originalText, nodeInfo.text, normalizedOffset);
                    break;
                }
            }
            
            // Create range and highlight if we found both nodes
            if (startNode && endNode) {
                try {
                    let range = document.createRange();
                    range.setStart(startNode, startOffset);
                    range.setEnd(endNode, endOffset + 1);  // +1 because setEnd is exclusive
                    
                    // Store original formatting before highlighting
                    let formattingInfo = storeFormattingInfo(range);
                    originalFormattingInfo.push(formattingInfo);
                    
                    // Create highlight span
                    let highlightSpan = document.createElement('span');
                    highlightSpan.className = 'search-highlight';
                    highlightSpan.style.backgroundColor = '#FFFF00';
                    highlightSpan.style.color = '#000000';
                    
                    // Add a unique ID to track this highlight
                    let highlightId = 'highlight-' + Math.random().toString(36).substr(2, 9);
                    highlightSpan.setAttribute('data-highlight-id', highlightId);
                    
                    // Apply highlight
                    try {
                        range.surroundContents(highlightSpan);
                        searchResults.push(highlightSpan);
                        count++;
                    } catch (e) {
                        console.error("Error highlighting range:", e);
                        // This can fail if the range crosses element boundaries
                        // Let's try with a more complex highlighting approach
                        
                        // We'll create a document fragment with a highlight span
                        let fragment = document.createDocumentFragment();
                        let span = document.createElement('span');
                        span.className = 'search-highlight';
                        span.style.backgroundColor = '#FFFF00';
                        span.style.color = '#000000';
                        
                        // Add unique ID to track this highlight
                        span.setAttribute('data-highlight-id', highlightId);
                        
                        fragment.appendChild(span);
                        
                        // Extract contents to the span
                        span.appendChild(range.extractContents());
                        
                        // Insert the fragment
                        range.insertNode(fragment);
                        searchResults.push(span);
                        count++;
                    }
                    
                    // We need to rebuild after DOM changes
                    textNodes = [];
                    fullText = '';
                    
                    // Reset the TreeWalker
                    walker = document.createTreeWalker(
                        editor,
                        NodeFilter.SHOW_TEXT,
                        null,
                        false
                    );
                    
                    // Rebuild the text mapping
                    while (node = walker.nextNode()) {
                        let nodeText = normalizeSpaces(node.textContent);
                        textNodes.push({
                            node: node,
                            startIndex: fullText.length,
                            text: nodeText,
                            originalText: node.textContent
                        });
                        fullText += nodeText;
                    }
                    
                    // Update search text if case insensitive
                    if (!isCaseSensitive) {
                        textToSearch = fullText.toLowerCase();
                    } else {
                        textToSearch = fullText;
                    }
                    
                    // Start looking from where we left off
                    index = textToSearch.indexOf(searchPattern, index + 1);
                } catch (e) {
                    console.error("Error in search:", e);
                    index = textToSearch.indexOf(searchPattern, index + 1);
                }
            } else {
                index = textToSearch.indexOf(searchPattern, index + 1);
            }
        }
        
        // Select first result if any found
        if (searchResults.length > 0) {
            searchIndex = 0;
            selectSearchResult(0);
        }
        
        return count;
    }
    
    // Helper function to map an offset in normalized text back to the original text
    function mapNormalizedToOriginalOffset(originalText, normalizedText, normalizedOffset) {
        // If no normalization happened, return the same offset
        if (originalText === normalizedText) {
            return normalizedOffset;
        }
        
        // Count how many characters we've processed in both texts
        let originalIndex = 0;
        let normalizedIndex = 0;
        
        // Walk through the strings simultaneously
        while (normalizedIndex < normalizedOffset && originalIndex < originalText.length) {
            // Skip any characters that were normalized out
            if (originalText.charCodeAt(originalIndex) === 0xA0 && normalizedText.charAt(normalizedIndex) === ' ') {
                // We found a non-breaking space that was converted to space
                originalIndex++;
                normalizedIndex++;
            } else if (originalText.charAt(originalIndex) === normalizedText.charAt(normalizedIndex)) {
                // Character is the same in both
                originalIndex++;
                normalizedIndex++;
            } else {
                // Character was removed in normalization, skip in original only
                originalIndex++;
            }
        }
        
        return originalIndex;
    }

    function selectSearchResult(index) {
        if (searchResults.length === 0) return false;
        
        // Make sure index is within bounds
        index = Math.max(0, Math.min(index, searchResults.length - 1));
        searchIndex = index;
        
        // Get the highlight span
        let span = searchResults[index];
        
        // Create a range for the selection
        let range = document.createRange();
        range.selectNodeContents(span);
        
        // Apply the selection
        let selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        
        // Scroll to the selection
        span.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        return true;
    }

    function findNext() {
        if (searchResults.length === 0) return false;
        
        searchIndex++;
        if (searchIndex >= searchResults.length) {
            searchIndex = 0;
        }
        
        return selectSearchResult(searchIndex);
    }

    function findPrevious() {
        if (searchResults.length === 0) return false;
        
        searchIndex--;
        if (searchIndex < 0) {
            searchIndex = searchResults.length - 1;
        }
        
        return selectSearchResult(searchIndex);
    }

    function replaceSelection(replaceText) {
        if (searchResults.length === 0 || searchIndex < 0) return false;
        
        // Create history entry before change
        saveState();
        
        // Get the current highlighted span
        let highlightSpan = searchResults[searchIndex];
        
        // Check if the parent exists
        if (!highlightSpan.parentNode) return false;
        
        // Step 1: Create a text node with the replacement text
        let replacement = document.createTextNode(replaceText);
        
        // Step 2: Replace the highlighted span with the replacement text node
        // This removes the highlight and inserts the new text
        highlightSpan.parentNode.replaceChild(replacement, highlightSpan);
        
        // Step 3: Update our search results array
        searchResults.splice(searchIndex, 1);
        
        // Step 4: Adjust the current search index if needed
        if (searchIndex >= searchResults.length && searchResults.length > 0) {
            searchIndex = searchResults.length - 1;
        }
        
        // Step 5: Normalize the DOM to merge adjacent text nodes
        document.getElementById('editor').normalize();
        
        // Step 6: Select the next result if there are any left
        if (searchResults.length > 0) {
            selectSearchResult(searchIndex);
        }
        
        return true;
    }

    function replaceAll(searchText, replaceText) {
        if (!searchText) return 0;
        
        // Normalize the search text
        searchText = normalizeSpaces(searchText);
        
        // Check if this is a multi-line search
        if (searchText.includes('\n')) {
            // Return a special value to indicate multi-line search
            return -1;
        }
        
        // Create history entry before change
        saveState();
        
        let editor = document.getElementById('editor');
        let replacementCount = 0;
        
        // First perform the search to find all matches
        let matches = searchAndHighlight(searchText, window.isCaseSensitive || false);
        
        // Now replace all highlights with the replacement text
        let highlights = editor.querySelectorAll('.search-highlight');
        
        // Process each highlight
        for (let i = 0; i < highlights.length; i++) {
            let highlight = highlights[i];
            
            // Create a text node with the replacement
            let textNode = document.createTextNode(replaceText);
            
            // Replace the highlight with the text node
            if (highlight.parentNode) {
                highlight.parentNode.replaceChild(textNode, highlight);
                replacementCount++;
            }
        }
        
        // Clear search results since we've replaced all highlights
        searchResults = [];
        searchIndex = -1;
        
        // Normalize the DOM
        editor.normalize();
        
        return replacementCount;
    }
    """        

