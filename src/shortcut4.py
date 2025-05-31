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
        
        # Create header bar without line
        self.header_bar = Adw.HeaderBar()
        self.header_bar.set_title_widget(Gtk.Label(label="Shortcuts"))
        self.set_content(Gtk.Box(orientation=Gtk.Orientation.VERTICAL))
        self.get_content().append(self.header_bar)
        
        # Search button
        self.search_button = Gtk.ToggleButton()
        self.search_button.set_icon_name("system-search-symbolic")
        self.search_button.connect("toggled", self.on_search_toggled)
        self.header_bar.pack_start(self.search_button)
        
        # Close button (only one)
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
        
        # Content area with reduced margins to match original
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(16)
        content_box.set_margin_start(32)
        content_box.set_margin_end(32)
        content_box.set_spacing(24)
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
        
        # Page indicator with smaller buttons
        page_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        page_box.set_halign(Gtk.Align.CENTER)
        page_box.set_spacing(4)
        page_box.set_margin_top(16)
        content_box.append(page_box)
        
        self.page_buttons = []
        for i in range(4):
            btn = Gtk.Button(label=str(i + 1))
            btn.add_css_class("page-indicator")
            btn.connect("clicked", lambda x, page=i: self.show_page(page))
            page_box.append(btn)
            self.page_buttons.append(btn)
    
    def create_two_column_layout(self, left_group, right_group):
        """Create a two-column layout for shortcut groups"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.set_spacing(48)
        main_box.set_homogeneous(True)
        
        # Left column
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_box.set_spacing(24)
        if left_group:
            left_box.append(left_group)
        main_box.append(left_box)
        
        # Right column
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_box.set_spacing(24)
        if right_group:
            right_box.append(right_group)
        main_box.append(right_box)
        
        return main_box
    
    def create_shortcut_group(self, title, shortcuts):
        """Create a group of shortcuts with horizontal layout (text beside buttons)"""
        group_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        group_box.set_spacing(12)
        
        # Group title
        title_label = Gtk.Label(label=title)
        title_label.set_halign(Gtk.Align.START)
        title_label.add_css_class("group-title")
        group_box.append(title_label)
        
        # Shortcuts list
        for shortcut in shortcuts:
            # Horizontal layout: keys on left, description on right
            shortcut_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            shortcut_box.set_spacing(12)
            shortcut_box.add_css_class("shortcut-row")
            
            # Key combination container
            key_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            key_box.set_spacing(4)
            key_box.set_halign(Gtk.Align.START)
            key_box.set_valign(Gtk.Align.CENTER)
            
            for i, key in enumerate(shortcut['keys']):
                if i > 0:
                    plus_label = Gtk.Label(label="+")
                    plus_label.add_css_class("key-separator")
                    key_box.append(plus_label)
                
                key_label = Gtk.Label(label=key)
                key_label.add_css_class("key-button")
                key_box.append(key_label)
            
            shortcut_box.append(key_box)
            
            # Description beside the keys
            desc_label = Gtk.Label(label=shortcut['description'])
            desc_label.set_halign(Gtk.Align.START)
            desc_label.set_valign(Gtk.Align.CENTER)
            desc_label.add_css_class("shortcut-description")
            shortcut_box.append(desc_label)
            
            group_box.append(shortcut_box)
        
        return group_box
    
    def create_page_1(self):
        """Create first page with Undo/Redo and Line Spacing in two columns"""
        # Undo and Redo section
        undo_shortcuts = [
            {'keys': ['Ctrl', 'Z'], 'description': 'Undo'},
            {'keys': ['Shift', 'Ctrl', 'Z'], 'description': 'Redo'},
            {'keys': ['Ctrl', 'Y'], 'description': 'Redo Alt'},
        ]
        undo_group = self.create_shortcut_group("Undo and Redo", undo_shortcuts)
        
        # Line Spacing section
        spacing_shortcuts = [
            {'keys': ['Ctrl', '1'], 'description': 'Single Spacing'},
            {'keys': ['Ctrl', '5'], 'description': '1.5 Spacing'},
            {'keys': ['Ctrl', '2'], 'description': 'Double Spacing'},
            {'keys': ['Shift', 'Ctrl', '0'], 'description': 'Default Spacing'},
        ]
        spacing_group = self.create_shortcut_group("Line Spacing", spacing_shortcuts)
        
        page_layout = self.create_two_column_layout(undo_group, spacing_group)
        self.stack.add_titled(page_layout, "page1", "Page 1")
    
    def create_page_2(self):
        """Create second page with Interface shortcuts"""
        interface_shortcuts = [
            {'keys': ['Alt', 'F'], 'description': 'Toggle File Toolbar'},
            {'keys': ['Alt', 'H'], 'description': 'Toggle Header Bar'},
            {'keys': ['Alt', 'S'], 'description': 'Toggle Status Bar'},
            {'keys': ['Alt', 'T'], 'description': 'Toggle Format Toolbar'},
            {'keys': ['Alt', 'P'], 'description': 'Page Options'},
        ]
        interface_group = self.create_shortcut_group("Interface", interface_shortcuts)
        
        page_layout = self.create_two_column_layout(interface_group, None)
        self.stack.add_titled(page_layout, "page2", "Page 2")
    
    def create_page_3(self):
        """Create third page with Text Formatting and Clipboard in two columns"""
        # Text Formatting section
        format_shortcuts = [
            {'keys': ['Ctrl', 'B'], 'description': 'Bold'},
            {'keys': ['Ctrl', 'I'], 'description': 'Italic'},
            {'keys': ['Ctrl', 'U'], 'description': 'Underline'},
            {'keys': ['Shift', 'Ctrl', 'X'], 'description': 'Strikeout'},
            {'keys': ['Shift', 'Ctrl', '='], 'description': 'Superscript'},
            {'keys': ['Shift', 'Ctrl', '-'], 'description': 'Subscript'},
        ]
        format_group = self.create_shortcut_group("Text Formatting", format_shortcuts)
        
        # Clipboard section
        clipboard_shortcuts = [
            {'keys': ['Ctrl', 'C'], 'description': 'Copy'},
            {'keys': ['Ctrl', 'X'], 'description': 'Cut'},
            {'keys': ['Ctrl', 'V'], 'description': 'Paste'},
            {'keys': ['Ctrl', 'A'], 'description': 'Select All'},
        ]
        clipboard_group = self.create_shortcut_group("Clipboard", clipboard_shortcuts)
        
        page_layout = self.create_two_column_layout(format_group, clipboard_group)
        self.stack.add_titled(page_layout, "page3", "Page 3")
    
    def create_page_4(self):
        """Create fourth page with Find/Replace and Zoom in two columns"""
        # Find and Replace section
        find_shortcuts = [
            {'keys': ['Ctrl', 'F'], 'description': 'Find'},
            {'keys': ['Ctrl', 'H'], 'description': 'Find and Replace'},
        ]
        find_group = self.create_shortcut_group("Find and Replace", find_shortcuts)
        
        # Zoom section
        zoom_shortcuts = [
            {'keys': ['Ctrl', '='], 'description': 'Zoom In'},
            {'keys': ['Ctrl', '-'], 'description': 'Zoom Out'},
            {'keys': ['Ctrl', '0'], 'description': 'Reset Zoom'},
        ]
        zoom_group = self.create_shortcut_group("Zoom", zoom_shortcuts)
        
        page_layout = self.create_two_column_layout(find_group, zoom_group)
        self.stack.add_titled(page_layout, "page4", "Page 4")
    
    def show_page(self, page_num):
        """Show the specified page and update page indicators"""
        pages = ["page1", "page2", "page3", "page4"]
        if 0 <= page_num < len(pages):
            self.stack.set_visible_child_name(pages[page_num])
            self.current_page = page_num
            
            # Update page button styles
            for i, btn in enumerate(self.page_buttons):
                if i == page_num:
                    btn.add_css_class("active-page")
                else:
                    btn.remove_css_class("active-page")
    
    def on_search_toggled(self, button):
        """Toggle search bar visibility"""
        is_active = button.get_active()
        self.search_bar.set_search_mode(is_active)
        if is_active:
            self.search_entry.grab_focus()
        else:
            self.search_entry.set_text("")
            self.show_page(self.current_page)
    
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
        }
    
    def on_search_changed(self, entry):
        """Handle search text changes"""
        search_text = entry.get_text().lower().strip()
        
        if not search_text:
            self.show_page(self.current_page)
            return
        
        # Filter shortcuts based on search text
        filtered_groups = {}
        for group_name, shortcuts in self.all_shortcuts.items():
            filtered_shortcuts = []
            for shortcut in shortcuts:
                desc_match = search_text in shortcut['description'].lower()
                key_match = any(search_text in key.lower() for key in shortcut['keys'])
                
                if desc_match or key_match:
                    filtered_shortcuts.append(shortcut)
            
            if filtered_shortcuts:
                filtered_groups[group_name] = filtered_shortcuts
        
        self.show_search_results(filtered_groups)
    
    def show_search_results(self, filtered_groups):
        """Display search results"""
        search_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        search_box.set_spacing(24)
        
        if not filtered_groups:
            no_results = Gtk.Label(label="No shortcuts found")
            no_results.set_halign(Gtk.Align.CENTER)
            no_results.add_css_class("dim-label")
            search_box.append(no_results)
        else:
            for group_name, shortcuts in filtered_groups.items():
                group_widget = self.create_shortcut_group(group_name, shortcuts)
                search_box.append(group_widget)
        
        search_page = self.stack.get_child_by_name("search")
        if search_page:
            self.stack.remove(search_page)
        
        self.stack.add_named(search_box, "search")
        self.stack.set_visible_child_name("search")

class ShortcutsApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
    
    def on_activate(self, app):
        self.win = ShortcutsWindow(application=self)
        
        # Load custom CSS to exactly match the image
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data("""
            window {
                background: white;
            }
            
            headerbar {
                background: #fafafa;
                border: none;
                box-shadow: none;
            }
            
            searchbar {
                background: #fafafa;
                border: none;
            }
            
            .key-button {
                background: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
                color: #333;
                padding: 2px 8px;
                margin: 0 1px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
                font-size: 12px;
                font-weight: 400;
                min-width: 20px;
                min-height: 20px;
            }
            
            .key-separator {
                color: #666;
                font-size: 12px;
                margin: 0 3px;
                font-weight: 400;
            }
            
            .shortcut-row {
                margin: 4px 0;
                min-height: 28px;
            }
            
            .group-title {
                font-weight: 600;
                font-size: 14px;
                color: #1a1a1a;
                margin-bottom: 8px;
            }
            
            .shortcut-description {
                color: #333;
                font-size: 13px;
                font-weight: 400;
            }
            
            .page-indicator {
                min-width: 32px;
                min-height: 32px;
                border-radius: 16px;
                background: #e5e5e5;
                border: none;
                color: #666;
                font-size: 12px;
                font-weight: 500;
                margin: 0 2px;
            }
            
            .page-indicator:hover {
                background: #d5d5d5;
            }
            
            .page-indicator.active-page {
                background: #007acc;
                color: white;
            }
            
            .dim-label {
                color: #666;
                font-size: 13px;
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
