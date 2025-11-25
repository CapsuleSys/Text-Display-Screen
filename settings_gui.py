"""
GUI Settings Application for Text Display Screen

A tkinter-based settings interface that provides intuitive controls for all
display settings, visual effects, and system parameters. Runs independently
alongside the main display application with file-based settings synchronization.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from typing import Optional, Dict, Any, Callable
from config.settings import (
    Settings, 
    create_demo_settings, 
    create_transgender_pride_settings, 
    create_performance_settings
)
from config.enums import DisplayType, ColorScheme, TransitionMode, OverlayEffect


class SettingsGUI:
    """Main settings GUI application with tabbed interface."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.settings = Settings.create_default()
        self.widget_bindings = {}  # Map widget -> (settings_path, converter)
        self.status_label = None  # Will be created in _create_control_buttons
        
        self._setup_window()
        self._create_tabs()
        self._load_current_settings()
        
    def _setup_window(self):
        """Configure the main application window."""
        self.root.title("Text Display Screen - Settings")
        self.root.geometry("600x650")
        self.root.resizable(True, True)
        
        # Make window stay on top initially (user can change this)
        self.root.attributes('-topmost', False)
        
        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    def _create_tabs(self):
        """Create the tabbed interface with all settings categories."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Create tab frames
        self.display_frame = ttk.Frame(self.notebook)
        self.effects_frame = ttk.Frame(self.notebook)
        self.transitions_frame = ttk.Frame(self.notebook)
        self.advanced_frame = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.display_frame, text="Text Files")
        self.notebook.add(self.effects_frame, text="Visual Effects")
        self.notebook.add(self.transitions_frame, text="Transitions")
        self.notebook.add(self.advanced_frame, text="Advanced")
        
        # Create tab content
        self._create_display_tab()
        self._create_effects_tab()
        self._create_transitions_tab()
        self._create_advanced_tab()
        
        # Create control buttons at bottom
        self._create_control_buttons()
        
    def _create_display_tab(self):
        """Create the Text Files tab content."""
        frame = self.display_frame
        row = 0
        
        # Instructions
        ttk.Label(frame, text="Select text file to display:", font=("TkDefaultFont", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1
        
        # Text file selection
        ttk.Label(frame, text="Text File:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        
        # Get available text files
        text_files = self._get_available_text_files()
        self.current_text_file = "TextInputFiles/webcam_background.txt"  # Default
        
        self.text_file_var = tk.StringVar(value=self.current_text_file)
        text_file_combo = ttk.Combobox(frame, textvariable=self.text_file_var, 
                                      values=text_files, width=40, state="readonly")
        text_file_combo.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        text_file_combo.bind('<<ComboboxSelected>>', self._on_text_file_changed)
        row += 1
        
        # Current file info
        ttk.Label(frame, text="Current file info:", font=("TkDefaultFont", 9, "bold")).grid(
            row=row, column=0, sticky="w", padx=5, pady=(15, 5))
        row += 1
        
        self.file_info_label = ttk.Label(frame, text="Loading...", foreground="gray")
        self.file_info_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1
        
        # File preview area
        ttk.Label(frame, text="Preview (first few lines):", font=("TkDefaultFont", 9, "bold")).grid(
            row=row, column=0, sticky="nw", padx=5, pady=(15, 5))
        row += 1
        
        # Text preview with scrollbar
        preview_frame = ttk.Frame(frame)
        preview_frame.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        self.preview_text = tk.Text(preview_frame, height=8, width=50, wrap=tk.WORD, 
                                   state=tk.DISABLED, font=("Courier", 9))
        scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        
        self.preview_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # Load initial file info
        self._update_file_info()
        row += 1
        
        # Shuffle text order checkbox
        ttk.Separator(frame, orient="horizontal").grid(row=row, column=0, columnspan=2,
                                                       sticky="ew", padx=5, pady=10)
        row += 1
        
        self.shuffle_text_order_var = tk.BooleanVar(value=self.settings.transition.shuffle_text_order)
        shuffle_check = ttk.Checkbutton(frame, text="Shuffle text order (process messages in random sequence)",
                                       variable=self.shuffle_text_order_var)
        shuffle_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self._bind_widget(shuffle_check, "transition.shuffle_text_order", bool)
        row += 1
        
    def _create_effects_tab(self):
        """Create the Visual Effects tab content."""
        frame = self.effects_frame
        row = 0
        
        # Overlay Enabled
        self.overlay_enabled_var = tk.BooleanVar(value=self.settings.overlay.overlay_enabled)
        overlay_check = ttk.Checkbutton(frame, text="Enable Overlay Effects", 
                                       variable=self.overlay_enabled_var)
        overlay_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self._bind_widget(overlay_check, "overlay.overlay_enabled", bool)
        row += 1
        
        # Color Scheme
        ttk.Label(frame, text="Color Scheme:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.color_scheme_var = tk.StringVar(value=self.settings.overlay.color_scheme.value)
        color_schemes = ColorScheme.list_names()
        color_combo = ttk.Combobox(frame, textvariable=self.color_scheme_var, 
                                  values=color_schemes, width=20, state="readonly")
        color_combo.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        self._bind_widget(color_combo, "overlay.color_scheme", ColorScheme.from_string)
        row += 1
        
        # Transition Mode
        ttk.Label(frame, text="Transition Mode:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.transition_mode_var = tk.StringVar(value=self.settings.overlay.color_transition_mode.value)
        transition_modes = TransitionMode.list_names()
        transition_combo = ttk.Combobox(frame, textvariable=self.transition_mode_var,
                                       values=transition_modes, width=20, state="readonly")
        transition_combo.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        self._bind_widget(transition_combo, "overlay.color_transition_mode", TransitionMode.from_string)
        row += 1
        
        # Ghost Parameters Section
        ttk.Separator(frame, orient="horizontal").grid(row=row, column=0, columnspan=3, 
                                                       sticky="ew", padx=5, pady=10)
        row += 1
        ttk.Label(frame, text="Ghost Effect Parameters", font=("TkDefaultFont", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1
        
        # Ghost Chance
        ttk.Label(frame, text="Ghost Chance:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.ghost_chance_var = tk.DoubleVar(value=self.settings.overlay.ghost_chance)
        ghost_chance_scale = ttk.Scale(frame, from_=0.0, to=1.0, orient="horizontal",
                                      variable=self.ghost_chance_var, length=200)
        ghost_chance_scale.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        ghost_chance_label = ttk.Label(frame, text="")
        ghost_chance_label.grid(row=row, column=2, sticky="w", padx=5)
        
        def update_ghost_chance_label(*args):
            try:
                value = self.ghost_chance_var.get()
                ghost_chance_label.config(text=f"{value:.3f}")
            except (tk.TclError, ValueError):
                ghost_chance_label.config(text="--")
        self.ghost_chance_var.trace_add('write', update_ghost_chance_label)
        update_ghost_chance_label()
        
        self._bind_widget(ghost_chance_scale, "overlay.ghost_chance", float)
        row += 1
        
        # Ghost Decay
        ttk.Label(frame, text="Ghost Decay:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.ghost_decay_var = tk.DoubleVar(value=self.settings.overlay.ghost_decay)
        ghost_decay_scale = ttk.Scale(frame, from_=0.9, to=1.0, orient="horizontal",
                                     variable=self.ghost_decay_var, length=200)
        ghost_decay_scale.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        ghost_decay_label = ttk.Label(frame, text="")
        ghost_decay_label.grid(row=row, column=2, sticky="w", padx=5)
        
        def update_ghost_decay_label(*args):
            try:
                value = self.ghost_decay_var.get()
                ghost_decay_label.config(text=f"{value:.3f}")
            except (tk.TclError, ValueError):
                ghost_decay_label.config(text="--")
        self.ghost_decay_var.trace_add('write', update_ghost_decay_label)
        update_ghost_decay_label()
        
        self._bind_widget(ghost_decay_scale, "overlay.ghost_decay", float)
        row += 1
        
        # Flicker Parameters Section
        ttk.Separator(frame, orient="horizontal").grid(row=row, column=0, columnspan=3,
                                                       sticky="ew", padx=5, pady=10)
        row += 1
        ttk.Label(frame, text="Flicker Effect Parameters", font=("TkDefaultFont", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1
        
        # Flicker Chance
        ttk.Label(frame, text="Flicker Chance:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.flicker_chance_var = tk.DoubleVar(value=self.settings.overlay.flicker_chance)
        flicker_chance_scale = ttk.Scale(frame, from_=0.0, to=0.2, orient="horizontal",
                                        variable=self.flicker_chance_var, length=200)
        flicker_chance_scale.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        flicker_chance_label = ttk.Label(frame, text="")
        flicker_chance_label.grid(row=row, column=2, sticky="w", padx=5)
        
        def update_flicker_chance_label(*args):
            try:
                value = self.flicker_chance_var.get()
                flicker_chance_label.config(text=f"{value:.3f}")
            except (tk.TclError, ValueError):
                flicker_chance_label.config(text="--")
        self.flicker_chance_var.trace_add('write', update_flicker_chance_label)
        update_flicker_chance_label()
        
        self._bind_widget(flicker_chance_scale, "overlay.flicker_chance", float)
        row += 1
        
    def _create_transitions_tab(self):
        """Create the Transitions tab content."""
        frame = self.transitions_frame
        row = 0
        
        # Transition Speed
        ttk.Label(frame, text="Transition Speed (px/frame):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.transition_speed_var = tk.DoubleVar(value=self.settings.transition.transition_speed)
        transition_speed_scale = ttk.Scale(frame, from_=0.1, to=50.0, orient="horizontal",
                                          variable=self.transition_speed_var, length=300)
        transition_speed_scale.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        transition_speed_label = ttk.Label(frame, text="")
        transition_speed_label.grid(row=row, column=2, sticky="w", padx=5)
        
        def update_transition_speed_label(*args):
            try:
                value = self.transition_speed_var.get()
                transition_speed_label.config(text=f"{value:.1f}")
            except (tk.TclError, ValueError):
                transition_speed_label.config(text="--")
        self.transition_speed_var.trace_add('write', update_transition_speed_label)
        update_transition_speed_label()
        
        self._bind_widget(transition_speed_scale, "transition.transition_speed", float)
        row += 1
        
        # Text Change Interval
        ttk.Label(frame, text="Text Change Interval (frames):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.text_change_interval_var = tk.IntVar(value=self.settings.transition.text_change_interval)
        text_change_spin = ttk.Spinbox(frame, from_=60, to=18000, textvariable=self.text_change_interval_var, 
                                      width=15)
        text_change_spin.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        # Show seconds equivalent
        text_change_seconds_label = ttk.Label(frame, text="")
        text_change_seconds_label.grid(row=row, column=2, sticky="w", padx=5)
        
        def update_text_change_seconds(*args):
            try:
                frames = self.text_change_interval_var.get()
                if frames > 0:
                    seconds = frames / 60  # Assuming 60 FPS
                    text_change_seconds_label.config(text=f"({seconds:.1f}s @ 60fps)")
                else:
                    text_change_seconds_label.config(text="(0.0s @ 60fps)")
            except (tk.TclError, ValueError):
                text_change_seconds_label.config(text="(-- s @ 60fps)")
        self.text_change_interval_var.trace_add('write', update_text_change_seconds)
        update_text_change_seconds()
        
        self._bind_widget(text_change_spin, "transition.text_change_interval", int)
        row += 1
        
        # Blank Time Between Transitions
        ttk.Label(frame, text="Blank Time Between Transitions (frames):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.blank_time_var = tk.IntVar(value=self.settings.transition.blank_time_between_transitions)
        blank_time_scale = ttk.Scale(frame, from_=0, to=600, orient="horizontal",
                                    variable=self.blank_time_var, length=300)
        blank_time_scale.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        blank_time_label = ttk.Label(frame, text="")
        blank_time_label.grid(row=row, column=2, sticky="w", padx=5)
        
        def update_blank_time_label(*args):
            try:
                frames = self.blank_time_var.get()
                seconds = frames / 60  # Assuming 60 FPS
                blank_time_label.config(text=f"{frames} ({seconds:.1f}s @ 60fps)")
            except (tk.TclError, ValueError):
                blank_time_label.config(text="0 (0.0s @ 60fps)")
        self.blank_time_var.trace_add('write', update_blank_time_label)
        update_blank_time_label()
        
        self._bind_widget(blank_time_scale, "transition.blank_time_between_transitions", int)
        row += 1
        
    def _create_advanced_tab(self):
        """Create the Advanced tab content."""
        frame = self.advanced_frame
        row = 0
        
        # File Monitoring Section
        ttk.Label(frame, text="File Monitoring", font=("TkDefaultFont", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1
        
        # File Check Interval
        ttk.Label(frame, text="File Check Interval (frames):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.file_check_interval_var = tk.IntVar(value=self.settings.file_monitoring.file_check_interval)
        file_check_spin = ttk.Spinbox(frame, from_=30, to=1800, textvariable=self.file_check_interval_var,
                                     width=15)
        file_check_spin.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        self._bind_widget(file_check_spin, "file_monitoring.file_check_interval", int)
        row += 1
        
        # Debug Section
        ttk.Separator(frame, orient="horizontal").grid(row=row, column=0, columnspan=3,
                                                       sticky="ew", padx=5, pady=10)
        row += 1
        ttk.Label(frame, text="Debug Settings", font=("TkDefaultFont", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1
        
        # Debug Output Interval
        ttk.Label(frame, text="Debug Output Interval (frames):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.debug_interval_var = tk.IntVar(value=self.settings.debug.debug_output_interval)
        debug_spin = ttk.Spinbox(frame, from_=60, to=3600, textvariable=self.debug_interval_var, width=15)
        debug_spin.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        self._bind_widget(debug_spin, "debug.debug_output_interval", int)
        row += 1
        
    def _create_control_buttons(self):
        """Create control buttons at the bottom of the window."""
        # Status label above buttons (fixed position)
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 0))
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="gray")
        self.status_label.pack(side="left")
        
        # Button frame below status
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5))
        
        # Preset buttons
        ttk.Button(button_frame, text="Demo Settings", 
                  command=self._load_demo_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Transgender Pride", 
                  command=self._load_transgender_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Performance", 
                  command=self._load_performance_settings).pack(side="left", padx=5)
        
        # Save button
        ttk.Button(button_frame, text="Save Settings", 
                  command=self._save_current_settings).pack(side="right", padx=5)
        
    def _bind_widget(self, widget, settings_path: str, converter: Callable):
        """Bind a widget to a settings path for manual saving."""
        self.widget_bindings[widget] = (settings_path, converter)
        
    def _update_setting_from_widget(self, widget):
        """Update settings object when widget value changes."""
        if widget not in self.widget_bindings:
            return
            
        settings_path, converter = self.widget_bindings[widget]
        
        try:
            # Get value directly from the associated variable, not the widget
            if settings_path == "transition.shuffle_text_order":
                value = self.shuffle_text_order_var.get()
            elif settings_path == "overlay.overlay_enabled":
                value = self.overlay_enabled_var.get()
            elif settings_path == "overlay.color_scheme":
                value = self.color_scheme_var.get()
            elif settings_path == "overlay.color_transition_mode":
                value = self.transition_mode_var.get()
            elif settings_path == "overlay.ghost_chance":
                value = self.ghost_chance_var.get()
            elif settings_path == "overlay.ghost_decay":
                value = self.ghost_decay_var.get()
            elif settings_path == "overlay.flicker_chance":
                value = self.flicker_chance_var.get()
            elif settings_path == "transition.transition_speed":
                value = self.transition_speed_var.get()
            elif settings_path == "transition.text_change_interval":
                try:
                    value = self.text_change_interval_var.get()
                    if value <= 0:
                        value = 1500  # Default fallback
                except (tk.TclError, ValueError):
                    value = 1500  # Default fallback
            elif settings_path == "transition.blank_time_between_transitions":
                try:
                    value = self.blank_time_var.get()
                except (tk.TclError, ValueError):
                    value = 0  # Default fallback
            elif settings_path == "file_monitoring.file_check_interval":
                try:
                    value = self.file_check_interval_var.get()
                    if value <= 0:
                        value = 60  # Default fallback
                except (tk.TclError, ValueError):
                    value = 60  # Default fallback
            elif settings_path == "debug.debug_output_interval":
                try:
                    value = self.debug_interval_var.get()
                    if value <= 0:
                        value = 300  # Default fallback
                except (tk.TclError, ValueError):
                    value = 300  # Default fallback
            else:
                # Fallback for any other widgets
                if isinstance(widget, (ttk.Spinbox, ttk.Combobox)):
                    value = widget.get()
                else:
                    return
            
            # Convert value
            converted_value = converter(value)
            
            # Set value in settings using path
            obj = self.settings
            path_parts = settings_path.split('.')
            for part in path_parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, path_parts[-1], converted_value)
            
        except Exception as e:
            print(f"Error updating setting {settings_path}: {e}")
    
    def _load_current_settings(self):
        """Load current settings from file if it exists."""
        settings_file = "config/user_settings.json"
        if os.path.exists(settings_file):
            try:
                self.settings = Settings.load_from_file(settings_file)
                self._update_widgets_from_settings()
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def _update_widgets_from_settings(self):
        """Update all widgets to reflect current settings values."""
        # Overlay settings
        self.overlay_enabled_var.set(self.settings.overlay.overlay_enabled)
        self.color_scheme_var.set(self.settings.overlay.color_scheme.value)
        self.transition_mode_var.set(self.settings.overlay.color_transition_mode.value)
        self.ghost_chance_var.set(self.settings.overlay.ghost_chance)
        self.ghost_decay_var.set(self.settings.overlay.ghost_decay)
        self.flicker_chance_var.set(self.settings.overlay.flicker_chance)
        
        # Transition settings
        self.transition_speed_var.set(self.settings.transition.transition_speed)
        self.text_change_interval_var.set(self.settings.transition.text_change_interval)
        self.blank_time_var.set(self.settings.transition.blank_time_between_transitions)
        self.shuffle_text_order_var.set(self.settings.transition.shuffle_text_order)
        
        # Advanced settings
        self.file_check_interval_var.set(self.settings.file_monitoring.file_check_interval)
        self.debug_interval_var.set(self.settings.debug.debug_output_interval)
        
        # Text file selection - load current selection
        self._load_current_text_file_selection()
        self._update_file_info()
    

    
    def _load_demo_settings(self):
        """Load demo settings preset."""
        self.settings = create_demo_settings()
        self._update_widgets_from_settings()
        self._show_status("Demo settings loaded (press Save to apply)", "blue")
    
    def _load_transgender_settings(self):
        """Load transgender pride settings preset."""
        self.settings = create_transgender_pride_settings()
        self._update_widgets_from_settings()
        self._show_status("Transgender pride settings loaded (press Save to apply)", "blue")
    
    def _load_performance_settings(self):
        """Load performance settings preset."""
        self.settings = create_performance_settings()
        self._update_widgets_from_settings()
        self._show_status("Performance settings loaded (press Save to apply)", "blue")
    
    def _load_settings_file(self):
        """Load settings from a file dialog."""
        filename = filedialog.askopenfilename(
            title="Load Settings File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="config"
        )
        if filename:
            try:
                self.settings = Settings.load_from_file(filename)
                self._update_widgets_from_settings()
                self._show_status(f"Loaded: {os.path.basename(filename)}", "green")
            except Exception as e:
                self._show_status(f"Error loading: {str(e)}", "red")
    
    def _save_settings_file(self):
        """Save settings to a file dialog."""
        filename = filedialog.asksaveasfilename(
            title="Save Settings File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="config",
            defaultextension=".json"
        )
        if filename:
            try:
                self.settings.save_to_file(filename)
                self._show_status(f"Saved: {os.path.basename(filename)}", "green")
            except Exception as e:
                self._show_status(f"Error saving: {str(e)}", "red")
    

    
    def _save_current_settings(self):
        """Save current settings to file."""
        try:
            # Update settings from all widgets first
            for widget in self.widget_bindings:
                self._update_setting_from_widget(widget)
            
            # Check if text file selection changed
            selected_file = self.text_file_var.get()
            text_file_changed = selected_file != self.current_text_file
            
            # Validate and save settings
            is_valid = self.settings.validate()
            if is_valid:
                os.makedirs("config", exist_ok=True)
                self.settings.save_to_file("config/user_settings.json")
                
                # Apply text file change if it changed
                if text_file_changed:
                    self.current_text_file = selected_file
                    self._save_text_file_selection()
                    self._update_file_info()  # Update to show current file info
                    self._show_status(f"Settings saved, text file changed to: {os.path.basename(selected_file)}", "green")
                else:
                    self._show_status("Settings saved", "green")
            else:
                self._show_status("Validation error - check inputs", "red")
        except Exception as e:
            self._show_status(f"Save error: {str(e)}", "red")
    
    def _show_status(self, message: str, color: str = "black"):
        """Show status message in the GUI without popups or sounds."""
        if self.status_label:
            self.status_label.config(text=message, foreground=color)
            # Clear status after 3 seconds
            self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground="gray") if self.status_label else None)
    
    def _get_available_text_files(self):
        """Get list of available text files."""
        text_files = []
        text_dir = "TextInputFiles"
        if os.path.exists(text_dir):
            for file in os.listdir(text_dir):
                if file.endswith('.txt'):
                    text_files.append(os.path.join(text_dir, file))
        return text_files
    
    def _on_text_file_changed(self, event=None):
        """Handle text file selection change."""
        new_file = self.text_file_var.get()
        if new_file != self.current_text_file:
            # Just update the preview, don't save yet
            self._update_file_info_for_file(new_file)
            self._show_status(f"Previewing: {os.path.basename(new_file)} (press Save to apply)", "orange")
    
    def _update_file_info(self):
        """Update file info and preview for current text file."""
        self._update_file_info_for_file(self.current_text_file)
    
    def _update_file_info_for_file(self, file_path):
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
    
    def _update_preview(self, text):
        """Update the preview text widget."""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, text)
        self.preview_text.config(state=tk.DISABLED)
    
    def _save_text_file_selection(self):
        """Save the selected text file to a separate config file for the main app."""
        try:
            os.makedirs("config", exist_ok=True)
            with open("config/current_text_file.txt", 'w') as f:
                f.write(self.current_text_file)
        except Exception as e:
            self._show_status(f"Error saving text file selection: {e}", "red")
    
    def _load_current_text_file_selection(self):
        """Load the current text file selection from config."""
        try:
            if os.path.exists("config/current_text_file.txt"):
                with open("config/current_text_file.txt", 'r', encoding='utf-8') as f:
                    saved_file = f.read().strip()
                if os.path.exists(saved_file):
                    self.current_text_file = saved_file
                    self.text_file_var.set(saved_file)
        except Exception as e:
            print(f"Error loading text file selection: {e}")
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point for the settings GUI."""
    app = SettingsGUI()
    app.run()


if __name__ == "__main__":
    main()