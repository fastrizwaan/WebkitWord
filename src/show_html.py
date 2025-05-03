#!/usr/bin/env python3
# show_html.py - shows a dialog which let the user to copy the full/partial html
import os
import re
import subprocess
import tempfile
import time
import shutil
from datetime import datetime
from gi.repository import Gtk, Adw, Gdk, WebKit, GLib, Gio, Pango, PangoCairo, Gdk


def on_show_html_clicked(self, win, btn):
    """Handle Show HTML button click"""
    win.statusbar.set_text("Getting HTML content...")
    
    # Execute JavaScript to get the full HTML content with error handling
    js_code = """
    (function() {
        try {
            // Get the DOCTYPE
            const doctype = document.doctype;
            let doctypeString = "";
            if (doctype) {
                doctypeString = "<!DOCTYPE " + doctype.name + ">";
            }
            
            // Get the HTML content of the entire document
            const htmlContent = doctypeString + document.documentElement.outerHTML;
            
            // Try to get editor content, but handle case where it might not exist
            let editorContent = "";
            const editorElement = document.getElementById('editor');
            if (editorElement) {
                editorContent = editorElement.innerHTML;
            } else {
                // If no editor element exists, use the body content as a fallback
                editorContent = document.body.innerHTML;
            }
            
            return JSON.stringify({
                fullHtml: htmlContent,
                editorContent: editorContent
            });
        } catch (error) {
            return JSON.stringify({
                error: error.message,
                fullHtml: document.documentElement.outerHTML || "Error getting full HTML",
                editorContent: document.body.innerHTML || "Error getting editor content"
            });
        }
    })();
    """
    
    win.webview.evaluate_javascript(
        js_code,
        -1, None, None, None,
        lambda webview, result, data: self.show_html_dialog(win, webview, result),
        None
    )

def show_html_dialog(self, win, webview, result):
    """Show the HTML content in a dialog"""
    try:
        js_result = webview.evaluate_javascript_finish(result)
        full_html_content = ""
        editor_content = ""
        
        if js_result:
            # Get the HTML content from JSON response
            if hasattr(js_result, 'get_js_value'):
                result_str = js_result.get_js_value().to_string()
            else:
                result_str = js_result.to_string()
            
            # Parse the JSON result
            try:
                import json
                result_obj = json.loads(result_str)
                full_html_content = result_obj.get('fullHtml', '')
                editor_content = result_obj.get('editorContent', '')
                
                # Check if there was an error
                if 'error' in result_obj:
                    print(f"JavaScript error: {result_obj['error']}")
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}")
                full_html_content = result_str
                editor_content = result_str
            
            # Create a dialog with resizable text view
            dialog = Adw.Dialog()
            dialog.set_title("HTML Source")
            dialog.set_content_width(1024)  # Increase width for better viewing
            dialog.set_content_height(900)  # Increase height for better viewing
            
            # Create content box
            content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            content_box.set_margin_top(24)
            content_box.set_margin_bottom(24)
            content_box.set_margin_start(24)
            content_box.set_margin_end(24)
            
            # Add explanation label
            explanation = Gtk.Label()
            explanation.set_markup("<b>HTML Source Code:</b>")
            explanation.set_halign(Gtk.Align.START)
            content_box.append(explanation)
            
            # Create a horizontal box for view type toggle buttons
            view_toggle_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            view_toggle_box.set_margin_bottom(12)
            
            # Create toggle buttons for full HTML vs editor content
            full_html_button = Gtk.ToggleButton(label="Full HTML Document")
            full_html_button.set_active(True)  # Default to full HTML
            editor_content_button = Gtk.ToggleButton(label="Editor Content Only")
            
            # Make the buttons part of the same group
            full_html_button.set_group(editor_content_button)
            
            view_toggle_box.append(full_html_button)
            view_toggle_box.append(editor_content_button)
            content_box.append(view_toggle_box)
            
            # Create scrolled window for text view
            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_vexpand(True)
            scrolled_window.set_hexpand(True)
            
            # Create text view for HTML content
            text_view = Gtk.TextView()
            text_view.set_editable(True)  # Allow editing
            text_view.set_monospace(True)  # Use monospace font for code
            text_view.set_wrap_mode(Gtk.WrapMode.WORD)
            
            # Create text buffer and set content
            text_buffer = text_view.get_buffer()
            text_buffer.set_text(full_html_content)  # Default to full HTML
            
            scrolled_window.set_child(text_view)
            content_box.append(scrolled_window)
            
            # Connect toggle buttons to switch content
            def on_full_html_toggled(button):
                if button.get_active():
                    text_buffer.set_text(full_html_content)
                
            def on_editor_content_toggled(button):
                if button.get_active():
                    text_buffer.set_text(editor_content)
            
            full_html_button.connect("toggled", on_full_html_toggled)
            editor_content_button.connect("toggled", on_editor_content_toggled)
            
            # Add buttons box
            buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            buttons_box.set_halign(Gtk.Align.END)
            buttons_box.set_margin_top(12)
            
            # Copy button - left aligned with spacer to separate from other buttons
            copy_button = Gtk.Button(label="Copy to Clipboard")
            copy_button.connect("clicked", lambda btn: self.copy_html_to_clipboard(win, text_buffer))
            copy_button.set_halign(Gtk.Align.START)
            
            # Button spacer to push close/apply buttons to the right
            button_spacer = Gtk.Box()
            button_spacer.set_hexpand(True)
            
            # Apply changes button
            apply_button = Gtk.Button(label="Apply Changes")
            apply_button.add_css_class("suggested-action")
            apply_button.connect("clicked", lambda btn: self.apply_html_changes(win, dialog, text_buffer, full_html_button.get_active()))
            
            # Close button
            close_button = Gtk.Button(label="Close")
            close_button.connect("clicked", lambda btn: dialog.close())
            
            buttons_box.append(copy_button)
            buttons_box.append(button_spacer)
            buttons_box.append(close_button)
            buttons_box.append(apply_button)
            content_box.append(buttons_box)
            
            # Set dialog content and present
            dialog.set_child(content_box)
            dialog.present(win)
            
            # Update status
            win.statusbar.set_text("HTML content displayed")
        else:
            win.statusbar.set_text("Failed to get HTML content")
            
    except Exception as e:
        print(f"Error displaying HTML: {e}")
        win.statusbar.set_text(f"Error displaying HTML: {e}")

def apply_html_changes(self, win, dialog, text_buffer, is_full_html):
    """Apply the edited HTML content back to the editor"""
    try:
        # Get the text from the buffer
        start_iter = text_buffer.get_start_iter()
        end_iter = text_buffer.get_end_iter()
        html_content = text_buffer.get_text(start_iter, end_iter, True)
        
        # Escape for JavaScript
        js_content = html_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        
        if is_full_html:
            # For full HTML, extract just the content of the editor from the full HTML
            # This is a more conservative approach that doesn't try to replace the entire page
            js_code = """
            (function() {
                try {
                    // Parse the new HTML content
                    const parser = new DOMParser();
                    const newDoc = parser.parseFromString("%s", "text/html");
                    
                    // Find the editor content in the new HTML
                    const newEditorContent = newDoc.getElementById('editor');
                    
                    if (newEditorContent) {
                        // Update just the editor content
                        document.getElementById('editor').innerHTML = newEditorContent.innerHTML;
                        return true;
                    } else {
                        console.error("Could not find editor element in the new HTML");
                        return false;
                    }
                } catch (error) {
                    console.error("Error extracting editor content: " + error.message);
                    return false;
                }
            })();
            """ % js_content
            
            # Execute the JavaScript to update the editor content
            win.webview.evaluate_javascript(
                js_code,
                -1, None, None, None,
                lambda webview, result, data: self.handle_apply_html_result(win, webview, result),
                None
            )
        else:
            # For editor content only, set only the editor's content
            js_code = f'setContent("{js_content}");'
            self.execute_js(win, js_code)
        
        # Mark document as modified
        win.modified = True
        self.update_window_title(win)
        
        # Close the dialog
        dialog.close()
        
        # Update status
        win.statusbar.set_text("HTML changes applied")
        
    except Exception as e:
        print(f"Error applying HTML changes: {e}")
        win.statusbar.set_text(f"Error applying HTML changes: {e}")

def handle_apply_html_result(self, win, webview, result):
    """Handle the result of applying HTML changes"""
    try:
        js_result = webview.evaluate_javascript_finish(result)
        
        if hasattr(js_result, 'get_js_value') and js_result.get_js_value().to_boolean():
            win.statusbar.set_text("HTML changes applied successfully")
        else:
            win.statusbar.set_text("There was an issue applying HTML changes")
    except Exception as e:
        print(f"Error handling apply HTML result: {e}")
        win.statusbar.set_text(f"Error applying HTML changes: {e}")
        
def copy_html_to_clipboard(self, win, text_buffer):
    """Copy the HTML content to clipboard"""
    try:
        # Get the text from the buffer
        start_iter = text_buffer.get_start_iter()
        end_iter = text_buffer.get_end_iter()
        html_content = text_buffer.get_text(start_iter, end_iter, True)
        
        # Get the clipboard
        clipboard = Gdk.Display.get_default().get_clipboard()
        
        # Set the text to the clipboard
        clipboard.set(html_content)
        
        # Update status
        win.statusbar.set_text("HTML copied to clipboard")
        
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        win.statusbar.set_text(f"Error copying to clipboard: {e}")
##########################  /show html           


