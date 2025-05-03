#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, GLib, Gio, Pango, PangoCairo

# insert_table.py, This module contains find-related methods for the HTML Editor application

def _parse_color_string(self, color_str):
    """Parse a color string (hex, rgb, or rgba) into a Gdk.RGBA object"""
    try:
        rgba = Gdk.RGBA()
        
        if color_str.startswith('#'):
            # Hex color
            rgba.parse(color_str)
            return rgba
        elif color_str.startswith('rgb'):
            # RGB(A) color
            import re
            match = re.search(r'rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s]+([\d.]+))?\)', color_str)
            if match:
                r, g, b = float(match.group(1)), float(match.group(2)), float(match.group(3))
                a = float(match.group(4)) if match.group(4) else 1.0
                
                # Convert 0-255 range to 0-1 range if necessary
                if r > 1 or g > 1 or b > 1:
                    r, g, b = r/255, g/255, b/255
                
                rgba.red, rgba.green, rgba.blue, rgba.alpha = r, g, b, a
                return rgba
        
        return None
    except Exception as e:
        print(f"Error parsing color string '{color_str}': {e}")
        return None

def _is_dark_theme(self):
    """Check if the system is using dark theme"""
    try:
        style_manager = Adw.StyleManager.get_default()
        return style_manager.get_dark()
    except:
        # Fallback method
        settings = Gtk.Settings.get_default()
        return settings.get_property("gtk-application-prefer-dark-theme")

def _rgba_to_color(self, rgba):
    """Convert Gdk.RGBA to Gdk.Color for compatibility"""
    color = Gdk.Color()
    color.red = int(rgba.red * 65535)
    color.green = int(rgba.green * 65535)
    color.blue = int(rgba.blue * 65535)
    return color

def _update_margin_controls(self, win, webview, result):
    """Update margin spin buttons with current table margins"""
    try:
        js_result = webview.evaluate_javascript_finish(result)
        result_str = None
        
        if hasattr(js_result, 'get_js_value'):
            result_str = js_result.get_js_value().to_string()
        else:
            result_str = js_result.to_string()
        
        if result_str:
            import json
            margins = json.loads(result_str)
            
            if hasattr(win, 'margin_controls') and isinstance(margins, dict):
                for side in ['top', 'right', 'bottom', 'left']:
                    if side in win.margin_controls and side in margins:
                        win.margin_controls[side].set_value(margins[side])
    except Exception as e:
        print(f"Error updating margin controls: {e}")

def on_margin_changed(self, win, side, value):
    """Apply margin change to the active table"""
    js_code = f"""
    (function() {{
        // Pass all four sides with the updated value for the specified side
        const margins = getTableMargins() || {{ top: 0, right: 0, bottom: 0, left: 0 }};
        margins.{side} = {value};
        setTableMargins(margins.top, margins.right, margins.bottom, margins.left);
        return true;
    }})();
    """
    self.execute_js(win, js_code)
    win.statusbar.set_text(f"Applied {side} margin: {value}px")   

def on_table_float_clicked(self, win):
    """Make table float freely in the editor"""
    js_code = "setTableFloating();"
    self.execute_js(win, js_code)
    win.statusbar.set_text("Table is now floating")


############################# /TABLE RELATED HTMLEDITOR METHODS

#################### DIRECT COPY PASTE from TABLE52
def insert_table_js(self):
    """JavaScript for insert table and related functionality"""
    return f"""
    {self.table_theme_helpers_js()}
    {self.table_handles_css_js()}
    {self.table_insert_functions_js()}
    {self.table_activation_js()}
    {self.table_drag_resize_js()}
    {self.table_row_column_js()}
    {self.table_alignment_js()}
    {self.table_floating_js()}
    {self.table_event_handlers_js()}
    """

def table_z_index_js(self):
    return """
    // Function to change z-index of active element (bring forward)
    function bringElementForward() {
        if (!activeTable) return false;
        
        // Only apply to floating elements
        if (!activeTable.classList.contains('floating-table')) {
            // Make the element floating first
            activeTable.classList.add('floating-table');
            setTableFloating(activeTable);
        }
        
        // Get current z-index
        let currentZ = parseInt(activeTable.style.zIndex) || 50;
        
        // Increase z-index
        currentZ += 10;
        activeTable.style.zIndex = currentZ;
        
        // Notify that content changed
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
        
        return true;
    }
    
    // Function to change z-index of active element (send backward)
    function sendElementBackward() {
        if (!activeTable) return false;
        
        // Only apply to floating elements
        if (!activeTable.classList.contains('floating-table')) {
            // Make the element floating first
            activeTable.classList.add('floating-table');
            setTableFloating(activeTable);
        }
        
        // Get current z-index
        let currentZ = parseInt(activeTable.style.zIndex) || 50;
        
        // Decrease z-index but keep it above 0
        currentZ = Math.max(currentZ - 10, 10);
        activeTable.style.zIndex = currentZ;
        
        // Notify that content changed
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
        
        return true;
    }
"""

def table_theme_helpers_js(self):
    """JavaScript helper functions for theme detection and colors"""
    return """
    // Function to check if we're in dark mode
    function isDarkMode() {
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    
    // Function to get appropriate border color based on current theme
    function getBorderColor() {
        return isDarkMode() ? '#444' : '#ccc';
    }
    
    // Function to get appropriate header background color based on current theme
    function getHeaderBgColor() {
        return isDarkMode() ? '#2a2a2a' : '#f0f0f0';
    }
    """

def table_handles_css_js(self):
    """JavaScript that defines CSS for table handles with proper display properties"""
    return """
        // CSS for table handles
        const tableHandlesCSS = `
        /* Table drag handle - positioned inside the table */
        .table-drag-handle {
            position: absolute;
            top: 0;
            left: 0;
            width: 16px;
            height: 16px;
            background-color: #4e9eff;
            cursor: move;
            z-index: 1000;
            display: flex;  /* Changed from static display to allow proper show/hide */
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 10px;
            pointer-events: all;
            user-select: none;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
        }

        /* Table resize handle - triangular shape in bottom right */
        .table-handle {
            position: absolute;
            bottom: 0;
            right: 0;
            width: 0;
            height: 0;
            border-style: solid;
            border-width: 0 0 16px 16px;
            border-color: transparent transparent #4e9eff transparent;
            cursor: nwse-resize;
            z-index: 1000;
            pointer-events: all;
            user-select: none;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            display: block;  /* Added to allow proper show/hide */
        }
        
        /* Floating table styles */
        .floating-table {
            position: absolute !important;
            z-index: 50;
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
            background-color: rgba(255, 255, 255, 0.95);
            cursor: grab;
        }
        
        .floating-table:active {
            cursor: grabbing;
        }
        
        .floating-table .table-drag-handle {
            width: 20px !important;
            height: 20px !important;
            border-radius: 3px;
            opacity: 0.9;
        }

        @media (prefers-color-scheme: dark) {
            .table-drag-handle {
                background-color: #0078d7;
            }
            .table-handle {
                border-color: transparent transparent #0078d7 transparent;
            }
            .floating-table {
                background-color: rgba(45, 45, 45, 0.95);
                box-shadow: 0 3px 10px rgba(0,0,0,0.5);
            }
            .floating-table .table-drag-handle {
                background-color: #0078d7;
            }
        }`;
        
        // Function to add the table handle styles to the document
        function addTableHandleStyles() {
            // Check if our style element already exists
            let styleElement = document.getElementById('table-handle-styles');
            
            // If not, create and append it
            if (!styleElement) {
                styleElement = document.createElement('style');
                styleElement.id = 'table-handle-styles';
                styleElement.textContent = tableHandlesCSS;
                document.head.appendChild(styleElement);
            } else {
                // If it exists, update the content
                styleElement.textContent = tableHandlesCSS;
            }
        }
        """
        
def table_insert_functions_js(self):
    """JavaScript for inserting tables with default margins"""
    return """
    // Function to insert a table at the current cursor position
    function insertTable(rows, cols, hasHeader, borderWidth, tableWidth, isFloating) {
        // Get theme-appropriate colors
        const borderColor = getBorderColor();
        const headerBgColor = getHeaderBgColor();
        
        // Check if we're inserting inside another table cell
        const selection = window.getSelection();
        let isNestedTable = false;
        
        if (selection.rangeCount > 0) {
            let node = selection.anchorNode;
            while (node && node !== document.body) {
                if (node.tagName === 'TD' || node.tagName === 'TH') {
                    isNestedTable = true;
                    break;
                }
                node = node.parentNode;
            }
        }
        
        // Create table HTML
        let tableHTML = '<table cellspacing="0" cellpadding="5" ';
        
        // Add class and style attributes (including default margins)
        tableHTML += 'class="editor-table no-wrap" style="border-collapse: collapse; width: ' + tableWidth + '; margin: 6px 6px 0 0;">';
        
        // Create header row if requested
        if (hasHeader) {
            tableHTML += '<tr>';
            for (let j = 0; j < cols; j++) {
                tableHTML += '<th style="border: ' + borderWidth + 'px solid ' + borderColor + '; padding: 5px; background-color: ' + headerBgColor + ';"> </th>';
            }
            tableHTML += '</tr>';
            rows--; // Reduce regular rows by one since we added a header
        }
        
        // Create regular rows and cells
        for (let i = 0; i < rows; i++) {
            tableHTML += '<tr>';
            for (let j = 0; j < cols; j++) {
                tableHTML += '<td style="border: ' + borderWidth + 'px solid ' + borderColor + '; padding: 5px; min-width: 30px;"></td>';
            }
            tableHTML += '</tr>';
        }
        
        // Close the table tag
        tableHTML += '</table>';
        
        // Only add paragraph after table if it's not nested inside another table
        // Make sure to create a visible and properly sized paragraph element
        if (!isNestedTable) {
            tableHTML += '<p><br></p>';
        }
        
        // Insert the table at the current cursor position
        document.execCommand('insertHTML', false, tableHTML);
        
        // Activate the newly inserted table
        setTimeout(() => {
            const tables = document.querySelectorAll('table.editor-table');
            const newTable = tables[tables.length - 1] || document.querySelector('table:last-of-type');
            if (newTable) {
                // Ensure the editor-table class is present
                if (!newTable.classList.contains('editor-table')) {
                    newTable.classList.add('editor-table');
                }
                
                // Set default margins
                newTable.style.marginTop = '6px';
                newTable.style.marginRight = '6px';
                newTable.style.marginBottom = '0px';
                newTable.style.marginLeft = '0px';
                
                // Store margin values as attributes
                newTable.setAttribute('data-margin-top', '6');
                newTable.setAttribute('data-margin-right', '6');
                newTable.setAttribute('data-margin-bottom', '0');
                newTable.setAttribute('data-margin-left', '0');
                
                // Make table floating if requested
                if (isFloating) {
                    newTable.classList.add('floating-table');
                    setTableFloating(newTable);
                }
                
                activateTable(newTable);
                try {
                    window.webkit.messageHandlers.tableClicked.postMessage('table-clicked');
                } catch(e) {
                    console.log("Could not notify about table click:", e);
                }
                
                // Ensure the paragraph after the table is properly initialized
                if (!isNestedTable) {
                    const paraAfterTable = newTable.nextElementSibling;
                    if (paraAfterTable && paraAfterTable.tagName === 'P' && !paraAfterTable.innerHTML) {
                        paraAfterTable.innerHTML = '<br>';
                    }
                }
            }
        }, 10);
    }
    """

def table_activation_js(self):
    """JavaScript for table activation and deactivation"""
    return """
    // Variables for table handling
    var activeTable = null;
    var isDragging = false;
    var isResizing = false;
    var dragStartX = 0;
    var dragStartY = 0;
    var tableStartX = 0;
    var tableStartY = 0;
    
    // Function to find parent table element
    function findParentTable(element) {
        while (element && element !== document.body) {
            if (element.tagName === 'TABLE') {
                return element;
            }
            element = element.parentNode;
        }
        return null;
    }
    
    // Function to activate a table (add handles)
    function activateTable(tableElement) {
        if (activeTable === tableElement) return; // Already active
        
        // Deactivate any previously active tables
        if (activeTable && activeTable !== tableElement) {
            deactivateTable(activeTable);
        }
        
        activeTable = tableElement;
        
        // Store original styles and apply selection styling
        storeAndApplyTableStyles(tableElement);
        
        // Determine current table alignment class
        const currentClasses = tableElement.className;
        const alignmentClasses = ['left-align', 'right-align', 'center-align', 'no-wrap'];
        let currentAlignment = 'no-wrap';
        
        alignmentClasses.forEach(cls => {
            if (currentClasses.includes(cls)) {
                currentAlignment = cls;
            }
        });
        
        // Reset and apply the appropriate alignment class
        alignmentClasses.forEach(cls => tableElement.classList.remove(cls));
        tableElement.classList.add(currentAlignment);
        
        // Add resize handle if needed
        if (!tableElement.querySelector('.table-handle')) {
            const resizeHandle = document.createElement('div');
            resizeHandle.className = 'table-handle';
            
            // Make handle non-selectable and prevent focus
            resizeHandle.setAttribute('contenteditable', 'false');
            resizeHandle.setAttribute('unselectable', 'on');
            resizeHandle.setAttribute('tabindex', '-1');
            
            // Add event listener to prevent propagation of mousedown events
            resizeHandle.addEventListener('mousedown', function(e) {
                e.preventDefault();
                e.stopPropagation();
                startTableResize(e, tableElement);
            }, true);
            
            tableElement.appendChild(resizeHandle);
        }
        
        // Add drag handle if needed
        if (!tableElement.querySelector('.table-drag-handle')) {
            const dragHandle = document.createElement('div');
            dragHandle.className = 'table-drag-handle';
            dragHandle.innerHTML = '↕';
            
            // Set title based on whether it's a floating table or not
            if (tableElement.classList.contains('floating-table')) {
                dragHandle.title = 'Drag to move table freely';
            } else {
                dragHandle.title = 'Drag to reposition table between paragraphs';
            }
            
            // Make handle non-selectable and prevent focus
            dragHandle.setAttribute('contenteditable', 'false');
            dragHandle.setAttribute('unselectable', 'on');
            dragHandle.setAttribute('tabindex', '-1');
            
            // Add event listener to prevent propagation of mousedown events
            dragHandle.addEventListener('mousedown', function(e) {
                e.preventDefault();
                e.stopPropagation();
                startTableDrag(e, tableElement);
            }, true);
            
            tableElement.appendChild(dragHandle);
        }
        
        // Special styling for floating tables
        if (tableElement.classList.contains('floating-table')) {
            enhanceTableDragHandles(tableElement);
        }
    }
    
    // Store original table styles and apply selection styling
    function storeAndApplyTableStyles(tableElement) {
        // Add selected class for CSS styling
        tableElement.classList.add('table-selected');
        
        // Ensure table has editor-table class
        if (!tableElement.classList.contains('editor-table')) {
            tableElement.classList.add('editor-table');
        }
        
        // Ensure the table has position: relative for proper handle positioning
        // Only set relative position if not already a floating table
        if (!tableElement.classList.contains('floating-table')) {
            tableElement.style.position = 'relative';
        }
    }
    
    // Function to deactivate a specific table
    function deactivateTable(tableElement) {
        if (!tableElement) return;
        
        // Remove selected class
        tableElement.classList.remove('table-selected');
        
        // Remove handles
        const resizeHandle = tableElement.querySelector('.table-handle');
        if (resizeHandle) resizeHandle.remove();
        
        const dragHandle = tableElement.querySelector('.table-drag-handle');
        if (dragHandle) dragHandle.remove();
        
        if (tableElement === activeTable) {
            activeTable = null;
        }
    }
    
    // Function to deactivate all tables
    function deactivateAllTables() {
        const tables = document.querySelectorAll('table');
        
        tables.forEach(table => {
            deactivateTable(table);
        });
        
        // Always notify that tables are deactivated, regardless of whether activeTable was set
        activeTable = null;
        try {
            window.webkit.messageHandlers.tablesDeactivated.postMessage('tables-deactivated');
        } catch(e) {
            console.log("Could not notify about table deactivation:", e);
        }
    }
    
    // Function to update table colors based on current theme
    function updateTableThemeColors(tableElement) {
        if (!tableElement) return;
        
        const borderColor = getBorderColor();
        const headerBgColor = getHeaderBgColor();
        
        // Update all headers
        const headers = tableElement.querySelectorAll('th');
        headers.forEach(header => {
            header.style.backgroundColor = headerBgColor;
            header.style.borderColor = borderColor;
        });
        
        // Update all cells
        const cells = tableElement.querySelectorAll('td');
        cells.forEach(cell => {
            cell.style.borderColor = borderColor;
        });
    }
    """

def table_drag_resize_js(self):
    """JavaScript for table dragging and resizing"""
    return """
    // Function to start table drag
    function startTableDrag(e, tableElement) {
        e.preventDefault();
        if (!tableElement) return;
        
        isDragging = true;
        activeTable = tableElement;
        dragStartX = e.clientX;
        dragStartY = e.clientY;
        
        // Set cursor based on whether the table is floating or not
        if (tableElement.classList.contains('floating-table')) {
            document.body.style.cursor = 'grabbing';
        } else {
            document.body.style.cursor = 'move';
        }
    }
    
    // Function to move table
    function moveTable(e) {
        if (!isDragging || !activeTable) return;
        
        // Check if the table is a floating table
        if (activeTable.classList.contains('floating-table')) {
            // For floating tables, just move it to the mouse position with offset
            const deltaX = e.clientX - dragStartX;
            const deltaY = e.clientY - dragStartY;
            
            // Get current position from style
            const currentTop = parseInt(activeTable.style.top) || 0;
            const currentLeft = parseInt(activeTable.style.left) || 0;
            
            // Update position
            activeTable.style.top = `${currentTop + deltaY}px`;
            activeTable.style.left = `${currentLeft + deltaX}px`;
            
            // Update starting points for next movement
            dragStartX = e.clientX;
            dragStartY = e.clientY;
            
            try {
                window.webkit.messageHandlers.contentChanged.postMessage('changed');
            } catch(e) {
                console.log("Could not notify about content change:", e);
            }
        } else {
            const currentY = e.clientY;
            const deltaY = currentY - dragStartY;
            
            if (Math.abs(deltaY) > 30) {
                const editor = document.getElementById('editor');
                const blocks = Array.from(editor.children).filter(node => {
                    const style = window.getComputedStyle(node);
                    return style.display.includes('block') || node.tagName === 'TABLE';
                });
                
                const tableIndex = blocks.indexOf(activeTable);
                
                if (deltaY < 0 && tableIndex > 0) {
                    const targetElement = blocks[tableIndex - 1];
                    editor.insertBefore(activeTable, targetElement);
                    dragStartY = currentY;
                    try {
                        window.webkit.messageHandlers.contentChanged.postMessage('changed');
                    } catch(e) {
                        console.log("Could not notify about content change:", e);
                    }
                } 
                else if (deltaY > 0 && tableIndex < blocks.length - 1) {
                    const targetElement = blocks[tableIndex + 1];
                    if (targetElement.nextSibling) {
                        editor.insertBefore(activeTable, targetElement.nextSibling);
                    } else {
                        editor.appendChild(activeTable);
                    }
                    dragStartY = currentY;
                    try {
                        window.webkit.messageHandlers.contentChanged.postMessage('changed');
                    } catch(e) {
                        console.log("Could not notify about content change:", e);
                    }
                }
            }
        }
    }
    
    // Function to start table resize
    function startTableResize(e, tableElement) {
        e.preventDefault();
        isResizing = true;
        activeTable = tableElement;
        dragStartX = e.clientX;
        dragStartY = e.clientY;
        const style = window.getComputedStyle(tableElement);
        tableStartX = parseInt(style.width) || tableElement.offsetWidth;
        tableStartY = parseInt(style.height) || tableElement.offsetHeight;
    }
    
    // Function to resize table
    function resizeTable(e) {
        if (!isResizing || !activeTable) return;
        
        const deltaX = e.clientX - dragStartX;
        
        // Only adjust width, not height - this prevents the horizontal line artifact
        activeTable.style.width = (tableStartX + deltaX) + 'px';
    }
    """

def table_row_column_js(self):
    """JavaScript for table row and column operations"""
    return """
    // Function to add a row to the table
    function addTableRow(tableElement, position) {
        if (!tableElement && activeTable) {
            tableElement = activeTable;
        }
        
        if (!tableElement) return;
        
        const borderColor = getBorderColor();
        const rows = tableElement.rows;
        if (rows.length > 0) {
            // If position is provided, use it, otherwise append at the end
            const rowIndex = (position !== undefined) ? position : rows.length;
            const newRow = tableElement.insertRow(rowIndex);
            
            for (let i = 0; i < rows[0].cells.length; i++) {
                const cell = newRow.insertCell(i);
                cell.innerHTML = '&nbsp;';
                // Copy border style from other cells
                if (rows[0].cells[i].style.border) {
                    cell.style.border = rows[0].cells[i].style.border;
                } else {
                    cell.style.border = '1px solid ' + borderColor;
                }
                // Copy padding style from other cells
                if (rows[0].cells[i].style.padding) {
                    cell.style.padding = rows[0].cells[i].style.padding;
                } else {
                    cell.style.padding = '5px';
                }
            }
        }
        
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
    }
    
    // Function to add a column to the table
    function addTableColumn(tableElement, position) {
        if (!tableElement && activeTable) {
            tableElement = activeTable;
        }
        
        if (!tableElement) return;
        
        const borderColor = getBorderColor();
        const headerBgColor = getHeaderBgColor();
        const rows = tableElement.rows;
        for (let i = 0; i < rows.length; i++) {
            // If position is provided, use it, otherwise append at the end
            const cellIndex = (position !== undefined) ? position : rows[i].cells.length;
            const cell = rows[i].insertCell(cellIndex);
            cell.innerHTML = '&nbsp;';
            
            // Default styles based on theme
            let cellStyle = {
                border: '1px solid ' + borderColor,
                padding: '5px'
            };
            
            // Copy styles from adjacent cells if available
            if (rows[i].cells.length > 1) {
                const refCell = cellIndex > 0 ? 
                                rows[i].cells[cellIndex - 1] : 
                                rows[i].cells[cellIndex + 1];
                                
                if (refCell) {
                    if (refCell.style.border) {
                        cellStyle.border = refCell.style.border;
                    }
                    if (refCell.style.padding) {
                        cellStyle.padding = refCell.style.padding;
                    }
                    
                    // If it's a header cell, make new cell a header too
                    if (refCell.tagName === 'TH' && cell.tagName === 'TD') {
                        const headerCell = document.createElement('th');
                        headerCell.innerHTML = cell.innerHTML;
                        
                        // Apply all styles
                        Object.assign(headerCell.style, cellStyle);
                        headerCell.style.backgroundColor = headerBgColor;
                        
                        cell.parentNode.replaceChild(headerCell, cell);
                    } else {
                        // Apply styles to normal cell
                        Object.assign(cell.style, cellStyle);
                    }
                }
            } else {
                // Apply default styles if no reference cells
                Object.assign(cell.style, cellStyle);
                
                // If this is the first row, it might be a header
                if (i === 0 && rows[0].cells[0].tagName === 'TH') {
                    const headerCell = document.createElement('th');
                    headerCell.innerHTML = cell.innerHTML;
                    Object.assign(headerCell.style, cellStyle);
                    headerCell.style.backgroundColor = headerBgColor;
                    cell.parentNode.replaceChild(headerCell, cell);
                }
            }
        }
        
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
    }
    
    // Function to delete a row from the table
    function deleteTableRow(tableElement, rowIndex) {
        if (!tableElement && activeTable) {
            tableElement = activeTable;
        }
        
        if (!tableElement) return;
        
        const rows = tableElement.rows;
        if (rows.length > 1) {
            // If rowIndex is provided, delete that row, otherwise delete the last row
            const indexToDelete = (rowIndex !== undefined) ? rowIndex : rows.length - 1;
            if (indexToDelete >= 0 && indexToDelete < rows.length) {
                tableElement.deleteRow(indexToDelete);
            }
        }
        
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
    }
    
    // Function to delete a column from the table
    function deleteTableColumn(tableElement, colIndex) {
        if (!tableElement && activeTable) {
            tableElement = activeTable;
        }
        
        if (!tableElement) return;
        
        const rows = tableElement.rows;
        if (rows.length > 0 && rows[0].cells.length > 1) {
            // If colIndex is provided, delete that column, otherwise delete the last column
            const indexToDelete = (colIndex !== undefined) ? colIndex : rows[0].cells.length - 1;
            
            for (let i = 0; i < rows.length; i++) {
                if (indexToDelete >= 0 && indexToDelete < rows[i].cells.length) {
                    rows[i].deleteCell(indexToDelete);
                }
            }
        }
        
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
    }
    
    // Function to delete a table
    function deleteTable(tableElement) {
        if (!tableElement && activeTable) {
            tableElement = activeTable;
        }
        
        if (!tableElement) return;
        
        // Remove the table from the DOM
        tableElement.parentNode.removeChild(tableElement);
        
        // Reset activeTable reference
        activeTable = null;
        
        // Notify the app
        try {
            window.webkit.messageHandlers.tableDeleted.postMessage('table-deleted');
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about table deletion:", e);
        }
    }
    """

def table_alignment_js(self):
    """JavaScript for table alignment"""
    return """
    // Function to set table alignment
    function setTableAlignment(alignClass) {
        if (!activeTable) return;
        
        // Remove all alignment classes
        activeTable.classList.remove('left-align', 'right-align', 'center-align', 'no-wrap', 'floating-table');
        
        // Add the requested alignment class
        activeTable.classList.add(alignClass);
        
        // Reset positioning if it was previously floating
        if (activeTable.style.position === 'absolute') {
            activeTable.style.position = 'relative';
            activeTable.style.top = '';
            activeTable.style.left = '';
            activeTable.style.zIndex = '';
        }
        
        // Set width to auto except for full-width
        if (alignClass === 'no-wrap') {
            activeTable.style.width = '100%';
        } else {
            activeTable.style.width = 'auto';
        }
        
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
    }
    """
    
def table_floating_js(self):
    """JavaScript for floating table functionality"""
    return """
    // Function to make a table floating (freely positionable)
    function setTableFloating(tableElement) {
        if (!tableElement && activeTable) {
            tableElement = activeTable;
        }
        
        if (!tableElement) return;
        
        // First, remove any alignment classes
        tableElement.classList.remove('left-align', 'right-align', 'center-align', 'no-wrap');
        
        // Add floating class for special styling
        tableElement.classList.add('floating-table');
        
        // Set positioning to absolute
        tableElement.style.position = 'absolute';
        
        // Calculate initial position - center in the visible editor area
        const editorRect = document.getElementById('editor').getBoundingClientRect();
        const tableRect = tableElement.getBoundingClientRect();
        
        // Set initial position
        const editorScrollTop = document.getElementById('editor').scrollTop;
        
        // Position in the middle of the visible editor area
        const topPos = (editorRect.height / 2) - (tableRect.height / 2) + editorScrollTop;
        const leftPos = (editorRect.width / 2) - (tableRect.width / 2);
        
        tableElement.style.top = `${Math.max(topPos, editorScrollTop)}px`;
        tableElement.style.left = `${Math.max(leftPos, 0)}px`;
        
        // Enhance the drag handle for position control
        enhanceTableDragHandles(tableElement);
        
        // Ensure proper z-index to be above regular content
        tableElement.style.zIndex = "50";
        
        // Notify that content changed
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
        
        // Activate the table to show handles
        if (tableElement !== activeTable) {
            activateTable(tableElement);
        }
    }
    
    // Add enhanced drag handling for floating tables
    function enhanceTableDragHandles(tableElement) {
        if (!tableElement) return;
        
        // Find or create the drag handle
        let dragHandle = tableElement.querySelector('.table-drag-handle');
        if (!dragHandle) {
            // If it doesn't exist, we might need to activate the table first
            activateTable(tableElement);
            dragHandle = tableElement.querySelector('.table-drag-handle');
        }
        
        if (dragHandle) {
            // Update tooltip to reflect new functionality
            dragHandle.title = "Drag to move table freely";
            
            // Make the drag handle more visible for floating tables
            dragHandle.style.width = "20px";
            dragHandle.style.height = "20px";
            dragHandle.style.backgroundColor = "#4e9eff";
            dragHandle.style.borderRadius = "3px";
            dragHandle.style.opacity = "0.9";
        }
    }
    """

def table_event_handlers_js(self):
    """JavaScript for table event handlers with handle hiding during editing and tab navigation"""
    return """
    // Function to save editor state
    function saveState() {
        const editor = document.getElementById('editor');
        if (!editor) return;
        
        window.undoStack.push(editor.innerHTML);
        if (window.undoStack.length > 100) {
            window.undoStack.shift();
        }
    }
    
    // Function to handle dark mode changes
    function handleColorSchemeChange(e) {
        const tables = document.querySelectorAll('table');
        tables.forEach(updateTableThemeColors);
    }
    
    // Function to hide table handles
    function hideTableHandles() {
        if (activeTable) {
            const dragHandle = activeTable.querySelector('.table-drag-handle');
            const resizeHandle = activeTable.querySelector('.table-handle');
            
            if (dragHandle) dragHandle.style.display = 'none';
            if (resizeHandle) resizeHandle.style.display = 'none';
        }
    }
    
    // Function to show table handles
    function showTableHandles() {
        if (activeTable) {
            const dragHandle = activeTable.querySelector('.table-drag-handle');
            const resizeHandle = activeTable.querySelector('.table-handle');
            
            if (dragHandle) dragHandle.style.display = 'flex';
            if (resizeHandle) resizeHandle.style.display = 'block';
        }
    }
    
    // Check if element is a table cell
    function isTableCell(element) {
        return element && (element.tagName === 'TD' || element.tagName === 'TH');
    }
    
    // Find parent cell element
    function findParentCell(element) {
        while (element && element !== document.body) {
            if (element.tagName === 'TD' || element.tagName === 'TH') {
                return element;
            }
            element = element.parentNode;
        }
        return null;
    }
    
    // Add event handlers for table interactions
    document.addEventListener('DOMContentLoaded', function() {
        const editor = document.getElementById('editor');
        
        // Add the custom style for table handles
        addTableHandleStyles();
        
        // Handle mouse down events
        editor.addEventListener('mousedown', function(e) {
            // Prevent selection of table handles
            if (e.target.classList.contains('table-handle') || 
                e.target.classList.contains('table-drag-handle')) {
                e.preventDefault();
                e.stopPropagation();
                return;
            }
            
            let tableElement = findParentTable(e.target);
            
            if (e.target.classList.contains('table-drag-handle')) {
                if (e.button === 0) { // Left mouse button
                    startTableDrag(e, findParentTable(e.target));
                }
            }
            
            if (e.target.classList.contains('table-handle')) {
                startTableResize(e, findParentTable(e.target));
            }
        });
        
        // Handle focus events on cells to hide handles when editing
        editor.addEventListener('focusin', function(e) {
            const cell = findParentCell(e.target);
            if (cell && activeTable && activeTable.contains(cell)) {
                hideTableHandles();
            }
        });
        
        // Handle when user starts typing in a cell
        editor.addEventListener('keydown', function(e) {
            const cell = findParentCell(e.target);
            if (cell && activeTable && activeTable.contains(cell)) {
                // Hide handles when typing in cells (except for navigation keys and Tab)
                if (!['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Tab', 'Escape', 'Shift'].includes(e.key)) {
                    hideTableHandles();
                }
            }
        });
        
        // Handle mouse move events
        document.addEventListener('mousemove', function(e) {
            if (isDragging && activeTable) {
                moveTable(e);
            }
            if (isResizing && activeTable) {
                resizeTable(e);
            }
        });
        
        // Handle mouse up events
        document.addEventListener('mouseup', function() {
            if (isDragging || isResizing) {
                isDragging = false;
                isResizing = false;
                document.body.style.cursor = '';
                
                if (activeTable) {
                    try {
                        window.webkit.messageHandlers.contentChanged.postMessage('changed');
                    } catch(e) {
                        console.log("Could not notify about content change:", e);
                    }
                }
            }
        });
        
        // Handle click events for table selection
        editor.addEventListener('click', function(e) {
            let tableElement = findParentTable(e.target);
            
            if (!tableElement) {
                // We clicked outside any table
                if (activeTable) {
                    // If there was a previously active table, deactivate it
                    deactivateAllTables();
                } else {
                    // Even if there was no active table, still send the deactivation message
                    try {
                        window.webkit.messageHandlers.tablesDeactivated.postMessage('tables-deactivated');
                    } catch(e) {
                        console.log("Could not notify about table deactivation:", e);
                    }
                }
            } else if (tableElement !== activeTable) {
                // We clicked on a different table than the currently active one
                deactivateAllTables();
                activateTable(tableElement);
                
                // Show handles unless we clicked inside a cell for editing
                const cell = findParentCell(e.target);
                if (!cell || !isTableCell(e.target)) {
                    showTableHandles();
                }
                
                try {
                    window.webkit.messageHandlers.tableClicked.postMessage('table-clicked');
                } catch(e) {
                    console.log("Could not notify about table click:", e);
                }
            } else {
                // Clicking on the same table
                const cell = findParentCell(e.target);
                if (cell) {
                    // If clicking on a cell, hide handles for editing
                    hideTableHandles();
                } else if (!e.target.classList.contains('table-handle') && 
                          !e.target.classList.contains('table-drag-handle')) {
                    // If clicking elsewhere on the table (not handles), show handles
                    showTableHandles();
                }
            }
        });
        
        // Add a focusout handler to show handles again when leaving a cell
        editor.addEventListener('focusout', function(e) {
            if (activeTable) {
                // Check if the focus is moving outside the table
                setTimeout(() => {
                    const newFocusElement = document.activeElement;
                    if (!activeTable.contains(newFocusElement)) {
                        showTableHandles();
                    } else {
                        // If focus moved to another cell in the same table, keep handles hidden
                        const newCell = findParentCell(newFocusElement);
                        if (!newCell) {
                            showTableHandles();
                        }
                    }
                }, 0);
            }
        });

        // Add a document-level click handler that will deactivate tables when clicking outside the editor
        document.addEventListener('click', function(e) {
            // Check if the click is outside the editor
            if (!editor.contains(e.target) && activeTable) {
                deactivateAllTables();
            }
        });

        // Listen for color scheme changes
        if (window.matchMedia) {
            const colorSchemeQuery = window.matchMedia('(prefers-color-scheme: dark)');
            // Modern approach (newer browsers)
            if (colorSchemeQuery.addEventListener) {
                colorSchemeQuery.addEventListener('change', handleColorSchemeChange);
            } 
            // Legacy approach (older browsers)
            else if (colorSchemeQuery.addListener) {
                colorSchemeQuery.addListener(handleColorSchemeChange);
            }
        }
    });
    """    
    
def table_color_js(self):
    """JavaScript for table color operations with theme preservation"""
    return """
    // Function to set table background color
    function setTableBackgroundColor(color) {
        if (!activeTable) return false;
        
        activeTable.style.backgroundColor = color;
        
        // Store the background color
        activeTable.setAttribute('data-bg-color', color);
        
        // Notify that content changed
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
        
        return true;
    }
    
    // Function to set header background color
    function setHeaderBackgroundColor(color) {
        if (!activeTable) return false;
        
        const headers = activeTable.querySelectorAll('th');
        headers.forEach(header => {
            header.style.backgroundColor = color;
        });
        
        // Store the header color
        activeTable.setAttribute('data-header-color', color);
        
        // Notify that content changed
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
        
        return true;
    }
    
    // Function to set cell background color (only for the active cell)
    function setCellBackgroundColor(color) {
        if (!activeTable) return false;
        
        // Get the current selection
        const selection = window.getSelection();
        if (!selection.rangeCount) return false;
        
        // Find the active cell
        let activeCell = selection.anchorNode;
        
        // If the selection is in a text node, get the parent element
        if (activeCell.nodeType === Node.TEXT_NODE) {
            activeCell = activeCell.parentElement;
        }
        
        // Find the closest td or th element
        while (activeCell && activeCell.tagName !== 'TD' && activeCell.tagName !== 'TH') {
            activeCell = activeCell.parentElement;
        }
        
        // If we found a cell and it belongs to our active table
        if (activeCell && activeTable.contains(activeCell)) {
            activeCell.style.backgroundColor = color;
            
            // Store the color on the cell itself
            activeCell.setAttribute('data-cell-color', color);
            
            // Notify that content changed
            try {
                window.webkit.messageHandlers.contentChanged.postMessage('changed');
            } catch(e) {
                console.log("Could not notify about content change:", e);
            }
            
            return true;
        }
        
        return false;
    }
    
    // Function to set row background color
    function setRowBackgroundColor(color) {
        if (!activeTable) return false;
        
        // Get the current selection
        const selection = window.getSelection();
        if (!selection.rangeCount) return false;
        
        // Find the active cell
        let activeCell = selection.anchorNode;
        
        // If the selection is in a text node, get the parent element
        if (activeCell.nodeType === Node.TEXT_NODE) {
            activeCell = activeCell.parentElement;
        }
        
        // Find the closest td or th element
        while (activeCell && activeCell.tagName !== 'TD' && activeCell.tagName !== 'TH') {
            activeCell = activeCell.parentElement;
        }
        
        // If we found a cell and it belongs to our active table
        if (activeCell && activeTable.contains(activeCell)) {
            // Find the parent row
            const row = activeCell.parentElement;
            if (row && row.tagName === 'TR') {
                // Apply color to all cells in the row
                const cells = row.querySelectorAll('td, th');
                cells.forEach(cell => {
                    cell.style.backgroundColor = color;
                    cell.setAttribute('data-cell-color', color);
                });
                
                // Store the row color
                row.setAttribute('data-row-color', color);
                
                // Notify that content changed
                try {
                    window.webkit.messageHandlers.contentChanged.postMessage('changed');
                } catch(e) {
                    console.log("Could not notify about content change:", e);
                }
                
                return true;
            }
        }
        
        return false;
    }
    
    // Function to set column background color
    function setColumnBackgroundColor(color) {
        if (!activeTable) return false;
        
        // Get the current selection
        const selection = window.getSelection();
        if (!selection.rangeCount) return false;
        
        // Find the active cell
        let activeCell = selection.anchorNode;
        
        // If the selection is in a text node, get the parent element
        if (activeCell.nodeType === Node.TEXT_NODE) {
            activeCell = activeCell.parentElement;
        }
        
        // Find the closest td or th element
        while (activeCell && activeCell.tagName !== 'TD' && activeCell.tagName !== 'TH') {
            activeCell = activeCell.parentElement;
        }
        
        // If we found a cell and it belongs to our active table
        if (activeCell && activeTable.contains(activeCell)) {
            // Get the column index
            const cellIndex = activeCell.cellIndex;
            
            // Apply color to all cells in the same column
            const rows = activeTable.rows;
            for (let i = 0; i < rows.length; i++) {
                const cell = rows[i].cells[cellIndex];
                if (cell) {
                    cell.style.backgroundColor = color;
                    cell.setAttribute('data-cell-color', color);
                }
            }
            
            // Store the column color
            activeTable.setAttribute(`data-col-${cellIndex}-color`, color);
            
            // Notify that content changed
            try {
                window.webkit.messageHandlers.contentChanged.postMessage('changed');
            } catch(e) {
                console.log("Could not notify about content change:", e);
            }
            
            return true;
        }
        
        return false;
    }
    
    // Function to get current table colors
    function getTableColors() {
        if (!activeTable) return null;
        
        // Get stored values
        const bgColor = activeTable.getAttribute('data-bg-color') || activeTable.style.backgroundColor || '';
        const headerColor = activeTable.getAttribute('data-header-color') || '';
        const borderColor = activeTable.getAttribute('data-border-color') || '';
        
        // Get active cell color if there's a selection
        let cellColor = '';
        const selection = window.getSelection();
        if (selection.rangeCount) {
            let activeCell = selection.anchorNode;
            if (activeCell.nodeType === Node.TEXT_NODE) {
                activeCell = activeCell.parentElement;
            }
            while (activeCell && activeCell.tagName !== 'TD' && activeCell.tagName !== 'TH') {
                activeCell = activeCell.parentElement;
            }
            if (activeCell && activeTable.contains(activeCell)) {
                cellColor = activeCell.getAttribute('data-cell-color') || activeCell.style.backgroundColor || '';
            }
        }
        
        return {
            background: bgColor,
            header: headerColor,
            cell: cellColor,
            border: borderColor
        };
    }
    
    // Function to preserve table colors during theme changes
    function preserveTableColors() {
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            // Preserve background color
            const bgColor = table.getAttribute('data-bg-color');
            if (bgColor) {
                table.style.backgroundColor = bgColor;
            }
            
            // Preserve header colors
            const headerColor = table.getAttribute('data-header-color');
            const headers = table.querySelectorAll('th');
            headers.forEach(header => {
                if (headerColor) {
                    header.style.backgroundColor = headerColor;
                } else if (!header.getAttribute('data-cell-color')) {
                    // Set default header color based on theme
                    header.style.backgroundColor = getHeaderBgColor();
                }
            });
            
            // Preserve cell colors
            const cells = table.querySelectorAll('td, th');
            cells.forEach(cell => {
                const cellColor = cell.getAttribute('data-cell-color');
                if (cellColor) {
                    cell.style.backgroundColor = cellColor;
                }
            });
            
            // Preserve border colors
            const borderColor = table.getAttribute('data-border-color');
            if (borderColor) {
                cells.forEach(cell => {
                    cell.style.borderColor = borderColor;
                });
            }
        });
    }
    """
    
def table_border_style_js(self):
    """JavaScript for table border style manipulation with combined borders"""
    return """
    // Function to set table border style
    function setTableBorderStyle(style, width, color) {
        if (!activeTable) return false;
        
        // Get all cells in the table
        const cells = activeTable.querySelectorAll('th, td');
        
        // Get current values from table attributes
        let currentStyle = activeTable.getAttribute('data-border-style');
        let currentWidth = activeTable.getAttribute('data-border-width');
        let currentColor = activeTable.getAttribute('data-border-color');
        
        // If attributes don't exist, try to get from the first cell
        if (!currentStyle || !currentWidth || !currentColor) {
            if (cells.length > 0) {
                const firstCell = cells[0];
                const computedStyle = window.getComputedStyle(firstCell);
                
                // Try to get current style from computed style
                currentStyle = currentStyle || firstCell.style.borderStyle || computedStyle.borderStyle || 'solid';
                
                // Get current width
                if (!currentWidth) {
                    currentWidth = parseInt(firstCell.style.borderWidth) || 
                                  parseInt(computedStyle.borderWidth) || 1;
                }
                
                // Get current color
                currentColor = currentColor || firstCell.style.borderColor || 
                              computedStyle.borderColor || getBorderColor();
            } else {
                // Default values if no cells exist
                currentStyle = currentStyle || 'solid';
                currentWidth = currentWidth || 1;
                currentColor = currentColor || getBorderColor();
            }
        }
        
        // Use provided values or fall back to current/default values
        const newStyle = (style !== null && style !== undefined && style !== '') ? style : currentStyle;
        const newWidth = (width !== null && width !== undefined && width !== '') ? width : currentWidth;
        const newColor = (color !== null && color !== undefined && color !== '') ? color : currentColor;
        
        // Update all cells while preserving which borders are visible
        cells.forEach(cell => {
            // Check which borders are currently visible
            const hasTopBorder = cell.style.borderTopStyle !== 'none' && cell.style.borderTopWidth !== '0px';
            const hasRightBorder = cell.style.borderRightStyle !== 'none' && cell.style.borderRightWidth !== '0px';
            const hasBottomBorder = cell.style.borderBottomStyle !== 'none' && cell.style.borderBottomWidth !== '0px';
            const hasLeftBorder = cell.style.borderLeftStyle !== 'none' && cell.style.borderLeftWidth !== '0px';
            
            // Apply new properties only to existing borders
            if (hasTopBorder || cell.style.borderTopStyle) {
                cell.style.borderTopStyle = newStyle;
                cell.style.borderTopWidth = newWidth + 'px';
                cell.style.borderTopColor = newColor;
            }
            
            if (hasRightBorder || cell.style.borderRightStyle) {
                cell.style.borderRightStyle = newStyle;
                cell.style.borderRightWidth = newWidth + 'px';
                cell.style.borderRightColor = newColor;
            }
            
            if (hasBottomBorder || cell.style.borderBottomStyle) {
                cell.style.borderBottomStyle = newStyle;
                cell.style.borderBottomWidth = newWidth + 'px';
                cell.style.borderBottomColor = newColor;
            }
            
            if (hasLeftBorder || cell.style.borderLeftStyle) {
                cell.style.borderLeftStyle = newStyle;
                cell.style.borderLeftWidth = newWidth + 'px';
                cell.style.borderLeftColor = newColor;
            }
            
            // If cell has a generic border property, update it too
            if (cell.style.border || cell.getAttribute('style')?.includes('border:')) {
                // Check if the cell has any borders at all
                if (hasTopBorder || hasRightBorder || hasBottomBorder || hasLeftBorder) {
                    // Keep the border but update its properties
                    cell.style.borderStyle = newStyle;
                    cell.style.borderWidth = newWidth + 'px';
                    cell.style.borderColor = newColor;
                }
            }
        });
        
        // Store the current border settings on the table
        activeTable.setAttribute('data-border-style', newStyle);
        activeTable.setAttribute('data-border-width', newWidth);
        activeTable.setAttribute('data-border-color', newColor);
        
        // Also update the table's own border if it has one
        if (activeTable.style.border) {
            activeTable.style.borderStyle = newStyle;
            activeTable.style.borderWidth = newWidth + 'px';
            activeTable.style.borderColor = newColor;
        }
        
        // Notify that content changed
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
        
        return true;
    }
    
    // Function to set table border color
    function setTableBorderColor(color) {
        return setTableBorderStyle(null, null, color);
    }
    
    // Function to set table border width
    function setTableBorderWidth(width) {
        return setTableBorderStyle(null, width, null);
    }
    
    // Function to get current table border style
    function getTableBorderStyle() {
        if (!activeTable) return null;
        
        // First try to get from stored data attributes
        const storedStyle = activeTable.getAttribute('data-border-style');
        const storedWidth = activeTable.getAttribute('data-border-width');
        const storedColor = activeTable.getAttribute('data-border-color');
        
        if (storedStyle && storedWidth && storedColor) {
            return {
                style: storedStyle,
                width: parseInt(storedWidth),
                color: storedColor
            };
        }
        
        // If not stored, get from the first cell
        const firstCell = activeTable.querySelector('td, th');
        if (!firstCell) return {
            style: 'solid',
            width: 1,
            color: getBorderColor()
        };
        
        // Get computed style to ensure we get actual values
        const computedStyle = window.getComputedStyle(firstCell);
        
        const result = {
            style: firstCell.style.borderStyle || computedStyle.borderStyle || 'solid',
            width: parseInt(firstCell.style.borderWidth) || parseInt(computedStyle.borderWidth) || 1,
            color: firstCell.style.borderColor || computedStyle.borderColor || getBorderColor()
        };
        
        // Store these values for future use
        activeTable.setAttribute('data-border-style', result.style);
        activeTable.setAttribute('data-border-width', result.width);
        activeTable.setAttribute('data-border-color', result.color);
        
        return result;
    }
    
    // Function to get current table border properties (including shadow)
    function getTableBorderProperties() {
        if (!activeTable) return null;
        
        const borderStyle = getTableBorderStyle();
        const hasShadow = activeTable.getAttribute('data-border-shadow') === 'true' || 
                         (window.getComputedStyle(activeTable).boxShadow !== 'none' && 
                          window.getComputedStyle(activeTable).boxShadow !== '');
        
        return {
            ...borderStyle,
            shadow: hasShadow
        };
    }
    
    // Function to set table margins
    function setTableMargins(top, right, bottom, left) {
        if (!activeTable) return false;
        
        // Set margins individually if provided
        if (top !== undefined && top !== null) {
            activeTable.style.marginTop = top + 'px';
        }
        if (right !== undefined && right !== null) {
            activeTable.style.marginRight = right + 'px';
        }
        if (bottom !== undefined && bottom !== null) {
            activeTable.style.marginBottom = bottom + 'px';
        }
        if (left !== undefined && left !== null) {
            activeTable.style.marginLeft = left + 'px';
        }
        
        // Store margin values as attributes for later reference
        activeTable.setAttribute('data-margin-top', parseInt(activeTable.style.marginTop) || 0);
        activeTable.setAttribute('data-margin-right', parseInt(activeTable.style.marginRight) || 0);
        activeTable.setAttribute('data-margin-bottom', parseInt(activeTable.style.marginBottom) || 0);
        activeTable.setAttribute('data-margin-left', parseInt(activeTable.style.marginLeft) || 0);
        
        // Notify that content changed
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
        
        return true;
    }
    
    // Function to get current table margins
    function getTableMargins() {
        if (!activeTable) return null;
        
        // Try to get from stored attributes first
        const storedTop = activeTable.getAttribute('data-margin-top');
        const storedRight = activeTable.getAttribute('data-margin-right');
        const storedBottom = activeTable.getAttribute('data-margin-bottom');
        const storedLeft = activeTable.getAttribute('data-margin-left');
        
        if (storedTop !== null || storedRight !== null || storedBottom !== null || storedLeft !== null) {
            return {
                top: parseInt(storedTop) || 0,
                right: parseInt(storedRight) || 0,
                bottom: parseInt(storedBottom) || 0,
                left: parseInt(storedLeft) || 0
            };
        }
        
        // Otherwise get from computed style
        const computedStyle = window.getComputedStyle(activeTable);
        
        return {
            top: parseInt(computedStyle.marginTop) || 0,
            right: parseInt(computedStyle.marginRight) || 0,
            bottom: parseInt(computedStyle.marginBottom) || 0,
            left: parseInt(computedStyle.marginLeft) || 0
        };
    }
    
    // Enhanced function to apply border to specific sides of the table
    // Now supports combined options like 'outer' + 'horizontal'
    function applyTableBorderSides(sides) {
        if (!activeTable) return false;
        
        const cells = activeTable.querySelectorAll('td, th');
        const currentStyle = getTableBorderStyle();
        
        if (!currentStyle) return false;
        
        // Create the border string with preserved style, width and color
        const borderValue = `${currentStyle.width}px ${currentStyle.style} ${currentStyle.color}`;
        
        // Check for special combined cases
        const hasOuter = sides.includes('outer');
        const hasInner = sides.includes('inner');
        const hasHorizontal = sides.includes('horizontal');
        const hasVertical = sides.includes('vertical');
        
        // Apply borders based on selected sides
        cells.forEach(cell => {
            // Get row and column position
            const row = cell.parentElement;
            const rowIndex = row.rowIndex;
            const cellIndex = cell.cellIndex;
            const isFirstRow = rowIndex === 0;
            const isLastRow = rowIndex === activeTable.rows.length - 1;
            const isFirstColumn = cellIndex === 0;
            const isLastColumn = cellIndex === row.cells.length - 1;
            
            // Reset all borders first
            cell.style.borderTop = 'none';
            cell.style.borderRight = 'none';
            cell.style.borderBottom = 'none';
            cell.style.borderLeft = 'none';
            
            // Apply borders based on sides parameter and cell position
            if (sides.includes('all')) {
                cell.style.border = borderValue;
            } else if (sides.includes('none')) {
                cell.style.border = 'none';
            } else {
                // Outer + Inner Horizontal: Apply outer borders on all 4 sides PLUS inner horizontal borders
                if (hasOuter && hasInner && hasHorizontal && !hasVertical) {
                    // Apply outer borders (all 4 sides)
                    if (isFirstRow) cell.style.borderTop = borderValue;
                    if (isLastRow) cell.style.borderBottom = borderValue;
                    if (isFirstColumn) cell.style.borderLeft = borderValue;
                    if (isLastColumn) cell.style.borderRight = borderValue;
                    
                    // Plus inner horizontal borders
                    if (!isLastRow) cell.style.borderBottom = borderValue;
                }
                // Outer + Inner Vertical: Apply outer borders on all 4 sides PLUS inner vertical borders
                else if (hasOuter && hasInner && hasVertical && !hasHorizontal) {
                    // Apply outer borders (all 4 sides)
                    if (isFirstRow) cell.style.borderTop = borderValue;
                    if (isLastRow) cell.style.borderBottom = borderValue;
                    if (isFirstColumn) cell.style.borderLeft = borderValue;
                    if (isLastColumn) cell.style.borderRight = borderValue;
                    
                    // Plus inner vertical borders
                    if (!isLastColumn) cell.style.borderRight = borderValue;
                }
                // Handle outer borders
                else if (hasOuter) {
                    if (isFirstRow) cell.style.borderTop = borderValue;
                    if (isLastRow) cell.style.borderBottom = borderValue;
                    if (isFirstColumn) cell.style.borderLeft = borderValue;
                    if (isLastColumn) cell.style.borderRight = borderValue;
                    
                    // If outer + horizontal, add only top and bottom outer borders
                    if (hasHorizontal && !hasVertical) {
                        if (isFirstRow) cell.style.borderTop = borderValue;
                        if (isLastRow) cell.style.borderBottom = borderValue;
                        cell.style.borderLeft = 'none';
                        cell.style.borderRight = 'none';
                    }
                    
                    // If outer + vertical, add only left and right outer borders
                    if (hasVertical && !hasHorizontal) {
                        cell.style.borderTop = 'none';
                        cell.style.borderBottom = 'none';
                        if (isFirstColumn) cell.style.borderLeft = borderValue;
                        if (isLastColumn) cell.style.borderRight = borderValue;
                    }
                }
                
                // Handle inner borders
                else if (hasInner) {
                    if (!isLastRow) cell.style.borderBottom = borderValue;
                    if (!isLastColumn) cell.style.borderRight = borderValue;
                    
                    // If inner + horizontal, add only horizontal inner borders
                    if (hasHorizontal && !hasVertical) {
                        if (!isLastRow) cell.style.borderBottom = borderValue;
                        cell.style.borderRight = 'none';
                    }
                    
                    // If inner + vertical, add only vertical inner borders
                    if (hasVertical && !hasHorizontal) {
                        cell.style.borderBottom = 'none';
                        if (!isLastColumn) cell.style.borderRight = borderValue;
                    }
                }
                
                // Handle standalone horizontal/vertical if not combined with outer/inner
                else {
                    if (hasHorizontal) {
                        cell.style.borderTop = borderValue;
                        cell.style.borderBottom = borderValue;
                    }
                    
                    if (hasVertical) {
                        cell.style.borderLeft = borderValue;
                        cell.style.borderRight = borderValue;
                    }
                }
            }
        });
        
        // Notify that content changed
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
        
        return true;
    }
    """

def create_table_toolbar(self, win):
    """Create a toolbar for table editing"""
    toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    toolbar.set_margin_start(10)
    toolbar.set_margin_end(10)
    toolbar.set_margin_top(5)
    toolbar.set_margin_bottom(5)
    
    # Table operations label
    table_label = Gtk.Label(label="Table:")
    table_label.set_margin_end(10)
    toolbar.append(table_label)
    
    # Create a group for row operations
    row_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
    row_group.add_css_class("linked")
    
    # Add Row Above button
    add_row_above_button = Gtk.Button(icon_name="list-add-symbolic")
    add_row_above_button.set_tooltip_text("Add row above")
    add_row_above_button.connect("clicked", lambda btn: self.on_add_row_above_clicked(win))
    row_group.append(add_row_above_button)
    
    # Add Row Below button
    add_row_below_button = Gtk.Button(icon_name="list-add-symbolic")
    add_row_below_button.set_tooltip_text("Add row below")
    add_row_below_button.connect("clicked", lambda btn: self.on_add_row_below_clicked(win))
    row_group.append(add_row_below_button)
    
    # Add row group to toolbar
    toolbar.append(row_group)
    
    # Create a group for column operations
    col_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
    col_group.add_css_class("linked")
    col_group.set_margin_start(5)
    
    # Add Column Before button
    add_col_before_button = Gtk.Button(icon_name="list-add-symbolic")
    add_col_before_button.set_tooltip_text("Add column before")
    add_col_before_button.connect("clicked", lambda btn: self.on_add_column_before_clicked(win))
    col_group.append(add_col_before_button)
    
    # Add Column After button
    add_col_after_button = Gtk.Button(icon_name="list-add-symbolic")
    add_col_after_button.set_tooltip_text("Add column after")
    add_col_after_button.connect("clicked", lambda btn: self.on_add_column_after_clicked(win))
    col_group.append(add_col_after_button)
    
    # Add column group to toolbar
    toolbar.append(col_group)
    
    # Small separator
    separator1 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
    separator1.set_margin_start(5)
    separator1.set_margin_end(5)
    toolbar.append(separator1)
    
    # Create a group for delete operations
    delete_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
    delete_group.add_css_class("linked")
    
    # Delete Row button
    del_row_button = Gtk.Button(icon_name="list-remove-symbolic")
    del_row_button.set_tooltip_text("Delete row")
    del_row_button.connect("clicked", lambda btn: self.on_delete_row_clicked(win))
    delete_group.append(del_row_button)
    
    # Delete Column button
    del_col_button = Gtk.Button(icon_name="list-remove-symbolic")
    del_col_button.set_tooltip_text("Delete column")
    del_col_button.connect("clicked", lambda btn: self.on_delete_column_clicked(win))
    delete_group.append(del_col_button)
    
    # Delete Table button
    del_table_button = Gtk.Button(icon_name="edit-delete-symbolic")
    del_table_button.set_tooltip_text("Delete table")
    del_table_button.connect("clicked", lambda btn: self.on_delete_table_clicked(win))
    delete_group.append(del_table_button)
    
    # Add delete group to toolbar
    toolbar.append(delete_group)
    
    # Separator
    separator2 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
    separator2.set_margin_start(10)
    separator2.set_margin_end(10)
    toolbar.append(separator2)
    
    # Table properties button (combines border, margin, and color)
    table_props_button = Gtk.Button(icon_name="document-properties-symbolic")
    table_props_button.set_tooltip_text("Table Properties")
    table_props_button.connect("clicked", lambda btn: self.on_table_button_clicked(win, btn))
    toolbar.append(table_props_button)
    
    # Separator
    separator3 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
    separator3.set_margin_start(10)
    separator3.set_margin_end(10)
    toolbar.append(separator3)
    
    # Alignment options
    align_label = Gtk.Label(label="Align:")
    align_label.set_margin_end(5)
    toolbar.append(align_label)
    
    # Create a group for alignment buttons
    align_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
    align_group.add_css_class("linked")
    
    # Left alignment
    align_left_button = Gtk.Button(icon_name="format-justify-left-symbolic")
    align_left_button.set_tooltip_text("Align Left (text wraps around right)")
    align_left_button.connect("clicked", lambda btn: self.on_table_align_left(win))
    align_group.append(align_left_button)
    
    # Center alignment
    align_center_button = Gtk.Button(icon_name="format-justify-center-symbolic")
    align_center_button.set_tooltip_text("Center (no text wrap)")
    align_center_button.connect("clicked", lambda btn: self.on_table_align_center(win))
    align_group.append(align_center_button)
    
    # Right alignment
    align_right_button = Gtk.Button(icon_name="format-justify-right-symbolic")
    align_right_button.set_tooltip_text("Align Right (text wraps around left)")
    align_right_button.connect("clicked", lambda btn: self.on_table_align_right(win))
    align_group.append(align_right_button)
    
    # Full width (no wrap)
    full_width_button = Gtk.Button(icon_name="format-justify-fill-symbolic")
    full_width_button.set_tooltip_text("Full Width (no text wrap)")
    full_width_button.connect("clicked", lambda btn: self.on_table_full_width(win))
    align_group.append(full_width_button)
    
    # Add alignment group to toolbar
    toolbar.append(align_group)
    
    # Float button
    float_button = Gtk.Button(icon_name="overlapping-windows-symbolic")
    float_button.set_tooltip_text("Make table float freely in editor")
    float_button.set_margin_start(5)
    float_button.connect("clicked", lambda btn: self.on_table_float_clicked(win))
    toolbar.append(float_button)

    # Z-index controls - NEW
    # Separator for layer controls
    separator4 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
    separator4.set_margin_start(10)
    separator4.set_margin_end(10)
    toolbar.append(separator4)
    
    # Layer control options
    layer_label = Gtk.Label(label="Layer:")
    layer_label.set_margin_end(5)
    toolbar.append(layer_label)
    
    # Create a group for layer control buttons
    layer_group = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
    layer_group.add_css_class("linked")
    
    # Bring forward button (increase z-index)
    bring_forward_button = Gtk.Button(icon_name="go-up-symbolic")
    bring_forward_button.set_tooltip_text("Bring Forward (place above other elements)")
    bring_forward_button.connect("clicked", lambda btn: self.on_bring_forward_clicked(win, btn))
    layer_group.append(bring_forward_button)
    
    # Send backward button (decrease z-index)
    send_backward_button = Gtk.Button(icon_name="go-down-symbolic")
    send_backward_button.set_tooltip_text("Send Backward (place beneath other elements)")
    send_backward_button.connect("clicked", lambda btn: self.on_send_backward_clicked(win, btn))
    layer_group.append(send_backward_button)
    
    # Add layer control group to toolbar
    toolbar.append(layer_group)
    
    # Spacer
    spacer = Gtk.Box()
    spacer.set_hexpand(True)
    toolbar.append(spacer)
    
    # Close button
    close_button = Gtk.Button(icon_name="window-close-symbolic")
    close_button.set_tooltip_text("Close table toolbar")
    close_button.connect("clicked", lambda btn: self.on_close_table_toolbar_clicked(win))
    toolbar.append(close_button)
    
    return toolbar

def on_insert_table_clicked(self, win, btn):
    """Handle table insertion button click"""
    win.statusbar.set_text("Inserting table...")
    
    # Create a dialog to configure the table
    dialog = Adw.Dialog()
    dialog.set_title("Insert Table")
    dialog.set_content_width(350)
    
    # Create layout for dialog content
    content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
    content_box.set_margin_top(24)
    content_box.set_margin_bottom(24)
    content_box.set_margin_start(24)
    content_box.set_margin_end(24)
    
    # Rows input
    rows_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    rows_label = Gtk.Label(label="Rows:")
    rows_label.set_halign(Gtk.Align.START)
    rows_label.set_hexpand(True)
    
    rows_adjustment = Gtk.Adjustment(value=3, lower=1, upper=20, step_increment=1)
    rows_spin = Gtk.SpinButton()
    rows_spin.set_adjustment(rows_adjustment)
    
    rows_box.append(rows_label)
    rows_box.append(rows_spin)
    content_box.append(rows_box)
    
    # Columns input
    cols_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    cols_label = Gtk.Label(label="Columns:")
    cols_label.set_halign(Gtk.Align.START)
    cols_label.set_hexpand(True)
    
    cols_adjustment = Gtk.Adjustment(value=3, lower=1, upper=10, step_increment=1)
    cols_spin = Gtk.SpinButton()
    cols_spin.set_adjustment(cols_adjustment)
    
    cols_box.append(cols_label)
    cols_box.append(cols_spin)
    content_box.append(cols_box)
    
    # Header row checkbox
    header_check = Gtk.CheckButton(label="Include header row")
    header_check.set_active(True)
    content_box.append(header_check)
    
    # Border options
    border_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    border_label = Gtk.Label(label="Border width:")
    border_label.set_halign(Gtk.Align.START)
    border_label.set_hexpand(True)
    
    border_adjustment = Gtk.Adjustment(value=1, lower=0, upper=5, step_increment=1)
    border_spin = Gtk.SpinButton()
    border_spin.set_adjustment(border_adjustment)
    
    border_box.append(border_label)
    border_box.append(border_spin)
    content_box.append(border_box)
    
    # Table width options
    width_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    width_label = Gtk.Label(label="Table width:")
    width_label.set_halign(Gtk.Align.START)
    width_label.set_hexpand(True)
    
    width_combo = Gtk.DropDown()
    width_options = Gtk.StringList()
    width_options.append("Auto")
    width_options.append("100%")
    width_options.append("75%")
    width_options.append("50%")
    width_combo.set_model(width_options)
    width_combo.set_selected(1)  # Default to 100% (index 1)
    
    width_box.append(width_label)
    width_box.append(width_combo)
    content_box.append(width_box)
    
    # ADDED: Floating option checkbox
    float_check = Gtk.CheckButton(label="Free-floating (text wraps around)")
    float_check.set_active(False)  # Enabled by default
    content_box.append(float_check)
    
    # Set initial width based on floating setting (Auto for floating tables)
    width_combo.set_selected(1)  # Start with Auto since floating is active by default
    
    # Connect change handler for float check to update width combo
    def on_float_check_toggled(check_button):
        if check_button.get_active():  # If float is enabled
            width_combo.set_selected(0)  # Set to "Auto"
        else:  # If float is disabled
            width_combo.set_selected(1)  # Set to "100%"
    
    float_check.connect("toggled", on_float_check_toggled)
    
    # Button box
    button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    button_box.set_halign(Gtk.Align.END)
    button_box.set_margin_top(16)
    
    cancel_button = Gtk.Button(label="Cancel")
    cancel_button.connect("clicked", lambda btn: dialog.close())
    
    insert_button = Gtk.Button(label="Insert")
    insert_button.add_css_class("suggested-action")
    insert_button.connect("clicked", lambda btn: self.on_table_dialog_response(
        win, dialog, 
        rows_spin.get_value_as_int(), 
        cols_spin.get_value_as_int(),
        header_check.get_active(),
        border_spin.get_value_as_int(),
        width_options.get_string(width_combo.get_selected()),
        float_check.get_active()  # Pass floating state
    ))
    
    button_box.append(cancel_button)
    button_box.append(insert_button)
    content_box.append(button_box)
    
    # Set dialog content and present
    dialog.set_child(content_box)
    dialog.present(win)

def on_table_dialog_response(self, win, dialog, rows, cols, has_header, border_width, width_option, is_floating):
    """Handle response from the table dialog"""
    dialog.close()
    
    # Prepare the width value
    width_value = "auto"
    if width_option != "Auto":
        width_value = width_option
    
    # Execute JavaScript to insert the table
    js_code = f"""
    (function() {{
        insertTable({rows}, {cols}, {str(has_header).lower()}, {border_width}, "{width_value}", {str(is_floating).lower()});
        return true;
    }})();
    """
    self.execute_js(win, js_code)
    
    # Update status message based on table type
    if is_floating:
        win.statusbar.set_text("Floating table inserted")
    else:
        win.statusbar.set_text("Table inserted")        

def on_table_clicked(self, win, manager, message):
    """Handle table click event from editor"""
    win.table_toolbar_revealer.set_reveal_child(True)
    win.statusbar.set_text("Table selected")
    
    # Update margin controls with current table margins
    js_code = """
    (function() {
        const margins = getTableMargins();
        return JSON.stringify(margins);
    })();
    """
    
    win.webview.evaluate_javascript(
        js_code,
        -1, None, None, None,
        lambda webview, result, data: self._update_margin_controls(win, webview, result),
        None
    )
    
def on_table_deleted(self, win, manager, message):
    """Handle table deleted event from editor"""
    win.table_toolbar_revealer.set_reveal_child(False)
    win.statusbar.set_text("Table deleted")

def on_tables_deactivated(self, win, manager, message):
    """Handle event when all tables are deactivated"""
    win.table_toolbar_revealer.set_reveal_child(False)
    win.statusbar.set_text("No table selected")
    
   

# Table operation methods
def on_add_row_above_clicked(self, win):
    """Add a row above the current row in the active table"""
    js_code = """
    (function() {
        if (!activeTable) return;
        
        // Get the current row index
        let selection = window.getSelection();
        if (selection.rangeCount < 1) {
            // If no selection, add at the beginning
            addTableRow(activeTable, 0);
            return;
        }
        
        let range = selection.getRangeAt(0);
        let cell = range.startContainer;
        
        // Find the TD/TH parent
        while (cell && cell.tagName !== 'TD' && cell.tagName !== 'TH' && cell !== activeTable) {
            cell = cell.parentNode;
        }
        
        if (!cell || (cell.tagName !== 'TD' && cell.tagName !== 'TH')) {
            // If no cell is selected, add at the beginning
            addTableRow(activeTable, 0);
            return;
        }
        
        // Find the TR parent
        let row = cell;
        while (row && row.tagName !== 'TR') {
            row = row.parentNode;
        }
        
        if (!row) {
            addTableRow(activeTable, 0);
            return;
        }
        
        // Find the row index - this is the simple approach
        let rowIndex = Array.from(activeTable.rows).indexOf(row);
        
        // If we're at the first row, we need to insert at position 0
        if (rowIndex === 0) {
            // Create a new row directly at the start of the table
            const newRow = activeTable.insertRow(0);
            
            // Create cells matching the current row's cells
            for (let i = 0; i < row.cells.length; i++) {
                const cell = row.cells[i];
                const newCell = newRow.insertCell(i);
                
                // Copy cell type (TD or TH)
                if (cell.tagName === 'TH') {
                    const headerCell = document.createElement('th');
                    headerCell.innerHTML = '&nbsp;';
                    // Copy styles
                    headerCell.style.border = cell.style.border || '1px solid ' + getBorderColor();
                    headerCell.style.padding = cell.style.padding || '5px';
                    headerCell.style.backgroundColor = cell.style.backgroundColor || getHeaderBgColor();
                    newRow.replaceChild(headerCell, newCell);
                } else {
                    newCell.innerHTML = '&nbsp;';
                    newCell.style.border = cell.style.border || '1px solid ' + getBorderColor();
                    newCell.style.padding = cell.style.padding || '5px';
                }
            }
        } else {
            // For other rows, use the regular addTableRow function
            addTableRow(activeTable, rowIndex);
        }
        
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
    })();
    """
    self.execute_js(win, js_code)

def on_add_row_below_clicked(self, win):
    """Add a row below the current row in the active table"""
    js_code = """
    (function() {
        if (!activeTable) return;
        
        // Get the current row index
        let selection = window.getSelection();
        if (selection.rangeCount < 1) return;
        
        let range = selection.getRangeAt(0);
        let cell = range.startContainer;
        
        // Find the TD/TH parent
        while (cell && cell.tagName !== 'TD' && cell.tagName !== 'TH' && cell !== activeTable) {
            cell = cell.parentNode;
        }
        
        if (!cell || (cell.tagName !== 'TD' && cell.tagName !== 'TH')) {
            // If no cell is selected, just add to the end
            addTableRow(activeTable);
            return;
        }
        
        // Find the TR parent
        let row = cell;
        while (row && row.tagName !== 'TR') {
            row = row.parentNode;
        }
        
        if (!row) return;
        
        // Find the row index
        let rowIndex = row.rowIndex;
        
        // Add a row below this one
        addTableRow(activeTable, rowIndex + 1);
    })();
    """
    self.execute_js(win, js_code)

def on_add_column_before_clicked(self, win):
    """Add a column before the current column in the active table"""
    js_code = """
    (function() {
        if (!activeTable) return;
        
        // Get the current cell index
        let selection = window.getSelection();
        if (selection.rangeCount < 1) return;
        
        let range = selection.getRangeAt(0);
        let cell = range.startContainer;
        
        // Find the TD/TH parent
        while (cell && cell.tagName !== 'TD' && cell.tagName !== 'TH' && cell !== activeTable) {
            cell = cell.parentNode;
        }
        
        if (!cell || (cell.tagName !== 'TD' && cell.tagName !== 'TH')) {
            // If no cell is selected, just add to the start
            addTableColumn(activeTable, 0);
            return;
        }
        
        // Find the cell index
        let cellIndex = cell.cellIndex;
        
        // Add a column before the current one
        addTableColumn(activeTable, cellIndex);
    })();
    """
    self.execute_js(win, js_code)     
    
    
def on_add_column_after_clicked(self, win):
    """Add a column after the current column in the active table"""
    js_code = """
    (function() {
        if (!activeTable) return;
        
        // Get the current cell index
        let selection = window.getSelection();
        if (selection.rangeCount < 1) return;
        
        let range = selection.getRangeAt(0);
        let cell = range.startContainer;
// Find the TD/TH parent
        while (cell && cell.tagName !== 'TD' && cell.tagName !== 'TH' && cell !== activeTable) {
            cell = cell.parentNode;
        }
        
        if (!cell || (cell.tagName !== 'TD' && cell.tagName !== 'TH')) {
            // If no cell is selected, just add to the end
            addTableColumn(activeTable);
            return;
        }
        
        // Find the cell index
        let cellIndex = cell.cellIndex;
        
        // Add a column after the current one
        addTableColumn(activeTable, cellIndex + 1);
    })();
    """
    self.execute_js(win, js_code)

def on_delete_row_clicked(self, win):
    """Delete the current row from the active table"""
    js_code = """
    (function() {
        if (!activeTable) return;
        
        // Get the current row index
        let selection = window.getSelection();
        if (selection.rangeCount < 1) return;
        
        let range = selection.getRangeAt(0);
        let cell = range.startContainer;
        
        // Find the TD/TH parent
        while (cell && cell.tagName !== 'TD' && cell.tagName !== 'TH' && cell !== activeTable) {
            cell = cell.parentNode;
        }
        
        if (!cell || (cell.tagName !== 'TD' && cell.tagName !== 'TH')) {
            // If no cell is selected, just delete the last row
            deleteTableRow(activeTable);
            return;
        }
        
        // Find the TR parent
        let row = cell;
        while (row && row.tagName !== 'TR') {
            row = row.parentNode;
        }
        
        if (!row) return;
        
        // Find the row index
        let rowIndex = row.rowIndex;
        
        // Delete this row
        deleteTableRow(activeTable, rowIndex);
    })();
    """
    self.execute_js(win, js_code)

def on_delete_column_clicked(self, win):
    """Delete the current column from the active table"""
    js_code = """
    (function() {
        if (!activeTable) return;
        
        // Get the current cell index
        let selection = window.getSelection();
        if (selection.rangeCount < 1) return;
        
        let range = selection.getRangeAt(0);
        let cell = range.startContainer;
        
        // Find the TD/TH parent
        while (cell && cell.tagName !== 'TD' && cell.tagName !== 'TH' && cell !== activeTable) {
            cell = cell.parentNode;
        }
        
        if (!cell || (cell.tagName !== 'TD' && cell.tagName !== 'TH')) {
            // If no cell is selected, just delete the last column
            deleteTableColumn(activeTable);
            return;
        }
        
        // Find the cell index
        let cellIndex = cell.cellIndex;
        
        // Delete this column
        deleteTableColumn(activeTable, cellIndex);
    })();
    """
    self.execute_js(win, js_code)

def on_delete_table_clicked(self, win):
    """Delete the entire table"""
    js_code = "deleteTable(activeTable);"
    self.execute_js(win, js_code)

def on_table_align_left(self, win):
    """Align table to the left with text wrapping around right"""
    js_code = "setTableAlignment('left-align');"
    self.execute_js(win, js_code)

def on_table_align_center(self, win):
    """Align table to the center with no text wrapping"""
    js_code = "setTableAlignment('center-align');"
    self.execute_js(win, js_code)

def on_table_align_right(self, win):
    """Align table to the right with text wrapping around left"""
    js_code = "setTableAlignment('right-align');"
    self.execute_js(win, js_code)

def on_table_full_width(self, win):
    """Make table full width with no text wrapping"""
    js_code = "setTableAlignment('no-wrap');"
    self.execute_js(win, js_code)

def on_close_table_toolbar_clicked(self, win):
    """Hide the table toolbar and deactivate tables"""
    win.table_toolbar_revealer.set_reveal_child(False)
    js_code = "deactivateAllTables();"
    self.execute_js(win, js_code)
    win.statusbar.set_text("Table toolbar closed")

def on_table_button_clicked(self, win, button):
    """Show the table properties popup with tabs"""
    # Create a popover for table properties
    popover = Gtk.Popover()
    popover.set_parent(button)
    
    # Create the content box with reduced margins and spacing
    content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)  # Reduced from 8
    content_box.set_margin_start(8)  # Reduced from 12
    content_box.set_margin_end(8)
    content_box.set_margin_top(8)
    content_box.set_margin_bottom(8)
    content_box.set_size_request(320, 230)  # Reduced from 350, 250
    
    # Create header with title and close button
    header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
    header_box.set_margin_bottom(6)  # Reduced from 8
    
    # Add title label
    title_label = Gtk.Label(label="<b>Table Properties</b>")
    title_label.set_use_markup(True)
    title_label.set_halign(Gtk.Align.START)
    title_label.set_hexpand(True)
    header_box.append(title_label)
    
    # Add close button [x]
    close_button = Gtk.Button.new_from_icon_name("window-close-symbolic")
    close_button.set_tooltip_text("Close")
    close_button.add_css_class("flat")
    close_button.connect("clicked", lambda btn: popover.popdown())
    header_box.append(close_button)
    
    content_box.append(header_box)
    
    # Create tab view
    tab_view = Gtk.Notebook()
    tab_view.set_vexpand(True)
    
    # Create Border tab
    border_page = self._create_border_tab(win, popover)
    tab_view.append_page(border_page, Gtk.Label(label="Border"))
    
    # Create Margin tab
    margin_page = self._create_margin_tab(win, popover)
    tab_view.append_page(margin_page, Gtk.Label(label="Margin"))
    
    # Create Color tab
    color_page = self._create_color_tab(win, popover)
    tab_view.append_page(color_page, Gtk.Label(label="Color"))
    
    content_box.append(tab_view)
    
    # Set the content and show the popover
    popover.set_child(content_box)
    popover.popup()
    
    # Get current properties to initialize the dialogs
    self._initialize_table_properties(win, popover)

def _create_border_tab(self, win, popover):
    """Create the border properties tab"""
    border_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    border_box.set_margin_start(12)
    border_box.set_margin_end(12)
    border_box.set_margin_top(12)
    border_box.set_margin_bottom(12)
    
    # Border style and width in a single row
    style_width_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    
    # Border style dropdown (more compact)
    style_label = Gtk.Label(label="Style:")
    style_label.set_halign(Gtk.Align.START)
    
    style_combo = Gtk.DropDown()
    style_options = Gtk.StringList()
    styles = ["solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"]
    for style in styles:
        style_options.append(style)
    style_combo.set_model(style_options)
    style_combo.set_selected(0)  # Default to solid
    
    # Border width spinner (more compact)
    width_label = Gtk.Label(label="Width:")
    width_label.set_halign(Gtk.Align.START)
    
    width_adjustment = Gtk.Adjustment(value=1, lower=0, upper=10, step_increment=1)
    width_spin = Gtk.SpinButton()
    width_spin.set_adjustment(width_adjustment)
    width_spin.set_width_chars(3)  # Make it more compact
    
    # Connect style change
    style_combo.connect("notify::selected", lambda cb, p: self.on_border_style_changed(
        win, styles[cb.get_selected()], width_spin.get_value_as_int()))
    
    # Connect width change
    width_spin.connect("value-changed", lambda spin: self.on_border_width_changed(
        win, styles[style_combo.get_selected()], spin.get_value_as_int()))
    
    # Add all to the row
    style_width_box.append(style_label)
    style_width_box.append(style_combo)
    style_width_box.append(width_label)
    style_width_box.append(width_spin)
    border_box.append(style_width_box)
    
    # Border shadow option
    shadow_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    shadow_label = Gtk.Label(label="Shadow:")
    shadow_label.set_halign(Gtk.Align.START)
    
    shadow_switch = Gtk.Switch()
    shadow_switch.set_active(False)
    shadow_switch.connect("notify::active", lambda sw, _: self.on_border_shadow_changed(win, sw.get_active()))
    
    shadow_box.append(shadow_label)
    shadow_box.append(shadow_switch)
    border_box.append(shadow_box)
    
    # Add a separator
    border_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
    
    # Border display options title (more compact)
    display_label = Gtk.Label(label="Border Display:")
    display_label.set_halign(Gtk.Align.START)
    display_label.set_margin_top(4)
    border_box.append(display_label)
    
    # Create a horizontal box for all border options
    all_options_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    
    # Create a linked box for primary border toggles
    primary_border_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    primary_border_box.add_css_class("linked")
    
    # Create the primary border buttons
    border_options = [
        {"icon": "table-border-all-symbolic", "tooltip": "All Borders", "value": "all"},
        {"icon": "table-border-none-symbolic", "tooltip": "No Borders", "value": "none"},
        {"icon": "table-border-outer-symbolic", "tooltip": "Outer Borders", "value": "outer"},
        {"icon": "table-border-inner-symbolic", "tooltip": "Inner Borders", "value": "inner"}
    ]
    
    for option in border_options:
        button = Gtk.Button.new_from_icon_name(option["icon"])
        button.set_tooltip_text(option["tooltip"])
        button.connect("clicked", lambda btn, border_option=option["value"]: self.on_border_display_option_clicked(
            win, None, width_spin, border_option))
        primary_border_box.append(button)
    
    all_options_box.append(primary_border_box)
    
    # Create a linked box for combo border options
    combo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    combo_box.add_css_class("linked")
    
    # Create horizontal/vertical buttons
    combo_options = [
        {"icon": "table-border-horizontal-symbolic", "tooltip": "Horizontal Borders", "value": "horizontal"},
        {"icon": "table-border-vertical-symbolic", "tooltip": "Vertical Borders", "value": "vertical"}
    ]
    
    for option in combo_options:
        button = Gtk.Button.new_from_icon_name(option["icon"])
        button.set_tooltip_text(option["tooltip"])
        button.connect("clicked", lambda btn, border_option=option["value"]: self.on_border_display_option_clicked(
            win, None, width_spin, border_option))
        combo_box.append(button)
    
    all_options_box.append(combo_box)
    border_box.append(all_options_box)
    
    # Create a second row for combination border options
    combo_row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    combo_row2.set_margin_top(4)
    
    # First linked box for combined options
    combo_box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    combo_box2.add_css_class("linked")
    
    combo_options2 = [
        {"icon": "table-border-outer-horizontal-symbolic", "tooltip": "Outer Horizontal", "value": ["outer", "horizontal"]},
        {"icon": "table-border-outer-vertical-symbolic", "tooltip": "Outer Vertical", "value": ["outer", "vertical"]},
        {"icon": "table-border-inner-horizontal-symbolic", "tooltip": "Inner Horizontal", "value": ["inner", "horizontal"]},
        {"icon": "table-border-inner-vertical-symbolic", "tooltip": "Inner Vertical", "value": ["inner", "vertical"]}
    ]
    
    for option in combo_options2:
        button = Gtk.Button.new_from_icon_name(option["icon"])
        button.set_tooltip_text(option["tooltip"])
        if isinstance(option["value"], list):
            button.connect("clicked", lambda btn, border_types=option["value"]: self._apply_combined_borders(
                win, width_spin, border_types))
        else:
            button.connect("clicked", lambda btn, border_option=option["value"]: self.on_border_display_option_clicked(
                win, None, width_spin, border_option))
        combo_box2.append(button)
    
    combo_row2.append(combo_box2)
    
    # Second linked box for all combined options
    combo_box3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    combo_box3.add_css_class("linked")
    
    combo_options3 = [
        {"icon": "table-border-outer-inner-horizontal-symbolic", "tooltip": "Outer + Inner Horizontal", "value": ["outer", "inner", "horizontal"]},
        {"icon": "table-border-outer-inner-vertical-symbolic", "tooltip": "Outer + Inner Vertical", "value": ["outer", "inner", "vertical"]}
    ]
    
    for option in combo_options3:
        button = Gtk.Button.new_from_icon_name(option["icon"])
        button.set_tooltip_text(option["tooltip"])
        button.connect("clicked", lambda btn, border_types=option["value"]: self._apply_combined_borders(
            win, width_spin, border_types))
        combo_box3.append(button)
    
    combo_row2.append(combo_box3)
    border_box.append(combo_row2)
    
    # Store references for later initialization
    border_box.style_combo = style_combo
    border_box.width_spin = width_spin
    border_box.shadow_switch = shadow_switch
    
    return border_box

def _create_margin_tab(self, win, popover):
    """Create the margin properties tab with default values"""
    margin_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    margin_box.set_margin_start(12)
    margin_box.set_margin_end(12)
    margin_box.set_margin_top(12)
    margin_box.set_margin_bottom(12)
    
    # Create grid for margin controls
    margin_grid = Gtk.Grid()
    margin_grid.set_row_spacing(8)
    margin_grid.set_column_spacing(12)
    margin_grid.set_halign(Gtk.Align.CENTER)
    
    margin_controls = {}
    
    # Define positions for a visual layout with default values
    positions = {
        'top': (0, 1, 6),      # (row, col, default_value)
        'left': (1, 0, 0),
        'right': (1, 2, 6),
        'bottom': (2, 1, 0)
    }
    
    for side, (row, col, default_value) in positions.items():
        # Create a box for label and spin button
        side_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        # Add label
        label = Gtk.Label(label=side.capitalize())
        label.set_halign(Gtk.Align.CENTER)
        side_box.append(label)
        
        # Create spin button with appropriate default value
        adjustment = Gtk.Adjustment(value=default_value, lower=0, upper=100, step_increment=1)
        spin = Gtk.SpinButton()
        spin.set_adjustment(adjustment)
        spin.set_width_chars(5)
        
        # Connect change signal
        spin.connect("value-changed", lambda s, sd=side: self.on_margin_changed(win, sd, s.get_value_as_int()))
        
        side_box.append(spin)
        margin_grid.attach(side_box, col, row, 1, 1)
        margin_controls[side] = spin
    
    # Add a visual representation of the table in the center
    table_visual = Gtk.DrawingArea()
    table_visual.set_size_request(80, 60)
    table_visual.set_content_width(80)
    table_visual.set_content_height(60)
    
    def draw_table_visual(area, cr, width, height, data):
        # Draw a simple table representation
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.rectangle(10, 10, width - 20, height - 20)
        cr.fill()
        
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.rectangle(10, 10, width - 20, height - 20)
        cr.stroke()
    
    table_visual.set_draw_func(draw_table_visual, None)
    margin_grid.attach(table_visual, 1, 1, 1, 1)
    
    margin_box.append(margin_grid)
    
    # Add separator before default button
    separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    separator.set_margin_top(8)
    separator.set_margin_bottom(8)
    margin_box.append(separator)
    
    # Add default button
    default_button = Gtk.Button(label="Reset to Default Margins")
    default_button.connect("clicked", lambda btn: self._reset_default_margins(win, margin_controls))
    margin_box.append(default_button)
    
    # Store margin controls for later reference
    margin_box.margin_controls = margin_controls
    
    return margin_box

def _create_color_tab(self, win, popover):
    """Create the color properties tab with GTK4 compatible color handling and compact layout"""
    color_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)  # Reduced from 12
    color_box.set_margin_start(8)  # Reduced from 12
    color_box.set_margin_end(8)
    color_box.set_margin_top(8)
    color_box.set_margin_bottom(8)
    
    # Helper function to create color button with custom color picker
    def create_color_button_row(label_text, apply_function):
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)  # Reduced from 8
        label = Gtk.Label(label=label_text)
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        
        # Create a button with color icon instead of ColorButton
        color_button = Gtk.Button()
        color_button.set_size_request(36, 20)  # Reduced from 40, 24
        
        # Create a DrawingArea for color display
        color_display = Gtk.DrawingArea()
        color_display.set_size_request(28, 16)  # Reduced from 30, 18
        color_button.set_child(color_display)
        
        # Default color
        color_button.current_color = "#000000"
        
        # Draw function for color display
        def draw_color(area, cr, width, height, data):
            rgba = self._parse_color_string(color_button.current_color)
            if rgba:
                cr.set_source_rgba(rgba.red, rgba.green, rgba.blue, rgba.alpha)
            else:
                cr.set_source_rgba(0, 0, 0, 1)  # Default to black
            cr.rectangle(2, 2, width - 4, height - 4)
            cr.fill()
            
            # Draw border
            cr.set_source_rgba(0.5, 0.5, 0.5, 1)
            cr.rectangle(2, 2, width - 4, height - 4)
            cr.set_line_width(1)
            cr.stroke()
        
        color_display.set_draw_func(draw_color, None)
        
        # Connect click handler to show color dialog
        color_button.connect("clicked", lambda btn: self._show_color_dialog(win, btn, apply_function))
        
        row_box.append(label)
        row_box.append(color_button)
        return row_box, color_button
    
    # Border color row
    border_color_box, border_color_button = create_color_button_row(
        "Border Color:", self._apply_border_color)
    color_box.append(border_color_box)
    
    # Table background color row
    table_color_box, table_color_button = create_color_button_row(
        "Table Color:", self._apply_table_color)
    color_box.append(table_color_box)
    
    # Header color row
    header_color_box, header_color_button = create_color_button_row(
        "Header Color:", self._apply_header_color)
    color_box.append(header_color_box)
    
    # Row color row (NEW)
    row_color_box, row_color_button = create_color_button_row(
        "Row Color:", self._apply_row_color)
    color_box.append(row_color_box)
    
    # Column color row (NEW)
    column_color_box, column_color_button = create_color_button_row(
        "Column Color:", self._apply_column_color)
    color_box.append(column_color_box)
    
    # Cell color row
    cell_color_box, cell_color_button = create_color_button_row(
        "Current Cell Color:", self._apply_cell_color)
    color_box.append(cell_color_box)
    
    # Add separator
    separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    separator.set_margin_top(6)  # Reduced from 8
    separator.set_margin_bottom(6)
    color_box.append(separator)
    
    # Add default button
    default_button = Gtk.Button(label="Reset to Default Colors")
    default_button.connect("clicked", lambda btn: self._reset_default_colors(win))
    color_box.append(default_button)
    
    # Store color buttons for later initialization
    color_box.border_color_button = border_color_button
    color_box.table_color_button = table_color_button
    color_box.header_color_button = header_color_button
    color_box.row_color_button = row_color_button
    color_box.column_color_button = column_color_button
    color_box.cell_color_button = cell_color_button
    
    return color_box

def _initialize_table_properties(self, win, popover):
    """Initialize the table properties popup with current values"""
    # Get current table properties
    js_code = """
    (function() {
        const borderProps = getTableBorderProperties();
        const margins = getTableMargins();
        const colors = getTableColors();
        
        return JSON.stringify({
            border: borderProps,
            margins: margins,
            colors: colors
        });
    })();
    """
    
    win.webview.evaluate_javascript(
        js_code,
        -1, None, None, None,
        lambda webview, result, data: self._on_get_table_properties(win, webview, result, popover),
        None
    )

def _on_get_table_properties(self, win, webview, result, popover):
    """Handle getting current table properties"""
    try:
        js_result = webview.evaluate_javascript_finish(result)
        result_str = None
        
        if hasattr(js_result, 'get_js_value'):
            result_str = js_result.get_js_value().to_string()
        else:
            result_str = js_result.to_string()
        
        if result_str:
            import json
            properties = json.loads(result_str)
            
            # Get references to the tab pages
            content_box = popover.get_child()
            notebook = None
            
            # Find the notebook widget (skip header)
            for child in content_box:
                if isinstance(child, Gtk.Notebook):
                    notebook = child
                    break
            
            if notebook:
                border_page = notebook.get_nth_page(0)
                margin_page = notebook.get_nth_page(1)
                color_page = notebook.get_nth_page(2)
                
                # Initialize border controls
                if properties.get('border'):
                    border_style = properties['border'].get('style', 'solid')
                    border_width = properties['border'].get('width', 1)
                    has_shadow = properties['border'].get('shadow', False)
                    
                    # Find index of style
                    styles = ["solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"]
                    try:
                        style_index = styles.index(border_style)
                    except ValueError:
                        style_index = 0  # Default to solid
                    
                    border_page.style_combo.set_selected(style_index)
                    border_page.width_spin.set_value(border_width)
                    border_page.shadow_switch.set_active(has_shadow)
                
                # Initialize margin controls
                if properties.get('margins'):
                    margins = properties['margins']
                    for side in ['top', 'right', 'bottom', 'left']:
                        if side in margin_page.margin_controls and side in margins:
                            margin_page.margin_controls[side].set_value(margins[side])
                
                # Initialize color controls
                if properties.get('colors'):
                    colors = properties['colors']
                    
                    # Set border color
                    if colors.get('border'):
                        color_page.border_color_button.current_color = colors['border']
                        color_display = color_page.border_color_button.get_child()
                        if color_display:
                            color_display.queue_draw()
                    
                    # Set table background color
                    if colors.get('background'):
                        color_page.table_color_button.current_color = colors['background']
                        color_display = color_page.table_color_button.get_child()
                        if color_display:
                            color_display.queue_draw()
                    
                    # Set header color
                    if colors.get('header'):
                        color_page.header_color_button.current_color = colors['header']
                        color_display = color_page.header_color_button.get_child()
                        if color_display:
                            color_display.queue_draw()
                    
                    # Set cell color (if selected)
                    if colors.get('cell'):
                        color_page.cell_color_button.current_color = colors['cell']
                        color_display = color_page.cell_color_button.get_child()
                        if color_display:
                            color_display.queue_draw()
                    
    except Exception as e:
        print(f"Error initializing table properties: {e}")     
        
def on_border_style_changed(self, win, style, width):
    """Apply border style change immediately while preserving other properties"""
    # Execute JavaScript to apply the border style while preserving width
    js_code = f"""
    (function() {{
        // Get current border properties first
        const currentStyle = getTableBorderStyle();
        const currentWidth = currentStyle ? currentStyle.width : {width};
        const currentColor = currentStyle ? currentStyle.color : getBorderColor();
        
        // Apply with preserved values
        setTableBorderStyle('{style}', currentWidth, currentColor);
        return true;
    }})();
    """
    win.webview.evaluate_javascript(js_code, -1, None, None, None, None, None)
    
    # Update status message
    win.statusbar.set_text(f"Applied {style} border style")

def on_border_width_changed(self, win, style, width):
    """Apply border width change immediately while preserving other properties"""
    # Execute JavaScript to apply the border width while preserving style
    js_code = f"""
    (function() {{
        // Get current border properties first
        const currentStyle = getTableBorderStyle();
        const currentBorderStyle = currentStyle ? currentStyle.style : 'solid';
        const currentColor = currentStyle ? currentStyle.color : getBorderColor();
        
        // Apply with preserved values
        setTableBorderStyle(currentBorderStyle, {width}, currentColor);
        return true;
    }})();
    """
    win.webview.evaluate_javascript(js_code, -1, None, None, None, None, None)
    
    # Update status message
    win.statusbar.set_text(f"Applied {width}px border width")       

def on_border_shadow_changed(self, win, active):
    """Apply or remove border shadow"""
    js_code = f"""
    (function() {{
        if (!activeTable) return false;
        
        if ({str(active).lower()}) {{
            activeTable.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.2)';
        }} else {{
            activeTable.style.boxShadow = 'none';
        }}
        
        // Store shadow state
        activeTable.setAttribute('data-border-shadow', {str(active).lower()});
        
        // Notify that content changed
        try {{
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        }} catch(e) {{
            console.log("Could not notify about content change:", e);
        }}
        
        return true;
    }})();
    """
    self.execute_js(win, js_code)
    win.statusbar.set_text(f"Border shadow {'enabled' if active else 'disabled'}")
    


def _reset_default_margins(self, win, margin_controls):
    """Reset margins to default values"""
    default_margins = {
        'top': 6,
        'right': 6,
        'bottom': 0,
        'left': 0
    }
    
    # Update spin buttons
    for side, value in default_margins.items():
        if side in margin_controls:
            margin_controls[side].set_value(value)
    
    # Apply the margins in JavaScript
    js_code = f"""
    (function() {{
        setTableMargins({default_margins['top']}, {default_margins['right']}, 
                        {default_margins['bottom']}, {default_margins['left']});
        return true;
    }})();
    """
    self.execute_js(win, js_code)
    win.statusbar.set_text("Reset to default margins")


def _get_color_from_button(self, color_button):
    """Get color from button in a safe way that handles deprecation"""
    try:
        # Try the standard method first
        rgba = color_button.get_rgba()
        hex_color = f"#{int(rgba.red * 255):02x}{int(rgba.green * 255):02x}{int(rgba.blue * 255):02x}"
        return hex_color
    except:
        try:
            # Try alternative methods
            color = color_button.get_color()
            red = (color.red >> 8) / 255.0
            green = (color.green >> 8) / 255.0
            blue = (color.blue >> 8) / 255.0
            hex_color = f"#{int(red * 255):02x}{int(green * 255):02x}{int(blue * 255):02x}"
            return hex_color
        except:
            # Final fallback
            return "#000000"

def _set_color_on_button(self, color_button, color_string):
    """Set color on button in a safe way that handles deprecation"""
    try:
        rgba = self._parse_color_string(color_string)
        if rgba:
            try:
                color_button.set_rgba(rgba)
            except:
                # Try alternative methods
                color_button.set_color(self._rgba_to_color(rgba))
    except Exception as e:
        print(f"Error setting color on button: {e}")


def _show_color_dialog(self, win, color_button, apply_function):
    """Show a color dialog compatible with GTK4"""
    try:
        # Try using GTK4 ColorDialog
        try:
            dialog = Gtk.ColorDialog()
            dialog.set_title("Choose Color")
            
            # Set initial color
            initial_rgba = self._parse_color_string(color_button.current_color)
            if not initial_rgba:
                initial_rgba = Gdk.RGBA()
                initial_rgba.parse("#000000")
            
            dialog.choose_rgba(
                win,
                initial_rgba,
                None,
                lambda dlg, result, data: self._on_color_chosen(dlg, result, color_button, apply_function, win),
                None
            )
            return
        except AttributeError:
            # ColorDialog not available, use ColorChooserDialog
            dialog = Gtk.ColorChooserDialog(
                title="Choose Color",
                transient_for=win
            )
            
            # Set initial color
            initial_rgba = self._parse_color_string(color_button.current_color)
            if initial_rgba:
                try:
                    dialog.set_rgba(initial_rgba)
                except AttributeError:
                    pass
            
            # Connect response handler
            dialog.connect("response", lambda dlg, response: self._on_color_dialog_response(
                dlg, response, color_button, apply_function, win))
            
            dialog.show()
    except Exception as e:
        print(f"Error showing color dialog: {e}")
        # Fallback to preset color popover
        self._show_color_preset_popover(win, color_button, apply_function)

def _on_color_chosen(self, dialog, result, color_button, apply_function, win):
    """Handle color selection from GTK4 ColorDialog"""
    try:
        rgba = dialog.choose_rgba_finish(result)
        if rgba:
            # Convert to hex color
            hex_color = f"#{int(rgba.red * 255):02x}{int(rgba.green * 255):02x}{int(rgba.blue * 255):02x}"
            color_button.current_color = hex_color
            
            # Update color display
            color_display = color_button.get_child()
            if color_display:
                color_display.queue_draw()
            
            # Apply the color
            apply_function(win, hex_color)
    except Exception as e:
        print(f"Error choosing color: {e}")

def _on_color_dialog_response(self, dialog, response, color_button, apply_function, win):
    """Handle response from ColorChooserDialog"""
    if response == Gtk.ResponseType.OK:
        try:
            rgba = dialog.get_rgba()
            hex_color = f"#{int(rgba.red * 255):02x}{int(rgba.green * 255):02x}{int(rgba.blue * 255):02x}"
            color_button.current_color = hex_color
            
            # Update color display
            color_display = color_button.get_child()
            if color_display:
                color_display.queue_draw()
            
            # Apply the color
            apply_function(win, hex_color)
        except Exception as e:
            print(f"Error getting color: {e}")
    
    dialog.destroy()

def _apply_border_color(self, win, hex_color):
    """Apply border color"""
    try:
        print(f"Applying border color: {hex_color}")  # Debug print
        
        js_code = f"""
        (function() {{
            if (!activeTable) return false;
            
            // Apply the color to all cells' borders
            const cells = activeTable.querySelectorAll('td, th');
            cells.forEach(cell => {{
                cell.style.borderColor = '{hex_color}';
            }});
            
            // Store the color for theme preservation
            activeTable.setAttribute('data-border-color', '{hex_color}');
            
            // Debug output
            console.log('Applied border color:', '{hex_color}');
            
            // Notify that content changed
            try {{
                window.webkit.messageHandlers.contentChanged.postMessage('changed');
            }} catch(e) {{
                console.log("Could not notify about content change:", e);
            }}
            
            return true;
        }})();
        """
        self.execute_js(win, js_code)
        win.statusbar.set_text(f"Applied border color: {hex_color}")
    except Exception as e:
        print(f"Error applying border color: {e}")
        win.statusbar.set_text("Error applying border color")

def _apply_table_color(self, win, hex_color):
    """Apply table background color"""
    try:
        print(f"Applying table color: {hex_color}")  # Debug print
        
        js_code = f"""
        (function() {{
            if (!activeTable) return false;
            
            // Apply the color
            activeTable.style.backgroundColor = '{hex_color}';
            
            // Store the color for theme preservation
            activeTable.setAttribute('data-bg-color', '{hex_color}');
            
            // Debug output
            console.log('Applied table color:', '{hex_color}');
            
            // Notify that content changed
            try {{
                window.webkit.messageHandlers.contentChanged.postMessage('changed');
            }} catch(e) {{
                console.log("Could not notify about content change:", e);
            }}
            
            return true;
        }})();
        """
        self.execute_js(win, js_code)
        win.statusbar.set_text(f"Applied table color: {hex_color}")
    except Exception as e:
        print(f"Error applying table color: {e}")
        win.statusbar.set_text("Error applying table color")

def _apply_header_color(self, win, hex_color):
    """Apply header background color"""
    try:
        print(f"Applying header color: {hex_color}")  # Debug print
        
        js_code = f"""
        (function() {{
            if (!activeTable) return false;
            
            // Apply the color to all header cells
            const headers = activeTable.querySelectorAll('th');
            headers.forEach(header => {{
                header.style.backgroundColor = '{hex_color}';
            }});
            
            // Store the color for theme preservation
            activeTable.setAttribute('data-header-color', '{hex_color}');
            
            // Debug output
            console.log('Applied header color:', '{hex_color}');
            
            // Notify that content changed
            try {{
                window.webkit.messageHandlers.contentChanged.postMessage('changed');
            }} catch(e) {{
                console.log("Could not notify about content change:", e);
            }}
            
            return true;
        }})();
        """
        self.execute_js(win, js_code)
        win.statusbar.set_text(f"Applied header color: {hex_color}")
    except Exception as e:
        print(f"Error applying header color: {e}")
        win.statusbar.set_text("Error applying header color")

def _apply_cell_color(self, win, hex_color):
    """Apply cell background color"""
    try:
        print(f"Applying cell color: {hex_color}")  # Debug print
        
        js_code = f"""
        (function() {{
            if (!activeTable) return false;
            
            // Get the current selection
            const selection = window.getSelection();
            if (!selection.rangeCount) return false;
            
            // Find the active cell
            let activeCell = selection.anchorNode;
            
            // If the selection is in a text node, get the parent element
            if (activeCell.nodeType === Node.TEXT_NODE) {{
                activeCell = activeCell.parentElement;
            }}
            
            // Find the closest td or th element
            while (activeCell && activeCell.tagName !== 'TD' && activeCell.tagName !== 'TH') {{
                activeCell = activeCell.parentElement;
            }}
            
            // If we found a cell and it belongs to our active table
            if (activeCell && activeTable.contains(activeCell)) {{
                activeCell.style.backgroundColor = '{hex_color}';
                
                // Store the color on the cell itself
                activeCell.setAttribute('data-cell-color', '{hex_color}');
                
                // Debug output
                console.log('Applied cell color:', '{hex_color}');
                
                // Notify that content changed
                try {{
                    window.webkit.messageHandlers.contentChanged.postMessage('changed');
                }} catch(e) {{
                    console.log("Could not notify about content change:", e);
                }}
                
                return true;
            }}
            
            return false;
        }})();
        """
        self.execute_js(win, js_code)
        win.statusbar.set_text(f"Applied cell color: {hex_color}")
    except Exception as e:
        print(f"Error applying cell color: {e}")
        win.statusbar.set_text("Error applying cell color")

def _apply_row_color(self, win, hex_color):
    """Apply row background color"""
    try:
        print(f"Applying row color: {hex_color}")  # Debug print
        
        js_code = f"""
        (function() {{
            if (!activeTable) return false;
            
            // Apply row color
            setRowBackgroundColor('{hex_color}');
            
            return true;
        }})();
        """
        self.execute_js(win, js_code)
        win.statusbar.set_text(f"Applied row color: {hex_color}")
    except Exception as e:
        print(f"Error applying row color: {e}")
        win.statusbar.set_text("Error applying row color")

def _apply_column_color(self, win, hex_color):
    """Apply column background color"""
    try:
        print(f"Applying column color: {hex_color}")  # Debug print
        
        js_code = f"""
        (function() {{
            if (!activeTable) return false;
            
            // Apply column color
            setColumnBackgroundColor('{hex_color}');
            
            return true;
        }})();
        """
        self.execute_js(win, js_code)
        win.statusbar.set_text(f"Applied column color: {hex_color}")
    except Exception as e:
        print(f"Error applying column color: {e}")
        win.statusbar.set_text("Error applying column color")

def _reset_default_colors(self, win):
    """Reset table colors to default values"""
    js_code = """
    (function() {
        if (!activeTable) return false;
        
        // Get default colors based on theme
        const borderColor = getBorderColor();
        const headerBgColor = getHeaderBgColor();
        
        // Reset border color
        setTableBorderColor(borderColor);
        
        // Reset table background color
        activeTable.style.backgroundColor = '';
        activeTable.removeAttribute('data-bg-color');
        
        // Reset header color
        const headers = activeTable.querySelectorAll('th');
        headers.forEach(header => {
            header.style.backgroundColor = headerBgColor;
        });
        activeTable.setAttribute('data-header-color', headerBgColor);
        
        // Reset all cell colors
        const cells = activeTable.querySelectorAll('td');
        cells.forEach(cell => {
            cell.style.backgroundColor = '';
            cell.removeAttribute('data-cell-color');
        });
        
        // Notify that content changed
        try {
            window.webkit.messageHandlers.contentChanged.postMessage('changed');
        } catch(e) {
            console.log("Could not notify about content change:", e);
        }
        
        return JSON.stringify({
            border: borderColor,
            header: headerBgColor
        });
    })();
    """
    
    # Execute the reset and update color buttons
    win.webview.evaluate_javascript(
        js_code,
        -1, None, None, None,
        lambda webview, result, data: self._update_color_buttons_after_reset(webview, result, win),
        None
    )
    
    win.statusbar.set_text("Reset to default colors")

# 2. Helper method to update color buttons after reset
def _update_color_buttons_after_reset(self, webview, result, win):
    """Update color buttons after resetting to defaults"""
    try:
        js_result = webview.evaluate_javascript_finish(result)
        if js_result:
            result_str = js_result.to_string() if hasattr(js_result, 'to_string') else str(js_result)
            import json
            colors = json.loads(result_str)
            
            # Update color buttons if they exist in the current context
            for child in win.main_box:
                if isinstance(child, Gtk.Popover):
                    content = child.get_child()
                    if content and isinstance(content, Gtk.Box):
                        for widget in content:
                            if isinstance(widget, Gtk.Notebook):
                                color_page = widget.get_nth_page(2)  # Color tab
                                if color_page:
                                    # Update border color button
                                    if hasattr(color_page, 'border_color_button'):
                                        rgba = self._parse_color_string(colors['border'])
                                        if rgba:
                                            color_page.border_color_button.set_rgba(rgba)
                                    
                                    # Clear other color buttons
                                    if hasattr(color_page, 'table_color_button'):
                                        rgba = Gdk.RGBA()
                                        rgba.parse('#ffffff')
                                        color_page.table_color_button.set_rgba(rgba)
                                    
                                    if hasattr(color_page, 'header_color_button'):
                                        rgba = self._parse_color_string(colors['header'])
                                        if rgba:
                                            color_page.header_color_button.set_rgba(rgba)
                                    
                                    if hasattr(color_page, 'cell_color_button'):
                                        rgba = Gdk.RGBA()
                                        rgba.parse('#ffffff')
                                        color_page.cell_color_button.set_rgba(rgba)
    except Exception as e:
        print(f"Error updating color buttons: {e}")


def on_border_display_option_clicked(self, win, popover, width_spin, option):
    """Apply the selected border display option while preserving style and width"""
    js_code = f"""
    (function() {{
        // Get current border properties
        const currentStyle = getTableBorderStyle();
        let style = currentStyle ? currentStyle.style : 'solid';
        let width = currentStyle ? currentStyle.width : {width_spin.get_value()};
        let color = currentStyle ? currentStyle.color : getBorderColor();
        
        // Ensure we have valid values
        if (!style || style === 'none') {{
            style = 'solid';
        }}
        
        // First apply the current style, width, and color
        setTableBorderStyle(style, width, color);
        
        // Then apply the border option
        applyTableBorderSides(['{option}']);
        
        return true;
    }})();
    """
    win.webview.evaluate_javascript(js_code, -1, None, None, None, None, None)
    
    # Update status message
    win.statusbar.set_text(f"Applied {option} borders")
    
    # Close the popover if provided
    if popover:
        popover.popdown()
        
def _apply_combined_borders(self, win, width_spin, border_types):
    """Apply combined border options while preserving properties"""
    border_types_js = str(border_types).replace("'", '"')
    
    js_code = f"""
    (function() {{
        // Get current border properties
        const currentStyle = getTableBorderStyle();
        let style = currentStyle ? currentStyle.style : 'solid';
        let width = currentStyle ? currentStyle.width : {width_spin.get_value()};
        let color = currentStyle ? currentStyle.color : getBorderColor();
        
        // Ensure we have valid values
        if (!style || style === 'none') {{
            style = 'solid';
        }}
        
        // First apply the current style, width, and color
        setTableBorderStyle(style, width, color);
        
        // Then apply the combined border options
        applyTableBorderSides({border_types_js});
        
        return true;
    }})();
    """
    win.webview.evaluate_javascript(js_code, -1, None, None, None, None, None)
    
    # Update status message
    border_text = " + ".join(border_types)
    win.statusbar.set_text(f"Applied {border_text} borders")
    
    
#############
def on_border_width_changed(self, win, style, width):
    """Apply border width change immediately while preserving other properties and border display"""
    # Execute JavaScript to apply the border width while preserving style and display option
    js_code = f"""
    (function() {{
        // Get current border properties first
        const currentStyle = getTableBorderStyle();
        const currentBorderStyle = currentStyle ? currentStyle.style : '{style}';
        const currentColor = currentStyle ? currentStyle.color : getBorderColor();
        
        // Apply with preserved values
        setTableBorderStyle(currentBorderStyle, {width}, currentColor);
        
        // Re-apply the current border option
        const borderOption = activeTable ? (activeTable.getAttribute('data-border-option') || 'all') : 'all';
        
        // Handle JSON array format for combined options
        if (borderOption.startsWith('[')) {{
            try {{
                const parsedOption = JSON.parse(borderOption);
                applyTableBorderSides(parsedOption);
            }} catch(e) {{
                console.error("Error parsing border option:", e);
                applyTableBorderSides(['all']);
            }}
        }} else {{
            // Simple string option
            applyTableBorderSides([borderOption]);
        }}
        
        return true;
    }})();
    """
    win.webview.evaluate_javascript(js_code, -1, None, None, None, None, None)
    
    # Update status message
    win.statusbar.set_text(f"Applied {width}px border width")
        
def on_border_display_option_clicked(self, win, popover, width_spin, option):
    """Apply the selected border display option while preserving style and width"""
    js_code = f"""
    (function() {{
        // Get current border properties
        const currentStyle = getTableBorderStyle();
        let style = currentStyle ? currentStyle.style : 'solid';
        let width = currentStyle ? currentStyle.width : {width_spin.get_value()};
        let color = currentStyle ? currentStyle.color : getBorderColor();
        
        // Ensure we have valid values
        if (!style || style === 'none') {{
            style = 'solid';
        }}
        
        // First apply the current style, width, and color
        setTableBorderStyle(style, width, color);
        
        // Then apply the border option
        applyTableBorderSides(['{option}']);
        
        // Store the selected border option for future reference
        if (activeTable) {{
            activeTable.setAttribute('data-border-option', '{option}');
        }}
        
        return true;
    }})();
    """
    win.webview.evaluate_javascript(js_code, -1, None, None, None, None, None)
    
    # Update status message
    win.statusbar.set_text(f"Applied {option} borders")
    
    # Close the popover if provided
    if popover:
        popover.popdown()
        
# Z-index control handlers
def on_bring_forward_clicked(self, win, btn):
    """Bring the selected element forward in the z-order"""
    js_code = "bringElementForward();"
    self.execute_js(win, js_code)
    win.statusbar.set_text("Element brought forward")

def on_send_backward_clicked(self, win, btn):
    """Send the selected element backward in the z-order"""
    js_code = "sendElementBackward();"
    self.execute_js(win, js_code)
    win.statusbar.set_text("Element sent backward")


