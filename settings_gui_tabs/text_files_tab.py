"""
Text Files tab for Settings GUI.

Handles text file selection, preview, and shuffle settings.
"""

import tkinter as tk
from tkinter import ttk
import os
from typing import Callable


class TextFilesTab:
    """Text files tab content and logic."""
    
    def __init__(
        self,
        parent_frame: ttk.Frame,
        settings,
        bind_widget_callback: Callable,
        show_status_callback: Callable
    ):
        """Initialise the text files tab.
        
        Args:
            parent_frame: Parent ttk.Frame to contain tab content
            settings: Settings instance
            bind_widget_callback: Callback for binding widgets to settings
            show_status_callback: Callback for showing status messages
        """
        self.frame = parent_frame
        self.settings = settings
        self._bind_widget = bind_widget_callback
        self._show_status = show_status_callback
        
        self.current_text_file = "TextInputFiles/webcam_background.txt"  # Default
        self.text_file_var = None
        self.file_info_label = None
        self.preview_text = None
        self.shuffle_text_order_var = None
        
        self._create_content()
    
    def _create_content(self) -> None:
        """Create the tab content."""
        row = 0
        
        # Instructions
        ttk.Label(self.frame, text="Select text file to display:", 
                 font=("TkDefaultFont", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1
        
        # Text file selection
        ttk.Label(self.frame, text="Text File:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5)
        
        # Get available text files
        text_files = self._get_available_text_files()
        
        self.text_file_var = tk.StringVar(value=self.current_text_file)
        text_file_combo = ttk.Combobox(
            self.frame, 
            textvariable=self.text_file_var,
            values=text_files, 
            width=40, 
            state="readonly"
        )
        text_file_combo.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        text_file_combo.bind('<<ComboboxSelected>>', self._on_text_file_changed)
        row += 1
        
        # Current file info
        ttk.Label(self.frame, text="Current file info:", 
                 font=("TkDefaultFont", 9, "bold")).grid(
            row=row, column=0, sticky="w", padx=5, pady=(15, 5))
        row += 1
        
        self.file_info_label = ttk.Label(self.frame, text="Loading...", 
                                        foreground="grey")
        self.file_info_label.grid(row=row, column=0, columnspan=2, 
                                 sticky="w", padx=5, pady=5)
        row += 1
        
        # File preview area
        ttk.Label(self.frame, text="Preview (first few lines):", 
                 font=("TkDefaultFont", 9, "bold")).grid(
            row=row, column=0, sticky="nw", padx=5, pady=(15, 5))
        row += 1
        
        # Text preview with scrollbar
        preview_frame = ttk.Frame(self.frame)
        preview_frame.grid(row=row, column=0, columnspan=2, 
                          sticky="nsew", padx=5, pady=5)
        
        self.preview_text = tk.Text(
            preview_frame, 
            height=8, 
            width=50, 
            wrap=tk.WORD,
            state=tk.DISABLED, 
            font=("Courier", 9)
        )
        scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", 
                                 command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        
        self.preview_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # Load initial file info
        self._load_current_text_file_selection()
        self._update_file_info()
        row += 1
        
        # Shuffle text order checkbox
        ttk.Separator(self.frame, orient="horizontal").grid(
            row=row, column=0, columnspan=2,
            sticky="ew", padx=5, pady=10)
        row += 1
        
        self.shuffle_text_order_var = tk.BooleanVar(
            value=self.settings.transition.shuffle_text_order
        )
        shuffle_check = ttk.Checkbutton(
            self.frame,
            text="Shuffle text order (process messages in random sequence)",
            variable=self.shuffle_text_order_var
        )
        shuffle_check.grid(row=row, column=0, columnspan=2, 
                          sticky="w", padx=5, pady=5)
        self._bind_widget(shuffle_check, "transition.shuffle_text_order", bool)
        row += 1
    
    def _get_available_text_files(self) -> list[str]:
        """Get list of available text files."""
        text_files = []
        text_dir = "TextInputFiles"
        if os.path.exists(text_dir):
            for file in os.listdir(text_dir):
                if file.endswith('.txt'):
                    text_files.append(os.path.join(text_dir, file))
        return text_files
    
    def _on_text_file_changed(self, event=None) -> None:
        """Handle text file selection change."""
        new_file = self.text_file_var.get()
        if new_file != self.current_text_file:
            # Just update the preview, don't save yet
            self._update_file_info_for_file(new_file)
            self._show_status(
                f"Previewing: {os.path.basename(new_file)} (press Save to apply)",
                "orange"
            )
    
    def _update_file_info(self) -> None:
        """Update file info and preview for current text file."""
        self._update_file_info_for_file(self.current_text_file)
    
    def _update_file_info_for_file(self, file_path: str) -> None:
        """Update file info and preview for specified file."""
        if not os.path.exists(file_path):
            self.file_info_label.config(text="File not found")
            self._update_preview("File not found")
            return
        
        try:
            # Get file stats
            file_size = os.path.getsize(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                line_count = len(content.split('\n\n'))  # Count text blocks
                char_count = len(content)
            
            info = f"Size: {file_size} bytes | Blocks: {line_count} | Characters: {char_count}"
            self.file_info_label.config(text=info)
            
            # Update preview
            preview_lines = content.split('\n')[:20]  # First 20 lines
            preview = '\n'.join(preview_lines)
            if len(content.split('\n')) > 20:
                preview += "\n\n... (truncated)"
            self._update_preview(preview)
            
        except Exception as e:
            self.file_info_label.config(text=f"Error reading file: {e}")
            self._update_preview(f"Error: {e}")
    
    def _update_preview(self, text: str) -> None:
        """Update the preview text widget."""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, text)
        self.preview_text.config(state=tk.DISABLED)
    
    def _load_current_text_file_selection(self) -> None:
        """Load the current text file selection from config."""
        try:
            if os.path.exists("config/current_text_file.txt"):
                with open("config/current_text_file.txt", 'r', encoding='utf-8') as f:
                    saved_file = f.read().strip()
                if os.path.exists(saved_file):
                    self.current_text_file = saved_file
                    if self.text_file_var:
                        self.text_file_var.set(saved_file)
        except Exception as e:
            # Just use default if loading fails
            pass
    
    def _save_text_file_selection(self) -> None:
        """Save the selected text file to a separate config file for the main app."""
        try:
            os.makedirs("config", exist_ok=True)
            with open("config/current_text_file.txt", 'w') as f:
                f.write(self.current_text_file)
        except Exception as e:
            self._show_status(f"Error saving text file selection: {e}", "red")
