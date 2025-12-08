"""Advanced tab for the settings GUI.

This module contains the AdvancedTab class which handles advanced settings
including file monitoring, debug configuration, and duplicated effect transition
range controls for convenient fine-tuning.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Any


class AdvancedTab:
    """Manages the advanced settings tab.
    
    This tab serves dual purposes:
    1. Standalone advanced settings (file monitoring, debug logging)
    2. Duplicated effect transition range controls from Transitions tab
    
    The duplication exists for user convenience - advanced users can fine-tune
    effect variation ranges here without switching tabs. The same tkinter
    variables are used, so changes in either tab are synchronized.
    
    Sections:
    - File Monitoring: How often to check for text file changes
    - Debug Settings: Logging level configuration
    - Speed Variation: Min/max transition speed range (duplicated)
    - Ghost Parameter Ranges: Chance/decay variation (duplicated)
    - Flicker Parameter Ranges: Chance/intensity variation (duplicated)
    """
    
    def __init__(
        self,
        parent_frame: ttk.Frame,
        settings: Any,
        create_slider_callback: Callable,
        bind_widget_callback: Callable,
        # Shared variables from transitions tab for synchronization
        speed_min_var: tk.DoubleVar,
        speed_max_var: tk.DoubleVar,
        ghost_chance_min_var: tk.DoubleVar,
        ghost_chance_max_var: tk.DoubleVar,
        ghost_decay_min_var: tk.DoubleVar,
        ghost_decay_max_var: tk.DoubleVar,
        flicker_chance_min_var: tk.DoubleVar,
        flicker_chance_max_var: tk.DoubleVar,
        flicker_intensity_min_var: tk.DoubleVar,
        flicker_intensity_max_var: tk.DoubleVar
    ):
        """Initialize the advanced tab.
        
        Args:
            parent_frame: The parent frame to place this tab's content in
            settings: The settings object containing all configuration
            create_slider_callback: Callback to create sliders with labels
            bind_widget_callback: Callback to bind widgets to settings
            speed_min_var: Shared variable for speed min (from transitions tab)
            speed_max_var: Shared variable for speed max (from transitions tab)
            ghost_chance_min_var: Shared variable for ghost chance min (from transitions tab)
            ghost_chance_max_var: Shared variable for ghost chance max (from transitions tab)
            ghost_decay_min_var: Shared variable for ghost decay min (from transitions tab)
            ghost_decay_max_var: Shared variable for ghost decay max (from transitions tab)
            flicker_chance_min_var: Shared variable for flicker chance min (from transitions tab)
            flicker_chance_max_var: Shared variable for flicker chance max (from transitions tab)
            flicker_intensity_min_var: Shared variable for flicker intensity min (from transitions tab)
            flicker_intensity_max_var: Shared variable for flicker intensity max (from transitions tab)
        """
        self.frame = parent_frame
        self.settings = settings
        self._create_slider = create_slider_callback
        self._bind_widget = bind_widget_callback
        
        # Store shared variables from transitions tab
        self.speed_min_var = speed_min_var
        self.speed_max_var = speed_max_var
        self.ghost_chance_min_var = ghost_chance_min_var
        self.ghost_chance_max_var = ghost_chance_max_var
        self.ghost_decay_min_var = ghost_decay_min_var
        self.ghost_decay_max_var = ghost_decay_max_var
        self.flicker_chance_min_var = flicker_chance_min_var
        self.flicker_chance_max_var = flicker_chance_max_var
        self.flicker_intensity_min_var = flicker_intensity_min_var
        self.flicker_intensity_max_var = flicker_intensity_max_var
        
        # Store tab-specific variables
        self.file_check_interval_var: tk.IntVar
        self.debug_interval_var: tk.IntVar
        
        self._create_content()
    
    def _create_content(self) -> None:
        """Create all the content for the advanced tab."""
        frame = self.frame
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
        
        # Effect Transition Ranges Section
        ttk.Separator(frame, orient="horizontal").grid(row=row, column=0, columnspan=3,
                                                       sticky="ew", padx=5, pady=10)
        row += 1
        
        effect_ranges_frame = ttk.LabelFrame(frame, text="Effect Transition Parameter Ranges", padding=10)
        effect_ranges_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        row += 1
        
        ttk.Label(effect_ranges_frame, text="Configure min/max bounds for random effect transitions",
                 font=("TkDefaultFont", 9)).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        # Speed variation ranges
        ttk.Label(effect_ranges_frame, text="Speed Variation", font=("TkDefaultFont", 9, "bold")).grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(5, 2))
        
        self._create_slider(
            effect_ranges_frame, 2, "Speed Min (px/frame):",
            self.speed_min_var, 0.1, 50.0,
            "transition.speed_min", float,
            format_str="{:.1f}", label_padx=20, pady=2
        )
        
        self._create_slider(
            effect_ranges_frame, 3, "Speed Max (px/frame):",
            self.speed_max_var, 0.1, 50.0,
            "transition.speed_max", float,
            format_str="{:.1f}", label_padx=20, pady=2
        )
        
        # Ghost parameter ranges
        ttk.Label(effect_ranges_frame, text="Ghost Parameters", font=("TkDefaultFont", 9, "bold")).grid(
            row=4, column=0, columnspan=3, sticky="w", pady=(10, 2))
        
        self._create_slider(
            effect_ranges_frame, 5, "Ghost Chance Min:",
            self.ghost_chance_min_var, 0.0, 1.0,
            "transition.ghost_chance_min", float,
            label_padx=20, pady=2
        )
        
        self._create_slider(
            effect_ranges_frame, 6, "Ghost Chance Max:",
            self.ghost_chance_max_var, 0.0, 1.0,
            "transition.ghost_chance_max", float,
            label_padx=20, pady=2
        )
        
        self._create_slider(
            effect_ranges_frame, 7, "Ghost Decay Min:",
            self.ghost_decay_min_var, 0.9, 1.0,
            "transition.ghost_decay_min", float,
            format_str="{:.4f}", label_padx=20, pady=2
        )
        
        self._create_slider(
            effect_ranges_frame, 8, "Ghost Decay Max:",
            self.ghost_decay_max_var, 0.9, 1.0,
            "transition.ghost_decay_max", float,
            format_str="{:.4f}", label_padx=20, pady=2
        )
        
        # Flicker parameter ranges
        ttk.Label(effect_ranges_frame, text="Flicker Parameters", font=("TkDefaultFont", 9, "bold")).grid(
            row=9, column=0, columnspan=3, sticky="w", pady=(10, 2))
        
        self._create_slider(
            effect_ranges_frame, 10, "Flicker Chance Min:",
            self.flicker_chance_min_var, 0.0, 0.2,
            "transition.flicker_chance_min", float,
            label_padx=20, pady=2
        )
        
        self._create_slider(
            effect_ranges_frame, 11, "Flicker Chance Max:",
            self.flicker_chance_max_var, 0.0, 0.2,
            "transition.flicker_chance_max", float,
            label_padx=20, pady=2
        )
        
        self._create_slider(
            effect_ranges_frame, 12, "Flicker Intensity Min:",
            self.flicker_intensity_min_var, 0.0, 1.0,
            "transition.flicker_intensity_min", float,
            label_padx=20, pady=2
        )
        
        self._create_slider(
            effect_ranges_frame, 13, "Flicker Intensity Max:",
            self.flicker_intensity_max_var, 0.0, 1.0,
            "transition.flicker_intensity_max", float,
            label_padx=20, pady=2
        )
