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
from config.enums import DisplayType, ColourScheme, TransitionMode, OverlayEffect
from logger_setup import setup_logger
from settings_gui_tabs import TextFilesTab, VisualEffectsTab, TransitionsTab, AdvancedTab

logger = setup_logger(__name__)


class SettingsGUI:
    """Main settings GUI application with tabbed interface."""
    
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.settings = Settings.create_default()
        self.widget_bindings = {}  # Map widget -> (settings_path, converter)
        self.status_label = None  # Will be created in _create_control_buttons
        
        # Tab instances will hold references to all tab-specific widgets
        self.text_files_tab: Optional[TextFilesTab] = None
        self.visual_effects_tab: Optional[VisualEffectsTab] = None
        self.transitions_tab: Optional[TransitionsTab] = None
        self.advanced_tab: Optional[AdvancedTab] = None
        
        self._setup_window()
        self._create_tabs()
        self._load_current_settings()
        
    def _setup_window(self) -> None:
        """Configure the main application window."""
        self.root.title("Text Display Screen - Settings")
        self.root.geometry("600x650")
        self.root.resizable(True, True)
        
        # Make window stay on top initially (user can change this)
        self.root.attributes('-topmost', False)
        
        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def _create_slider_with_label(
        self,
        parent: tk.Frame | ttk.Frame | ttk.LabelFrame,
        row: int,
        label_text: str,
        variable: tk.DoubleVar | tk.IntVar,
        from_: float,
        to: float,
        settings_path: str,
        converter: type,
        format_str: str = "{:.3f}",
        column_offset: int = 0,
        label_padx: int = 5,
        pady: int = 5
    ) -> int:
        """Create a slider control with label and live value display.
        
        This helper eliminates the duplicate pattern of creating sliders with
        labels and live value updates that appears 20+ times in this file.
        
        Args:
            parent: Parent frame to contain the slider
            row: Grid row to place slider in
            label_text: Text for the slider label
            variable: tkinter variable bound to the slider
            from_: Minimum slider value
            to: Maximum slider value
            settings_path: Dot-separated path for settings binding
            converter: Type converter function (int, float, etc.)
            format_str: Format string for value display (default: "{:.3f}")
            column_offset: Column offset for positioning (default: 0)
            label_padx: Horizontal padding for label (default: 5, use 20 for indented sliders)
            pady: Vertical padding (default: 5, use 2 for compact layouts)
        
        Returns:
            Next row number (row + 1)
        """
        # Create label
        ttk.Label(parent, text=label_text).grid(
            row=row, column=column_offset, sticky="w", padx=label_padx, pady=pady
        )
        
        # Create slider
        slider = ttk.Scale(
            parent,
            from_=from_,
            to=to,
            orient="horizontal",
            variable=variable,
            length=200
        )
        slider.grid(row=row, column=column_offset + 1, sticky="w", pady=pady)
        
        # Create value label
        value_label = ttk.Label(parent, text="")
        value_label.grid(row=row, column=column_offset + 2, sticky="w", padx=5)
        
        # Create update function for live value display
        def update_label(*args):
            try:
                value = variable.get()
                value_label.config(text=format_str.format(value))
            except (tk.TclError, ValueError):
                value_label.config(text="--")
        
        # Bind update function and call once to set initial value
        variable.trace_add('write', update_label)
        update_label()
        
        # Bind widget to settings path
        self._bind_widget(slider, settings_path, converter)
        
        return row + 1
        
    def _create_tabs(self) -> None:
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
        
        # Create tab content using tab classes
        self.text_files_tab = TextFilesTab(
            parent_frame=self.display_frame,
            settings=self.settings,
            bind_widget_callback=self._bind_widget,
            show_status_callback=self._show_status
        )
        
        self.visual_effects_tab = VisualEffectsTab(
            parent_frame=self.effects_frame,
            settings=self.settings,
            create_slider_callback=self._create_slider_with_label,
            bind_widget_callback=self._bind_widget
        )
        
        self.transitions_tab = TransitionsTab(
            parent_frame=self.transitions_frame,
            settings=self.settings,
            create_slider_callback=self._create_slider_with_label,
            bind_widget_callback=self._bind_widget
        )
        
        self.advanced_tab = AdvancedTab(
            parent_frame=self.advanced_frame,
            settings=self.settings,
            create_slider_callback=self._create_slider_with_label,
            bind_widget_callback=self._bind_widget,
            # Pass shared variables from transitions tab for synchronization
            speed_min_var=self.transitions_tab.speed_min_var,
            speed_max_var=self.transitions_tab.speed_max_var,
            ghost_chance_min_var=self.transitions_tab.ghost_chance_min_var,
            ghost_chance_max_var=self.transitions_tab.ghost_chance_max_var,
            ghost_decay_min_var=self.transitions_tab.ghost_decay_min_var,
            ghost_decay_max_var=self.transitions_tab.ghost_decay_max_var,
            flicker_chance_min_var=self.transitions_tab.flicker_chance_min_var,
            flicker_chance_max_var=self.transitions_tab.flicker_chance_max_var,
            flicker_intensity_min_var=self.transitions_tab.flicker_intensity_min_var,
            flicker_intensity_max_var=self.transitions_tab.flicker_intensity_max_var
        )
        
        # Create control buttons at bottom
        self._create_control_buttons()
        
    def _create_control_buttons(self) -> None:
        """Create control buttons at the bottom of the window."""
        # Status label above buttons (fixed position)
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 0))
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="grey")
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
        
    def _bind_widget(self, widget, settings_path: str, converter: Callable) -> None:
        """Bind a widget to a settings path for manual saving."""
        self.widget_bindings[widget] = (settings_path, converter)
        
    def _update_setting_from_widget(self, widget) -> None:
        """Update settings object when widget value changes.
        
        This method implements the widget-to-settings synchronisation system.
        When a widget is modified, this extracts the value, converts it to the
        appropriate type, and updates the corresponding nested settings attribute.
        
        Process:
        1. Look up the widget's registered settings path and converter function
        2. Extract the value from the widget's associated tkinter variable
        3. Convert the value using the registered converter (e.g., str → enum)
        4. Navigate the nested settings object path (e.g., "overlay.ghost_chance")
        5. Update the final attribute with the converted value
        
        Error Handling:
        - TclError: Catches invalid widget values (e.g., empty string in number field)
        - ValueError: Catches conversion failures, uses default fallback values
        - Prints errors to console without raising (allows GUI to continue)
        
        Settings Path Format:
        - Dot-separated path: "parent.child.attribute"
        - Example: "overlay.ghost_chance" → settings.overlay.ghost_chance
        - Supports arbitrary nesting depth
        
        Widget Binding:
        - Widgets are registered via _bind_widget(widget, path, converter)
        - The large if-elif chain maps paths to their tkinter variables
        - This is a known code smell; future refactoring should use a dictionary
          dispatch pattern (widget_value_getters) - see Phase 2 plan
        """
        if widget not in self.widget_bindings:
            return
            
        settings_path, converter = self.widget_bindings[widget]
        
        try:
            # Get value directly from the associated variable, not the widget
            if settings_path == "transition.shuffle_text_order":
                value = self.text_files_tab.shuffle_text_order_var.get()
            elif settings_path == "overlay.overlay_enabled":
                value = self.visual_effects_tab.overlay_enabled_var.get()
            elif settings_path == "overlay.colour_scheme":
                value = self.visual_effects_tab.colour_scheme_var.get()
            elif settings_path == "overlay.colour_transition_mode":
                value = self.visual_effects_tab.transition_mode_var.get()
            elif settings_path == "overlay.ghost_chance":
                value = self.visual_effects_tab.ghost_chance_var.get()
            elif settings_path == "overlay.ghost_decay":
                value = self.visual_effects_tab.ghost_decay_var.get()
            elif settings_path == "overlay.flicker_chance":
                value = self.visual_effects_tab.flicker_chance_var.get()
            elif settings_path == "overlay.enable_colour_averaging":
                value = self.visual_effects_tab.enable_colour_averaging_var.get()
            elif settings_path == "overlay.colour_averaging_interval":
                try:
                    value = self.visual_effects_tab.colour_averaging_interval_var.get()
                    if value <= 0:
                        value = 30  # Default fallback
                except (tk.TclError, ValueError):
                    value = 30  # Default fallback
            elif settings_path == "transition.transition_speed":
                value = self.transitions_tab.transition_speed_var.get()
            elif settings_path == "transition.text_change_interval":
                try:
                    value = self.transitions_tab.text_change_interval_var.get()
                    if value <= 0:
                        value = 1500  # Default fallback
                except (tk.TclError, ValueError):
                    value = 1500  # Default fallback
            elif settings_path == "transition.blank_time_between_transitions":
                try:
                    value = self.transitions_tab.blank_time_var.get()
                except (tk.TclError, ValueError):
                    value = 0  # Default fallback
            # Effect transition settings
            elif settings_path == "transition.transition_colour_scheme":
                value = self.transitions_tab.transition_colour_scheme_var.get()
            elif settings_path == "transition.colour_scheme_order":
                value = self.transitions_tab.colour_scheme_order_var.get()
            elif settings_path == "transition.transition_colour_mode":
                value = self.transitions_tab.transition_colour_mode_var.get()
            elif settings_path == "transition.colour_mode_order":
                value = self.transitions_tab.colour_mode_order_var.get()
            elif settings_path == "transition.transition_ghost_params":
                value = self.transitions_tab.transition_ghost_params_var.get()
            elif settings_path == "transition.ghost_params_order":
                value = self.transitions_tab.ghost_params_order_var.get()
            elif settings_path == "transition.ghost_chance_min":
                value = self.transitions_tab.ghost_chance_min_var.get()
            elif settings_path == "transition.ghost_chance_max":
                value = self.transitions_tab.ghost_chance_max_var.get()
            elif settings_path == "transition.ghost_decay_min":
                value = self.transitions_tab.ghost_decay_min_var.get()
            elif settings_path == "transition.ghost_decay_max":
                value = self.transitions_tab.ghost_decay_max_var.get()
            elif settings_path == "transition.transition_flicker_params":
                value = self.transitions_tab.transition_flicker_params_var.get()
            elif settings_path == "transition.flicker_params_order":
                value = self.transitions_tab.flicker_params_order_var.get()
            elif settings_path == "transition.flicker_chance_min":
                value = self.transitions_tab.flicker_chance_min_var.get()
            elif settings_path == "transition.flicker_chance_max":
                value = self.transitions_tab.flicker_chance_max_var.get()
            elif settings_path == "transition.flicker_intensity_min":
                value = self.transitions_tab.flicker_intensity_min_var.get()
            elif settings_path == "transition.flicker_intensity_max":
                value = self.transitions_tab.flicker_intensity_max_var.get()
            elif settings_path == "transition.transition_speed_variation":
                value = self.transitions_tab.transition_speed_variation_var.get()
            elif settings_path == "transition.speed_order":
                value = self.transitions_tab.speed_order_var.get()
            elif settings_path == "transition.speed_min":
                value = self.transitions_tab.speed_min_var.get()
            elif settings_path == "transition.speed_max":
                value = self.transitions_tab.speed_max_var.get()
            elif settings_path == "file_monitoring.file_check_interval":
                try:
                    value = self.advanced_tab.file_check_interval_var.get()
                    if value <= 0:
                        value = 60  # Default fallback
                except (tk.TclError, ValueError):
                    value = 60  # Default fallback
            elif settings_path == "debug.debug_output_interval":
                try:
                    value = self.advanced_tab.debug_interval_var.get()
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
            logger.error(f"Error updating setting {settings_path}: {e}")
    
    def _load_current_settings(self) -> None:
        """Load current settings from file if it exists."""
        settings_file = "config/user_settings.json"
        if os.path.exists(settings_file):
            try:
                self.settings = Settings.load_from_file(settings_file)
                self._update_widgets_from_settings()
            except Exception as e:
                logger.error(f"Error loading settings: {e}")
    
    def _update_widgets_from_settings(self) -> None:
        """Update all widgets to reflect current settings values."""
        # Text Files tab
        self.text_files_tab.shuffle_text_order_var.set(self.settings.transition.shuffle_text_order)
        
        # Visual Effects tab
        self.visual_effects_tab.overlay_enabled_var.set(self.settings.overlay.overlay_enabled)
        self.visual_effects_tab.colour_scheme_var.set(self.settings.overlay.colour_scheme.value)
        self.visual_effects_tab.transition_mode_var.set(self.settings.overlay.colour_transition_mode.value)
        self.visual_effects_tab.ghost_chance_var.set(self.settings.overlay.ghost_chance)
        self.visual_effects_tab.ghost_decay_var.set(self.settings.overlay.ghost_decay)
        self.visual_effects_tab.flicker_chance_var.set(self.settings.overlay.flicker_chance)
        self.visual_effects_tab.enable_colour_averaging_var.set(self.settings.overlay.enable_colour_averaging)
        self.visual_effects_tab.colour_averaging_interval_var.set(self.settings.overlay.colour_averaging_interval)
        
        # Transitions tab
        self.transitions_tab.transition_speed_var.set(self.settings.transition.transition_speed)
        self.transitions_tab.text_change_interval_var.set(self.settings.transition.text_change_interval)
        self.transitions_tab.blank_time_var.set(self.settings.transition.blank_time_between_transitions)
        self.transitions_tab.transition_colour_scheme_var.set(self.settings.transition.transition_colour_scheme)
        self.transitions_tab.colour_scheme_order_var.set(self.settings.transition.colour_scheme_order)
        self.transitions_tab.transition_colour_mode_var.set(self.settings.transition.transition_colour_mode)
        self.transitions_tab.colour_mode_order_var.set(self.settings.transition.colour_mode_order)
        self.transitions_tab.transition_ghost_params_var.set(self.settings.transition.transition_ghost_params)
        self.transitions_tab.ghost_params_order_var.set(self.settings.transition.ghost_params_order)
        self.transitions_tab.ghost_chance_min_var.set(self.settings.transition.ghost_chance_min)
        self.transitions_tab.ghost_chance_max_var.set(self.settings.transition.ghost_chance_max)
        self.transitions_tab.ghost_decay_min_var.set(self.settings.transition.ghost_decay_min)
        self.transitions_tab.ghost_decay_max_var.set(self.settings.transition.ghost_decay_max)
        self.transitions_tab.transition_flicker_params_var.set(self.settings.transition.transition_flicker_params)
        self.transitions_tab.flicker_params_order_var.set(self.settings.transition.flicker_params_order)
        self.transitions_tab.flicker_chance_min_var.set(self.settings.transition.flicker_chance_min)
        self.transitions_tab.flicker_chance_max_var.set(self.settings.transition.flicker_chance_max)
        self.transitions_tab.flicker_intensity_min_var.set(self.settings.transition.flicker_intensity_min)
        self.transitions_tab.flicker_intensity_max_var.set(self.settings.transition.flicker_intensity_max)
        self.transitions_tab.transition_speed_variation_var.set(self.settings.transition.transition_speed_variation)
        self.transitions_tab.speed_order_var.set(self.settings.transition.speed_order)
        self.transitions_tab.speed_min_var.set(self.settings.transition.speed_min)
        self.transitions_tab.speed_max_var.set(self.settings.transition.speed_max)
        
        # Advanced tab
        self.advanced_tab.file_check_interval_var.set(self.settings.file_monitoring.file_check_interval)
        self.advanced_tab.debug_interval_var.set(self.settings.debug.debug_output_interval)
        
        # Text file selection - load current selection
        self.text_files_tab._load_current_text_file_selection()
        self.text_files_tab._update_file_info()
    

    
    def _load_demo_settings(self) -> None:
        """Load demo settings preset."""
        self.settings = create_demo_settings()
        self._update_widgets_from_settings()
        self._show_status("Demo settings loaded (press Save to apply)", "blue")
    
    def _load_transgender_settings(self) -> None:
        """Load transgender pride settings preset."""
        self.settings = create_transgender_pride_settings()
        self._update_widgets_from_settings()
        self._show_status("Transgender pride settings loaded (press Save to apply)", "blue")
    
    def _load_performance_settings(self) -> None:
        """Load performance settings preset."""
        self.settings = create_performance_settings()
        self._update_widgets_from_settings()
        self._show_status("Performance settings loaded (press Save to apply)", "blue")
    
    def _load_settings_file(self) -> None:
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
    
    def _save_settings_file(self) -> None:
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
    

    
    def _save_current_settings(self) -> None:
        """Save current settings to file."""
        try:
            # Update settings from all widgets first
            for widget in self.widget_bindings:
                self._update_setting_from_widget(widget)
            
            # Check if text file selection changed
            selected_file = self.text_files_tab.text_file_var.get()
            text_file_changed = selected_file != self.text_files_tab.current_text_file
            
            # Validate and save settings
            is_valid = self.settings.validate()
            if is_valid:
                os.makedirs("config", exist_ok=True)
                self.settings.save_to_file("config/user_settings.json")
                
                # Apply text file change if it changed
                if text_file_changed:
                    self.text_files_tab.current_text_file = selected_file
                    self.text_files_tab._save_text_file_selection()
                    self.text_files_tab._update_file_info()  # Update to show current file info
                    self._show_status(f"Settings saved, text file changed to: {os.path.basename(selected_file)}", "green")
                else:
                    self._show_status("Settings saved", "green")
            else:
                self._show_status("Validation error - check inputs", "red")
        except Exception as e:
            self._show_status(f"Save error: {str(e)}", "red")
    
    def _show_status(self, message: str, colour: str = "black") -> None:
        """Show status message in the GUI without popups or sounds."""
        if self.status_label:
            self.status_label.config(text=message, foreground=colour)
            # Clear status after 3 seconds
            self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground="grey") if self.status_label else None)
    
    
    def run(self) -> None:
        """Start the GUI application."""
        self.root.mainloop()


def main() -> None:
    """Main entry point for the settings GUI."""
    app = SettingsGUI()
    app.run()


if __name__ == "__main__":
    main()