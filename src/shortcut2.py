#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GObject

class ShortcutsWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_default_size(800, 600)
        self.set_title("Shortcuts")
        
        # Create header bar
        self.header_bar = Adw.HeaderBar()
        self.set_content(Gtk.Box(orientation=Gtk.Orientation.VERTICAL))
        self.get_content().append(self.header_bar)
        
        # Search button
        self.search_button = Gtk.ToggleButton()
        self.search_button.set_icon_name("system-search-symbolic")
        self.search_button.connect("toggled", self.on_search_toggled)
        self.header_bar.pack_start(self.search_button)
        
        # Close button
        close_button = Gtk.Button()
        close_button.set_icon_name("window-close-symbolic")
        close_button.connect("clicked", lambda x: self.close())
        self.header_bar.pack_end(close_button)
        
        # Main content
        self.setup_main_content()
        
        # Current page
        self.current_page = 0
        self.all_shortcuts = self.get_all_shortcuts()
        self.show_page(0)
    
    def setup_main_content(self):
        # Get the main content box
        main_box = self.get_content()
        
        # Search bar (initially hidden)
        self.search_bar = Gtk.SearchBar()
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search Shortcuts")
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.search_bar.set_child(self.search_entry)
        main_box.append(self.search_bar)
        
        # Content area with margins - matching original spacing
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(32)
        content_box.set_margin_end(32)
        content_box.set_spacing(24)  # Reduced spacing between groups
        main_box.append(content_box)
        
        # Scrolled window for shortcuts
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        content_box.append(scrolled)
        
        # Stack for different pages
        self.stack = Gtk.Stack()
        scrolled.set_child(self.stack)
        
        # Create pages
        self.create_page_1()
        self.create_page_2()
        self.create_page_3()
        self.create_page_4()
        
        # Page indicator
        page_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        page_box.set_halign(Gtk.Align.CENTER)
        page_box.set_spacing(8)
        content_box.append(page_box)
        
        self.page_buttons = []
        for i in range(4):
            btn = Gtk.Button(label=str(i + 1))
            btn.add_css_class("circular")
            btn.connect("clicked", lambda x, page=i: self.show_page(page))
            page_box.append(btn)
            self.page_buttons.append(btn)
    
    def create_shortcut_group(self, title, shortcuts):
        """Create a group of shortcuts with proper styling"""
        group_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        group_box.set_spacing(4)
        
        # Group title
        title_label = Gtk.Label(label=title)
        title_label.set_halign(Gtk.Align.START)
        title_label.add_css_class("group-title")
        title_label.set_margin_bottom(8)
        group_box.append(title_label)
        
        # Shortcuts list
        for shortcut in shortcuts:
            shortcut_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            shortcut_box.set_spacing(24)  # Increased spacing between keys and description
            shortcut_box.add_css_class("shortcut-row")
            
            # Key combination - fixed width container for alignment like original
            key_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            key_container.set_size_request(220, -1)  # Increased width for better alignment
            key_container.set_halign(Gtk.Align.START)
            key_container.add_css_class("shortcut-keys")
            
            key_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            key_box.set_spacing(6)  # Slightly more spacing between keys
            key_box.set_halign(Gtk.Align.START)
            
            for i, key in enumerate(shortcut['keys']):
                if i > 0:
                    plus_label = Gtk.Label(label="+")
                    plus_label.set_margin_start(6)
                    plus_label.set_margin_end(6)
                    plus_label.add_css_class("shortcut-description")
                    key_box.append(plus_label)
                
                key_label = Gtk.Label(label=key)
                key_label.add_css_class("mycutebutton")
                key_box.append(key_label)
            
            key_container.append(key_box)
            shortcut_box.append(key_container)
            
            # Description - properly aligned
            desc_label = Gtk.Label(label=shortcut['description'])
            desc_label.set_halign(Gtk.Align.START)
            desc_label.set_valign(Gtk.Align.CENTER)
            desc_label.set_hexpand(True)
            desc_label.add_css_class("shortcut-description")
            shortcut_box.append(desc_label)
            
            group_box.append(shortcut_box)
        
        return group_box
    
    def create_page_1(self):
        """Create first page with Undo/Redo and Line Spacing"""
        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page_box.set_spacing(24)
        
        # Undo and Redo section
        undo_shortcuts = [
            {'keys': ['Ctrl', 'Z'], 'description': 'Undo'},
            {'keys': ['Shift', 'Ctrl', 'Z'], 'description': 'Redo'},
            {'keys': ['Ctrl', 'Y'], 'description': 'Redo Alt'},
        ]
        page_box.append(self.create_shortcut_group("Undo and Redo", undo_shortcuts))
        
        # Line Spacing section
        spacing_shortcuts = [
            {'keys': ['Ctrl', '1'], 'description': 'Single Spacing'},
            {'keys': ['Ctrl', '5'], 'description': '1.5 Spacing'},
            {'keys': ['Ctrl', '2'], 'description': 'Double Spacing'},
            {'keys': ['Shift', 'Ctrl', '0'], 'description': 'Default Spacing'},
        ]
        page_box.append(self.create_shortcut_group("Line Spacing", spacing_shortcuts))
        
        self.stack.add_titled(page_box, "page1", "Page 1")
    
    def create_page_2(self):
        """Create second page with Interface shortcuts"""
        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page_box.set_spacing(24)
        
        # Interface section
        interface_shortcuts = [
            {'keys': ['Alt', 'F'], 'description': 'Toggle File Toolbar'},
            {'keys': ['Alt', 'H'], 'description': 'Toggle Header Bar'},
            {'keys': ['Alt', 'S'], 'description': 'Toggle Status Bar'},
            {'keys': ['Alt', 'T'], 'description': 'Toggle Format Toolbar'},
            {'keys': ['Alt', 'P'], 'description': 'Page Options'},
        ]
        page_box.append(self.create_shortcut_group("Interface", interface_shortcuts))
        
        self.stack.add_titled(page_box, "page2", "Page 2")
    
    def create_page_3(self):
        """Create third page with Text Formatting and Clipboard"""
        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page_box.set_spacing(24)
        
        # Text Formatting section
        format_shortcuts = [
            {'keys': ['Ctrl', 'B'], 'description': 'Bold'},
            {'keys': ['Ctrl', 'I'], 'description': 'Italic'},
            {'keys': ['Ctrl', 'U'], 'description': 'Underline'},
            {'keys': ['Shift', 'Ctrl', 'X'], 'description': 'Strikeout'},
            {'keys': ['Shift', 'Ctrl', '='], 'description': 'Superscript'},
            {'keys': ['Shift', 'Ctrl', '-'], 'description': 'Subscript'},
        ]
        page_box.append(self.create_shortcut_group("Text Formatting", format_shortcuts))
        
        # Clipboard section
        clipboard_shortcuts = [
            {'keys': ['Ctrl', 'C'], 'description': 'Copy'},
            {'keys': ['Ctrl', 'X'], 'description': 'Cut'},
            {'keys': ['Ctrl', 'V'], 'description': 'Paste'},
            {'keys': ['Ctrl', 'A'], 'description': 'Select All'},
        ]
        page_box.append(self.create_shortcut_group("Clipboard", clipboard_shortcuts))
        
        self.stack.add_titled(page_box, "page3", "Page 3")
    
    def create_page_4(self):
        """Create fourth page with Find/Replace and Zoom"""
        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page_box.set_spacing(24)
        
        # Find and Replace section
        find_shortcuts = [
            {'keys': ['Ctrl', 'F'], 'description': 'Find'},
            {'keys': ['Ctrl', 'H'], 'description': 'Find and Replace'},
        ]
        page_box.append(self.create_shortcut_group("Find and Replace", find_shortcuts))
        
        # Zoom section
        zoom_shortcuts = [
            {'keys': ['Ctrl', '='], 'description': 'Zoom In'},
            {'keys': ['Ctrl', '-'], 'description': 'Zoom Out'},
            {'keys': ['Ctrl', '0'], 'description': 'Reset Zoom'},
        ]
        page_box.append(self.create_shortcut_group("Zoom", zoom_shortcuts))
        
        self.stack.add_titled(page_box, "page4", "Page 4")
    
    def show_page(self, page_num):
        """Show the specified page and update page indicators"""
        pages = ["page1", "page2", "page3", "page4"]
        if 0 <= page_num < len(pages):
            self.stack.set_visible_child_name(pages[page_num])
            self.current_page = page_num
            
            # Update page button styles
            for i, btn in enumerate(self.page_buttons):
                if i == page_num:
                    btn.add_css_class("suggested-action")
                else:
                    btn.remove_css_class("suggested-action")
    
    def on_search_toggled(self, button):
        """Toggle search bar visibility"""
        is_active = button.get_active()
        self.search_bar.set_search_mode(is_active)
        if is_active:
            self.search_entry.grab_focus()
        else:
            self.search_entry.set_text("")
            self.show_page(self.current_page)  # Reset to current page
    
    def get_all_shortcuts(self):
        """Get all shortcuts data for searching"""
        return {
            'Undo and Redo': [
                {'keys': ['Ctrl', 'Z'], 'description': 'Undo'},
                {'keys': ['Shift', 'Ctrl', 'Z'], 'description': 'Redo'},
                {'keys': ['Ctrl', 'Y'], 'description': 'Redo Alt'},
            ],
            'Line Spacing': [
                {'keys': ['Ctrl', '1'], 'description': 'Single Spacing'},
                {'keys': ['Ctrl', '5'], 'description': '1.5 Spacing'},
                {'keys': ['Ctrl', '2'], 'description': 'Double Spacing'},
                {'keys': ['Shift', 'Ctrl', '0'], 'description': 'Default Spacing'},
            ],
            'Interface': [
                {'keys': ['Alt', 'F'], 'description': 'Toggle File Toolbar'},
                {'keys': ['Alt', 'H'], 'description': 'Toggle Header Bar'},
                {'keys': ['Alt', 'S'], 'description': 'Toggle Status Bar'},
                {'keys': ['Alt', 'T'], 'description': 'Toggle Format Toolbar'},
                {'keys': ['Alt', 'P'], 'description': 'Page Options'},
            ],
            'Text Formatting': [
                {'keys': ['Ctrl', 'B'], 'description': 'Bold'},
                {'keys': ['Ctrl', 'I'], 'description': 'Italic'},
                {'keys': ['Ctrl', 'U'], 'description': 'Underline'},
                {'keys': ['Shift', 'Ctrl', 'X'], 'description': 'Strikeout'},
                {'keys': ['Shift', 'Ctrl', '='], 'description': 'Superscript'},
                {'keys': ['Shift', 'Ctrl', '-'], 'description': 'Subscript'},
            ],
            'Clipboard': [
                {'keys': ['Ctrl', 'C'], 'description': 'Copy'},
                {'keys': ['Ctrl', 'X'], 'description': 'Cut'},
                {'keys': ['Ctrl', 'V'], 'description': 'Paste'},
                {'keys': ['Ctrl', 'A'], 'description': 'Select All'},
            ],
            'Find and Replace': [
                {'keys': ['Ctrl', 'F'], 'description': 'Find'},
                {'keys': ['Ctrl', 'H'], 'description': 'Find and Replace'},
            ],
            'Zoom': [
                {'keys': ['Ctrl', '='], 'description': 'Zoom In'},
                {'keys': ['Ctrl', '-'], 'description': 'Zoom Out'},
                {'keys': ['Ctrl', '0'], 'description': 'Reset Zoom'},
            ],
            'Navigation': [
                {'keys': ['Ctrl', 'Home'], 'description': 'Go to Beginning'},
                {'keys': ['Ctrl', 'End'], 'description': 'Go to End'},
                {'keys': ['Ctrl', 'G'], 'description': 'Go to Line'},
            ],
            'File Operations': [
                {'keys': ['Ctrl', 'N'], 'description': 'New Document'},
                {'keys': ['Ctrl', 'O'], 'description': 'Open Document'},
                {'keys': ['Ctrl', 'S'], 'description': 'Save Document'},
                {'keys': ['Ctrl', 'Shift', 'S'], 'description': 'Save As'},
            ]
        }
    
    def on_search_changed(self, entry):
        """Handle search text changes"""
        search_text = entry.get_text().lower().strip()
        
        if not search_text:
            # If search is empty, show current page
            self.show_page(self.current_page)
            return
        
        # Filter shortcuts based on search text
        filtered_groups = {}
        for group_name, shortcuts in self.all_shortcuts.items():
            filtered_shortcuts = []
            for shortcut in shortcuts:
                # Search in description and key combinations
                desc_match = search_text in shortcut['description'].lower()
                key_match = any(search_text in key.lower() for key in shortcut['keys'])
                
                if desc_match or key_match:
                    filtered_shortcuts.append(shortcut)
            
            if filtered_shortcuts:
                filtered_groups[group_name] = filtered_shortcuts
        
        # Show filtered results
        self.show_search_results(filtered_groups)
    
    def show_search_results(self, filtered_groups):
        """Display search results"""
        # Create search results page
        search_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        search_box.set_spacing(32)
        
        if not filtered_groups:
            # No results found
            no_results = Gtk.Label(label="No shortcuts found")
            no_results.set_halign(Gtk.Align.CENTER)
            no_results.add_css_class("dim-label")
            search_box.append(no_results)
        else:
            # Show filtered results
            for group_name, shortcuts in filtered_groups.items():
                group_widget = self.create_shortcut_group(group_name, shortcuts)
                search_box.append(group_widget)
        
        # Remove existing search page if it exists
        search_page = self.stack.get_child_by_name("search")
        if search_page:
            self.stack.remove(search_page)
        
        # Add new search results
        self.stack.add_named(search_box, "search")
        self.stack.set_visible_child_name("search")

class ShortcutsApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
    
    def on_activate(self, app):
        # Create window first
        self.win = ShortcutsWindow(application=self)
        
        # Load custom CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data("""
            .mycutebutton {
                background: white;
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
                color: #2e2e2e;
                padding: 6px 12px;
                margin: 2px;
                font-family: sans-serif;
                font-size: 0.9em;
                min-width: 24px;
                min-height: 24px;
            }
            
            window {
                background: #fafafa;
            }
            
            headerbar {
                background: #fafafa;
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            }
            
            searchbar {
                background: #fafafa;
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            }
            
            .shortcut-row {
                padding: 8px 0;
            }
            
            .shortcut-keys {
                min-width: 220px;
            }
            
            .group-title {
                font-weight: bold;
                font-size: 1.1em;
                margin-bottom: 12px;
                color: #2e2e2e;
            }
            
            .shortcut-description {
                color: #2e2e2e;
                font-size: 0.95em;
            }
        """.encode())
        
        Gtk.StyleContext.add_provider_for_display(
            self.win.get_display(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        self.win.present()

def main():
    app = ShortcutsApp(application_id="com.example.shortcuts")
    return app.run()

if __name__ == '__main__':
    main()
