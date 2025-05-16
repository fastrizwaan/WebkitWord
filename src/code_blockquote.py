#!/usr/bin/env python3
# cod_blockquote.py - formatting related methods with Pygments highlighting
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, GLib, Gio, Pango, PangoCairo
import json
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter
import re

def add_code_and_blockquote_controls(self, win):
    """Add code block and blockquote buttons to the formatting toolbar"""
    code_blockquote_group = Gtk.Box(css_classes=["linked"], orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    code_blockquote_group.set_margin_start(0)
    code_blockquote_group.set_margin_end(0)
    
    # Code Block button with dropdown for language selection
    code_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    code_icon = Gtk.Image.new_from_icon_name("format-code-symbolic")
    code_icon.set_margin_top(4)
    code_icon.set_margin_bottom(0)
    code_box.append(code_icon)
    
    # Color indicator for visual feedback (optional)
    code_indicator = Gtk.Box()
    code_indicator.add_css_class("color-indicator")
    code_indicator.set_size_request(16, 2)
    code_box.append(code_indicator)

    # Create code block popover for the dropdown
    code_popover = Gtk.Popover()
    code_popover.set_autohide(True)
    code_popover.set_has_arrow(False)

    code_box_menu = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    code_box_menu.set_margin_start(6)
    code_box_menu.set_margin_end(6)
    code_box_menu.set_margin_top(6)
    code_box_menu.set_margin_bottom(6)

    # Add language options
    langs_label = Gtk.Label(label="Language:")
    langs_label.set_halign(Gtk.Align.START)
    langs_label.set_margin_bottom(6)
    code_box_menu.append(langs_label)

    # Create language options grid
    langs_grid = Gtk.Grid()
    langs_grid.set_row_spacing(4)
    langs_grid.set_column_spacing(4)
    langs_grid.set_row_homogeneous(True)
    langs_grid.set_column_homogeneous(True)
    
    # List of common programming languages
    languages = [
        "plain", "python", "javascript", "html", "css", 
        "java", "c", "cpp", "csharp", "php", 
        "ruby", "go", "swift", "kotlin", "rust",
        "bash", "sql", "json", "xml", "yaml"
    ]
    
    # Create language buttons and add to grid
    row, col = 0, 0
    cols_per_row = 4
    for lang in languages:
        lang_button = Gtk.Button(label=lang)
        lang_button.connect("clicked", lambda btn, l=lang: self.on_code_language_selected(win, l, code_popover))
        langs_grid.attach(lang_button, col, row, 1, 1)
        col += 1
        if col >= cols_per_row:
            col = 0
            row += 1

    code_box_menu.append(langs_grid)
    code_popover.set_child(code_box_menu)

    # Create the SplitButton
    win.code_button = Adw.SplitButton()
    win.code_button.set_tooltip_text("Insert Code Block")
    win.code_button.set_focus_on_click(False)
    win.code_button.set_size_request(40, 36)
    win.code_button.set_child(code_box)
    win.code_button.set_popover(code_popover)
    
    # Connect click handlers
    win.code_button.connect("clicked", lambda btn: self.on_code_button_clicked(win, "plain"))
    code_blockquote_group.append(win.code_button)
    
    # Blockquote button
    win.blockquote_button = Gtk.Button(icon_name="format-blockquote-symbolic")
    win.blockquote_button.set_tooltip_text("Blockquote")
    win.blockquote_button.set_focus_on_click(False)
    win.blockquote_button.set_size_request(40, 36)
    win.blockquote_button.connect("clicked", lambda btn: self.on_blockquote_clicked(win))
    code_blockquote_group.append(win.blockquote_button)
    
    # Add the group to the toolbar
    win.toolbars_wrapbox.append(code_blockquote_group)

def on_code_language_selected(self, win, language, popover):
    """Handle language selection for code block"""
    popover.popdown()
    self.on_code_button_clicked(win, language)
    win.statusbar.set_text(f"Selected {language} for code highlighting")
def on_code_button_clicked(self, win, language="plain"):
    """Insert a code block with the specified language or toggle existing code block"""
    # First check if the cursor is already inside a code block
    win.webview.evaluate_javascript(
        """
        (function() {
            // Check if cursor is inside a code block
            const selection = window.getSelection();
            if (!selection.rangeCount) return false;
            
            let node = selection.anchorNode;
            if (node.nodeType === 3) { // Text node
                node = node.parentNode;
            }
            
            // Look for code element
            let codeElement = null;
            let preElement = null;
            let currentNode = node;
            
            while (currentNode && currentNode !== document.body) {
                if (currentNode.nodeName === 'CODE') {
                    codeElement = currentNode;
                }
                if (currentNode.nodeName === 'PRE') {
                    preElement = currentNode;
                    if (!codeElement && currentNode.querySelector('code')) {
                        codeElement = currentNode.querySelector('code');
                    }
                    break;
                }
                currentNode = currentNode.parentNode;
            }
            
            // If we're in a code block, toggle it off
            if (codeElement && preElement) {
                const content = codeElement.textContent || '';
                
                // Create a paragraph to replace the code block
                const paragraph = document.createElement('p');
                paragraph.textContent = content;
                
                // Replace the pre element with the paragraph
                if (preElement.parentNode) {
                    preElement.parentNode.replaceChild(paragraph, preElement);
                    
                    // Set selection inside paragraph
                    const range = document.createRange();
                    range.selectNodeContents(paragraph);
                    range.collapse(false); // Collapse to end
                    selection.removeAllRanges();
                    selection.addRange(range);
                    
                    // Notify about content change
                    try {
                        window.webkit.messageHandlers.contentChanged.postMessage('changed');
                    } catch(e) {
                        console.log('Could not notify about content change:', e);
                    }
                    
                    return true; // We toggled a code block
                }
            }
            
            return false; // Not in a code block
        })();
        """,
        -1, None, None, None,
        lambda webview, result, data: self._handle_toggle_result(
            win, webview, result, language),
        None
    )

def _handle_toggle_result(self, win, webview, result, language):
    """Handle result from toggle check - if not toggled, insert a code block"""
    try:
        js_result = webview.evaluate_javascript_finish(result)
        toggled = False
        
        # Check if we got a valid result indicating toggle happened
        if js_result:
            # Get the value as a boolean if possible
            if hasattr(js_result, 'get_js_value'):
                toggled = js_result.get_js_value().to_boolean()
            elif hasattr(js_result, 'to_string'):
                toggled_str = js_result.to_string().lower()
                toggled = toggled_str == 'true'
            else:
                toggled_str = str(js_result).lower()
                toggled = toggled_str == 'true'
        
        if toggled:
            # Code block was toggled off, update status
            win.statusbar.set_text("Converted code block to text")
        else:
            # Not in a code block or toggle failed, insert a new code block
            self._get_selection_and_insert_code_block(win, language)
            
    except Exception as e:
        print(f"Error handling toggle result: {e}")
        # Fall back to inserting a new code block
        self._get_selection_and_insert_code_block(win, language)

def _get_selection_and_insert_code_block(self, win, language):
    """Get selection and insert a new code block"""
    # Get any selected text
    win.webview.evaluate_javascript(
        "window.getSelection().toString();",
        -1, None, None, None,
        lambda webview, result, data: self._insert_code_block_with_selection(
            win, webview, result, language),
        None
    )
def _insert_code_block_with_selection(self, win, webview, result, language):
    """Insert code block with selected text if available"""
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
        
        # Escape the text for JavaScript
        import json
        escaped_text = json.dumps(selected_text)
        
        # JavaScript to insert code block using DOM manipulation
        js_code = """
        (function() {
            // Create a document fragment to hold all the elements
            const fragment = document.createDocumentFragment();
            
            // Create pre element
            const preElement = document.createElement('pre');
            preElement.style.backgroundColor = '#f5f5f5';
            preElement.style.padding = '10px';
            preElement.style.border = '1px solid #ddd';
            preElement.style.borderRadius = '5px';
            preElement.style.overflowX = 'auto';
            preElement.style.margin = '10px 0';
            preElement.style.whiteSpace = 'pre-wrap';
            preElement.setAttribute('data-language', '%s');
            preElement.contentEditable = 'true'; // Ensure the pre element is editable
            
            // Create code element
            const codeElement = document.createElement('code');
            codeElement.className = 'language-%s';
            codeElement.style.fontFamily = 'monospace';
            codeElement.style.whiteSpace = 'pre';
            codeElement.style.display = 'block';
            codeElement.contentEditable = 'true'; // Ensure the code element is editable
            
            // Set text content directly (preserves whitespace and newlines)
            if (%s && %s.trim()) {
                codeElement.textContent = %s;
            } else {
                // If no text is selected, add a <br> to make it clickable
                codeElement.innerHTML = '<br>';
                
                // Also set a data attribute to mark this as a new empty block
                codeElement.setAttribute('data-empty', 'true');
            }
            
            // Add code to pre
            preElement.appendChild(codeElement);
            
            // Add the pre element to the fragment
            fragment.appendChild(preElement);
            
            // Create paragraph after code block for spacing and to provide a place to type
            const paragraph = document.createElement('p');
            paragraph.innerHTML = '<br>';
            paragraph.style.margin = '10px 0';
            fragment.appendChild(paragraph);
            
            // Get current selection and insert the fragment
            const selection = window.getSelection();
            if (selection.rangeCount > 0) {
                const range = selection.getRangeAt(0);
                
                // Remove selected content
                range.deleteContents();
                
                // Insert our fragment with code block and paragraph
                range.insertNode(fragment);
                
                // Determine where to place the cursor
                if (codeElement.getAttribute('data-empty') === 'true') {
                    // If it's a new empty block, place cursor inside the code block
                    const newRange = document.createRange();
                    newRange.selectNodeContents(codeElement);
                    newRange.collapse(true); // Collapse to start
                    selection.removeAllRanges();
                    selection.addRange(newRange);
                } else {
                    // Otherwise, place cursor after the paragraph we added
                    const newRange = document.createRange();
                    newRange.selectNodeContents(paragraph);
                    newRange.collapse(true); // Collapse to start
                    selection.removeAllRanges();
                    selection.addRange(newRange);
                }
            }
            
            // Apply syntax highlighting if available
            if (window.Prism) {
                window.Prism.highlightElement(codeElement);
            }
            
            // Notify content change
            try {
                window.webkit.messageHandlers.contentChanged.postMessage('changed');
            } catch(e) {
                console.log('Could not notify about content change:', e);
            }
        })();
        """ % (language, language, escaped_text, escaped_text, escaped_text)
        
        # Execute the JavaScript
        self.execute_js(win, js_code)
        
        # Update status
        win.statusbar.set_text(f"Inserted {language} code block")
            
    except Exception as e:
        print(f"Error inserting code block: {e}")
        win.statusbar.set_text(f"Error inserting code block: {e}")

def on_blockquote_clicked(self, win):
    """Insert a blockquote or toggle existing blockquote"""
    # First check if the cursor is already inside a blockquote
    win.webview.evaluate_javascript(
        """
        (function() {
            // Check if cursor is inside a blockquote
            const selection = window.getSelection();
            if (!selection.rangeCount) return false;
            
            let node = selection.anchorNode;
            if (node.nodeType === 3) { // Text node
                node = node.parentNode;
            }
            
            // Look for blockquote element
            let blockquoteElement = null;
            let currentNode = node;
            
            while (currentNode && currentNode !== document.body) {
                if (currentNode.nodeName === 'BLOCKQUOTE') {
                    blockquoteElement = currentNode;
                    break;
                }
                currentNode = currentNode.parentNode;
            }
            
            // If we're in a blockquote, toggle it off
            if (blockquoteElement) {
                // Get all content nodes from the blockquote
                const contentNodes = Array.from(blockquoteElement.childNodes);
                
                // Create a document fragment to hold the content
                const fragment = document.createDocumentFragment();
                
                // Move content from blockquote to fragment
                contentNodes.forEach(node => {
                    // If it's a paragraph inside the blockquote, extract its content
                    if (node.nodeName === 'P') {
                        // Create a new paragraph to ensure proper formatting
                        const newParagraph = document.createElement('p');
                        newParagraph.textContent = node.textContent || '';
                        fragment.appendChild(newParagraph);
                    } else {
                        // For other nodes, clone them directly
                        fragment.appendChild(node.cloneNode(true));
                    }
                });
                
                // Replace the blockquote with the fragment
                if (blockquoteElement.parentNode) {
                    // Insert the fragment before the blockquote
                    blockquoteElement.parentNode.insertBefore(fragment, blockquoteElement);
                    
                    // Remove the blockquote
                    blockquoteElement.parentNode.removeChild(blockquoteElement);
                    
                    // Notify about content change
                    try {
                        window.webkit.messageHandlers.contentChanged.postMessage('changed');
                    } catch(e) {
                        console.log('Could not notify about content change:', e);
                    }
                    
                    return true; // We toggled a blockquote
                }
            }
            
            return false; // Not in a blockquote
        })();
        """,
        -1, None, None, None,
        lambda webview, result, data: self._handle_blockquote_toggle_result(
            win, webview, result),
        None
    )

def _handle_blockquote_toggle_result(self, win, webview, result):
    """Handle result from blockquote toggle check - if not toggled, insert a blockquote"""
    try:
        js_result = webview.evaluate_javascript_finish(result)
        toggled = False
        
        # Check if we got a valid result indicating toggle happened
        if js_result:
            # Get the value as a boolean if possible
            if hasattr(js_result, 'get_js_value'):
                toggled = js_result.get_js_value().to_boolean()
            elif hasattr(js_result, 'to_string'):
                toggled_str = js_result.to_string().lower()
                toggled = toggled_str == 'true'
            else:
                toggled_str = str(js_result).lower()
                toggled = toggled_str == 'true'
        
        if toggled:
            # Blockquote was toggled off, update status
            win.statusbar.set_text("Converted blockquote to text")
        else:
            # Not in a blockquote or toggle failed, insert a new blockquote
            self._get_selection_and_insert_blockquote(win)
            
    except Exception as e:
        print(f"Error handling blockquote toggle result: {e}")
        # Fall back to inserting a new blockquote
        self._get_selection_and_insert_blockquote(win)

def _get_selection_and_insert_blockquote(self, win):
    """Get selection and insert a new blockquote"""
    # Get any selected text
    win.webview.evaluate_javascript(
        "window.getSelection().toString();",
        -1, None, None, None,
        lambda webview, result, data: self._insert_blockquote_with_selection(
            win, webview, result),
        None
    )

def _insert_blockquote_with_selection(self, win, webview, result):
    """Insert blockquote with selected text if available"""
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
        
        # If no text is selected or it's empty, use a placeholder
        if not selected_text or not selected_text.strip():
            selected_text = "Blockquote content"
        
        # Escape the text for JavaScript
        import json
        escaped_text = json.dumps(selected_text)
        
        # JavaScript to insert blockquote using DOM manipulation
        js_code = """
        (function() {
            // Create a document fragment to hold the elements
            const fragment = document.createDocumentFragment();
            
            // Create blockquote element
            const blockquoteElement = document.createElement('blockquote');
            blockquoteElement.style.borderLeft = '4px solid #ccc';
            blockquoteElement.style.margin = '10px 0';
            blockquoteElement.style.padding = '10px 20px';
            blockquoteElement.style.color = '#666';
            blockquoteElement.style.backgroundColor = '#f9f9f9';
            
            // Create paragraph for text
            const paragraphElement = document.createElement('p');
            paragraphElement.textContent = %s;
            
            // Add paragraph to blockquote
            blockquoteElement.appendChild(paragraphElement);
            
            // Add blockquote to fragment
            fragment.appendChild(blockquoteElement);
            
            // Create paragraph after blockquote for spacing
            const spacerParagraph = document.createElement('p');
            spacerParagraph.innerHTML = '<br>';
            spacerParagraph.style.margin = '10px 0';
            fragment.appendChild(spacerParagraph);
            
            // Get selection and insert blockquote
            const selection = window.getSelection();
            if (selection.rangeCount > 0) {
                const range = selection.getRangeAt(0);
                
                // Remove selected content
                range.deleteContents();
                
                // Insert blockquote and spacing paragraph
                range.insertNode(fragment);
                
                // Move cursor after the blockquote to the spacer paragraph
                const newRange = document.createRange();
                newRange.selectNodeContents(spacerParagraph);
                newRange.collapse(true); // Collapse to start
                selection.removeAllRanges();
                selection.addRange(newRange);
            }
            
            // Notify content change
            try {
                window.webkit.messageHandlers.contentChanged.postMessage('changed');
            } catch(e) {
                console.log('Could not notify about content change:', e);
            }
        })();
        """ % escaped_text
        
        # Execute the JavaScript
        self.execute_js(win, js_code)
        
        # Update status message
        win.statusbar.set_text("Inserted blockquote")
            
    except Exception as e:
        print(f"Error inserting blockquote: {e}")
        win.statusbar.set_text(f"Error inserting blockquote: {e}")

def add_syntax_highlighting_js(self):
    """Add JavaScript for syntax highlighting and code block editing"""
    return """
    // Load Prism.js for syntax highlighting
    function loadSyntaxHighlighter() {
        // Check if Prism already loaded
        if (window.Prism) {
            return Promise.resolve(window.Prism);
        }
        
        // Load Prism.js
        return new Promise((resolve, reject) => {
            // Add CSS
            const css = document.createElement('link');
            css.rel = 'stylesheet';
            css.href = 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css';
            document.head.appendChild(css);
            
            // Add JavaScript
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js';
            script.onload = () => {
                resolve(window.Prism);
            };
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
    
    // Apply syntax highlighting to code blocks
    function applySyntaxHighlighting() {
        loadSyntaxHighlighter()
            .then(Prism => {
                // Find code blocks
                const codeBlocks = document.querySelectorAll('code[class*="language-"]');
                
                // Apply highlighting
                if (codeBlocks.length > 0) {
                    Prism.highlightAll();
                }
            })
            .catch(error => {
                console.error('Error loading syntax highlighter:', error);
            });
    }
    
    // Setup special key handling for code blocks
    function setupCodeBlockKeyHandling() {
        document.addEventListener('keydown', function(event) {
            // Check if cursor is inside a code block
            const selection = window.getSelection();
            if (!selection.rangeCount) return;
            
            // Get the node where the cursor is
            let node = selection.anchorNode;
            if (node.nodeType === 3) { // Text node
                node = node.parentNode;
            }
            
            // Look for code or pre element
            let codeElement = null;
            let currentNode = node;
            while (currentNode && currentNode !== document.body) {
                if (currentNode.nodeName === 'CODE') {
                    codeElement = currentNode;
                    break;
                }
                if (currentNode.nodeName === 'PRE' && currentNode.querySelector('code')) {
                    codeElement = currentNode.querySelector('code');
                    break;
                }
                currentNode = currentNode.parentNode;
            }
            
            if (!codeElement) return; // Not in a code block
            
            // Handle Tab key for indentation
            if (event.key === 'Tab') {
                event.preventDefault();
                document.execCommand('insertText', false, '    ');
                return;
            }
            
            // Handle Enter key to preserve indentation
            if (event.key === 'Enter') {
                event.preventDefault();
                
                // Get the text up to the cursor
                const cursorPosition = selection.getRangeAt(0).startOffset;
                const textBeforeCursor = selection.anchorNode.textContent || '';
                
                // Find the last newline before cursor
                let lastNewlinePos = textBeforeCursor.lastIndexOf('\\n');
                if (lastNewlinePos === -1) lastNewlinePos = 0;
                
                // Get the indentation from the current line
                let indentation = '';
                for (let i = lastNewlinePos; i < textBeforeCursor.length; i++) {
                    if (textBeforeCursor[i] === ' ' || textBeforeCursor[i] === '\\t') {
                        indentation += textBeforeCursor[i];
                    } else {
                        break;
                    }
                }
                
                // Insert newline with indentation
                document.execCommand('insertText', false, '\\n' + indentation);
                return;
            }
            
            // Handle Backspace to improve code editing
            if (event.key === 'Backspace') {
                // Only special handling if selection is collapsed (no text selected)
                if (selection.isCollapsed) {
                    const range = selection.getRangeAt(0);
                    const cursorPosition = range.startOffset;
                    
                    // Check if cursor is at the beginning of a line with indentation
                    if (node.nodeType === 3) { // Text node
                        const textBeforeCursor = node.textContent.substring(0, cursorPosition);
                        
                        // Find the last newline before cursor
                        const lastNewlinePos = textBeforeCursor.lastIndexOf('\\n');
                        
                        // If we're at the beginning of an indented line
                        if (lastNewlinePos !== -1 && 
                            textBeforeCursor.substring(lastNewlinePos + 1).trim() === '' && 
                            textBeforeCursor.substring(lastNewlinePos + 1).length >= 4) {
                            
                            // Remove 4 spaces at once (one indentation level)
                            event.preventDefault();
                            
                            // Create a range to delete the last 4 spaces
                            const deleteRange = document.createRange();
                            deleteRange.setStart(node, cursorPosition - 4);
                            deleteRange.setEnd(node, cursorPosition);
                            deleteRange.deleteContents();
                            
                            // Update selection
                            selection.removeAllRanges();
                            selection.addRange(deleteRange);
                            return;
                        }
                    }
                }
            }
        });
        
        // Make code blocks easier to click and edit
        document.addEventListener('click', function(event) {
            let target = event.target;
            
            // Check if we clicked on a code block or its parent pre
            if (target.tagName === 'PRE' && target.querySelector('code')) {
                // Redirect the click to the code element
                target = target.querySelector('code');
                
                // If the code is empty or just has a <br>, make sure we can place the cursor
                if (!target.textContent.trim()) {
                    // Set cursor inside
                    const range = document.createRange();
                    range.selectNodeContents(target);
                    range.collapse(true);
                    
                    const selection = window.getSelection();
                    selection.removeAllRanges();
                    selection.addRange(range);
                    
                    // Prevent further propagation
                    event.stopPropagation();
                }
            }
            
            // Handle click directly on code element
            if (target.tagName === 'CODE') {
                // If the code is empty or just has a <br>, make sure we can place the cursor
                if (!target.textContent.trim()) {
                    // Ensure there's at least a <br> for the cursor
                    if (target.innerHTML === '') {
                        target.innerHTML = '<br>';
                    }
                    
                    // Set cursor inside
                    const range = document.createRange();
                    range.selectNodeContents(target);
                    range.collapse(true);
                    
                    const selection = window.getSelection();
                    selection.removeAllRanges();
                    selection.addRange(range);
                }
            }
        });
    }
    
    // Initialize code block behavior when document is loaded
    document.addEventListener('DOMContentLoaded', function() {
        // Load syntax highlighter
        loadSyntaxHighlighter()
            .then(() => {
                applySyntaxHighlighting();
            })
            .catch(error => {
                console.error('Error loading syntax highlighter:', error);
            });
        
        // Setup key handling
        setupCodeBlockKeyHandling();
    });
    """

def _get_code_and_blockquote_styles(self):
    """Return CSS styles for code blocks and blockquotes"""
    return """
        /* Code Block Styles */
        pre {
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            overflow-x: auto;
            font-family: monospace;
            font-size: 0.9em;
            line-height: 1.5;
            white-space: pre-wrap;
            position: relative;
            min-height: 1.5em; /* Ensure empty blocks have height */
        }
        
        code {
            font-family: 'Courier New', Courier, monospace;
            white-space: pre;
            tab-size: 4;
            display: block;
            min-height: 1em; /* Ensure empty blocks have height */
            outline: none; /* Remove focus outline */
            caret-color: #000; /* Make cursor visible */
        }
        
        /* Fix for empty code blocks to make them clickable */
        pre:empty::after {
            content: "";
            display: inline-block;
            min-height: 1em;
        }
        
        code:empty::after {
            content: "";
            display: inline-block;
            min-height: 1em;
        }
        
        /* Language label */
        pre[data-language]::before {
            content: attr(data-language);
            position: absolute;
            top: -10px;
            right: 10px;
            font-size: 0.8em;
            background-color: #ddd;
            padding: 2px 5px;
            border-radius: 3px;
            color: #555;
            pointer-events: none; /* Don't interfere with editing */
        }
        
        /* Add a subtle highlight when code block is focused */
        pre:focus-within {
            box-shadow: 0 0 0 2px rgba(66, 153, 225, 0.3);
        }
        
        /* Blockquote Styles */
        blockquote {
            border-left: 4px solid #ccc;
            margin: 10px 0;
            padding: 10px 20px;
            color: #666;
            background-color: #f9f9f9;
        }
        
        blockquote p {
            margin: 0;
        }
        
        /* Dark mode styles */
        @media (prefers-color-scheme: dark) {
            pre {
                background-color: #2d2d2d;
                border-color: #555;
                color: #ddd;
            }
            
            pre[data-language]::before {
                background-color: #555;
                color: #eee;
            }
            
            code {
                color: #ddd;
                caret-color: #fff; /* Make cursor visible in dark mode */
            }
            
            blockquote {
                border-color: #555;
                color: #bbb;
                background-color: #2d2d2d;
            }
            
            pre:focus-within {
                box-shadow: 0 0 0 2px rgba(66, 153, 225, 0.5);
            }
        }
    """

def setup_code_block_key_handlers_js(self):
    """JavaScript to handle special key events in code blocks"""
    return """
    // Handle special key events in code blocks
    function setupCodeBlockKeyHandler() {
        document.addEventListener('keydown', function(event) {
            // Find if cursor is inside a code block
            const selection = window.getSelection();
            if (!selection.rangeCount) return;
            
            const range = selection.getRangeAt(0);
            let node = range.startContainer;
            
            // Look for code element in parents
            let codeElement = null;
            while (node && node !== document.body) {
                if (node.nodeName === 'CODE') {
                    codeElement = node;
                    break;
                }
                node = node.parentNode;
            }
            
            if (!codeElement) return; // Not in a code block
            
            // Handle tab key for indentation
            if (event.key === 'Tab') {
                event.preventDefault();
                
                // Insert spaces for indentation
                document.execCommand('insertText', false, '    ');
                return;
            }
            
            // Handle enter key to preserve indentation
            if (event.key === 'Enter') {
                event.preventDefault();
                
                // Get the text content
                const text = codeElement.textContent;
                
                // Get cursor position within the text
                const sel = window.getSelection();
                const range = sel.getRangeAt(0);
                const preCaret = document.createRange();
                preCaret.selectNodeContents(codeElement);
                preCaret.setEnd(range.startContainer, range.startOffset);
                const cursorPos = preCaret.toString().length;
                
                // Find the start of the current line
                let lineStart = cursorPos;
                while (lineStart > 0 && text[lineStart - 1] !== '\\n') {
                    lineStart--;
                }
                
                // Find indentation of current line
                let indent = '';
                for (let i = lineStart; i < text.length && i < cursorPos; i++) {
                    if (text[i] === ' ' || text[i] === '\\t') {
                        indent += text[i];
                    } else {
                        break;
                    }
                }
                
                // Insert newline with the same indentation
                document.execCommand('insertText', false, '\\n' + indent);
                return;
            }
        });
    }
    """
def add_code_and_blockquote_controls(self, win):
    """Add code block and blockquote buttons to the formatting toolbar"""
    code_blockquote_group = Gtk.Box(css_classes=["linked"], orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    code_blockquote_group.set_margin_start(0)
    code_blockquote_group.set_margin_end(0)
    
    # Code Block button with dropdown for language selection
    code_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    code_icon = Gtk.Image.new_from_icon_name("format-code-symbolic")
    code_icon.set_margin_top(4)
    code_icon.set_margin_bottom(0)
    code_box.append(code_icon)
    
    # Color indicator for visual feedback (optional)
    code_indicator = Gtk.Box()
    code_indicator.add_css_class("color-indicator")
    code_indicator.set_size_request(16, 2)
    code_box.append(code_indicator)

    # Create code block popover for the dropdown
    code_popover = Gtk.Popover()
    code_popover.set_autohide(True)
    code_popover.set_has_arrow(False)

    code_box_menu = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    code_box_menu.set_margin_start(6)
    code_box_menu.set_margin_end(6)
    code_box_menu.set_margin_top(6)
    code_box_menu.set_margin_bottom(6)

    # Add language options
    langs_label = Gtk.Label(label="Language:")
    langs_label.set_halign(Gtk.Align.START)
    langs_label.set_margin_bottom(6)
    code_box_menu.append(langs_label)

    # Create language options grid
    langs_grid = Gtk.Grid()
    langs_grid.set_row_spacing(4)
    langs_grid.set_column_spacing(4)
    langs_grid.set_row_homogeneous(True)
    langs_grid.set_column_homogeneous(True)
    
    # List of common programming languages
    languages = [
        "plain", "python", "javascript", "html", "css", 
        "java", "c", "cpp", "csharp", "php", 
        "ruby", "go", "swift", "kotlin", "rust",
        "bash", "sql", "json", "xml", "yaml"
    ]
    
    # Create language buttons and add to grid
    row, col = 0, 0
    cols_per_row = 4
    for lang in languages:
        lang_button = Gtk.Button(label=lang)
        lang_button.connect("clicked", lambda btn, l=lang: self.on_code_language_selected(win, l, code_popover))
        langs_grid.attach(lang_button, col, row, 1, 1)
        col += 1
        if col >= cols_per_row:
            col = 0
            row += 1

    code_box_menu.append(langs_grid)
    code_popover.set_child(code_box_menu)

    # Create the SplitButton
    win.code_button = Adw.SplitButton()
    win.code_button.set_tooltip_text("Insert Code Block")
    win.code_button.set_focus_on_click(False)
    win.code_button.set_size_request(40, 36)
    win.code_button.set_child(code_box)
    win.code_button.set_popover(code_popover)
    
    # Connect click handlers
    win.code_button.connect("clicked", lambda btn: self.on_code_button_clicked(win, "plain"))
    code_blockquote_group.append(win.code_button)
    
    # Blockquote button
    win.blockquote_button = Gtk.Button(icon_name="format-blockquote-symbolic")
    win.blockquote_button.set_tooltip_text("Blockquote")
    win.blockquote_button.set_focus_on_click(False)
    win.blockquote_button.set_size_request(40, 36)
    win.blockquote_button.connect("clicked", lambda btn: self.on_blockquote_clicked(win))
    code_blockquote_group.append(win.blockquote_button)
    
    # Add the group to the toolbar
    win.toolbars_wrapbox.append(code_blockquote_group)

def on_code_language_selected(self, win, language, popover):
    """Handle language selection for code block"""
    popover.popdown()
    self.on_code_button_clicked(win, language)
    win.statusbar.set_text(f"Selected {language} for code highlighting")

def on_code_button_clicked(self, win, language="plain"):
    """Insert a code block with the specified language or toggle existing code block"""
    # First check if the cursor is already inside a code block
    win.webview.evaluate_javascript(
        """
        (function() {
            // Check if cursor is inside a code block
            const selection = window.getSelection();
            if (!selection.rangeCount) return false;
            
            let node = selection.anchorNode;
            if (node.nodeType === 3) { // Text node
                node = node.parentNode;
            }
            
            // Look for code element
            let codeElement = null;
            let preElement = null;
            let currentNode = node;
            
            while (currentNode && currentNode !== document.body) {
                if (currentNode.nodeName === 'CODE') {
                    codeElement = currentNode;
                }
                if (currentNode.nodeName === 'PRE') {
                    preElement = currentNode;
                    if (!codeElement && currentNode.querySelector('code')) {
                        codeElement = currentNode.querySelector('code');
                    }
                    break;
                }
                currentNode = currentNode.parentNode;
            }
            
            // If we're in a code block, toggle it off
            if (codeElement && preElement) {
                const content = codeElement.textContent || '';
                
                // Create a paragraph to replace the code block
                const paragraph = document.createElement('p');
                paragraph.textContent = content;
                
                // Replace the pre element with the paragraph
                if (preElement.parentNode) {
                    preElement.parentNode.replaceChild(paragraph, preElement);
                    
                    // Set selection inside paragraph
                    const range = document.createRange();
                    range.selectNodeContents(paragraph);
                    range.collapse(false); // Collapse to end
                    selection.removeAllRanges();
                    selection.addRange(range);
                    
                    // Notify about content change
                    try {
                        window.webkit.messageHandlers.contentChanged.postMessage('changed');
                    } catch(e) {
                        console.log('Could not notify about content change:', e);
                    }
                    
                    return true; // We toggled a code block
                }
            }
            
            return false; // Not in a code block
        })();
        """,
        -1, None, None, None,
        lambda webview, result, data: self._handle_toggle_result(
            win, webview, result, language),
        None
    )

def _handle_toggle_result(self, win, webview, result, language):
    """Handle result from toggle check - if not toggled, insert a code block"""
    try:
        js_result = webview.evaluate_javascript_finish(result)
        toggled = False
        
        # Check if we got a valid result indicating toggle happened
        if js_result:
            # Get the value as a boolean if possible
            if hasattr(js_result, 'get_js_value'):
                toggled = js_result.get_js_value().to_boolean()
            elif hasattr(js_result, 'to_string'):
                toggled_str = js_result.to_string().lower()
                toggled = toggled_str == 'true'
            else:
                toggled_str = str(js_result).lower()
                toggled = toggled_str == 'true'
        
        if toggled:
            # Code block was toggled off, update status
            win.statusbar.set_text("Converted code block to text")
        else:
            # Not in a code block or toggle failed, insert a new code block
            self._get_selection_and_insert_code_block(win, language)
            
    except Exception as e:
        print(f"Error handling toggle result: {e}")
        # Fall back to inserting a new code block
        self._get_selection_and_insert_code_block(win, language)

def _get_selection_and_insert_code_block(self, win, language):
    """Get selection and insert a new code block"""
    # Get any selected text
    win.webview.evaluate_javascript(
        "window.getSelection().toString();",
        -1, None, None, None,
        lambda webview, result, data: self._insert_code_block_with_selection(
            win, webview, result, language),
        None
    )

def _insert_code_block_with_selection(self, win, webview, result, language):
    """Insert code block with selected text if available and apply Pygments highlighting"""
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
        
        # Apply syntax highlighting using Pygments
        highlighted_code = self._apply_pygments_highlighting(selected_text, language)
        
        # Make highlighted code safe for insertion into JavaScript
        import json
        escaped_highlighted_code = json.dumps(highlighted_code)
        
        # JavaScript to insert code block using DOM manipulation
        js_code = """
        (function() {
            // Create a document fragment to hold all the elements
            const fragment = document.createDocumentFragment();
            
            // Create pre element
            const preElement = document.createElement('pre');
            preElement.style.backgroundColor = '#f5f5f5';
            preElement.style.padding = '10px';
            preElement.style.border = '1px solid #ddd';
            preElement.style.borderRadius = '5px';
            preElement.style.overflowX = 'auto';
            preElement.style.margin = '10px 0';
            preElement.style.whiteSpace = 'pre-wrap';
            preElement.setAttribute('data-language', '%s');
            preElement.contentEditable = 'true'; // Ensure the pre element is editable
            
            // Insert the Pygments highlighted HTML
            preElement.innerHTML = %s;
            
            // Add the pre element to the fragment
            fragment.appendChild(preElement);
            
            // Create paragraph after code block for spacing and to provide a place to type
            const paragraph = document.createElement('p');
            paragraph.innerHTML = '<br>';
            paragraph.style.margin = '10px 0';
            fragment.appendChild(paragraph);
            
            // Get current selection and insert the fragment
            const selection = window.getSelection();
            if (selection.rangeCount > 0) {
                const range = selection.getRangeAt(0);
                
                // Remove selected content
                range.deleteContents();
                
                // Insert our fragment with code block and paragraph
                range.insertNode(fragment);
                
                // Place cursor after the paragraph we added
                const newRange = document.createRange();
                newRange.selectNodeContents(paragraph);
                newRange.collapse(true); // Collapse to start
                selection.removeAllRanges();
                selection.addRange(newRange);
            }
            
            // Notify content change
            try {
                window.webkit.messageHandlers.contentChanged.postMessage('changed');
            } catch(e) {
                console.log('Could not notify about content change:', e);
            }
        })();
        """ % (language, escaped_highlighted_code)
        
        # Execute the JavaScript
        self.execute_js(win, js_code)
        
        # Update status
        win.statusbar.set_text(f"Inserted {language} code block with syntax highlighting")
            
    except Exception as e:
        print(f"Error inserting code block: {e}")
        win.statusbar.set_text(f"Error inserting code block: {e}")

def _apply_pygments_highlighting(self, code_text, language):
    """Apply Pygments syntax highlighting to the code and return HTML"""
    try:
        # Use the appropriate lexer for the language
        try:
            lexer = get_lexer_by_name(language, stripall=True)
        except:
            # Fallback to plain text lexer if language not recognized
            lexer = TextLexer()
        
        # Use HTML formatter with some styling
        formatter = HtmlFormatter(
            style='default',
            linenos=False,
            cssclass='pygments',
            noclasses=True,  # Inline styles instead of CSS classes
            wrapcode=True
        )
        
        # If no text, create a placeholder
        if not code_text or not code_text.strip():
            code_text = " "  # Empty space to ensure the block is clickable
        
        # Apply highlighting and wrap with <code> tags
        highlighted_html = highlight(code_text, lexer, formatter)
        
        # The highlighted HTML already includes some styling, but we need to make it editable
        highlighted_html = highlighted_html.replace('<div class="pygments"', '<code class="language-' + language + '"')
        highlighted_html = highlighted_html.replace('</div>', '</code>')
        
        return highlighted_html
        
    except Exception as e:
        print(f"Error in Pygments highlighting: {e}")
        # Fallback to plain code tag if highlighting fails
        return f'<code class="language-{language}">{code_text}</code>'

def add_syntax_highlighting_css(self):
    """Return CSS for syntax highlighting using Pygments"""
    return """
    /* Pygments Syntax Highlighting Styles */
    pre {
        background-color: #f8f8f8;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        overflow-x: auto;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9em;
        line-height: 1.5;
        position: relative;
    }
    
    pre[data-language]::before {
        content: attr(data-language);
        position: absolute;
        top: -10px;
        right: 10px;
        font-size: 0.8em;
        background-color: #ddd;
        padding: 2px 5px;
        border-radius: 3px;
        color: #555;
    }
    
    pre code {
        font-family: 'Courier New', Courier, monospace;
        white-space: pre;
        display: block;
    }
    
    /* Token colors (based on Pygments default style) */
    .pygments .hll { background-color: #ffffcc }
    .pygments .c { color: #408080; font-style: italic } /* Comment */
    .pygments .err { border: 1px solid #FF0000 } /* Error */
    .pygments .k { color: #008000; font-weight: bold } /* Keyword */
    .pygments .o { color: #666666 } /* Operator */
    .pygments .ch { color: #408080; font-style: italic } /* Comment.Hashbang */
    .pygments .cm { color: #408080; font-style: italic } /* Comment.Multiline */
    .pygments .cp { color: #BC7A00 } /* Comment.Preproc */
    .pygments .cpf { color: #408080; font-style: italic } /* Comment.PreprocFile */
    .pygments .c1 { color: #408080; font-style: italic } /* Comment.Single */
    .pygments .cs { color: #408080; font-style: italic } /* Comment.Special */
    .pygments .gd { color: #A00000 } /* Generic.Deleted */
    .pygments .ge { font-style: italic } /* Generic.Emph */
    .pygments .gr { color: #FF0000 } /* Generic.Error */
    .pygments .gh { color: #000080; font-weight: bold } /* Generic.Heading */
    .pygments .gi { color: #00A000 } /* Generic.Inserted */
    .pygments .go { color: #888888 } /* Generic.Output */
    .pygments .gp { color: #000080; font-weight: bold } /* Generic.Prompt */
    .pygments .gs { font-weight: bold } /* Generic.Strong */
    .pygments .gu { color: #800080; font-weight: bold } /* Generic.Subheading */
    .pygments .gt { color: #0044DD } /* Generic.Traceback */
    .pygments .kc { color: #008000; font-weight: bold } /* Keyword.Constant */
    .pygments .kd { color: #008000; font-weight: bold } /* Keyword.Declaration */
    .pygments .kn { color: #008000; font-weight: bold } /* Keyword.Namespace */
    .pygments .kp { color: #008000 } /* Keyword.Pseudo */
    .pygments .kr { color: #008000; font-weight: bold } /* Keyword.Reserved */
    .pygments .kt { color: #B00040 } /* Keyword.Type */
    .pygments .m { color: #666666 } /* Literal.Number */
    .pygments .s { color: #BA2121 } /* Literal.String */
    .pygments .na { color: #7D9029 } /* Name.Attribute */
    .pygments .nb { color: #008000 } /* Name.Builtin */
    .pygments .nc { color: #0000FF; font-weight: bold } /* Name.Class */
    .pygments .no { color: #880000 } /* Name.Constant */
    .pygments .nd { color: #AA22FF } /* Name.Decorator */
    .pygments .ni { color: #999999; font-weight: bold } /* Name.Entity */
    .pygments .ne { color: #D2413A; font-weight: bold } /* Name.Exception */
    .pygments .nf { color: #0000FF } /* Name.Function */
    .pygments .nl { color: #A0A000 } /* Name.Label */
    .pygments .nn { color: #0000FF; font-weight: bold } /* Name.Namespace */
    .pygments .nt { color: #008000; font-weight: bold } /* Name.Tag */
    .pygments .nv { color: #19177C } /* Name.Variable */
    .pygments .ow { color: #AA22FF; font-weight: bold } /* Operator.Word */
    .pygments .w { color: #bbbbbb } /* Text.Whitespace */
    .pygments .mb { color: #666666 } /* Literal.Number.Bin */
    .pygments .mf { color: #666666 } /* Literal.Number.Float */
    .pygments .mh { color: #666666 } /* Literal.Number.Hex */
    .pygments .mi { color: #666666 } /* Literal.Number.Integer */
    .pygments .mo { color: #666666 } /* Literal.Number.Oct */
    .pygments .sa { color: #BA2121 } /* Literal.String.Affix */
    .pygments .sb { color: #BA2121 } /* Literal.String.Backtick */
    .pygments .sc { color: #BA2121 } /* Literal.String.Char */
    .pygments .dl { color: #BA2121 } /* Literal.String.Delimiter */
    .pygments .sd { color: #BA2121; font-style: italic } /* Literal.String.Doc */
    .pygments .s2 { color: #BA2121 } /* Literal.String.Double */
    .pygments .se { color: #BB6622; font-weight: bold } /* Literal.String.Escape */
    .pygments .sh { color: #BA2121 } /* Literal.String.Heredoc */
    .pygments .si { color: #BB6688; font-weight: bold } /* Literal.String.Interpol */
    .pygments .sx { color: #008000 } /* Literal.String.Other */
    .pygments .sr { color: #BB6688 } /* Literal.String.Regex */
    .pygments .s1 { color: #BA2121 } /* Literal.String.Single */
    .pygments .ss { color: #19177C } /* Literal.String.Symbol */
    .pygments .bp { color: #008000 } /* Name.Builtin.Pseudo */
    .pygments .fm { color: #0000FF } /* Name.Function.Magic */
    .pygments .vc { color: #19177C } /* Name.Variable.Class */
    .pygments .vg { color: #19177C } /* Name.Variable.Global */
    .pygments .vi { color: #19177C } /* Name.Variable.Instance */
    .pygments .vm { color: #19177C } /* Name.Variable.Magic */
    .pygments .il { color: #666666 } /* Literal.Number.Integer.Long */
    
    /* Dark mode styles */
    @media (prefers-color-scheme: dark) {
        pre {
            background-color: #2d2d2d;
            border-color: #555;
            color: #f8f8f2;
        }
        
        pre[data-language]::before {
            background-color: #555;
            color: #eee;
        }
        
        /* Monokai-inspired color scheme for dark mode */
        .pygments .hll { background-color: #49483e }
        .pygments .c { color: #75715e } /* Comment */
        .pygments .err { color: #960050; background-color: #1e0010 } /* Error */
        .pygments .k { color: #66d9ef } /* Keyword */
        .pygments .l { color: #ae81ff } /* Literal */
        .pygments .n { color: #f8f8f2 } /* Name */
        .pygments .o { color: #f92672 } /* Operator */
        .pygments .p { color: #f8f8f2 } /* Punctuation */
        .pygments .ch { color: #75715e } /* Comment.Hashbang */
        .pygments .cm { color: #75715e } /* Comment.Multiline */
        .pygments .cp { color: #75715e } /* Comment.Preproc */
        .pygments .cpf { color: #75715e } /* Comment.PreprocFile */
        .pygments .c1 { color: #75715e } /* Comment.Single */
        .pygments .cs { color: #75715e } /* Comment.Special */
        .pygments .gd { color: #f92672 } /* Generic.Deleted */
        .pygments .ge { font-style: italic } /* Generic.Emph */
        .pygments .gi { color: #a6e22e } /* Generic.Inserted */
        .pygments .gs { font-weight: bold } /* Generic.Strong */
        .pygments .gu { color: #75715e } /* Generic.Subheading */
        .pygments .kc { color: #66d9ef } /* Keyword.Constant */
        .pygments .kd { color: #66d9ef } /* Keyword.Declaration */
        .pygments .kn { color: #f92672 } /* Keyword.Namespace */
        .pygments .kp { color: #66d9ef } /* Keyword.Pseudo */
        .pygments .kr { color: #66d9ef } /* Keyword.Reserved */
        .pygments .kt { color: #66d9ef } /* Keyword.Type */
        .pygments .m { color: #ae81ff } /* Literal.Number */
        .pygments .s { color: #e6db74 } /* Literal.String */
        .pygments .na { color: #a6e22e } /* Name.Attribute */
        .pygments .nb { color: #f8f8f2 } /* Name.Builtin */
        .pygments .nc { color: #a6e22e } /* Name.Class */
        .pygments .no { color: #66d9ef } /* Name.Constant */
        .pygments .nd { color: #a6e22e } /* Name.Decorator */
        .pygments .ni { color: #f8f8f2 } /* Name.Entity */
        .pygments .ne { color: #a6e22e } /* Name.Exception */
        .pygments .nf { color: #a6e22e } /* Name.Function */
        .pygments .nl { color: #f8f8f2 } /* Name.Label */
        .pygments .nn { color: #f8f8f2 } /* Name.Namespace */
        .pygments .nx { color: #a6e22e } /* Name.Other */
        .pygments .py { color: #f8f8f2 } /* Name.Property */
        .pygments .nt { color: #f92672 } /* Name.Tag */
        .pygments .nv { color: #f8f8f2 } /* Name.Variable */
        .pygments .ow { color: #f92672 } /* Operator.Word */
        .pygments .w { color: #f8f8f2 } /* Text.Whitespace */
        .pygments .mb { color: #ae81ff } /* Literal.Number.Bin */
        .pygments .mf { color: #ae81ff } /* Literal.Number.Float */
        .pygments .mh { color: #ae81ff } /* Literal.Number.Hex */
        .pygments .mi { color: #ae81ff } /* Literal.Number.Integer */
        .pygments .mo { color: #ae81ff } /* Literal.Number.Oct */
        .pygments .sa { color: #e6db74 } /* Literal.String.Affix */
        .pygments .sb { color: #e6db74 } /* Literal.String.Backtick */
        .pygments .sc { color: #e6db74 } /* Literal.String.Char */
        .pygments .dl { color: #e6db74 } /* Literal.String.Delimiter */
        .pygments .sd { color: #e6db74 } /* Literal.String.Doc */
        .pygments .s2 { color: #e6db74 } /* Literal.String.Double */
        .pygments .se { color: #ae81ff } /* Literal.String.Escape */
        .pygments .sh { color: #e6db74 } /* Literal.String.Heredoc */
        .pygments .si { color: #e6db74 } /* Literal.String.Interpol */
        .pygments .sx { color: #e6db74 } /* Literal.String.Other */
        .pygments .sr { color: #e6db74 } /* Literal.String.Regex */
        .pygments .s1 { color: #e6db74 } /* Literal.String.Single */
        .pygments .ss { color: #e6db74 } /* Literal.String.Symbol */
        .pygments .bp { color: #f8f8f2 } /* Name.Builtin.Pseudo */
        .pygments .fm { color: #a6e22e } /* Name.Function.Magic */
        .pygments .vc { color: #f8f8f2 } /* Name.Variable.Class */
        .pygments .vg { color: #f8f8f2 } /* Name.Variable.Global */
        .pygments .vi { color: #f8f8f2 } /* Name.Variable.Instance */
        .pygments .vm { color: #f8f8f2 } /* Name.Variable.Magic */
        .pygments .il { color: #ae81ff } /* Literal.Number.Integer.Long */
    }
    """

def setup_web_editor(self, win):
    """Setup the web editor with Pygments syntax highlighting support"""
    # Make sure to add the Pygments CSS to the editor's header
    win.webview.evaluate_javascript(
        f"""
        // Add Pygments CSS to head
        const style = document.createElement('style');
        style.textContent = `{self.add_syntax_highlighting_css()}`;
        document.head.appendChild(style);
        """,
        -1, None, None, None, None, None
    )
    
    # Register content change handler
    win.webview.register_script_message_handler("contentChanged")
    win.webview.connect("script-message-received::contentChanged", 
                        lambda webview, message: self.on_content_changed(win))
    
def _apply_pygments_highlighting(self, code_text, language):
    """Apply Pygments syntax highlighting to the code and return HTML"""
    try:
        # Use the appropriate lexer for the language
        try:
            lexer = get_lexer_by_name(language, stripall=True)
        except:
            # Fallback to plain text lexer if language not recognized
            lexer = TextLexer()
        
        # Use HTML formatter with some styling, but WITHOUT wrapping tags
        formatter = HtmlFormatter(
            style='default',
            linenos=False,
            noclasses=True,  # Inline styles instead of CSS classes
            nowrap=True  # This is key - prevents the <div> wrapper
        )
        
        # If no text, create a placeholder
        if not code_text or not code_text.strip():
            code_text = " "  # Empty space to ensure the block is clickable
        
        # Apply highlighting - this will return just the highlighted content without wrapper tags
        highlighted_text = highlight(code_text, lexer, formatter)
        
        # Return the highlighted text without any wrapper tags
        return highlighted_text
        
    except Exception as e:
        print(f"Error in Pygments highlighting: {e}")
        # Fallback to plain text if highlighting fails
        return code_text

############
def _get_selection_and_insert_code_block(self, win, webview, result, language):
    """Extract selected text and insert code block"""
    try:
        js_result = webview.evaluate_javascript_finish(result)
        if js_result:
            # Get the selected text from the result
            selected_text = ""
            if hasattr(js_result, 'get_js_value'):
                selected_text = js_result.get_js_value().to_string()
            elif hasattr(js_result, 'to_string'):
                selected_text = js_result.to_string()
            else:
                selected_text = str(js_result)
            
            # Insert the code block with the selected text
            self._insert_code_block_with_selection(win, language, selected_text)
        else:
            # No selection, insert an empty code block
            self._insert_code_block_with_selection(win, language, "")
    except Exception as e:
        print(f"Error getting selected text: {e}")
        win.statusbar.set_text(f"Error inserting code block: {e}")

def _get_selection_and_insert_blockquote(self, win, webview, result):
    """Extract selected text and insert blockquote"""
    try:
        js_result = webview.evaluate_javascript_finish(result)
        if js_result:
            # Get the selected text from the result
            selected_text = ""
            if hasattr(js_result, 'get_js_value'):
                selected_text = js_result.get_js_value().to_string()
            elif hasattr(js_result, 'to_string'):
                selected_text = js_result.to_string()
            else:
                selected_text = str(js_result)
            
            # Insert the blockquote with the selected text
            self._insert_blockquote_with_selection(win, selected_text)
        else:
            # No selection, insert an empty blockquote
            self._insert_blockquote_with_selection(win, "")
    except Exception as e:
        print(f"Error getting selected text: {e}")
        win.statusbar.set_text(f"Error inserting blockquote: {e}")        

def _insert_blockquote_with_selection(self, win, selected_text=None):
    """Insert blockquote as a table cell with selected text if available"""
    # If selected_text is not provided, get it from the current selection
    if selected_text is None:
        win.webview.evaluate_javascript(
            "window.getSelection().toString();",
            -1, None, None, None,
            lambda webview, result, data: self._get_selection_and_insert_blockquote(win, webview, result),
            None
        )
        return

    # Create a table-based blockquote similar to text box approach
    js_code = f"""
    (function() {{
        // Check if the current selection is inside a table
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
        insertTable(1, 1, false, 0, "100%", false);
        
        // Get the newly created table
        setTimeout(() => {{
            const tables = document.querySelectorAll('table.editor-table');
            const newTable = tables[tables.length - 1] || document.querySelector('table:last-of-type');
            if (newTable) {{
                // Apply styling specific to blockquote
                newTable.classList.add('blockquote-table');
                
                // Set width
                newTable.style.width = '100%';
                
                // Set background based on theme
                newTable.style.backgroundColor = isDarkMode() ? '#2d2d2d' : '#f9f9f9';
                newTable.setAttribute('data-bg-color', isDarkMode() ? '#2d2d2d' : '#f9f9f9');
                
                // Apply border styling for blockquote appearance
                newTable.style.borderLeft = isDarkMode() ? '4px solid #444' : '4px solid #ccc';
                newTable.style.borderTop = '0';
                newTable.style.borderRight = '0';
                newTable.style.borderBottom = '0';
                
                // Get the cell
                const cell = newTable.querySelector('td');
                if (cell) {{
                    // Set padding and styling
                    cell.style.padding = '10px 20px';
                    cell.style.color = isDarkMode() ? '#c0c0c0' : '#666';
                    
                    // Set the content - create a paragraph if needed
                    const content = `{selected_text.replace("'", "\\'")}`;
                    
                    if (content.includes('\\n')) {{
                        // For multi-line content, create paragraphs
                        const paragraphs = content.split('\\n').filter(p => p.trim() !== '');
                        let html = '';
                        paragraphs.forEach(para => {{
                            html += `<p>${{para}}</p>`;
                        }});
                        cell.innerHTML = html || '<p><br></p>';
                    }} else if (content.trim() === '') {{
                        cell.innerHTML = '<p><br></p>';
                    }} else {{
                        cell.innerHTML = `<p>${{content}}</p>`;
                    }}
                }}
                
                // Set up the table for editor context
                activateTable(newTable);
            }}
        }}, 50);
        
        return true;
    }})();
    """
    win.webview.evaluate_javascript(js_code, -1, None, None, None, None, None)
    win.statusbar.set_text("Blockquote inserted")



    